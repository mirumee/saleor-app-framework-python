import logging
from collections import defaultdict

from fastapi import Depends, Request
from fastapi.exceptions import HTTPException

from saleor_app.errors import InstallAppError
from saleor_app.install import install_app
from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.schemas.core import InstallData, Saleor
from saleor_app.schemas.utils import LazyUrl
from saleor_app.security import SaleorDomainSecurity

logger = logging.getLogger(__name__)


async def manifest(request: Request):
    manifest = request.app.manifest
    for name, field in manifest:
        if isinstance(field, LazyUrl):
            setattr(manifest, name, field(request))
    for extension in manifest.extensions:
        if isinstance(extension.url, LazyUrl):
            extension.url = extension.url(request)
    return manifest


async def install(
    request: Request,
    data: InstallData,
    saleor: Saleor = Depends(SaleorDomainSecurity()),
):
    events = defaultdict(list)
    if hasattr(request.app, "webhook_router"):
        if request.app.webhook_router.http_routes:
            events[request.url_for("handle-webhook")] = list(
                request.app.webhook_router.http_routes.keys()
            )
        for event_type, sqs_handler in request.app.webhook_router.sqs_routes.items():
            key = str(sqs_handler.target_url)
            events[key].append(event_type)

    if events:
        try:
            webhook_data = await install_app(
                saleor=saleor,
                auth_token=data.auth_token,
                manifest=request.app.manifest,
                events=events,
                use_insecure_saleor_http=request.app.use_insecure_saleor_http,
            )
        except (InstallAppError, GraphQLError) as exc:
            logger.debug(str(exc), exc_info=1)
            raise HTTPException(
                status_code=403, detail="Incorrect token or not enough permissions"
            )
    else:
        webhook_data = None

    await request.app.save_app_data(
        saleor=saleor,
        auth_token=data.auth_token,
        webhook_data=webhook_data,
    )

    return {}
