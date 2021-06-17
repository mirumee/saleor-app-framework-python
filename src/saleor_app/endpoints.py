from typing import Any, List

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.templating import Jinja2Templates

from saleor_app.deps import (
    get_settings,
    saleor_domain_header,
    verify_saleor_domain,
    verify_webhook_signature,
    webhook_event_type,
    ConfigurationFormDeps,
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


async def get_form(commons: ConfigurationFormDeps = Depends()):
    context = {
        "request": commons.request,
        "form_url": commons.request.url,
        "domain": commons.saleor_domain,
        "token": commons.token,
    }
    return Jinja2Templates(directory=commons.settings.static_dir).TemplateResponse(
        "configuration/index.html", context
    )
