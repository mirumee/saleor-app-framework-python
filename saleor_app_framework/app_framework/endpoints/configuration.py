from typing import Awaitable, Callable

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..core.conf import settings
from ..core.install import install_app
from ..schemas.core import (
    ConfigurationData,
    ConfigurationDataClass,
    ConfigurationDataUpdate,
    ConfigurationDataUpdateClass,
    DomainName,
)
from ..schemas.webhooks.core import InstallAppData
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
):
    router = APIRouter(responses={400: {"description": "Missing required header"}})

    @router.get("/", response_class=HTMLResponse)
    async def get_form(
        request: Request,
        saleor_domain=Depends(saleor_domain_header),
        saleor_token=Depends(saleor_token),
    ):
        context = {
            "request": request,
            "form_url": request.url,
            "domain": saleor_domain,
            "token": saleor_token,
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

    @router.put("/data")
    async def update_configuration_data(
        data: configuration_data_update_model,
        _domain_is_valid=Depends(verify_saleor_domain(validate_domain)),
        _token_is_valid=Depends(verify_saleor_token),
        saleor_domain=Depends(saleor_domain_header),
    ):
        return await update_configuration(saleor_domain, data)

    @router.post("/install")
    async def install(
        data: InstallAppData,
        _domain_is_valid=Depends(verify_saleor_domain(validate_domain)),
        saleor_domain=Depends(saleor_domain_header),
    ):
        domain = saleor_domain
        auth_token = data.auth_token
        await install_app(domain, auth_token, [])
        return {}

    return router
