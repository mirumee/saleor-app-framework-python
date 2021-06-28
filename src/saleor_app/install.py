import logging
import secrets
import string
from typing import Awaitable, Callable, List

from saleor_app.conf import get_settings
from saleor_app.errors import InstallAppError
from saleor_app.graphql import GraphQLError, get_executor, get_saleor_api_url
from saleor_app.mutations import CREATE_WEBHOOK
from saleor_app.schemas.core import AppToken, DomainName, Url, WebhookData

logger = logging.getLogger(__name__)


async def install_app(
    domain: DomainName,
    token: AppToken,
    events: List[str],
    target_url: Url,
    save_app_data: Callable[[DomainName, WebhookData], Awaitable],
):
    alphabet = string.ascii_letters + string.digits
    secret_key = "".join(secrets.choice(alphabet) for i in range(20))

    api_url = get_saleor_api_url(domain)
    executor = get_executor(host=api_url, auth_token=token)

    settings = get_settings()

    response, errors = await executor(
        CREATE_WEBHOOK,
        variables={
            "input": {
                "targetUrl": target_url,
                "events": [event.upper() for event in events],
                "name": settings.app_name,
                "secretKey": secret_key,
            }
        },
    )

    if errors:
        raise GraphQLError("Webhook create mutation raised an error.")

    webhook_error = response["data"].get("webhookErrors")
    if webhook_error:
        logger.warning(
            "Unable to finish installation of app for %s. Received error: %s",
            domain,
            webhook_error,
        )
        raise InstallAppError("Failed to create webhook for %s.", domain)

    saleor_webhook_id = response["data"]["webhookCreate"]["webhook"]["id"]
    install_app_data = WebhookData(
        token=token, webhook_id=saleor_webhook_id, webhook_secret_key=secret_key
    )
    await save_app_data(domain, install_app_data)
