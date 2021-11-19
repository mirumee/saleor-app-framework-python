from unittest.mock import AsyncMock, MagicMock

import pytest

from saleor_app.conf import Settings
from saleor_app.graphql import get_executor, get_saleor_api_url


@pytest.fixture()
def settings(monkeypatch):
    app_settings = Settings.construct(
        static_dir="", project_dir="", templates_dir="", manifest_path=""
    )
    monkeypatch.setattr("saleor_app.graphql.get_settings", lambda: app_settings)
    return app_settings


def test_get_saleor_api_url_debug_enabled(settings):
    settings.debug = True

    api_url = get_saleor_api_url("localhost:8000")

    assert api_url == "http://localhost:8000/graphql/"


def test_get_saleor_api_url(settings):
    settings.debug = False

    api_url = get_saleor_api_url("localhost:8000")
    assert api_url == "https://localhost:8000/graphql/"


@pytest.mark.asyncio
async def test_get_executor(monkeypatch, settings):
    settings.debug = False
    api_response = {"data": {"user": {"email": "admin@example.com"}}}
    response = AsyncMock()
    response.__aenter__.return_value.json.return_value = api_response
    request = MagicMock(return_value=response)
    monkeypatch.setattr("saleor_app.graphql.ClientSession.request", request)
    api_url = get_saleor_api_url("localhost:8000")
    executor = get_executor(host=api_url, auth_token="saleor-token")
    user_query = """
        query User($id: ID!) {
            user(id: $id) {
                email
            }
        }
    """
    await executor(user_query, variables={"id": "user-id"})
    request.assert_called_once_with(
        "POST",
        url="https://localhost:8000/graphql/",
        json={"query": user_query, "variables": {"id": "user-id"}},
        headers={"Authorization": "Bearer saleor-token"},
        timeout=10,
    )


@pytest.mark.asyncio
async def test_get_executor_returns_json_response(monkeypatch, settings):
    settings.debug = False
    api_response = {"data": {"user": {"email": "admin@example.com"}}}
    response = AsyncMock()
    response.__aenter__.return_value.json.return_value = api_response
    request = MagicMock(return_value=response)
    monkeypatch.setattr("saleor_app.graphql.ClientSession.request", request)
    api_url = get_saleor_api_url("localhost:8000")
    executor = get_executor(host=api_url, auth_token="saleor-token")
    user_query = """
        query User($id: ID!) {
            user(id: $id) {
                email
            }
        }
    """
    response, _errors = await executor(user_query, variables={"id": "user-id"})

    request.assert_called_once_with(
        "POST",
        url="https://localhost:8000/graphql/",
        json={"query": user_query, "variables": {"id": "user-id"}},
        headers={"Authorization": "Bearer saleor-token"},
        timeout=10,
    )

    assert response == api_response
