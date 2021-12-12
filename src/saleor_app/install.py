import logging
import secrets
import string
from typing import Awaitable, Callable, List

from saleor_app.errors import InstallAppError
from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.saleor.mutations import CREATE_WEBHOOK
from saleor_app.saleor.utils import get_client_for_app
from saleor_app.schemas.core import AppToken, DomainName, Url, WebhookData
from saleor_app.schemas.manifest import Manifest

logger = logging.getLogger(__name__)


async def install_app(
    saleor_domain: DomainName,
    auth_token: AppToken,
    manifest: Manifest,
    events: List[str],
    target_url: Url,
    save_app_data_callback: Callable[[DomainName, WebhookData], Awaitable],
    use_insecure_saleor_http: bool,
):
    alphabet = string.ascii_letters + string.digits
    secret_key = "".join(secrets.choice(alphabet) for _ in range(20))

    schema = "http" if use_insecure_saleor_http else "https"

    async with get_client_for_app(
        f"{schema}://{saleor_domain}", manifest=manifest, auth_token=auth_token
    ) as saleor:
        try:
            response = await saleor.execute(
                CREATE_WEBHOOK,
                variables={
                    "input": {
                        "targetUrl": target_url,
                        "events": [event.upper() for event in events],
                        "name": f"{manifest.name}-http",
                        "secretKey": secret_key,
                    }
                },
            )
        except GraphQLError as exc:
            logger.warning("Webhook create mutation raised an error: %s", exc)
            raise

    webhook_error = response["webhookCreate"].get("errors")
    if webhook_error:
        logger.warning(
            "Unable to finish installation of app for %s. Received error: %s",
            saleor_domain,
            webhook_error,
        )
        raise InstallAppError("Failed to create webhook for %s.", saleor_domain)

    saleor_webhook_id = response["webhookCreate"]["webhook"]["id"]
    install_app_data = WebhookData(
        token=auth_token, webhook_id=saleor_webhook_id, webhook_secret_key=secret_key
    )
    await save_app_data_callback(saleor_domain, install_app_data)
