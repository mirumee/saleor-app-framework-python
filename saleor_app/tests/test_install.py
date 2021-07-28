from unittest.mock import AsyncMock, MagicMock

import pytest

from saleor_app.conf import get_settings
from saleor_app.errors import InstallAppError
from saleor_app.graphql import GraphQLError
from saleor_app.install import CREATE_WEBHOOK, install_app
from saleor_app.schemas.core import WebhookData


@pytest.mark.asyncio
async def test_install_app(monkeypatch):
    saleor_webhook_id = "V2ViaG9vazoz"
    json_response = {
        "data": {"webhookCreate": {"errors": [], "webhook": {"id": saleor_webhook_id}}}
    }
    settings = get_settings()
    response = MagicMock()
    response.__getitem__.side_effect = json_response.__getitem__
    response.get.side_effect = json_response.get

    errors = None

    mocked_executor = AsyncMock(return_value=(response, errors))
    monkeypatch.setattr(
        "saleor_app.install.get_executor", lambda host, auth_token: mocked_executor
    )
    monkeypatch.setattr("saleor_app.install.secrets.choice", lambda _: "a")

    save_app_data_fun = AsyncMock()

    events = ["ORDER_CREATED", "PRODUCT_CREATED"]
    target_url = "saleor.io/app/webhook-url"
    saleor_store_domain = "saleor.io"
    saleor_app_token = "saleor-token"

    await install_app(
        domain=saleor_store_domain,
        token=saleor_app_token,
        events=events,
        target_url=target_url,
        save_app_data=save_app_data_fun,
    )

    expected_secret_key = "a" * 20
    variables = {
        "input": {
            "targetUrl": target_url,
            "events": [event.upper() for event in events],
            "name": settings.app_name,
            "secretKey": expected_secret_key,
        }
    }
    mocked_executor.assert_awaited_once_with(CREATE_WEBHOOK, variables=variables)

    save_app_data_fun.assert_awaited_once_with(
        saleor_store_domain,
        WebhookData(
            token=saleor_app_token,
            webhook_id=saleor_webhook_id,
            webhook_secret_key=expected_secret_key,
        ),
    )


@pytest.mark.asyncio
async def test_install_app_graphql_error(monkeypatch):
    json_failed_response = {
        "errors": [
            {
                "message": "You do not have permission to perform this action",
            }
        ]
    }
    settings = get_settings()
    response = MagicMock()
    response.__getitem__.side_effect = json_failed_response.__getitem__
    response.get.side_effect = json_failed_response.get

    errors = [
        {
            "message": "You do not have permission to perform this action",
        }
    ]

    mocked_executor = AsyncMock(return_value=(response, errors))
    monkeypatch.setattr(
        "saleor_app.install.get_executor", lambda host, auth_token: mocked_executor
    )
    monkeypatch.setattr("saleor_app.install.secrets.choice", lambda _: "a")

    save_app_data_fun = AsyncMock()

    events = ["ORDER_CREATED", "PRODUCT_CREATED"]
    target_url = "saleor.io/app/webhook-url"
    saleor_store_domain = "saleor.io"
    saleor_app_token = "saleor-token"

    with pytest.raises(GraphQLError):
        await install_app(
            domain=saleor_store_domain,
            token=saleor_app_token,
            events=events,
            target_url=target_url,
            save_app_data=save_app_data_fun,
        )

    expected_secret_key = "a" * 20
    variables = {
        "input": {
            "targetUrl": target_url,
            "events": [event.upper() for event in events],
            "name": settings.app_name,
            "secretKey": expected_secret_key,
        }
    }
    mocked_executor.assert_awaited_once_with(CREATE_WEBHOOK, variables=variables)

    assert not save_app_data_fun.called


@pytest.mark.asyncio
async def test_install_app_mutation_error(monkeypatch):
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
    settings = get_settings()
    response = MagicMock()
    response.__getitem__.side_effect = json_failed_response.__getitem__
    response.get.side_effect = json_failed_response.get

    errors = None

    mocked_executor = AsyncMock(return_value=(response, errors))
    monkeypatch.setattr(
        "saleor_app.install.get_executor", lambda host, auth_token: mocked_executor
    )
    monkeypatch.setattr("saleor_app.install.secrets.choice", lambda _: "a")

    save_app_data_fun = AsyncMock()

    events = ["ORDER_CREATED", "PRODUCT_CREATED"]
    target_url = "saleor.io/app/webhook-url"
    saleor_store_domain = "saleor.io"
    saleor_app_token = "saleor-token"

    with pytest.raises(InstallAppError):
        await install_app(
            domain=saleor_store_domain,
            token=saleor_app_token,
            events=events,
            target_url=target_url,
            save_app_data=save_app_data_fun,
        )

    expected_secret_key = "a" * 20
    variables = {
        "input": {
            "targetUrl": target_url,
            "events": [event.upper() for event in events],
            "name": settings.app_name,
            "secretKey": expected_secret_key,
        }
    }
    mocked_executor.assert_awaited_once_with(CREATE_WEBHOOK, variables=variables)

    assert not save_app_data_fun.called
