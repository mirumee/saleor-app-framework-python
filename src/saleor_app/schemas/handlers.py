from typing import Awaitable, Callable, List, Optional

from pydantic import AnyHttpUrl, BaseModel, create_model

from saleor_app.schemas.core import DomainName
from saleor_app.schemas.webhook import Webhook

SALEOR_EVENT_TYPES = (
    "ORDER_CREATED",
    "ORDER_CONFIRMED",
    "ORDER_FULLY_PAID",
    "ORDER_UPDATED",
    "ORDER_CANCELLED",
    "ORDER_FULFILLED",
    "DRAFT_ORDER_CREATED",
    "DRAFT_ORDER_UPDATED",
    "DRAFT_ORDER_DELETED",
    "SALE_CREATED",
    "SALE_UPDATED",
    "SALE_DELETED",
    "INVOICE_REQUESTED",
    "INVOICE_DELETED",
    "INVOICE_SENT",
    "CUSTOMER_CREATED",
    "CUSTOMER_UPDATED",
    "PRODUCT_CREATED",
    "PRODUCT_UPDATED",
    "PRODUCT_DELETED",
    "PRODUCT_VARIANT_CREATED",
    "PRODUCT_VARIANT_UPDATED",
    "PRODUCT_VARIANT_DELETED",
    "PRODUCT_VARIANT_OUT_OF_STOCK",
    "PRODUCT_VARIANT_BACK_IN_STOCK",
    "CHECKOUT_CREATED",
    "CHECKOUT_UPDATED",
    "FULFILLMENT_CREATED",
    "FULFILLMENT_CANCELED",
    "NOTIFY_USER",
    "PAGE_CREATED",
    "PAGE_UPDATED",
    "PAGE_DELETED",
    "PAYMENT_AUTHORIZE",
    "PAYMENT_CAPTURE",
    "PAYMENT_CONFIRM",
    "PAYMENT_LIST_GATEWAYS",
    "PAYMENT_PROCESS",
    "PAYMENT_REFUND",
    "PAYMENT_VOID",
    "SHIPPING_LIST_METHODS_FOR_CHECKOUT",
    "TRANSLATION_CREATED",
    "TRANSLATION_UPDATED",
)


WebHookHandlerSignature = Optional[Callable[[List[Webhook], DomainName], Awaitable]]


class WebhookHandlersBase(BaseModel):
    def get(self, event_name) -> Optional[Callable[[BaseModel], Awaitable]]:
        return self.__dict__.get(event_name)

    def get_assigned_events(self) -> List[str]:
        return [k for k, v in self.__dict__.items() if v is not None]


WebhookHandlers = create_model(
    "WebhookHandlers",
    __base__=WebhookHandlersBase,
    **{
        event_type.lower(): (WebHookHandlerSignature, None)
        for event_type in SALEOR_EVENT_TYPES
    },
)


class SQSUrl(AnyHttpUrl):
    allowed_schemes = {"awssqs"}


class SQSHandler(BaseModel):
    queue_url: SQSUrl
    handler: WebHookHandlerSignature


class SQSHandlersBase(WebhookHandlersBase):
    def get_assigned_events(self) -> List[str]:
        sqs_queue_events = {}
        for event_type, sqs_handler in self.__dict__.items():
            if sqs_handler is not None:
                sqs_queue_events.setdefault(str(sqs_handler.queue_url), [])
                sqs_queue_events[str(sqs_handler.queue_url)].append(event_type)
        return sqs_queue_events


SQSHandlers = create_model(
    "SQSHandlers",
    __base__=SQSHandlersBase,
    **{event_type.lower(): (SQSHandler, None) for event_type in SALEOR_EVENT_TYPES},
)
