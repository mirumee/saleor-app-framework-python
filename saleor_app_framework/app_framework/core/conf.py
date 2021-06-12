import importlib
import logging
import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings

SETTINGS_ENV_VARIABLE = "APP_SETTINGS"


logger = logging.getLogger(__file__)
PROJECT_DIR = os.path.dirname(__file__)


class Settings(BaseSettings):
    app_name: str = "App"
    project_dir: str
    static_dir: str
    templates_dir: str
    manifest_path: str
    debug: bool = True
    dev_saleor_domain: Optional[str] = None
    dev_saleor_token: Optional[str] = None


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class'
            % (module_path, class_name)
        ) from err


@lru_cache()
def get_settings() -> Settings:
    settings_path = os.environ.get(SETTINGS_ENV_VARIABLE)
    if not settings_path:
        raise Exception(
            f"Env {SETTINGS_ENV_VARIABLE} was not provided. Provide python path to "
            f"project's settings class."
        )
    settings = import_string(settings_path)()
    if not isinstance(settings, Settings):
        logger.warning("Incorrect type of settings object.")
    return settings
