from typing import List

from fastapi import Depends, Header, Request
from fastapi.exceptions import HTTPException

from saleor_app.deps import saleor_domain_header, verify_saleor_domain
from saleor_app.errors import InstallAppError
from saleor_app.http import SALEOR_EVENT_HEADER
from saleor_app.install import install_app
from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.schemas.core import InstallData
from saleor_app.schemas.utils import LazyUrl
from saleor_app.schemas.webhook import Webhook


async def manifest(request: Request):
    manifest = request.app.manifest
    for name, field in manifest:
        if isinstance(field, LazyUrl):
            setattr(manifest, name, field(request))
    for extension in manifest.extensions:
        if isinstance(extension.url, LazyUrl):
            extension.url = extension.url(request)
    manifest.app_url = ""
    return manifest


async def install(
    request: Request,
    data: InstallData,
    _domain_is_valid=Depends(verify_saleor_domain),
    saleor_domain=Depends(saleor_domain_header),
):
    events = {}
    if request.app.http_webhook_handlers:
        events[
            request.url_for("handle-webhook")
        ] = request.app.http_webhook_handlers.get_assigned_events()
    if request.app.sqs_handlers:
        events.update(request.app.sqs_handlers.get_assigned_events())

    if events:
        try:
            webhook_data = await install_app(
                saleor_domain=saleor_domain,
                auth_token=data.auth_token,
                manifest=request.app.manifest,
                events=events,
                use_insecure_saleor_http=request.app.use_insecure_saleor_http,
            )
        except (InstallAppError, GraphQLError):
            raise HTTPException(
                status_code=403, detail="Incorrect token or not enough permissions"
            )
    else:
        webhook_data = None

    await request.app.save_app_data(
        saleor_domain=saleor_domain,
        auth_token=data.auth_token,
        webhook_data=webhook_data,
    )

    return {}


async def handle_webhook(
    request: Request,
    payload: List[Webhook],  # FIXME provide a way to proper define payload types
    saleor_domain=Depends(saleor_domain_header),
    _event_type=Header(None, alias=SALEOR_EVENT_HEADER),
):
    return {}
