import os
from typing import Optional

import uvicorn
from configuration_endpoints import router
from db import configuration, get_db
from settings import settings
from sqlalchemy.orm.exc import NoResultFound
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from webhooks import webhook_handlers

from saleor_app.app import SaleorApp
from saleor_app.schemas.core import DomainName, WebhookData


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


async def get_webhook_details(domain_name: DomainName) -> Optional[WebhookData]:
    query = configuration.select().where(configuration.c.domain_name == domain_name)
    db = next(get_db())
    try:
        result = db.execute(query).one()
        return WebhookData(
            token=result.webhook_token,
            webhook_id=result.webhook_id,
            webhook_secret_key=result.webhook_secret,
        )
    except NoResultFound:
        return None


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
