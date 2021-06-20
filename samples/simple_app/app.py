import os
from pathlib import Path

from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from saleor_app.app import SaleorApp
from saleor_app.conf import Settings
from saleor_app.deps import ConfigurationFormDeps, ConfigurationDataDeps
from saleor_app.endpoints import get_form
from saleor_app.schemas.handlers import Payload, WebhookHandlers
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.manifest import SettingsManifest


PROJECT_DIR = Path(__file__).parent

settings = Settings(
    app_name="SimpleApp",
    project_dir=PROJECT_DIR,
    static_dir=PROJECT_DIR / "static",
    templates_dir=PROJECT_DIR / "static",
    manifest_path=PROJECT_DIR / "manifest.json",
    debug=True,
    manifest=SettingsManifest(
        name="Sample Saleor App",
        version="0.1.0",
        about="Sample Saleor App seving as an example.",
        dataPrivacy="",
        dataPrivacyUrl="",
        homepageUrl="http://172.17.0.1:5000/homepageUrl",
        supportUrl="http://172.17.0.1:5000/supportUrl",
        appUrl="http://172.17.0.1:5000/appUrl",
        tokenTargetUrl="http://172.17.0.1:5000/tokenTargetUrl",
        id="saleor-simple-sample",
        permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"]
    ),
    dev_saleor_domain="127.0.0.1:5000",
    dev_saleor_token="test_token",
)


class ConfigurationData(BaseModel):
    public_api_token: str
    private_api_key: int


async def validate_domain(domain_name:str)->bool:
    return domain_name == "172.17.0.1:8000"


async def store_app_data(domain_name: DomainName, app_data: WebhookData):
    print("Called store_app_data")
    print(domain_name)
    print(app_data)


async def get_webhook_details(domain_name: DomainName):
    print("Called store_app_data")


async def product_created(payload: Payload):
    print("Product created!")
    print(payload)


async def product_updated(payload: Payload):
    print("Product updated!")
    print(payload)


async def product_deleted(payload: Payload):
    print("Product deleted!")
    print(payload)


webhook_handlers = WebhookHandlers(
    product_created=product_created,
    product_updated=product_updated,
    product_deleted=product_deleted,
)


app = SaleorApp(
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    webhook_handlers=webhook_handlers,
    get_webhook_details=get_webhook_details,
)
app.configuration_router.get("/", response_class=HTMLResponse, name="configuration-form")(get_form)


@app.configuration_router.get("/data")
async def get_configuration_data(commons: ConfigurationDataDeps = Depends()):
    return ConfigurationData(public_api_token="api_token", private_api_key=1)


app.include_saleor_app_routes()


app.add_middleware(CORSMiddleware,
        allow_origins=["*"],
        allow_headers=["*"],
        allow_methods=["OPTIONS", "GET", "POST"],
)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


if __name__ == "__main__":
    os.environ["APP_SETTINGS"] = "app.settings"
    uvicorn.run("app:app", host="0.0.0.0", port=5000, debug=True, reload=True)
