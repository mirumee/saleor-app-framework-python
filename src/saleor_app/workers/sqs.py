import asyncio
import logging
from typing import Any, List, Union

import boto3
from pydantic import ValidationError

from saleor_app.settings import AWSSettings
from saleor_app.workers.base import SaleorAppWorker
from saleor_app.workers.errors import (
    NonTransientError,
    TransientError,
    UnrecognizedEventPayload,
)

logger = logging.getLogger(__name__)


class SaleorAppSQSWorker(SaleorAppWorker):
    def __init__(
        self,
        queue_name: str,
        max_number_of_messages: int = 1,
        wait_time_seconds: int = 0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.transient_error_wait_seconds = 5
        self.queue_name = queue_name
        self.max_number_of_messages = max_number_of_messages
        self.wait_time_seconds = wait_time_seconds

    async def process_message(
        self, message
    ):  # TODO: figure out the type of a message and mark that as the return type
        try:
            webhook = self.parse_webhook_payload(message_body=message.body)
        except ValidationError:
            raise UnrecognizedEventPayload(
                "The message body was not recognized", message=message
            )

        # TODO: allow to decide if not recognized events should be ignored or dead lettered
        handler = (
            self.handlers.get()
        )  # TODO: figure out how to get an event_type from a message, is it in the message? if not add to webhook meta?
        await handler(webhook, message)
        return message

    async def handle_non_transient_error(self, message, exc):
        """
        This handler will do nothing, thus allowing the loop to exhaust the
        attempts of a message retrieval which will result in a SQS dead letter
        """
        return

    async def handle_transient_error(self, message, exc):
        while True:
            logger.warning(
                "Transient error occured halting, will retry again in %s seconds",
                self.transient_error_wait_seconds,
                exc_info=exc,
            )
            asyncio.sleep(self.transient_error_wait_seconds)
            try:
                await self.process_message(message)
            except TransientError as new_exc:
                exc = new_exc
            else:
                break

    async def handle_unhandled_exceptions(self, exc):
        """
        This handler will do nothing, thus allowing the loop to exhaust the
        attempts of a message retrieval which will result in a SQS dead letter
        """
        # This should not happen, that's why it's critical
        logger.critical(
            "Failed to handle a message, message will be put in SQS deadletter",
            exc_info=exc,
        )
        return

    async def loop(self):
        aws_settings: AWSSettings = self.app.settings.aws
        sqs = boto3.resource(
            "sqs",
            region_name=aws_settings.region,
            endpoint_url=aws_settings.endpoint_url,
            aws_access_key_id=aws_settings.access_key_id,
            aws_secret_access_key=aws_settings.secret_access_key,
        )
        sqs_queue = sqs.get_queue_by_name(QueueName=self.queue_name)

        while True:
            messages = sqs_queue.receive_messages(
                MaxNumberOfMessages=self.max_number_of_messages,
                WaitTimeSeconds=self.wait_time_seconds,
            )
            coros = [self.process_message(message) for message in messages]
            results: List[Union[Any, Exception]] = asyncio.gather(
                *coros, return_exceptions=True
            )  # TODO: figure out the type of a message and put it instead of Any
            successful_results = []
            for result in results:
                if isinstance(result, TransientError):
                    await self.handle_transient_error(result.message, result)
                elif isinstance(result, NonTransientError):
                    await self.handle_non_transient_error(result.message, result)
                elif isinstance(result, Exception):
                    await self.handle_unhandled_exceptions(result)
                else:
                    successful_results.append(result)

            for message in successful_results:
                message.delete()
