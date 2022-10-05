import logging
import secrets
import string
from typing import Dict, Tuple

from saleor_app.errors import InstallAppError
from saleor_app.saleor.exceptions import GraphQLError
from saleor_app.saleor.mutations import CREATE_WEBHOOK
from saleor_app.saleor.utils import get_client_for_app
from saleor_app.schemas.core import AppToken, DomainName, WebhookData
from saleor_app.schemas.handlers import SaleorEventType
from saleor_app.schemas.manifest import Manifest

logger = logging.getLogger(__name__)


async def install_app(
    saleor_domain: DomainName,
    auth_token: AppToken,
    manifest: Manifest,
    events: Dict[str, Tuple[SaleorEventType, str]],
    use_insecure_saleor_http: bool,
):
    alphabet = string.ascii_letters + string.digits
    secret_key = "".join(secrets.choice(alphabet) for _ in range(20))

    schema = "http" if use_insecure_saleor_http else "https"

    errors = []

    async with get_client_for_app(
        f"{schema}://{saleor_domain}", manifest=manifest, auth_token=auth_token
    ) as saleor_client:
        for target_url, target_events in events.items():
            for event_type, subscription_query in target_events:
                webhook_input = {
                    "targetUrl": str(target_url),
                    "events": [event_type.upper()],
                    "name": f"{manifest.name}",
                    "secretKey": secret_key,
                }

                if subscription_query:
                    webhook_input["query"] = subscription_query

                try:
                    response = await saleor_client.execute(
                        CREATE_WEBHOOK,
                        variables={"input": webhook_input},
                    )
                except GraphQLError as exc:
                    errors.append(exc)

    if errors:
        logger.error("Unable to finish installation of app for %s.", saleor_domain)
        logger.debug(
            "Unable to finish installation of app for %s. Received errors: %s",
            saleor_domain,
            list(map(str, errors)),
        )
        raise InstallAppError("Failed to create webhooks for %s.", saleor_domain)

    saleor_webhook_id = response["webhookCreate"]["webhook"]["id"]
    return WebhookData(webhook_id=saleor_webhook_id, webhook_secret_key=secret_key)
