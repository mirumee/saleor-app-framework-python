from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from saleor_app.app import SaleorApp
from saleor_app.schemas.core import DomainName, WebhookData

from .configuration_endpoints import router as configuration_router
from .db import configuration, get_db
from .extension import router as extension_router
from .settings import settings
from .webhooks import webhook_handlers


async def validate_domain(domain_name: DomainName) -> bool:
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


async def get_webhook_details(domain_name: DomainName) -> WebhookData:
    return WebhookData(
        token="auth-token",
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    )


app = SaleorApp(
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    http_webhook_handlers=webhook_handlers,
    get_webhook_details=get_webhook_details,
)
app.configuration_router.include_router(configuration_router)
app.include_router(extension_router, prefix="/products")
app.include_saleor_app_routes()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["OPTIONS", "GET", "POST"],
)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
