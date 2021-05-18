from typing import List

from ..schemas.core import DomainName
from ..schemas.webhooks import WebhookEvent


async def install_app(domain: DomainName, token: str, events: List[WebhookEvent]):
    ...
