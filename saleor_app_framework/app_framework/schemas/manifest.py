from typing import List

from pydantic import BaseModel


class Manifest(BaseModel):
    name: str
    version: str
    about: str
    dataPrivacy: str
    dataPrivacyUrl: str
    homepageUrl: str
    supportUrl: str
    configurationUrl: str
    appUrl: str
    tokenTargetUrl: str
    id: str
    permissions: List[str]
