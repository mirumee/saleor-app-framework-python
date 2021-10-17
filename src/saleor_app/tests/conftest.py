import os

import pytest

from saleor_app.conf import get_settings
from saleor_app.tests.sample_app import get_app


@pytest.fixture(autouse=True, scope="session")
def app_settings_env():
    os.environ["APP_SETTINGS"] = "saleor_app.tests.sample_settings.test_app_settings"


@pytest.fixture()
def clear_settings_cache():
    get_settings.cache_clear()


@pytest.fixture
def app(clear_settings_cache):
    return get_app()
