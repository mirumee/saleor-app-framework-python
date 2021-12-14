from saleor_app.schemas.core import DomainName
from saleor_app.schemas.handlers import Payload, WebhookHandlers


async def product_created(payload: Payload, saleor_domain: DomainName):
    print("Product created!")
    print(payload)


async def product_updated(payload: Payload, saleor_domain: DomainName):
    print("Product updated!")
    print(payload)


async def product_deleted(payload: Payload, saleor_domain: DomainName):
    print("Product deleted!")
    print(payload)


http_webhook_handlers = WebhookHandlers(
    product_created=product_created,
    product_updated=product_updated,
    product_deleted=product_deleted,
)
