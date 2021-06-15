from typing import Any, List

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends

from saleor_app.deps import (
    get_settings,
    saleor_domain_header,
    verify_saleor_domain,
    verify_webhook_signature,
    webhook_event_type,
)
from saleor_app.errors import InstallAppError
from saleor_app.graphql import GraphqlError
from saleor_app.install import install_app
from saleor_app.schemas.core import InstallData
from saleor_app.schemas.manifest import Manifest


async def manifest(request: Request, settings=Depends(get_settings)):
    manifest = settings.manifest.dict()
    manifest["tokenTargetUrl"] = request.url_for("app-install")
    manifest["configurationUrl"] = request.url_for("configuration-form")
    return Manifest(**manifest)


async def install(
    request: Request,
    data: InstallData,
    _domain_is_valid=Depends(verify_saleor_domain),
    saleor_domain=Depends(saleor_domain_header),
):
    target_url = request.url_for("handle-webhook")
    domain = saleor_domain
    auth_token = data.auth_token

    try:
        await install_app(
            domain,
            auth_token,
            request.app.extra["saleor"]["webhook_handlers"].get_assigned_events(),
            target_url,
            request.app.extra["saleor"]["save_app_data"],
        )
    except (InstallAppError, GraphqlError):
        raise HTTPException(
            status_code=403, detail="Incorrect token or not enough permissions"
        )

    return {}


async def handle_webhook(
    request: Request,
    payload: List[Any],  # FIXME provide a way to proper define payload types
    _domain_is_valid=Depends(verify_saleor_domain),
    event_type=Depends(webhook_event_type),
    _signature_is_valid=Depends(verify_webhook_signature),
):
    response = {}
    handler = request.app.extra["saleor"]["webhook_handlers"].get(event_type)
    if handler is not None:
        response = await handler(payload)
    return response or {}


class SaleorFastAPIApp(FastAPI):
    def __init__(
        self,
        *,
        validate_domain,
        save_app_data,
        webhook_handlers,
        get_webhook_details,
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
