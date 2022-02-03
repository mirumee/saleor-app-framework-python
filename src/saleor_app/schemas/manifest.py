from enum import Enum
from typing import List, Union

from pydantic import AnyHttpUrl, BaseModel, Field

from saleor_app.schemas.utils import LazyUrl


class TargetType(str, Enum):
    POPUP = "POPUP"
    APP_PAGE = "APP_PAGE"


class MountType(str, Enum):
    PRODUCT_DETAILS_MORE_ACTIONS = "PRODUCT_DETAILS_MORE_ACTIONS"
    PRODUCT_OVERVIEW_CREATE = "PRODUCT_OVERVIEW_CREATE"
    PRODUCT_OVERVIEW_MORE_ACTIONS = "PRODUCT_OVERVIEW_MORE_ACTIONS"
    NAVIGATION_CATALOG = "NAVIGATION_CATALOG"
    NAVIGATION_ORDERS = "NAVIGATION_ORDERS"
    NAVIGATION_CUSTOMERS = "NAVIGATION_CUSTOMERS"
    NAVIGATION_DISCOUNTS = "NAVIGATION_DISCOUNTS"
    NAVIGATION_TRANSLATIONS = "NAVIGATION_TRANSLATIONS"
    NAVIGATION_PAGES = "NAVIGATION_PAGES"


class Extension(BaseModel):
    label: str
    mount: MountType
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
    token_target_url: Union[AnyHttpUrl, LazyUrl] = Field(
        LazyUrl("app-install"), alias="tokenTargetUrl"
    )

    class Config:
        allow_population_by_field_name = True
