from typing import Union

from .payments import PaymentAuthorize

WebhookEvent = Union[
    PaymentAuthorize,
]
