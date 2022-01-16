from enum import Enum
from typing import List, Union

from pydantic import AnyHttpUrl, BaseModel, Field, root_validator

from saleor_app.schemas.utils import LazyUrl


class ViewType(str, Enum):
    PRODUCT = "PRODUCT"


class ExtensionType(str, Enum):
    OVERVIEW = "OVERVIEW"
    DETAILS = "DETAILS"


class TargetType(str, Enum):
    MORE_ACTIONS = "MORE-ACTIONS"
    CREATE = "CREATE"


class Extension(BaseModel):
    label: str
    view: ViewType
    type: ExtensionType
    target: TargetType
    permissions: List[str]
    url: Union[AnyHttpUrl, LazyUrl]

    class Config:
        allow_population_by_field_name = True


class Manifest(BaseModel):
    id: str
    permissions: List[str]
    name: str
    version: str
    about: str
    extensions: List[Extension]
    data_privacy: str = Field(..., alias="dataPrivacy")
    data_privacy_url: Union[AnyHttpUrl, LazyUrl] = Field(..., alias="dataPrivacyUrl")
    homepage_url: Union[AnyHttpUrl, LazyUrl] = Field(..., alias="homepageUrl")
    support_url: Union[AnyHttpUrl, LazyUrl] = Field(..., alias="supportUrl")
    configuration_url: Union[AnyHttpUrl, LazyUrl] = Field(..., alias="configurationUrl")
    app_url: Union[AnyHttpUrl, LazyUrl] = Field("", alias="appUrl")
    token_target_url: Union[AnyHttpUrl, LazyUrl] = Field(..., alias="tokenTargetUrl")

    class Config:
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def default_token_target_url(cls, values):
        if not values.get("token_target_url"):
            values["token_target_url"] = LazyUrl("app-install")
        return values
