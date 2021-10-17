from pathlib import Path

from saleor_app.conf import Settings, SettingsManifest
from saleor_app.schemas.core import SaleorPermissions

PROJECT_DIR = Path(__file__).parent


class AppSettings(Settings):
    database_dsn: str


settings = AppSettings(
    app_name="ComplexApp",
    project_dir=PROJECT_DIR,
    static_dir=PROJECT_DIR / "static",
    templates_dir=PROJECT_DIR / "static",
    debug=True,
    manifest=SettingsManifest(
        name="Sample Saleor App",
        version="0.1.0",
        about="Sample Saleor App seving as an example.",
        data_privacy="",
        data_privacy_url="",
        homepage_url="http://172.17.0.1:5000/homepageUrl",
        support_url="http://172.17.0.1:5000/supportUrl",
        id="saleor-complex-sample",
        permissions=[
            SaleorPermissions.MANAGE_PRODUCTS,
            SaleorPermissions.MANAGE_USERS,
        ],
        configuration_url_for="configuration-form",
        extensions=[
            {
                "url_for": "custom-add-product",
                "label": "Custom Product Create",
                "view": "PRODUCT",
                "type": "OVERVIEW",
                "target": "CREATE",
                "permissions": [
                    SaleorPermissions.MANAGE_PRODUCTS,
                ],
            }
        ],
    ),
    dev_saleor_domain="127.0.0.1:5000",
    dev_saleor_token="test_token",
    database_dsn="sqlite:///db.sqlite3",
)
