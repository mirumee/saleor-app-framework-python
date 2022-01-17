import json
from unittest.mock import AsyncMock

from httpx import AsyncClient

from saleor_app.deps import SALEOR_DOMAIN_HEADER
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.manifest import Manifest

# app.dependency_overrides[verify_saleor_domain] = lambda: True
# app.dependency_overrides[saleor_domain_header] = lambda: saleor_domain
# app.dependency_overrides[webhook_event_type] = lambda: "product_created"


async def test_manifest(saleor_app):
    base_url = "http://test_app.saleor.local"

    async with AsyncClient(app=saleor_app, base_url=base_url) as ac:
        response = await ac.get("configuration/manifest")

    manifest = saleor_app.manifest.dict(by_alias=True)
    manifest["appUrl"] = ""
    manifest["tokenTargetUrl"] = f"{base_url}/configuration/install"
    manifest["configurationUrl"] = f"{base_url}/configuration"
    manifest["extensions"][0]["url"] = f"{base_url}/extension"

    manifest = json.loads(json.dumps(Manifest(**manifest).dict(by_alias=True)))

    assert response.status_code == 200
    assert response.json() == manifest


async def test_install(saleor_app_with_webhooks, get_webhook_details, monkeypatch):
    install_app_mock = AsyncMock()
    monkeypatch.setattr("saleor_app.endpoints.install_app", install_app_mock)
    base_url = "http://test_app.saleor.local"

    saleor_app_with_webhooks.validate_domain = AsyncMock(return_value=True)

    async with AsyncClient(app=saleor_app_with_webhooks, base_url=base_url) as ac:
        response = await ac.post(
            "configuration/install",
            json={"auth_token": "saleor-app-token"},
            headers={SALEOR_DOMAIN_HEADER: "example.com"},
        )

    assert response.status_code == 200

    install_app_mock.assert_awaited_once_with(
        saleor_domain="example.com",
        auth_token="saleor-app-token",
        manifest=saleor_app_with_webhooks.manifest,
        events={
            "awssqs://username:password@localstack:4566/account_id/order_created": [
                SaleorEventType.ORDER_CREATED,
            ],
            "awssqs://username:password@localstack:4566/account_id/order_updated": [
                SaleorEventType.ORDER_UPDATED,
            ],
            "http://test_app.saleor.local/webhook": [
                SaleorEventType.PRODUCT_CREATED,
                SaleorEventType.PRODUCT_UPDATED,
                SaleorEventType.PRODUCT_DELETED,
            ],
        },
        use_insecure_saleor_http=False,
    )
