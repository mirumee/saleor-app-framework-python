from typing import Any, Awaitable, Callable, List, Optional, Union

from pydantic import BaseModel

from saleor_app.schemas.core import DomainName

Payload = Union[BaseModel, Any]


class WebhookHandlers(BaseModel):
    order_created: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    order_confirmed: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    order_fully_paid: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    order_updated: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    order_cancelled: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    order_fulfilled: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    invoice_requested: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    invoice_deleted: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    invoice_sent: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    fulfillment_created: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    customer_created: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    customer_updated: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    product_created: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    product_updated: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    product_deleted: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    product_variant_created: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    product_variant_updated: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    product_variant_deleted: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    checkout_created: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    checkout_updated: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    notify_user: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    page_created: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    page_updated: Optional[Callable[[Payload, DomainName], Awaitable]] = None
    page_deleted: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    payment_list_gateways: Optional[Callable[[Payload, DomainName], Awaitable]] = None

    def get(self, event_name) -> Optional[Callable[[BaseModel], Awaitable]]:
        return self.__dict__.get(event_name)

    def get_assigned_events(self) -> List[str]:
        return [k for k, v in self.__dict__.items() if v is not None]
