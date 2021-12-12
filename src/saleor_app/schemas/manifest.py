from enum import Enum
from typing import Callable, List, Union

from pydantic import AnyHttpUrl, BaseModel, Field, root_validator
from starlette.requests import Request


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
    url: Union[AnyHttpUrl, Callable[[str], str]]

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
    data_privacy_url: Union[AnyHttpUrl, Callable[[str], str]] = Field(
        ..., alias="dataPrivacyUrl"
    )
    homepage_url: Union[AnyHttpUrl, Callable[[str], str]] = Field(
        ..., alias="homepageUrl"
    )
    support_url: Union[AnyHttpUrl, Callable[[str], str]] = Field(
        ..., alias="supportUrl"
    )
    configuration_url: Union[AnyHttpUrl, Callable[[str], str]] = Field(
        ..., alias="configurationUrl"
    )
    app_url: Union[AnyHttpUrl, Callable[[str], str]] = Field("", alias="appUrl")
    token_target_url: Union[AnyHttpUrl, Callable[[str], str]] = Field(
        ..., alias="tokenTargetUrl"
    )

    class Config:
        allow_population_by_field_name = True

    @staticmethod
    def url_for(name: str):
        def resolve(request: Request):
            return request.url_for(name=name)

        return resolve

    @root_validator(pre=True)
    def default_token_target_url(cls, values):
        if not values.get("token_target_url"):
            values["token_target_url"] = cls.url_for("app-install")
        return values
