import json
from typing import List

from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse, PlainTextResponse

from saleor_app.app import SaleorApp
from saleor_app.deps import ConfigurationFormDeps
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.core import DomainName, WebhookData
from saleor_app.schemas.manifest import Manifest
from saleor_app.schemas.utils import LazyUrl
from saleor_app.deps import saleor_domain_header
from saleor_app.schemas.webhook import Webhook

async def validate_domain(saleor_domain: DomainName) -> bool:
    return saleor_domain == "mcabra.eu.saleor.cloud"


async def store_app_data(
    saleor_domain: DomainName, auth_token: str, webhook_data: WebhookData
):
    print("Called store_app_data")
    print(saleor_domain)
    print(auth_token)
    print(webhook_data) 


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
    app_url=LazyUrl("configuration-form"),
    extensions=[],
)


app = SaleorApp(
    manifest=manifest,
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    use_insecure_saleor_http=False,
)


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

app.include_saleor_app_routes()

async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return WebhookData(
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    ) # 

app.include_webhook_router(get_webhook_details=get_webhook_details)


MOJE_QUERY = """{test}"""

@app.webhook_router.http_event_route(SaleorEventType.CUSTOMER_CREATED, subscription_query=MOJE_QUERY)
async def customer_created(
    payload: List[Webhook],
    saleor_domain=Depends(saleor_domain_header)
):
    print (payload)

