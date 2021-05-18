from typing import Awaitable, Callable

from fastapi import APIRouter, Depends
from fastapi.requests import Request

from ..schemas.core import DomainName
from .deps import saleor_domain_header, verify_saleor_domain


# TODO Finish the view
def initialize_webhook_router(
    validate_domain: Callable[[DomainName], Awaitable[bool]],
):
    router = APIRouter(
        prefix="/webhook"
    )  # responses={400: {"description": "Missing required header"}})

    @router.post("/")
    async def handle_webhook():
        ...

    @router.post("/register")
    async def register_webhook(
        request: Request,
        # register_data: WebhookRegister,
        _domain_is_valid=Depends(verify_saleor_domain(validate_domain)),
        saleor_domain=Depends(saleor_domain_header),
    ):
        # TODO to be implemented in separate PR

        # webhook_url = request.url_for("handle_webhook")
        return {}

    return router
