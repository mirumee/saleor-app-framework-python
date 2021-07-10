import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings

from saleor_app.schemas import manifest
from saleor_app.utils import import_string

SETTINGS_ENV_VARIABLE = "APP_SETTINGS"
logger = logging.getLogger(__name__)


class SettingsManifest(BaseSettings, manifest.SettingsManifest):
    class Config:
        allow_population_by_field_name = True
        env_prefix = "manifest_"

        # Pydatnic raises a FutureWarning when we use alias parameter without env
        # parameter. The reason for that is that they dropped support for assigning
        # settings from ENV by alias name. The 'fields' is only required to
        fields = {
            "data_privacy": {
                "env": "manifest_data_privacy",
            },
            "data_privacy_url": {
                "env": "manifest_data_privacy_url",
            },
            "homepage_url": {
                "env": "manifest_homepage_url",
            },
            "support_url": {
                "env": "manifest_support_url",
            },
            "app_url": {
                "env": "manifest_app_url",
            },
            "configuration_url": {
                "env": "manifest_configuration_url",
            },
        }


class Settings(BaseSettings):
    app_name: str = "App"
    project_dir: Path
    static_dir: Path
    templates_dir: Path
    debug: bool = True
    manifest: SettingsManifest
    dev_saleor_domain: Optional[str] = None
    dev_saleor_token: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    settings_path = os.environ.get(SETTINGS_ENV_VARIABLE)
    if not settings_path:
        raise Exception(
            f"Env {SETTINGS_ENV_VARIABLE} was not provided. Provide python path to "
            f"project's settings class."
        )
    settings = import_string(settings_path)
    if not isinstance(settings, Settings):
        logger.warning("Incorrect type of settings object.")
    return settings
