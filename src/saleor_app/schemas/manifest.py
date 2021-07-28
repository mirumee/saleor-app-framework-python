from typing import List, Optional

from pydantic import BaseModel, Field


class SettingsManifest(BaseModel):
    name: str
    version: str
    about: str
    data_privacy: str = Field(..., alias="dataPrivacy")
    data_privacy_url: str = Field(..., alias="dataPrivacyUrl")
    homepage_url: str = Field(..., alias="homepageUrl")
    support_url: str = Field(..., alias="supportUrl")
    id: str
    permissions: List[str]
    app_url: Optional[str] = Field(default=None, alias="appUrl")
    configuration_url: Optional[str] = Field(default=None, alias="configurationUrl")


class Manifest(SettingsManifest):
    app_url: str = Field(..., alias="appUrl")
    configuration_url: str = Field(..., alias="configurationUrl")
    token_target_url: str = Field(..., alias="tokenTargetUrl")
    extensions: List[dict] = Field(...)
