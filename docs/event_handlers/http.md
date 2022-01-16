# HTTP Webhook Event Handling

While it's not neccesary for every Saleor app to receive domain events from Saleor it is possible, as described in [:saleor-saleor: Saleor's docs](https://docs.saleor.io/docs/3.0/developer/extending#apps).

To configure your app to listen to HTTP webhooks issued from Saleor you need to provide your app with two more arguments.

## Setting up the Saleor App

### Defining webhook handlers

An HTTP webhook handler is a function that is exactly ile one that one would use as a FastAPI endpoint. There is no need to register those as routes since that is deatl with when the app is initialized.

An example of a http webhook handler is:

```python
from saleor_app.schemas.webhook import Webhook
from saleor_app.deps import saleor_domain_header # (1)


async def product_created(
    payload: List[Webhook],
    saleor_domain=Depends(saleor_domain_header)  # (2)
):
    await do_something(payload, saleor_domain)
```

1. :information_source: `saleor_app.deps` contains a set of FastAPI dependencies that you might find useful
2. :information_source: since `product_created` is just a FastAPI endpoint you have access for everything a usual endpoint would, like `request: Request`

### Getting Webhook details

The framework ensures that the webhook comes from a trusted source but to achieve that it needs to be provided with a way of retreivng the webhook_secret your app sotred when the `save_app_data` was invoked (upon app installation). To do that you need to provide the `SaleorApp` with an async function doing just that.

```python
from saleor_app.schemas.core import DomainName, WebhookData


async def get_webhook_details(saleor_domain: DomainName) -> WebhookData:
    return WebhookData(
        webhook_id="webhook-id",
        webhook_secret_key="webhook-secret-key",
    ) # (1)

```

1. :material-database: Typically the data would be taken from a database

The function takes the `saleor_domain` and must return a `WebhookData` Pytantic model instance

### Injecting the handlers into the app

Now when your handlers code is prepared you can provide it to the `SaleorApp`:

```python
from saleor_app.schemas.handlers import WebhookHandlers


app = SaleorApp(
    # ...
    get_webhook_details=get_webhook_details,
    http_webhook_handlers=WebhookHandlers(
        product_created=product_created,
    ),
    # ...
)
```

### Reinstall the app

Neither Saleor nor the app will automatically update the registered webhooks, you need to reinstall the app in Saleor if it was already installed.
