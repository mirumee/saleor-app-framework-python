from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from httpx import AsyncClient

from saleor_app.conf import get_settings
from saleor_app.deps import (
    saleor_domain_header,
    verify_saleor_domain,
    verify_webhook_signature,
    webhook_event_type,
)
from saleor_app.schemas.handlers import WebhookHandlers
from saleor_app.tests.sample_app import get_app, store_app_data


@pytest.mark.asyncio
async def test_manifest(app):
    settings = get_settings()
    manifest = settings.manifest.dict(by_alias=True)

    base_url = "http://test"
    manifest["appUrl"] = ""
    manifest["tokenTargetUrl"] = f"{base_url}/configuration/install"
    manifest["configurationUrl"] = f"{base_url}/configuration/"

    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("configuration/manifest")
    assert response.status_code == 200
    assert response.json() == manifest


@pytest.mark.asyncio
async def test_install(app, monkeypatch):
    app.dependency_overrides[verify_saleor_domain] = lambda: True
    app.dependency_overrides[saleor_domain_header] = lambda: "example.com"

    install_app_mock = AsyncMock()
    monkeypatch.setattr("saleor_app.endpoints.install_app", install_app_mock)

    base_url = "http://test"
    async with AsyncClient(app=app, base_url=base_url) as ac:
        await ac.post("configuration/install", json={"auth_token": "saleor-app-token"})
    install_app_mock.assert_awaited_once_with(
        "example.com",
        "saleor-app-token",
        ["product_created", "product_updated", "product_deleted"],
        "http://test/webhook/",
        store_app_data,
    )


@pytest.mark.asyncio
async def test_install_failed_installation(app, monkeypatch):
    app.dependency_overrides[verify_saleor_domain] = lambda: True
    app.dependency_overrides[saleor_domain_header] = lambda: "example.com"

    json_failed_response = {
        "data": {
            "webhookCreate": {
                "errors": [
                    {
                        "field": None,
                        "message": "Missing token or app",
                        "code": "INVALID",
                    }
                ],
                "webhook": None,
            }
        }
    }
    response = MagicMock()
    response.__getitem__.side_effect = json_failed_response.__getitem__
    response.get.side_effect = json_failed_response.get

    errors = None

    mocked_executor = AsyncMock(return_value=(response, errors))
    monkeypatch.setattr(
        "saleor_app.install.get_executor", lambda host, auth_token: mocked_executor
    )

    base_url = "http://test"
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "configuration/install", json={"auth_token": "saleor-app-token"}
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_install_invalid_saleor_domain(app, monkeypatch):
    app.dependency_overrides[saleor_domain_header] = lambda: "example.com"

    install_app_mock = AsyncMock()
    monkeypatch.setattr("saleor_app.endpoints.install_app", install_app_mock)

    base_url = "http://test"
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "configuration/install", json={"auth_token": "saleor-app-token"}
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_install_missing_saleor_domain_header(app, monkeypatch):
    install_app_mock = AsyncMock()
    monkeypatch.setattr("saleor_app.endpoints.install_app", install_app_mock)

    base_url = "http://test"
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "configuration/install", json={"auth_token": "saleor-app-token"}
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_handle_webhook(monkeypatch):
    product_created_mock = AsyncMock(return_value="")
    product_updated_mock = AsyncMock(return_value="")
    monkeypatch.setattr(
        "saleor_app.tests.sample_app.product_created", product_created_mock
    )

    saleor_domain = "example.com"
    app = get_app()

    verify_saleor_domain_mock = Mock(return_value=True)
    saleor_domain_header_mock = Mock(return_value=saleor_domain)
    webhook_event_type_mock = Mock(return_value="product_created")
    verify_webhook_signature_mock = Mock(return_value=lambda: True)

    app.dependency_overrides[verify_saleor_domain] = lambda: verify_saleor_domain_mock()
    app.dependency_overrides[saleor_domain_header] = lambda: saleor_domain_header_mock()
    app.dependency_overrides[webhook_event_type] = lambda: webhook_event_type_mock()
    app.dependency_overrides[
        verify_webhook_signature
    ] = lambda: verify_webhook_signature_mock()

    base_url = "http://test.com"

    app.extra["saleor"]["webhook_handlers"] = WebhookHandlers(
        product_created=product_created_mock,
        product_updated=product_updated_mock,
    )
    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        await ac.post("/webhook", json=webhook_payload)
    product_created_mock.assert_called_once_with(webhook_payload, saleor_domain)

    assert not product_updated_mock.called

    assert verify_saleor_domain_mock.called
    assert saleor_domain_header_mock.called
    assert webhook_event_type_mock.called
    assert verify_webhook_signature_mock.called
