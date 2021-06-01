from typing import Awaitable, Callable

from fastapi import APIRouter

from .core.types import DomainName, InstallAppData
from .endpoints import configuration, manifest, webhook
from .schemas.core import (
    ConfigurationData,
    ConfigurationDataClass,
    ConfigurationDataUpdate,
    ConfigurationDataUpdateClass,
)
from .schemas.webhooks.handlers import WebhookHandlers


def initialize_router(
    configuration_data_model: ConfigurationDataClass,
    configuration_data_update_model: ConfigurationDataUpdateClass,
    get_configuration: Callable[[DomainName], Awaitable[ConfigurationData]],
    update_configuration: Callable[
        [DomainName, ConfigurationDataUpdate], Awaitable[ConfigurationData]
    ],
    validate_domain: Callable[[DomainName], Awaitable[bool]],
    configuration_template: str,
    save_app_data: Callable[[DomainName, InstallAppData], Awaitable],
    webhook_handlers: WebhookHandlers,
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
            save_app_data,
            webhook_handlers.get_assigned_events(),
        )
    )

    router.include_router(configuration_router)
    router.include_router(
        webhook.initialize_webhook_router(validate_domain, webhook_handlers)
    )

    return router
