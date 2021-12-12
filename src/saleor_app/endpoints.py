import json
from typing import List

from fastapi import Depends, Header, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse

from saleor_app.deps import (
    ConfigurationFormDeps,
    saleor_domain_header,
    verify_saleor_domain,
)
from saleor_app.errors import InstallAppError
from saleor_app.http import SALEOR_EVENT_HEADER
from saleor_app.install import install_app
from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.schemas.core import InstallData
from saleor_app.schemas.webhook import Webhook


async def manifest(request: Request):
    manifest = request.app.manifest
    for name, field in manifest:
        if callable(field):
            setattr(manifest, name, field(request))
    for extension in manifest.extensions:
        if callable(extension.url):
            extension.url = extension.url(request)
    manifest.app_url = "http://127.0.0.1"
    return manifest


async def install(
    request: Request,
    data: InstallData,
    _domain_is_valid=Depends(verify_saleor_domain),
    saleor_domain=Depends(saleor_domain_header),
):
    try:
        await install_app(
            saleor_domain=saleor_domain,
            auth_token=data.auth_token,
            manifest=request.app.manifest,
            events=request.app.webhook_handlers.get_assigned_events(),
            target_url=request.url_for("handle-webhook"),
            save_app_data_callback=request.app.extra["saleor"]["save_app_data"],
            use_insecure_saleor_http=request.app.use_insecure_saleor_http,
        )
    except (InstallAppError, GraphQLError):
        raise HTTPException(
            status_code=403, detail="Incorrect token or not enough permissions"
        )

    return {}


async def handle_webhook(
    request: Request,
    payload: List[Webhook],  # FIXME provide a way to proper define payload types
    saleor_domain=Depends(saleor_domain_header),
    _event_type=Header(None, alias=SALEOR_EVENT_HEADER),
):
    return {}


async def get_public_form(commons: ConfigurationFormDeps = Depends()):
    context = {
        "request": str(commons.request),
        "form_url": str(commons.request.url),
        "saleor_domain": commons.saleor_domain,
    }
    return PlainTextResponse(json.dumps(context, indent=4))
