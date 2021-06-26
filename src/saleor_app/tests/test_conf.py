import os
from unittest.mock import patch

import pytest

from saleor_app.conf import SETTINGS_ENV_VARIABLE, Settings, get_settings

settings = Settings.construct(
    app_name="TMP app",
    project_dir=".",
    static_dir="static",
    templates_dir="templates",
)

APP_SETTINGS = "saleor_app.tests.test_conf.settings"


def test_get_settings_returns_settings_object(clear_settings_cache):
    with patch.dict(os.environ, {SETTINGS_ENV_VARIABLE: APP_SETTINGS}):
        assert isinstance(get_settings(), Settings)


def test_get_settings_raises_error_when_incorrect_path(clear_settings_cache):
    with pytest.raises(ImportError):
        with patch.dict(os.environ, {SETTINGS_ENV_VARIABLE: "wrong.python.path"}):
            get_settings()


def test_get_settings(clear_settings_cache):
    with patch.dict(os.environ, {SETTINGS_ENV_VARIABLE: APP_SETTINGS}):
        settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.app_name == "TMP app"
