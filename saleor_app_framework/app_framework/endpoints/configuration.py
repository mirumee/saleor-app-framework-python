from typing import Awaitable, Callable, List

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..core.conf import settings
from ..core.errors import InstallAppError
from ..core.graphql import GraphqlError
from ..core.install import install_app
from ..core.types import DomainName, WebhookData
from ..schemas.core import (
    ConfigurationData,
    ConfigurationDataClass,
    ConfigurationDataUpdate,
    ConfigurationDataUpdateClass,
)
from ..schemas.webhooks.core import InstallData
from .deps import (
    saleor_domain_header,
    saleor_token,
    verify_saleor_domain,
    verify_saleor_token,
)


def initialize_configuration_router(
    configuration_data_model: ConfigurationDataClass,
    configuration_data_update_model: ConfigurationDataUpdateClass,
    get_configuration: Callable[[DomainName], Awaitable[ConfigurationData]],
    update_configuration: Callable[
        [DomainName, ConfigurationDataUpdate], Awaitable[ConfigurationData]
    ],
    validate_domain: Callable[[DomainName], Awaitable[bool]],
    configuration_template: str,
    save_app_data: Callable[[DomainName, WebhookData], Awaitable],
    webhook_events: List[str],
):
    router = APIRouter(responses={400: {"description": "Missing required header."}})

    @router.get("/", response_class=HTMLResponse, name="configuration-form")
    async def get_form(
        request: Request,
        saleor_domain=Depends(saleor_domain_header),
        token=Depends(saleor_token),
    ):
        context = {
            "request": request,
            "form_url": request.url,
            "domain": saleor_domain,
            "token": token,
        }
        return Jinja2Templates(directory=settings.STATIC_DIR).TemplateResponse(
            configuration_template, context
        )

    @router.get("/data", response_model=configuration_data_model)
    async def get_configuration_data(
        _domain_is_valid=Depends(verify_saleor_domain(validate_domain)),
        _token_is_valid=Depends(verify_saleor_token),
        saleor_domain=Depends(saleor_domain_header),
    ):
        return await get_configuration(saleor_domain)

    @router.post("/data")
    async def update_configuration_data(
        data: configuration_data_update_model,
        _domain_is_valid=Depends(verify_saleor_domain(validate_domain)),
        _token_is_valid=Depends(verify_saleor_token),
        saleor_domain=Depends(saleor_domain_header),
    ):
        return await update_configuration(saleor_domain, data)

    @router.post(
        "/install",
        responses={
            400: {"description": "Missing required header."},
            403: {"description": "Incorrect token or not enough permissions."},
        },
        name="app-install",
    )
    async def install(
        request: Request,
        data: InstallData,
        _domain_is_valid=Depends(verify_saleor_domain(validate_domain)),
        saleor_domain=Depends(saleor_domain_header),
    ):
        target_url = request.url_for("handle-webhook")
        domain = saleor_domain
        auth_token = data.auth_token

        try:
            await install_app(
                domain, auth_token, webhook_events, target_url, save_app_data
            )
        except (InstallAppError, GraphqlError):
            raise HTTPException(
                status_code=403, detail="Incorrect token or not enough permissions."
            )

        return {}

    return router
