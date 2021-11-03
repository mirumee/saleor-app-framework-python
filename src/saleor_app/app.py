from typing import Awaitable, Callable, Optional

from fastapi import APIRouter, FastAPI

from saleor_app.endpoints import handle_webhook, install, manifest
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.handlers import WebhookHandlers
from saleor_app.schemas.manifest import Manifest


class SaleorApp(FastAPI):
    def __init__(
        self,
        *,
        validate_domain: Callable[[DomainName], Awaitable[bool]],
        save_app_data: Callable[[DomainName, WebhookData], Awaitable],
        webhook_handlers: WebhookHandlers,
        get_webhook_details: Callable[[DomainName], Awaitable[Optional[WebhookData]]],
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.extra["saleor"] = {
            "validate_domain": validate_domain,
            "save_app_data": save_app_data,
            "webhook_handlers": webhook_handlers,
            "get_webhook_details": get_webhook_details,
        }
        self.configuration_router = APIRouter(
            prefix="/configuration", tags=["configuration"]
        )
        self.include_webhook_router()

    def include_saleor_app_routes(self):
        # TODO: ensure a configuration-form path was defined at this point
        self.configuration_router.get("/manifest", response_model=Manifest)(manifest)
        self.configuration_router.post(
            "/install",
            responses={
                400: {"description": "Missing required header"},
                403: {"description": "Incorrect token or not enough permissions"},
            },
            name="app-install",
        )(install)

        self.include_router(self.configuration_router)

    def include_webhook_router(self):
        router = APIRouter(
            prefix="/webhook",
            responses={
                400: {"description": "Missing required header"},
                401: {"description": "Incorrect signature"},
                404: {"description": "Incorrect saleor event"},
            },
        )
        router.post("/", name="handle-webhook")(handle_webhook)
        self.include_router(router)
