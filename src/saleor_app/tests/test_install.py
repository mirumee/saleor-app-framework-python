from unittest.mock import AsyncMock

from saleor_app.install import install_app
from saleor_app.saleor.client import SaleorClient
from saleor_app.saleor.mutations import CREATE_WEBHOOK
from saleor_app.schemas.core import WebhookData


async def test_install_app(mocker, manifest):
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.return_value = {
        "webhookCreate": {"webhook": {"id": "123"}}
    }
    mock_get_client_for_app = mocker.patch(
        "saleor_app.install.get_client_for_app", return_value=mock_saleor_client
    )
    mocker.patch("saleor_app.install.secrets.choice", return_value="A")

    assert (
        await install_app(
            saleor_domain="saleor_domain",
            auth_token="test_token",
            manifest=manifest,
            events={"queue_1": ["TEST_EVENT_1"], "url_1": ["TEST_EVENT_2"]},
            use_insecure_saleor_http=True,
        )
        == WebhookData(webhook_id="123", webhook_secret_key="A" * 20)
    )

    mock_get_client_for_app.assert_called_once_with(
        "http://saleor_domain", manifest=manifest, auth_token="test_token"
    )

    assert mock_saleor_client.__aenter__.return_value.execute.call_count == 2
    mock_saleor_client.__aenter__.return_value.execute.assert_any_await(
        CREATE_WEBHOOK,
        variables={
            "input": {
                "targetUrl": "queue_1",
                "events": ["TEST_EVENT_1"],
                "name": f"{manifest.name}",
                "secretKey": "A" * 20,
            }
        },
    )

    mock_saleor_client.__aenter__.return_value.execute.assert_any_await(
        CREATE_WEBHOOK,
        variables={
            "input": {
                "targetUrl": "url_1",
                "events": ["TEST_EVENT_2"],
                "name": f"{manifest.name}",
                "secretKey": "A" * 20,
            }
        },
    )


async def test_install_app_secure_https(mocker, manifest):
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.return_value = {
        "webhookCreate": {"webhook": {"id": "123"}}
    }
    mock_get_client_for_app = mocker.patch(
        "saleor_app.install.get_client_for_app", return_value=mock_saleor_client
    )
    mocker.patch("saleor_app.install.secrets.choice", return_value="A")
    assert (
        await install_app(
            saleor_domain="saleor_domain",
            auth_token="test_token",
            manifest=manifest,
            events={"queue_1": ["TEST_EVENT_1"], "url_1": ["TEST_EVENT_2"]},
            use_insecure_saleor_http=False,
        )
        == WebhookData(webhook_id="123", webhook_secret_key="A" * 20)
    )

    mock_get_client_for_app.assert_called_once_with(
        "https://saleor_domain", manifest=manifest, auth_token="test_token"
    )
