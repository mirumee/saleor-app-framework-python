import os

from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import uvicorn

from saleor_app.app import SaleorApp
from saleor_app.schemas.core import DomainName, WebhookData

from settings import settings
from webhooks import webhook_handlers
from configuration_endpoints import router
from db import get_db, configuration


async def validate_domain(domain_name: str) -> bool:
    return domain_name == "172.17.0.1:8000"


async def store_app_data(domain_name: DomainName, app_data: WebhookData):
    print("Called store_app_data")
    query = configuration.insert().values(
        domain_name=domain_name,
        webhook_id=app_data.webhook_id,
        webhook_token=app_data.token,
        webhook_secret=app_data.webhook_secret_key,
    )
    db = next(get_db())
    db.execute(query)
    db.commit()


async def get_webhook_details(domain_name: DomainName):
    print("Called store_app_data")


app = SaleorApp(
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    webhook_handlers=webhook_handlers,
    get_webhook_details=get_webhook_details,
)
app.configuration_router.include_router(router)
app.include_saleor_app_routes()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["OPTIONS", "GET", "POST"],
)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


if __name__ == "__main__":
    os.environ["APP_SETTINGS"] = "app.settings"
    uvicorn.run("app:app", host="0.0.0.0", port=5000, debug=True, reload=True)
