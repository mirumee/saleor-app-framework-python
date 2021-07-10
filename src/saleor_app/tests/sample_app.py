import os

from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from saleor_app.app import SaleorApp
from saleor_app.conf import get_settings
from saleor_app.endpoints import get_form
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.handlers import Payload, WebhookHandlers

os.environ["APP_SETTINGS"] = "saleor_app.tests.conftest.test_app_settings"


class ConfigurationData(BaseModel):
    public_api_token: str
    private_api_key: int


async def validate_domain(domain_name: str) -> bool:
    return domain_name == "172.17.0.1:8000"


async def store_app_data(domain_name: DomainName, app_data: WebhookData):
    ...


async def get_webhook_details(domain_name: DomainName):
    ...


async def product_created(payload: Payload, saleor_domain: DomainName):
    ...


async def product_updated(payload: Payload, saleor_domain: DomainName):
    ...


async def product_deleted(payload: Payload, saleor_domain: DomainName):
    ...


def get_app():
    webhook_handlers = WebhookHandlers(
        product_created=product_created,
        product_updated=product_updated,
        product_deleted=product_deleted,
    )

    settings = get_settings()
    app = SaleorApp(
        validate_domain=validate_domain,
        save_app_data=store_app_data,
        webhook_handlers=webhook_handlers,
        get_webhook_details=get_webhook_details,
    )
    app.configuration_router.get(
        "/", response_class=HTMLResponse, name="configuration-form"
    )(get_form)

    app.include_saleor_app_routes()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_headers=["*"],
        allow_methods=["OPTIONS", "GET", "POST"],
    )
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
    return app
