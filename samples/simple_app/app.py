import json
from typing import List, Optional

from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, BaseSettings
from starlette.middleware.cors import CORSMiddleware

from saleor_app.app import SaleorApp
from saleor_app.deps import (
    ConfigurationDataDeps,
    ConfigurationFormDeps,
    saleor_domain_header,
)
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.manifest import Manifest
from saleor_app.schemas.utils import LazyUrl
from saleor_app.schemas.webhook import Webhook


class Settings(BaseSettings):
    debug: bool = False
    development_auth_token: Optional[str] = None


settings = Settings(
    debug=True,
    development_auth_token="test_token",
)


class ConfigurationData(BaseModel):
    public_api_token: str
    private_api_key: int


async def validate_domain(saleor_domain: DomainName) -> bool:
    return saleor_domain == "172.17.0.1:8000"


async def store_app_data(
    saleor_domain: DomainName, auth_token: str, webhook_data: WebhookData
):
    print("Called store_app_data")
    print(saleor_domain)
    print(auth_token)
    print(webhook_data)


async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return WebhookData(
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    )


async def example_dependency():
    return "example"


manifest = Manifest(
    name="Sample Saleor App",
    version="0.1.0",
    about="Sample Saleor App seving as an example.",
    data_privacy="",
    data_privacy_url="http://samle-saleor-app.example.com/dataPrivacyUrl",
    homepage_url="http://samle-saleor-app.example.com/homepageUrl",
    support_url="http://samle-saleor-app.example.com/supportUrl",
    id="saleor-simple-sample",
    permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"],
    configuration_url=LazyUrl("configuration-form"),
    extensions=[],
)


app = SaleorApp(
    manifest=manifest,
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    use_insecure_saleor_http=settings.debug,
    development_auth_token=settings.development_auth_token,
)
app.include_webhook_router(get_webhook_details=get_webhook_details)


@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_CREATED)
async def product_created(
    payload: List[Webhook],
    saleor_domain=Depends(saleor_domain_header),
    example=Depends(example_dependency),
):
    print("Product created!")
    print(payload)


@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_UPDATED)
async def product_updated(
    payload: List[Webhook],
    saleor_domain=Depends(saleor_domain_header),
    example=Depends(example_dependency),
):
    print("Product updated!")
    print(payload)


@app.configuration_router.get(
    "/", response_class=HTMLResponse, name="configuration-form"
)
async def get_public_form(commons: ConfigurationFormDeps = Depends()):
    context = {
        "request": str(commons.request),
        "form_url": str(commons.request.url),
        "saleor_domain": commons.saleor_domain,
    }
    return PlainTextResponse(json.dumps(context, indent=4))


@app.configuration_router.get("/data")
async def get_configuration_data(commons: ConfigurationDataDeps = Depends()):
    return ConfigurationData(public_api_token="api_token", private_api_key=11)


app.include_saleor_app_routes()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["OPTIONS", "GET", "POST"],
)
