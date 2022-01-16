import hashlib
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from saleor_app.deps import (
    saleor_domain_header,
    saleor_token,
    verify_saleor_domain,
    verify_saleor_token,
    verify_webhook_signature,
)
from saleor_app.saleor.client import SaleorClient
from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.schemas.core import WebhookData


async def test_saleor_domain_header_missing():
    with pytest.raises(HTTPException) as excinfo:
        await saleor_domain_header(None)

    assert str(excinfo.value.detail) == "Missing X-SALEOR-DOMAIN header."


async def test_saleor_domain_header():
    assert await saleor_domain_header("saleor_domain") == "saleor_domain"


async def test_saleor_token(mock_request):
    assert await saleor_token(mock_request, "token") == "token"


async def test_saleor_token_from_settings(mock_request):
    assert await saleor_token(mock_request, None) == "test_token"


async def test_saleor_token_missing(mock_request):
    mock_request.app.app_settings.development_auth_token = None
    with pytest.raises(HTTPException) as excinfo:
        assert await saleor_token(mock_request, None) == "test_token"

    assert str(excinfo.value.detail) == "Missing X-SALEOR-TOKEN header."


async def test_verify_saleor_token(mock_request, mocker):
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.return_value = {
        "tokenVerify": {"isValid": True}
    }
    mocker.patch("saleor_app.deps.get_client_for_app", return_value=mock_saleor_client)
    assert await verify_saleor_token(mock_request, "saleor_domain", "token")


async def test_verify_saleor_token_invalid(mock_request, mocker):
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.return_value = {
        "tokenVerify": {"isValid": False}
    }
    mocker.patch("saleor_app.deps.get_client_for_app", return_value=mock_saleor_client)
    with pytest.raises(HTTPException) as excinfo:
        await verify_saleor_token(mock_request, "saleor_domain", "token")

    assert (
        excinfo.value.detail
        == "Provided X-SALEOR-DOMAIN and X-SALEOR-TOKEN are incorrect."
    )


async def test_verify_saleor_token_saleor_error(mock_request, mocker):
    mock_saleor_client = AsyncMock(SaleorClient)
    mock_saleor_client.__aenter__.return_value.execute.side_effect = GraphQLError(
        "error"
    )
    mocker.patch("saleor_app.deps.get_client_for_app", return_value=mock_saleor_client)
    assert not await verify_saleor_token(mock_request, "saleor_domain", "token")


async def test_verify_saleor_domain(mock_request):
    mock_request.app.validate_domain.return_value = True
    assert await verify_saleor_domain(mock_request, "saleor_domain")


async def test_verify_saleor_domain_invalid(mock_request):
    mock_request.app.validate_domain.return_value = False
    with pytest.raises(HTTPException) as excinfo:
        await verify_saleor_domain(mock_request, "saleor_domain")

    assert excinfo.value.detail == "Provided domain saleor_domain is invalid."


async def test_verify_webhook_signature(mock_request, mocker):
    mock_request.app.get_webhook_details.return_value = WebhookData(
        webhook_id="webhook_id", webhook_secret_key="webhook_secret_key"
    )
    mock_hmac_new = mocker.patch("saleor_app.deps.hmac.new")
    mock_hmac_new.return_value.hexdigest.return_value = "test_signature"
    assert (
        await verify_webhook_signature(mock_request, "test_signature", "saleor_domain")
        is None
    )
    mock_hmac_new.assert_called_once_with(
        b"webhook_secret_key", b"request_body", hashlib.sha256
    )


async def test_verify_webhook_signature_invalid(mock_request, mocker):
    mock_request.app.get_webhook_details.return_value = WebhookData(
        webhook_id="webhook_id", webhook_secret_key="webhook_secret_key"
    )
    mock_hmac_new = mocker.patch("saleor_app.deps.hmac.new")
    mock_hmac_new.return_value.hexdigest.return_value = "test_signature"

    with pytest.raises(HTTPException) as excinfo:
        await verify_webhook_signature(mock_request, "BAD_signature", "saleor_domain")

    assert excinfo.value.detail == "Invalid webhook signature for x-saleor-signature"
