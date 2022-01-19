import pytest
from starlette.routing import NoMatchFound

from saleor_app.webhook import WebhookRouter


async def test_saleor_app_init(
    saleor_app,
    manifest,
):
    assert saleor_app.manifest == manifest

    assert saleor_app.url_path_for("manifest") == "/configuration/manifest"
    assert saleor_app.url_path_for("app-install") == "/configuration/install"

    with pytest.raises(NoMatchFound):
        saleor_app.url_path_for("handle-webhook")


async def test_include_webhook_router(saleor_app, get_webhook_details):
    saleor_app.include_webhook_router(get_webhook_details)

    assert saleor_app.get_webhook_details == get_webhook_details
    assert saleor_app.url_path_for("handle-webhook") == "/webhook"
    assert isinstance(saleor_app.webhook_router, WebhookRouter)
