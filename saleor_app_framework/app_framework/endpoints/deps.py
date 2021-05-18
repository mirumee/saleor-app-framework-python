from typing import Awaitable, Callable

from fastapi import Depends, Header, HTTPException

from ..core.conf import settings
from ..core.validators import verify_token
from ..schemas.core import DomainName

SALEOR_DOMAIN_HEADER = "x-saleor-domain"
SALEOR_TOKEN_HEADER = "x-saleor-token"


async def saleor_domain_header(
    saleor_domain=Header(None, alias=SALEOR_DOMAIN_HEADER)
) -> DomainName:
    if settings.DEBUG:
        saleor_domain = saleor_domain or settings.DEV_SALEOR_DOMAIN
    if not saleor_domain:
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_DOMAIN_HEADER.upper()} header"
        )
    return saleor_domain


async def saleor_token(saleor_token=Header(None, alias=SALEOR_TOKEN_HEADER)) -> str:
    if settings.DEBUG:
        saleor_token = saleor_token or settings.DEV_SALEOR_TOKEN
    if not saleor_token:
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_TOKEN_HEADER.upper()} header"
        )
    return saleor_token


async def verify_saleor_token(
    domain=Depends(saleor_domain_header), token=Depends(saleor_token)
) -> bool:
    is_valid = await verify_token(domain, token)
    if not is_valid:
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
            raise HTTPException(
                status_code=400, detail=f"Provided domain {saleor_domain} is invalid."
            )
        return True

    return fun
