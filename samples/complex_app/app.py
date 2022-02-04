from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from saleor_app.app import SaleorApp
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.handlers import SaleorEventType

from .db import get_db, get_domain_config, update_domain_config
from .endpoints.configuration import router as configuration_router
from .endpoints.extension import router as extension_router
from .settings import manifest, settings
from .webhooks import product_created, product_deleted, product_updated


async def validate_domain(saleor_domain: DomainName) -> bool:
    db = next(get_db())
    db_config = get_domain_config(db, saleor_domain)
    if db_config:
        return True
    return False


async def store_app_data(
    saleor_domain: DomainName, auth_token: str, webhook_data: WebhookData
):
    print("Called store_app_data")
    db = next(get_db())
    update_domain_config(
        db,
        saleor_domain,
        auth_token,
        webhook_data.webhook_id,
        webhook_data.webhook_secret_key,
    )


async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    db = next(get_db())
    db_config = get_domain_config(db, saleor_domain)
    return WebhookData(
        webhook_id=db_config.webhook_id,
        webhook_secret_key=db_config.webhook_secret,
    )


app = SaleorApp(
    manifest=manifest,
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    use_insecure_saleor_http=settings.debug,
)
app.configuration_router.include_router(configuration_router)
app.include_router(extension_router, prefix="/products")
app.include_saleor_app_routes()
app.include_webhook_router(get_webhook_details)

app.webhook_router.http_event_route(SaleorEventType.PRODUCT_CREATED)(product_created)
app.webhook_router.http_event_route(SaleorEventType.PRODUCT_UPDATED)(product_updated)
app.webhook_router.http_event_route(SaleorEventType.PRODUCT_DELETED)(product_deleted)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["OPTIONS", "GET", "POST"],
)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
