# AWS SQS Handlers

!!! warning "Experimental"

    SQS event handing is in the works, more content to come


## SQS Consumer

The Saleor App Framework does not provide any means to consume events from an SQS queue. An SQS worker is a work in progress.

## Registering SQS handlers

```python
from saleor_app.schemas.handlers import SQSUrl


@app.webhook_router.sqs_event_route(
    SQSUrl(
        None,
        scheme="awssqs",
        user="test",
        password="test",
        host="localstack",
        port="4566",
        path="/00000000/product_updated",
    ),
    SaleorEventType.PRODUCT_UPDATED,
)
async def product_updated(
    payload: List[Webhook],
    saleor_domain=Depends(saleor_domain_header),
    example=Depends(example_dependency),
):
    print("Product updated!")
    print(payload)
```
