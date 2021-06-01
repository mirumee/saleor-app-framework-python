import logging
from typing import Awaitable, Callable

from fastapi import Depends, Header, HTTPException

from ..core.conf import settings
from ..core.types import DomainName
from ..core.validators import verify_token
from ..schemas.webhooks.handlers import WebhookHandlers

logger = logging.getLogger(__file__)

SALEOR_DOMAIN_HEADER = "x-saleor-domain"
SALEOR_TOKEN_HEADER = "x-saleor-token"
SALEOR_EVENT_HEADER = "x-saleor-event"
SALEOR_SIGNATURE_HEADER = "x-saleor-signature"


async def saleor_domain_header(
    saleor_domain=Header(None, alias=SALEOR_DOMAIN_HEADER)
) -> DomainName:
    if settings.DEBUG:
        saleor_domain = saleor_domain or settings.DEV_SALEOR_DOMAIN
    if not saleor_domain:
        logger.warning(f"Missing {SALEOR_DOMAIN_HEADER.upper()} header")
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_DOMAIN_HEADER.upper()} header"
        )
    return saleor_domain


async def saleor_token(token=Header(None, alias=SALEOR_TOKEN_HEADER)) -> str:
    if settings.DEBUG:
        token = token or settings.DEV_SALEOR_TOKEN
    if not token:
        logger.warning(f"Missing {SALEOR_TOKEN_HEADER.upper()} header")
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_TOKEN_HEADER.upper()} header"
        )
    return token


async def verify_saleor_token(
    domain=Depends(saleor_domain_header), token=Depends(saleor_token)
) -> bool:
    is_valid = await verify_token(domain, token)
    if not is_valid:
        logger.warning(
            f"Provided {SALEOR_DOMAIN_HEADER.upper()} and "
            f"{SALEOR_TOKEN_HEADER.upper()} are incorrect."
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"Provided {SALEOR_DOMAIN_HEADER.upper()} and "
                f"{SALEOR_TOKEN_HEADER.upper()} are incorrect."
            ),
        )
    return True


def verify_saleor_domain(
    validate_domain: Callable[[DomainName], Awaitable[bool]]
) -> Callable[[], Awaitable[bool]]:
    async def fun(saleor_domain=Depends(saleor_domain_header)) -> bool:
        domain_is_valid = await validate_domain(saleor_domain)
        if not domain_is_valid:
            logger.warning(f"Provided domain {saleor_domain} is invalid.")
            raise HTTPException(
                status_code=400, detail=f"Provided domain {saleor_domain} is invalid."
            )
        return True

    return fun


async def webhook_event_type(event=Header(None, alias=SALEOR_EVENT_HEADER)) -> str:
    if not event:
        logger.warning(f"Missing {SALEOR_EVENT_HEADER.upper()} header.")
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_EVENT_HEADER.upper()} header."
        )
    if event not in WebhookHandlers.__fields__:
        logger.error(
            "Event from %s header %s doesn't have own handler",
            SALEOR_EVENT_HEADER,
            event,
        )
        raise HTTPException(
            status_code=404,
            detail=(
                f"Event from {SALEOR_EVENT_HEADER} header {event} doesn't have own "
                "handler on the app side."
            ),
        )
    return event
