from saleor_app.schemas.handlers import Payload, WebhookHandlers


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
