from typing import Awaitable, Callable, Optional

from fastapi import APIRouter, Depends, FastAPI
from fastapi.routing import APIRoute

from saleor_app.deps import verify_saleor_domain, verify_webhook_signature
from saleor_app.endpoints import handle_webhook, install, manifest
from saleor_app.http import WebhookRoute
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.handlers import WebhookHandlers
from saleor_app.schemas.manifest import Manifest


class SaleorApp(FastAPI):
    def __init__(
        self,
        *,
        manifest: Manifest,
        validate_domain: Callable[[DomainName], Awaitable[bool]],
        save_app_data: Callable[[DomainName, WebhookData], Awaitable],
        webhook_handlers: WebhookHandlers,
        get_webhook_details: Callable[[DomainName], Awaitable[WebhookData]],
        use_insecure_saleor_http: bool = False,
        development_auth_token: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.manifest = manifest
        self.webhook_handlers = webhook_handlers
        self.use_insecure_saleor_http = use_insecure_saleor_http
        self.development_auth_token = development_auth_token

        self.extra["saleor"] = {
            "validate_domain": validate_domain,
            "save_app_data": save_app_data,
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
            dependencies=[
                Depends(verify_saleor_domain),
                Depends(verify_webhook_signature),
            ],
            route_class=WebhookRoute,
        )

        router.post("", name="handle-webhook")(handle_webhook)
        self.webhook_handler_routes = {
            name: APIRoute(
                "",
                endpoint,
            )
            for name, endpoint in self.webhook_handlers
            if endpoint
        }
        self.include_router(router)
