from saleor_app.saleor.client import SaleorClient
from saleor_app.schemas.manifest import Manifest


def get_client_for_app(saleor_url: str, manifest: Manifest, **kwargs) -> SaleorClient:
    return SaleorClient(
        saleor_url=saleor_url,
        user_agent=f"saleor_client/{manifest.id}-{manifest.version}",
        **kwargs,
    )
