from unittest.mock import Mock

import pytest
from starlette.routing import NoMatchFound

from saleor_app.app import SaleorApp
from saleor_app.errors import ConfigurationError


async def test_saleor_app_init(
    saleor_app, manifest, settings_with_aws, http_webhook_handlers, sqs_handlers
):

    saleor_app.include_saleor_app_routes()

    assert saleor_app.manifest == manifest
    assert saleor_app.http_webhook_handlers == http_webhook_handlers
    assert saleor_app.sqs_handlers == sqs_handlers
    assert saleor_app.app_settings == settings_with_aws

    assert saleor_app.url_path_for("handle-webhook") == "/webhook"
    assert saleor_app.url_path_for("manifest") == "/configuration/manifest"
    assert saleor_app.url_path_for("app-install") == "/configuration/install"


async def test_saleor_app_no_handlers(manifest, settings):
    saleor_app = SaleorApp(
        manifest=manifest,
        validate_domain=Mock(),
        save_app_data=Mock(),
        get_webhook_details=Mock(),
        app_settings=settings,
        use_insecure_saleor_http=False,
    )
    with pytest.raises(NoMatchFound):
        saleor_app.url_path_for("handle-webhook")


async def test_saleor_app_sqs_missing_config(manifest, settings, sqs_handlers):
    with pytest.raises(ConfigurationError):
        SaleorApp(
            manifest=manifest,
            validate_domain=Mock(),
            save_app_data=Mock(),
            get_webhook_details=Mock(),
            app_settings=settings,
            sqs_handlers=sqs_handlers,
            use_insecure_saleor_http=False,
        )
