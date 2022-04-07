from saleor_app.schemas.manifest import Manifest
from saleor_app.schemas.utils import LazyUrl


manifest = Manifest(
    name="Sample Saleor App",
    version="0.1.0",
    about="Sample Saleor App seving as an example.",
    data_privacy="",
    data_privacy_url="http://samle-saleor-app.example.com/dataPrivacyUrl",
    homepage_url="http://samle-saleor-app.example.com/homepageUrl",
    support_url="http://samle-saleor-app.example.com/supportUrl",
    id="saleor-simple-sample",
    permissions=["MANAGE_PRODUCTS", "MANAGE_USERS"],
    app_url=LazyUrl("configuration-form"),
    extensions=[],
)
