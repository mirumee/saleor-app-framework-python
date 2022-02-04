from typing import List

from fastapi.param_functions import Depends

from saleor_app.deps import saleor_domain_header
from saleor_app.schemas.webhook import Webhook


async def product_created(
    payload: List[Webhook], saleor_domain=Depends(saleor_domain_header)
):
    print("Product created!")
    print(payload)


async def product_updated(
    payload: List[Webhook], saleor_domain=Depends(saleor_domain_header)
):
    print("Product updated!")
    print(payload)


async def product_deleted(
    payload: List[Webhook], saleor_domain=Depends(saleor_domain_header)
):
    print("Product deleted!")
    print(payload)
