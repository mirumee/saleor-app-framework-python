from unittest.mock import AsyncMock, Mock

import pytest

from saleor_app.app import SaleorApp
from saleor_app.schemas.handlers import SQSHandlers, WebhookHandlers
from saleor_app.schemas.manifest import Extension, Manifest
from saleor_app.schemas.utils import LazyUrl
from saleor_app.settings import AWSSettings, SaleorAppSettings


class TestSettings(SaleorAppSettings):
    debug: bool = False


@pytest.fixture
def settings():
    return TestSettings(
        debug=True,
        development_auth_token="test_token",
    )


@pytest.fixture
def settings_with_aws():
    return TestSettings(
        debug=True,
        development_auth_token="test_token",
        aws=AWSSettings(
            account_id="",
            access_key_id="",
            secret_access_key="",
            region="",
        ),
    )


@pytest.fixture
def manifest():
    return Manifest(
        name="Sample Saleor App",
        version="0.1.0",
        about="Sample Saleor App seving as an example.",
        data_privacy="",
        data_privacy_url="http://172.17.0.1:5000/dataPrivacyUrl",
        homepage_url="http://172.17.0.1:5000/homepageUrl",
        support_url="http://172.17.0.1:5000/supportUrl",
        id="saleor-simple-sample",
        permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"],
        configuration_url=LazyUrl("configuration-form"),
        extensions=[
            Extension(
                label="Custom Product Create",
                view="PRODUCT",
                type="OVERVIEW",
                target="CREATE",
                permissions=["MANAGE_PRODUCTS"],
                url=LazyUrl("extension"),
            )
        ],
    )


@pytest.fixture
def http_webhook_handlers():
    return WebhookHandlers(
        product_created=Mock(),
        product_updated=Mock(),
        product_deleted=Mock(),
    )


@pytest.fixture
def sqs_handlers():
    return SQSHandlers(
        product_created={
            "queue_url": "awssqs://user:password@sqs:4556/account_id/product_created"
        },
        product_updated={
            "queue_url": "awssqs://user:password@sqs:4556/account_id/product_updated"
        },
        product_deleted={
            "queue_url": "awssqs://user:password@sqs:4556/account_id/product_deleted"
        },
    )


@pytest.fixture
def saleor_app(manifest, settings_with_aws, http_webhook_handlers, sqs_handlers):
    saleor_app = SaleorApp(
        manifest=manifest,
        validate_domain=AsyncMock(),
        save_app_data=AsyncMock(),
        get_webhook_details=AsyncMock(),
        app_settings=settings_with_aws,
        http_webhook_handlers=http_webhook_handlers,
        sqs_handlers=sqs_handlers,
        use_insecure_saleor_http=False,
    )

    saleor_app.get("/configuration", name="configuration-form")(lambda x: x)
    saleor_app.get("/extension", name="extension")(lambda x: x)
    saleor_app.include_saleor_app_routes()

    return saleor_app


@pytest.fixture
def mock_request(saleor_app):
    return Mock(app=saleor_app, body=AsyncMock(return_value=b"request_body"))
