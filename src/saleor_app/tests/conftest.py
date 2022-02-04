from unittest.mock import AsyncMock, Mock

import pytest

from saleor_app.app import SaleorApp
from saleor_app.schemas.handlers import SaleorEventType, SQSUrl
from saleor_app.schemas.manifest import Extension, Manifest
from saleor_app.schemas.utils import LazyPath, LazyUrl
from saleor_app.settings import AWSSettings


@pytest.fixture
def aws_settings():
    return AWSSettings(
        account_id="",
        access_key_id="",
        secret_access_key="",
        region="",
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
        app_url=LazyUrl("configuration-form"),
        extensions=[
            Extension(
                label="Custom Product Create",
                mount="PRODUCT_OVERVIEW_CREATE",
                target="POPUP",
                permissions=["MANAGE_PRODUCTS"],
                url=LazyPath("extension"),
            )
        ],
    )


@pytest.fixture
def get_webhook_details():
    return AsyncMock()


@pytest.fixture
def webhook_handler():
    return AsyncMock()


@pytest.fixture
def saleor_app(manifest):
    saleor_app = SaleorApp(
        manifest=manifest,
        validate_domain=AsyncMock(),
        save_app_data=AsyncMock(),
        use_insecure_saleor_http=False,
        development_auth_token="test_token",
    )

    saleor_app.get("/configuration", name="configuration-form")(lambda x: x)
    saleor_app.get("/extension", name="extension")(lambda x: x)
    saleor_app.get("/test_webhook_handler", name="test-webhook-handler")(lambda x: x)
    saleor_app.include_saleor_app_routes()
    return saleor_app


@pytest.fixture
def saleor_app_with_webhooks(saleor_app, get_webhook_details, webhook_handler):
    saleor_app.include_webhook_router(get_webhook_details)
    saleor_app.webhook_router.http_event_route(SaleorEventType.PRODUCT_CREATED)(
        webhook_handler
    )
    saleor_app.webhook_router.http_event_route(SaleorEventType.PRODUCT_UPDATED)(
        webhook_handler
    )
    saleor_app.webhook_router.http_event_route(SaleorEventType.PRODUCT_DELETED)(
        webhook_handler
    )
    saleor_app.webhook_router.sqs_event_route(
        SQSUrl(
            None,
            scheme="awssqs",
            user="username",
            password="password",
            host="localstack",
            port="4566",
            path="/account_id/order_created",
        ),
        SaleorEventType.ORDER_CREATED,
    )(webhook_handler)
    saleor_app.webhook_router.sqs_event_route(
        SQSUrl(
            None,
            scheme="awssqs",
            user="username",
            password="password",
            host="localstack",
            port="4566",
            path="/account_id/order_updated",
        ),
        SaleorEventType.ORDER_UPDATED,
    )(webhook_handler)
    return saleor_app


@pytest.fixture
def mock_request(saleor_app):
    return Mock(app=saleor_app, body=AsyncMock(return_value=b"request_body"))
