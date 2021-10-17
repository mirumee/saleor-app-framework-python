from enum import Enum
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class ViewType(str, Enum):
    PRODUCT = "PRODUCT"


class ExtensionType(str, Enum):
    OVERVIEW = "OVERVIEW"
    DETAILS = "DETAILS"


class TargetType(str, Enum):
    MORE_ACTIONS = "MORE-ACTIONS"
    CREATE = "CREATE"


class BaseExtension(BaseModel):
    label: str
    view: ViewType
    type: ExtensionType
    target: TargetType
    permissions: List[str]

    class Config:
        allow_population_by_field_name = True


class SettingsExtension(BaseExtension):
    url_for: str


class Extension(BaseExtension):
    url: AnyHttpUrl


class BaseSettingsManifest(BaseModel):
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
    extensions: List[SettingsExtension]

    class Config:
        allow_population_by_field_name = True


class SettingsManifest(BaseSettingsManifest):
    configuration_url_for: str


class Manifest(BaseSettingsManifest):
    app_url: str = Field(..., alias="appUrl")
    configuration_url: str = Field(..., alias="configurationUrl")
    token_target_url: str = Field(..., alias="tokenTargetUrl")
    extensions: List[Extension]
