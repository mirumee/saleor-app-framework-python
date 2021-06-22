import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings

from saleor_app.schemas.manifest import SettingsManifest
from saleor_app.utils import import_string

SETTINGS_ENV_VARIABLE = "APP_SETTINGS"
logger = logging.getLogger(__file__)


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
