import asyncio
import logging
from signal import signal, SIGINT, SIGTERM

from saleor_app.app import SaleorApp
from saleor_app.schemas.webhook import Webhook

logger = logging.getLogger(__name__)


class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        self.received_signal = True


class SaleorAppWorker:
    def __init__(self, app: SaleorApp):
        self.app = app
        self.handlers = {
            name: handler for name, handler in self.app.sqs_webhook_handlers if handler
        }

    async def parse_webhook_payload(self, message_body):
        return Webhook.parse_raw(message_body)

    async def loop(self, queue_name: str):
        raise NotImplementedError()

    async def run(self, queue_name: str):
        signal_handler = SignalHandler()
        while not signal_handler.received_signal:
            logger.info("Starting the loop")
            try:
                await self.loop(queue_name=queue_name)
            except Exception as exc:
                logger.critical("The loop exited with an error, will run the loop again in 60 seconds", exc_info=exc)
                asyncio.sleep(60)
        logger.info("Stopping the loop")
