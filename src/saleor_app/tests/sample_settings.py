from pathlib import Path

from saleor_app.conf import Settings, SettingsManifest

manifest = SettingsManifest(
    name="SampleApp",
    version="1.0.0",
    about="",
    data_privacy="",
    data_privacy_url="127.0.0.1:8888/app-info/privacy",
    homepage_url="127.0.0.1:8888/app-info/homepage",
    support_url="127.0.0.1:8888/app-info/support",
    id="sample-app",
    permissions=[],
)

test_app_settings = Settings(
    static_dir=Path("."),
    project_dir=Path("."),
    templates_dir=Path("."),
    manifest=manifest,
)
