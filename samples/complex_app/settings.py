from pathlib import Path

from pydantic import BaseSettings, DirectoryPath

from saleor_app.schemas.core import SaleorPermissions
from saleor_app.schemas.manifest import (
    Extension,
    ExtensionType,
    Manifest,
    TargetType,
    ViewType,
)
from saleor_app.schemas.utils import LazyUrl

PROJECT_DIR = Path(__file__).parent


manifest = Manifest(
    name="Sample Complex Saleor App",
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
    configuration_url=LazyUrl("configuration-form"),
    extensions=[
        Extension(
            url=LazyUrl("custom-add-product"),
            label="Custom Product Create",
            view=ViewType.PRODUCT,
            type=ExtensionType.OVERVIEW,
            target=TargetType.CREATE,
            permissions=[
                SaleorPermissions.MANAGE_PRODUCTS,
            ],
        )
    ],
)


class AppSettings(BaseSettings):
    debug: bool
    database_dsn: str
    static_dir: DirectoryPath


settings = AppSettings(
    debug=True, database_dsn="sqlite:///db.sqlite3", static_dir=PROJECT_DIR / "static"
)
