import hashlib
import hmac
import logging
from typing import List, Optional

import jwt
from fastapi import Depends, Header, HTTPException, Query, Request

from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.saleor.mutations import VERIFY_APP_TOKEN, VERIFY_TOKEN
from saleor_app.saleor.utils import get_client_for_app
from saleor_app.schemas.core import DomainName

logger = logging.getLogger(__name__)

SALEOR_DOMAIN_HEADER = "x-saleor-domain"
SALEOR_TOKEN_HEADER = "x-saleor-token"
SALEOR_SIGNATURE_HEADER = "x-saleor-signature"
SALEOR_APP_TOKEN_HEADER = "x-saleor-app-token"


async def saleor_domain_header(
    saleor_domain: Optional[str] = Header(None, alias=SALEOR_DOMAIN_HEADER),
) -> DomainName:
    if not saleor_domain:
        logger.warning(f"Missing {SALEOR_DOMAIN_HEADER.upper()} header.")
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_DOMAIN_HEADER.upper()} header."
        )
    return saleor_domain


async def saleor_token(
    request: Request,
    token: Optional[str] = Header(None, alias=SALEOR_TOKEN_HEADER),
) -> str:
    if request.app.development_auth_token:
        token = token or request.app.development_auth_token
    if not token:
        logger.warning(f"Missing {SALEOR_TOKEN_HEADER.upper()} header.")
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_TOKEN_HEADER.upper()} header."
        )
    return token


async def saleor_app_token(
    request: Request,
    token: Optional[str] = Header(None, alias=SALEOR_APP_TOKEN_HEADER),
) -> str:
    if request.app.development_auth_token:
        token = token or request.app.development_auth_token
    if not token:
        logger.warning(f"Missing {SALEOR_APP_TOKEN_HEADER.upper()} header.")
        raise HTTPException(
            status_code=400, detail=f"Missing {SALEOR_APP_TOKEN_HEADER.upper()} header."
        )
    return token


async def verify_saleor_token(
    request: Request,
    saleor_domain=Depends(saleor_domain_header),
    token=Depends(saleor_token),
) -> bool:
    result = await _verify_token(
        request, saleor_domain, token, SALEOR_TOKEN_HEADER, VERIFY_TOKEN
    )
    return result


async def verify_saleor_app_token(
    request: Request,
    saleor_domain=Depends(saleor_domain_header),
    app_token=Depends(saleor_app_token),
) -> bool:
    result = await _verify_token(
        request, saleor_domain, app_token, SALEOR_APP_TOKEN_HEADER, VERIFY_APP_TOKEN
    )
    return result


async def _verify_token(
    request, saleor_domain, token, token_header, token_mutation
) -> bool:
    schema = "http" if request.app.use_insecure_saleor_http else "https"
    async with get_client_for_app(
        f"{schema}://{saleor_domain}", manifest=request.app.manifest
    ) as saleor_client:
        try:
            response = await saleor_client.execute(
                token_mutation,
                variables={
                    "token": token,
                },
            )
        except GraphQLError:
            return False

    token = response.get("appTokenVerify", {}) or response.get("tokenVerify", {})
    is_valid = token.get("isValid", False) or token.get("valid", False)

    if not is_valid:
        logger.warning(
            f"Provided {SALEOR_DOMAIN_HEADER.upper()} and "
            f"{token_header.upper()} are incorrect."
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"Provided {SALEOR_DOMAIN_HEADER.upper()} and "
                f"{token_header.upper()} are incorrect."
            ),
        )
    return True


async def verify_saleor_domain(
    request: Request,
    saleor_domain=Depends(saleor_domain_header),
) -> bool:
    domain_is_valid = await request.app.validate_domain(saleor_domain)
    if not domain_is_valid:
        logger.warning(f"Provided domain {saleor_domain} is invalid.")
        raise HTTPException(
            status_code=400, detail=f"Provided domain {saleor_domain} is invalid."
        )
    return True


async def verify_webhook_signature(
    request: Request,
    signature: Optional[str] = Header(None, alias=SALEOR_SIGNATURE_HEADER),
    domain_name=Depends(saleor_domain_header),
):
    if not signature:
        raise HTTPException(
            status_code=401,
            detail=(f"Missing signature header - {SALEOR_SIGNATURE_HEADER}"),
        )
    webhook_details = await request.app.get_webhook_details(domain_name)
    content = await request.body()
    webhook_signature_bytes = bytes(signature, "utf-8")

    secret_key_bytes = bytes(webhook_details.webhook_secret_key, "utf-8")
    content_signature_str = hmac.new(
        secret_key_bytes, content, hashlib.sha256
    ).hexdigest()
    content_signature = bytes(content_signature_str, "utf-8")

    if not hmac.compare_digest(content_signature, webhook_signature_bytes):
        raise HTTPException(
            status_code=401,
            detail=(f"Invalid webhook signature for {SALEOR_SIGNATURE_HEADER}"),
        )


def require_permission(permissions: List):
    """
    Validates is the requesting principal is authorized for the specified action

    Usage:

    ```
    Depends(require_permission([SaleorPermissions.MANAGE_PRODUCTS]))
    ```
    """

    async def func(
        saleor_domain=Depends(saleor_domain_header),
        saleor_token=Depends(saleor_token),
        _token_is_valid=Depends(verify_saleor_token),
    ):
        jwt_payload = jwt.decode(saleor_token, verify=False)
        user_permissions = set(jwt_payload.get("permissions", []))
        if not set([p.value for p in permissions]) - user_permissions:
            return True
        raise HTTPException(status_code=403, detail="Unauthorized user")

    return func


class ConfigurationFormDeps:
    def __init__(
        self,
        request: Request,
        domain=Query(...),
    ):
        self.request = request
        self.saleor_domain = domain


class ConfigurationDataDeps:
    def __init__(
        self,
        request: Request,
        saleor_domain=Depends(saleor_domain_header),
        _domain_is_valid=Depends(verify_saleor_domain),
        _token_is_valid=Depends(verify_saleor_token),
        token=Depends(saleor_token),
    ):
        self.request = request
        self.saleor_domain = saleor_domain
        self.token = token
