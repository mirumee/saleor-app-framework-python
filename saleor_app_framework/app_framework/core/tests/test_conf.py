import os
from unittest.mock import patch

import pytest

from ..conf import SETTINGS_ENV_VARIABLE, Settings, get_settings


class TmpSettings(Settings):
    app_name = "TMP app"
    manifest_path = ""
    static_dir = ""
    templates_dir = ""
    project_dir = ""


APP_SETTINGS = "saleor_app_framework.app_framework.core.tests.test_conf.TmpSettings"


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()


def test_get_settings_returns_settings_object():
    with patch.dict(
        os.environ,
        {SETTINGS_ENV_VARIABLE: APP_SETTINGS},
    ):
        assert isinstance(get_settings(), Settings)


def test_get_settings_raises_error_when_incorrect_path():
    with pytest.raises(ImportError):
        with patch.dict(os.environ, {SETTINGS_ENV_VARIABLE: "wrong.python.path"}):
            get_settings()


def test_get_settings():
    with patch.dict(
        os.environ,
        {SETTINGS_ENV_VARIABLE: APP_SETTINGS},
    ):
        settings = get_settings()
    assert isinstance(settings, TmpSettings)
    assert settings.app_name == "TMP app"
