from pathlib import Path

from saleor_app.conf import Settings
from saleor_app.schemas.manifest import SettingsManifest

manifest = SettingsManifest(
    name="SampleApp",
    version="1.0.0",
    about="",
    dataPrivacy="",
    dataPrivacyUrl="127.0.0.1:8888/app-info/privacy",
    homepageUrl="127.0.0.1:8888/app-info/homepage",
    supportUrl="127.0.0.1:8888/app-info/support",
    id="sample-app",
    permissions=[],
    appUrl="127.0.0.1:8000/app",
)
test_app_settings = Settings(
    static_dir=Path("."),
    project_dir=Path("."),
    templates_dir=Path("."),
    manifest=manifest,
)
