from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from saleor_app.conf import get_settings
from saleor_app.deps import saleor_domain_header, verify_saleor_domain
from saleor_app.tests.sample_app import store_app_data


@pytest.mark.asyncio
async def test_manifest(app):
    settings = get_settings()
    manifest = settings.manifest.dict()

    base_url = "http://test"
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
