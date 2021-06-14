import os
from unittest.mock import patch

import pytest

from ..conf import SETTINGS_ENV_VARIABLE, Settings, get_settings

settings = Settings.construct(
    app_name="TMP app",
    project_dir=".",
    manifest_path="/path",
    static_dir="static",
    templates_dir="templates",
)

APP_SETTINGS = "saleor_app_framework.app_framework.core.tests.test_conf.settings"


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()


def test_get_settings_returns_settings_object():
    with patch.dict(os.environ, {SETTINGS_ENV_VARIABLE: APP_SETTINGS}):
        assert isinstance(get_settings(), Settings)


def test_get_settings_raises_error_when_incorrect_path():
    with pytest.raises(ImportError):
        with patch.dict(os.environ, {SETTINGS_ENV_VARIABLE: "wrong.python.path"}):
            get_settings()


def test_get_settings():
    with patch.dict(os.environ, {SETTINGS_ENV_VARIABLE: APP_SETTINGS}):
        settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.app_name == "TMP app"
