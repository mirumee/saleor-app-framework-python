from typing import List

from pydantic import BaseModel


class SettingsManifest(BaseModel):
    name: str
    version: str
    about: str
    dataPrivacy: str
    dataPrivacyUrl: str
    homepageUrl: str
    supportUrl: str
    id: str
    permissions: List[str]
    appUrl: str


class Manifest(SettingsManifest):
    configurationUrl: str
    tokenTargetUrl: str
