from logging import debug
from pathlib import Path
from typing import List, Optional

from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, BaseSettings
from starlette.middleware.cors import CORSMiddleware

from saleor_app.app import SaleorApp
from saleor_app.deps import ConfigurationDataDeps, saleor_domain_header
from saleor_app.endpoints import get_public_form
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.handlers import WebhookHandlers
from saleor_app.schemas.manifest import Manifest
from saleor_app.schemas.webhook import Webhook

PROJECT_DIR = Path(__file__).parent


class Settings(BaseSettings):
    debug: bool = False
    dev_saleor_token: Optional[str]


settings = Settings(
    debug=True,
    dev_saleor_token="test_token",
)


class ConfigurationData(BaseModel):
    public_api_token: str
    private_api_key: int


async def validate_domain(domain_name: DomainName) -> bool:
    return domain_name == "172.17.0.1:8000"


async def store_app_data(domain_name: DomainName, app_data: WebhookData):
    print("Called store_app_data")
    print(domain_name)
    print(app_data)


async def get_webhook_details(domain_name: DomainName) -> WebhookData:
    return WebhookData(
        token="auth-token",
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    )

async def example_dependency():
    return "example"


async def product_created(payload: List[Webhook], saleor_domain=Depends(saleor_domain_header), example = Depends(example_dependency)):
    print(example)
    print(saleor_domain)
    print("Product created!")
    print(payload)


async def product_updated(payload: List[Webhook], saleor_domain=Depends(saleor_domain_header), example = Depends(example_dependency)):
    print(example)
    print(saleor_domain)
    print("Product updated!")
    print(payload)


async def product_deleted(payload: List[Webhook], saleor_domain=Depends(saleor_domain_header), example = Depends(example_dependency)):
    print(example)
    print(saleor_domain)
    print("Product deleted!")
    print(payload)


app = SaleorApp(
    manifest=Manifest(
        name="Sample Saleor App",
        version="0.1.0",
        about="Sample Saleor App seving as an example.",
        data_privacy="",
        data_privacy_url="http://172.17.0.1:5000/dataPrivacyUrl",
        homepage_url="http://172.17.0.1:5000/homepageUrl",
        support_url="http://172.17.0.1:5000/supportUrl",
        id="saleor-simple-sample",
        permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"],
        configuration_url=Manifest.url_for("configuration-form"),
        extensions=[],
    ),
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    webhook_handlers=WebhookHandlers(
        product_created=product_created,
        product_updated=product_updated,
        product_deleted=product_deleted,
    ),
    get_webhook_details=get_webhook_details,
    use_insecure_saleor_http=settings.debug,
    development_auth_token=settings.dev_saleor_token
)
app.configuration_router.get(
    "/", response_class=HTMLResponse, name="configuration-form"
)(get_public_form)


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
