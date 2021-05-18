import importlib
import os

SETTINGS_ENV_VARIABLE = "APP_SETTINGS_MODULE"


class ImproperlyConfigured(Exception):
    pass


class Settings(object):
    def __init__(self, settings_module):
        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        mod = importlib.import_module(self.SETTINGS_MODULE)

        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)


settings = Settings(os.environ.get(SETTINGS_ENV_VARIABLE))
