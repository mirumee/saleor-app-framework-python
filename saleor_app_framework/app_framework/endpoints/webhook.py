from typing import Any, Awaitable, Callable, List

from fastapi import APIRouter, Depends

from ..core.types import DomainName, WebhookData
from ..schemas.webhooks.handlers import WebhookHandlers
from .deps import verify_saleor_domain, verify_webhook_signature, webhook_event_type


def initialize_webhook_router(
    validate_domain: Callable[[DomainName], Awaitable[bool]],
    get_webhook_details: Callable[[DomainName], Awaitable[WebhookData]],
    webhook_handlers: WebhookHandlers,
):
    router = APIRouter(
        prefix="/webhook",
        responses={
            400: {"description": "Missing required header"},
            401: {"description": "Incorrect signature"},
            404: {"description": "Incorrect saleor event"},
        },
    )

    @router.post("/", name="handle-webhook")
    async def handle_webhook(
        payload: List[Any],  # FIXME provide a way to proper define payload types
        _domain_is_valid=Depends(verify_saleor_domain(validate_domain)),
        event_type=Depends(webhook_event_type),
        _signature_is_valid=Depends(verify_webhook_signature(get_webhook_details)),
    ):
        response = {}
        handler = webhook_handlers.get(event_type)
        if handler is not None:
            response = await handler(payload)
        return response or {}

    return router
