from typing import Awaitable, Callable

from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from .core.conf import settings
from .endpoints import configuration, manifest, webhook
from .schemas.core import (
    ConfigurationData,
    ConfigurationDataClass,
    ConfigurationDataUpdate,
    ConfigurationDataUpdateClass,
    DomainName,
)


def initialize_router(
    configuration_data_model: ConfigurationDataClass,
    configuration_data_update_model: ConfigurationDataUpdateClass,
    get_configuration: Callable[[DomainName], Awaitable[ConfigurationData]],
    update_configuration: Callable[
        [DomainName, ConfigurationDataUpdate], Awaitable[ConfigurationData]
    ],
    validate_domain: Callable[[DomainName], Awaitable[bool]],
    configuration_template: str,
) -> APIRouter:
    router = APIRouter()

    configuration_router = APIRouter(prefix="/configuration", tags=["configuration"])
    configuration_router.include_router(manifest.router)
    configuration_router.include_router(
        configuration.initialize_configuration_router(
            configuration_data_model,
            configuration_data_update_model,
            get_configuration,
            update_configuration,
            validate_domain,
            configuration_template,
        )
    )

    router.include_router(configuration_router)
    router.include_router(webhook.initialize_webhook_router(validate_domain))
    router.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    return router
