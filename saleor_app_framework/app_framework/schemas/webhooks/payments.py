from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

# PAYMENT_EVENTS = [
#     PAYMENT_AUTHORIZE,
#     PAYMENT_CAPTURE,
#     PAYMENT_CONFIRM,
#     PAYMENT_LIST_GATEWAYS,
#     PAYMENT_PROCESS,
#     PAYMENT_REFUND,
#     PAYMENT_VOID,
# ]


class Address(BaseModel):
    first_name: str
    last_name: str
    company_name: str
    street_address_1: str
    street_address_2: str
    city: str
    city_area: str
    postal_code: str
    country: str
    country_area: str
    phone: str


class PaymentBase(BaseModel):
    amount: Decimal
    currency: str
    billing: Optional[Address]
    shipping: Optional[Address]
    payment_id: int
    graphql_payment_id: str
    order_id: Optional[int]
    customer_ip_address: Optional[str]
    customer_email: str
    token: Optional[str] = None
    customer_id: Optional[str] = None
    reuse_source: bool = False
    data: Optional[dict] = None


class PaymentAuthorize(PaymentBase):
    ...
