# HTTP Webhook Event Handling

While it's not necessary for every Saleor app to receive domain events from Saleor it is possible, as described in [:saleor-saleor: Saleor's docs](https://docs.saleor.io/docs/3.0/developer/extending#apps).

To configure your app to listen to HTTP webhooks issued from Saleor you need to **register your handlers** similarly as you would register your FastAPI endpoints.

## Setting up the Saleor App

### Getting Webhook details

The framework ensures that the webhook comes from a trusted source but to achieve that it needs to be provided with a way of retrieving the `webhook_secret` your app stored when the `save_app_data` was invoked (upon app installation). To do that you need to provide the `SaleorApp` with an async function doing just that.

```python linenums="1"
from saleor_app.schemas.core import DomainName, WebhookData


async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return WebhookData(
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    ) # (1)

```

1. :material-database: Typically the data would be taken from a database

The function takes the `saleor_domain` and must return a `WebhookData` Pydantic model instance

### Enabling the webhook router

The framework provides a special webhook router that allows you to use many different endpoints under the `/webhook` route. That router needs to be enabled with the `get_webhook_details` function:

```python linenums="1" hl_lines="16"
from saleor_app.app import SaleorApp
from saleor_app.schemas.core import DomainName, WebhookData


async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return WebhookData(
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    )


app = SaleorApp(
    #[...]
)

app.include_webhook_router(get_webhook_details=get_webhook_details)
```
### Defining webhook handlers

An HTTP webhook handler is a function that is exactly like one that one would use as a FastAPI endpoint. The difference is that we register those with a special router.

An example of a HTTP webhook handler is:

```python linenums="1" hl_lines="21-26"
from saleor_app.app import SaleorApp
from saleor_app.deps import saleor_domain_header # (1)
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.webhook import Webhook
from saleor_app.schemas.core import DomainName, WebhookData


async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return WebhookData(
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    )


app = SaleorApp(
    #[...]
)
app.include_webhook_router(get_webhook_details=get_webhook_details)


@app.webhook_router.http_event_route(SaleorEventType.PRODUCT_CREATED)
async def product_created(
    payload: List[Webhook],
    saleor_domain=Depends(saleor_domain_header)  # (2)
):
    await do_something(payload, saleor_domain)
```

1. :information_source: `saleor_app.deps` contains a set of FastAPI dependencies that you might find useful
2. :information_source: since `product_created` is just a FastAPI endpoint you have access to everything a usual endpoint would, like `request: Request`

If your app is bigger and you need to import your endpoints from a different module you can:

```python linenums="1" hl_lines="6 22-26"
from saleor_app.app import SaleorApp
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.webhook import Webhook
from saleor_app.schemas.core import DomainName, WebhookData

from my_app.webhook_handlers import product_created


async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return WebhookData(
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    )


app = SaleorApp(
    #[...]
)
app.include_webhook_router(get_webhook_details=get_webhook_details)


@app.webhook_router.http_event_route(
    SaleorEventType.PRODUCT_CREATED
)(product_created)
```

### Reinstall the app

Neither Saleor nor the app will automatically update the registered webhooks, you need to reinstall the app in Saleor if it was already installed.
