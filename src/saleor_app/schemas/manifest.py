from typing import List

from pydantic import BaseSettings, Field


class SettingsManifest(BaseSettings):
    name: str
    version: str
    about: str
    data_privacy: str = Field(..., env="manifest_data_privacy", alias="dataPrivacy")
    data_privacy_url: str = Field(
        ..., env="manifest_data_privacy_url", alias="dataPrivacyUrl"
    )
    homepage_url: str = Field(..., env="manifest_homepage_url", alias="homepageUrl")
    support_url: str = Field(..., env="manifest_support_url", alias="supportUrl")
    id: str
    permissions: List[str]
    app_url: str = Field(..., env="manifest_app_url", alias="appUrl")

    class Config:
        allow_population_by_field_name = True
        env_prefix = "manifest_"


class Manifest(SettingsManifest):
    configuration_url: str = Field(
        ..., env="configuration_url", alias="configurationUrl"
    )
    token_target_url: str = Field(..., env="token_target_url", alias="tokenTargetUrl")
