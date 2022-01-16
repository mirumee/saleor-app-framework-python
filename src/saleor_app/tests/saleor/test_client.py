from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import ClientTimeout

from saleor_app.saleor.client import SaleorClient
from saleor_app.saleor.exceptions import GraphQLError


@pytest.mark.parametrize(
    "auth_token, timeout", ((None, None), (None, 5), ("token", None), ("token", 10))
)
async def test__init__(auth_token, timeout):
    kwargs = {
        "saleor_url": "http://saleor.local",
        "user_agent": "saleor_client/test-0.0.1",
    }
    if auth_token is not None:
        kwargs["auth_token"] = auth_token
    if timeout is not None:
        kwargs["timeout"] = timeout

    client = SaleorClient(**kwargs)

    assert str(client.session._base_url) == kwargs["saleor_url"]

    if auth_token is not None:
        assert client.session.headers["Authorization"] == f"Bearer {auth_token}"
    if timeout is not None:
        assert client.session.timeout == ClientTimeout(timeout)


async def test_close(mocker):
    client = SaleorClient(saleor_url="http://saleor.local", user_agent="test")
    spy = mocker.spy(client, "close")

    await client.close()

    spy.assert_awaited_once_with()


async def test_context_manager(mocker):
    async with SaleorClient(
        saleor_url="http://saleor.local", user_agent="test"
    ) as saleor:
        spy = mocker.spy(saleor, "close")
        assert isinstance(saleor, SaleorClient)

    spy.assert_awaited_once_with()


async def test_execute(monkeypatch):
    mock_session = AsyncMock(aiohttp.ClientSession)
    mock_session.post.return_value.__aenter__.return_value.json.return_value = {
        "data": "response_data"
    }
    async with SaleorClient(
        saleor_url="http://saleor.local", user_agent="test"
    ) as saleor:
        monkeypatch.setattr(saleor, "session", mock_session, raising=True)
        assert (
            await saleor.execute("QUERY", variables={"test": "value"})
            == "response_data"
        )

    mock_session.post.assert_called_once_with(
        url="/graphql/", json={"query": "QUERY", "variables": {"test": "value"}}
    )


async def test_execute_error(monkeypatch):
    mock_session = AsyncMock(aiohttp.ClientSession)
    mock_session.post.return_value.__aenter__.return_value.json.return_value = {
        "data": "response_data",
        "errors": [{"message": "there are errors"}],
    }
    async with SaleorClient(
        saleor_url="http://saleor.local", user_agent="test"
    ) as saleor:
        monkeypatch.setattr(saleor, "session", mock_session, raising=True)
        with pytest.raises(GraphQLError) as excinfo:
            await saleor.execute("QUERY", variables={"test": "value"})

    assert excinfo.value.errors == [{"message": "there are errors"}]
    assert excinfo.value.response_data == "response_data"
