import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from saleor_app.conf import get_settings
from saleor_app.deps import (
    SALEOR_DOMAIN_HEADER,
    SALEOR_EVENT_HEADER,
    SALEOR_SIGNATURE_HEADER,
    saleor_domain_header,
    verify_saleor_domain,
    verify_webhook_signature,
    webhook_event_type,
)
from saleor_app.schemas.handlers import WebhookHandlers
from saleor_app.schemas.manifest import Manifest
from saleor_app.tests.sample_app import store_app_data


@pytest.mark.asyncio
async def test_manifest(app):
    settings = get_settings()
    manifest = settings.manifest.dict(by_alias=True)

    base_url = "http://test"
    manifest["appUrl"] = ""
    manifest["tokenTargetUrl"] = f"{base_url}/configuration/install"
    manifest["configurationUrl"] = f"{base_url}/configuration"
    manifest["extensions"][0]["url"] = f"{base_url}/extension"

    manifest = json.loads(json.dumps(Manifest(**manifest).dict(by_alias=True)))

    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("configuration/manifest")
    assert response.status_code == 200
    assert response.json() == manifest


@pytest.mark.asyncio
async def test_install(app, monkeypatch):
    install_app_mock = AsyncMock()
    monkeypatch.setattr("saleor_app.endpoints.install_app", install_app_mock)

    base_url = "http://test"

    validate_domain_mock = AsyncMock(return_value=True)
    app.extra["saleor"]["validate_domain"] = validate_domain_mock

    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "configuration/install",
            json={"auth_token": "saleor-app-token"},
            headers={SALEOR_DOMAIN_HEADER: "example.com"},
        )
        assert response.status_code == 200
    install_app_mock.assert_awaited_once_with(
        "example.com",
        "saleor-app-token",
        ["product_created", "product_updated", "product_deleted"],
        "http://test/webhook",
        store_app_data,
    )

    assert validate_domain_mock.called


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
async def test_handle_webhook_incorrect_domain_header(app):
    saleor_domain = "example.com"

    app.dependency_overrides[webhook_event_type] = lambda: "product_created"
    app.dependency_overrides[verify_webhook_signature] = lambda: True

    base_url = "http://test.com"

    validate_domain_mock = AsyncMock(return_value=False)
    app.extra["saleor"]["validate_domain"] = validate_domain_mock

    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "/webhook",
            json=webhook_payload,
            headers={SALEOR_DOMAIN_HEADER: saleor_domain},
        )
        assert response.status_code == 400
    assert validate_domain_mock.called


@pytest.mark.asyncio
async def test_handle_webhook_missing_domain_header(app):
    app.dependency_overrides[webhook_event_type] = lambda: "product_created"
    app.dependency_overrides[verify_webhook_signature] = lambda: True

    base_url = "http://test.com"

    validate_domain_mock = AsyncMock(return_value=False)
    app.extra["saleor"]["validate_domain"] = validate_domain_mock

    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post("/webhook", json=webhook_payload)
        assert response.status_code == 400
    assert not validate_domain_mock.called


@pytest.mark.asyncio
async def test_handle_webhook_missing_event_type_header(app):
    saleor_domain = "example.com"

    app.dependency_overrides[verify_saleor_domain] = lambda: True
    app.dependency_overrides[saleor_domain_header] = lambda: saleor_domain

    app.dependency_overrides[verify_webhook_signature] = lambda: True

    base_url = "http://test.com"

    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post("/webhook", json=webhook_payload)
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_handle_webhook_incorrect_event_type_header(app):
    saleor_domain = "example.com"

    app.dependency_overrides[verify_saleor_domain] = lambda: True
    app.dependency_overrides[saleor_domain_header] = lambda: saleor_domain
    app.dependency_overrides[verify_webhook_signature] = lambda: True

    base_url = "http://test.com"

    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "/webhook",
            json=webhook_payload,
            headers={SALEOR_EVENT_HEADER: "incorrect_event_type"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_handle_webhook_missing_signature_header(app):
    saleor_domain = "example.com"

    app.dependency_overrides[verify_saleor_domain] = lambda: True
    app.dependency_overrides[saleor_domain_header] = lambda: saleor_domain
    app.dependency_overrides[webhook_event_type] = lambda: "product_created"

    base_url = "http://test.com"

    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post("/webhook", json=webhook_payload)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_handle_webhook_incorrect_signature_header(app):
    saleor_domain = "example.com"

    app.dependency_overrides[verify_saleor_domain] = lambda: True
    app.dependency_overrides[saleor_domain_header] = lambda: saleor_domain
    app.dependency_overrides[webhook_event_type] = lambda: "product_created"

    base_url = "http://test.com"

    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "/webhook",
            json=webhook_payload,
            headers={SALEOR_SIGNATURE_HEADER: "incorrect"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_handle_webhook_correct_signature_header(app):
    saleor_domain = "example.com"

    app.dependency_overrides[verify_saleor_domain] = lambda: True
    app.dependency_overrides[saleor_domain_header] = lambda: saleor_domain
    app.dependency_overrides[webhook_event_type] = lambda: "product_created"

    base_url = "http://test.com"

    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "/webhook",
            json=webhook_payload,
            headers={
                SALEOR_SIGNATURE_HEADER: (
                    "1d58736bf95a69ac1788c2548d5eef226aedf87a9794d42ba48609aeca760683"
                ),
            },
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_handle_webhook(app):
    product_created_mock = AsyncMock(return_value="")
    product_updated_mock = AsyncMock(return_value="")

    saleor_domain = "example.com"

    base_url = "http://test.com"

    validate_domain_mock = AsyncMock(return_value=True)
    app.extra["saleor"]["validate_domain"] = validate_domain_mock

    app.extra["saleor"]["http_webhook_handlers"] = WebhookHandlers(
        product_created=product_created_mock,
        product_updated=product_updated_mock,
    )
    webhook_payload = [{"data": "webhook-data"}]
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post(
            "/webhook",
            json=webhook_payload,
            headers={
                SALEOR_EVENT_HEADER: "product_created",
                SALEOR_SIGNATURE_HEADER: (
                    "1d58736bf95a69ac1788c2548d5eef226aedf87a9794d42ba48609aeca760683"
                ),
                SALEOR_DOMAIN_HEADER: saleor_domain,
            },
        )
        assert response.status_code == 200

    product_created_mock.assert_called_once_with(webhook_payload, saleor_domain)
    assert not product_updated_mock.called
