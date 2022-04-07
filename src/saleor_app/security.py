import hashlib
import hmac
import logging
from typing import Optional

import jwt
from fastapi import HTTPException, Request, Security
from fastapi.openapi.models import APIKey as APIKeyModel
from fastapi.openapi.models import APIKeyIn
from fastapi.security.base import SecurityBase
from jwt.api_jwk import PyJWKSet
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

from saleor_app.schemas.core import Saleor
from saleor_app.schemas.principals import SaleorPrincipal

logger = logging.getLogger(__name__)

SALEOR_DOMAIN_HEADER = "x-saleor-domain"
SALEOR_TOKEN_HEADER = "x-saleor-token"
SALEOR_SIGNATURE_HEADER = "x-saleor-signature"


class SaleorDomainSecurity(SecurityBase):
    def __init__(
        self,
        *,
        auto_error: bool = True,
    ):
        self.model = APIKeyModel(
            **{"in": APIKeyIn.header},
            name=SALEOR_DOMAIN_HEADER,
            description="Uses app's validate_domain method to check if a Saleor domain is authorized to use this app.",
        )
        self.scheme_name = "Saleor Domain Validation"
        self.auto_error = auto_error

    async def __call__(
        self,
        request: Request,
    ) -> Optional[Saleor]:

        saleor: str = request.headers.get(SALEOR_DOMAIN_HEADER)

        domain_is_valid = await request.app.validate_domain(saleor)
        if not domain_is_valid and self.auto_error:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Provided domain {saleor} is invalid.",
            )
        return Saleor(domain=saleor)


class SaleorUserAuthSecurity(SecurityBase):
    def __init__(
        self,
        *,
        auto_error: bool = True,
    ):
        self.model = APIKeyModel(
            **{"in": APIKeyIn.header},
            name=SALEOR_TOKEN_HEADER,
            description="Authenticates the user with the JWT issued by Saleor.",
        )
        self.scheme_name = "Saleor User Authentication"
        self.auto_error = auto_error

    async def __call__(
        self,
        request: Request,
        saleor: Saleor = Security(SaleorDomainSecurity(auto_error=False)),
    ) -> Optional[SaleorPrincipal]:

        if not saleor:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=f"Provided domain {saleor} is invalid.",
                )
            else:
                return None

        token: str = request.headers.get(SALEOR_TOKEN_HEADER)

        if not token:
            logger.warning(f"Missing {SALEOR_TOKEN_HEADER.upper()} header.")
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=f"Missing {SALEOR_TOKEN_HEADER.upper()} header.",
                )
            else:
                return None

        jwks = await request.app.get_saleor_jwks(saleor)
        signing_keys = PyJWKSet.from_dict(jwks)

        header = jwt.get_unverified_header(jwt=token)

        for key in signing_keys.keys:
            if key.key_id == header["kid"]:
                signing_key = key
                break

        payload = jwt.decode(jwt=token, key=signing_key.key, algorithms=[header["alg"]])

        return SaleorPrincipal(
            uid=payload["user_id"],
            saleor=saleor,
            permissions=payload.get("permissions", set()),
        )


class SaleorWebhookVerification(BaseModel):
    verified: bool
    saleor: Saleor


class SaleorWebhookSecurity(SecurityBase):
    def __init__(
        self,
        *,
        auto_error: bool = True,
    ):
        self.model = APIKeyModel(
            **{"in": APIKeyIn.header},
            name=SALEOR_SIGNATURE_HEADER,
            description="Verifies the source of a webhook by validating the signature of the webhook event.",
        )
        self.scheme_name = "Saleor Webhook Signature Verification"
        self.auto_error = auto_error

    async def __call__(
        self,
        request: Request,
        saleor: Saleor = Security(SaleorDomainSecurity(auto_error=False)),
    ) -> Optional[SaleorWebhookVerification]:

        signature: str = request.headers.get(SALEOR_SIGNATURE_HEADER)

        if not signature:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=(f"Missing signature header - {SALEOR_SIGNATURE_HEADER}"),
                )
            else:
                return None

        webhook_details = await request.app.get_webhook_details(saleor)
        content = await request.body()
        webhook_signature_bytes = bytes(signature, "utf-8")

        secret_key_bytes = bytes(webhook_details.webhook_secret_key, "utf-8")
        content_signature_str = hmac.new(
            secret_key_bytes, content, hashlib.sha256
        ).hexdigest()
        content_signature = bytes(content_signature_str, "utf-8")

        if not hmac.compare_digest(content_signature, webhook_signature_bytes):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=(f"Invalid webhook signature for {SALEOR_SIGNATURE_HEADER}"),
                )
            else:
                return None

        return SaleorWebhookVerification(verified=True, saleor=saleor)


saleor_user_auth_security = SaleorUserAuthSecurity()
saleor_webhook_security = SaleorWebhookSecurity()
