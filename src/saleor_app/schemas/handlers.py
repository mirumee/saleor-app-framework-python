from typing import Awaitable, Callable, List, Optional

from pydantic import BaseModel

from saleor_app.schemas.core import DomainName
from saleor_app.schemas.webhook import Webhook


class WebhookHandlers(BaseModel):
    order_created: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    order_confirmed: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    order_fully_paid: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    order_updated: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    order_cancelled: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    order_fulfilled: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    draft_order_created: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    draft_order_updated: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    draft_order_deleted: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None

    sale_created: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    sale_updated: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    sale_deleted: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    invoice_requested: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    invoice_deleted: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    invoice_sent: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    customer_created: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    customer_updated: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    product_created: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    product_updated: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    product_deleted: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    product_variant_created: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    product_variant_updated: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    product_variant_deleted: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    product_variant_out_of_stock: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    product_variant_back_in_stock: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None

    checkout_created: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    checkout_updated: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    fulfillment_created: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    fulfillment_canceled: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None

    notify_user: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    page_created: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    page_updated: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    page_deleted: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    payment_authorize: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    payment_capture: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    payment_confirm: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    payment_list_gateways: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    payment_process: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    payment_refund: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None
    payment_void: Optional[Callable[[List[Webhook], DomainName], Awaitable]] = None

    shipping_list_methods_for_checkout: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None

    translation_created: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None
    translation_updated: Optional[
        Callable[[List[Webhook], DomainName], Awaitable]
    ] = None

    def get(self, event_name) -> Optional[Callable[[BaseModel], Awaitable]]:
        return self.__dict__.get(event_name)

    def get_assigned_events(self) -> List[str]:
        return [k for k, v in self.__dict__.items() if v is not None]
