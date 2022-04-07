import json
from typing import Dict, List
from fastapi import Depends, Security
from fastapi.responses import PlainTextResponse

from pydantic import BaseSettings
from saleor_app.deps import ConfigurationDataDeps, ConfigurationFormDeps
from saleor_app.schemas.core import Saleor, WebhookData
from saleor_app.app import SaleorApp
from saleor_app.saleor.utils import get_client_for_app
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.webhook import Webhook
from saleor_app.security import SaleorWebhookVerification, saleor_webhook_security
from starlette.middleware.cors import CORSMiddleware

from single_tenant_app.db import (
    create_tables,
    upsert_app_data,
    retrieve_app_data,
    database,
)
from single_tenant_app.manifest import manifest


class Settings(BaseSettings):
    debug: bool = False
    saleor_domain: str
    use_insecure_saleor_http: bool = False


settings = Settings(
    debug=True,
    saleor_domain="172.17.0.1:8000",
    use_insecure_saleor_http=True,
)


async def validate_domain(saleor_domain: str) -> bool:
    return saleor_domain == settings.saleor_domain


async def store_app_data(
    saleor: Saleor, auth_token: str, webhook_data: WebhookData
):
    schema = "http" if settings.use_insecure_saleor_http else "https"
    async with get_client_for_app(
        f"{schema}://{saleor.domain}", manifest=manifest
    ) as saleor_client:
        jwks = json.dumps(await saleor_client.get_jwks())
    await upsert_app_data(
        auth_token=auth_token,
        webhook_id=webhook_data.webhook_id,
        webhook_secret=webhook_data.webhook_secret_key,
        saleor_jwks=jwks,
    )


async def get_webhook_details(saleor: Saleor) -> WebhookData:
    app_data = await retrieve_app_data()
    return WebhookData(
        webhook_id=app_data["webhook_id"],
        webhook_secret_key=app_data["webhook_secret"],
    )


async def get_saleor_jwks(saleor: Saleor) -> Dict[str, str]:
    app_data = await retrieve_app_data()
    return json.loads(app_data["saleor_jwks"])


app = SaleorApp(
    manifest=manifest,
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    get_saleor_jwks=get_saleor_jwks,
    use_insecure_saleor_http=settings.debug,
)
app.include_webhook_router(get_webhook_details=get_webhook_details)


@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_CREATED)
async def product_created(
    payload: List[Webhook],
    saleor_webhook_verification: SaleorWebhookVerification = Security(saleor_webhook_security)
):
    print("Product created!")
    print(payload, saleor_webhook_verification.saleor.domain)


@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_UPDATED)
async def product_updated(
    payload: List[Webhook],
    saleor_webhook_verification: SaleorWebhookVerification = Security(saleor_webhook_security)
):
    print("Product updated!")
    print(payload, saleor_webhook_verification.saleor.domain)


@app.configuration_router.get(
    "/", response_class=PlainTextResponse, name="configuration-form"
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
    return {
        "principal": commons.principal
    }


app.include_saleor_app_routes()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["OPTIONS", "GET", "POST"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    await create_tables()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
