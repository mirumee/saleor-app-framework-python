from typing import Set

from pydantic import BaseModel

from saleor_app.schemas.core import Saleor


class SaleorPrincipal(BaseModel):
    uid: str
    saleor: Saleor
    permissions: Set[str]
