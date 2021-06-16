from pathlib import Path

from saleor_app.conf import Settings
from saleor_app.schemas.manifest import SettingsManifest


PROJECT_DIR = Path(__file__).parent


class AppSettings(Settings):
    database_dsn: str


settings = AppSettings(
    app_name="ComplexApp",
    project_dir=PROJECT_DIR,
    static_dir=PROJECT_DIR / "static",
    templates_dir=PROJECT_DIR / "static",
    manifest_path=PROJECT_DIR / "manifest.json",
    debug=True,
    manifest=SettingsManifest(
        name="Sample Saleor App",
        version="0.1.0",
        about="Sample Saleor App seving as an example.",
        dataPrivacy="",
        dataPrivacyUrl="",
        homepageUrl="http://172.17.0.1:5000/homepageUrl",
        supportUrl="http://172.17.0.1:5000/supportUrl",
        appUrl="http://172.17.0.1:5000/appUrl",
        tokenTargetUrl="http://172.17.0.1:5000/tokenTargetUrl",
        id="saleor-complex-sample",
        permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"]
    ),
    dev_saleor_domain="127.0.0.1:5000",
    dev_saleor_token="test_token",
    database_dsn="sqlite:///db.sqlite3"
)
