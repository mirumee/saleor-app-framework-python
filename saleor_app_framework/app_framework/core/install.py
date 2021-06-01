import logging
import secrets
import string
from typing import Awaitable, Callable, List

from ..core.conf import settings
from .errors import InstallAppError
from .graphql import GraphqlError, get_executor, get_saleor_api_url
from .types import AppToken, DomainName, InstallAppData, Url

logger = logging.getLogger(__file__)


CREATE_WEBHOOK = """
mutation WebhookCreate($input: WebhookCreateInput!){
    webhookCreate(input: $input){
        webhookErrors{
         field
         message
         code
       }
       webhook {
             id
       }
   }
}
"""


async def install_app(
    domain: DomainName,
    token: AppToken,
    events: List[str],
    target_url: Url,
    save_app_data: Callable[[DomainName, InstallAppData], Awaitable],
):
    alphabet = string.ascii_letters + string.digits
    secret_key = "".join(secrets.choice(alphabet) for i in range(20))
    saleor_webhook_id = ""

    api_url = get_saleor_api_url(domain)
    executor = get_executor(host=api_url, auth_token=token)

    response = await executor(
        CREATE_WEBHOOK,
        variables={
            "input": {
                "targetUrl": target_url,
                "events": [event.upper() for event in events],
                "name": settings.APP_NAME,
                "secretKey": secret_key,
            }
        },
    )

    if response.get("errors"):
        raise GraphqlError("Webhook create mutation raised an error")

    webhook_error = response["data"].get("webhookErrors")
    if webhook_error:
        logger.warning(
            "Unable to finish installation of app for %s. Received error: %s",
            domain,
            webhook_error,
        )
        raise InstallAppError("Failed to create webhook for %s", domain)

    install_app_data = InstallAppData(
        token=token, webhook_id=saleor_webhook_id, webhook_secret_key=secret_key
    )
    await save_app_data(domain, install_app_data)
