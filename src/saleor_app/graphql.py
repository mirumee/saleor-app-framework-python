import json
import logging

from aiohttp import ClientError, ClientSession

from saleor_app.conf import get_settings
from saleor_app.errors import GraphQLError

DEFAULT_REQUEST_TIMEOUT = 10

logger = logging.getLogger("graphql")


def get_saleor_api_url(domain: str) -> str:
    protocol = "https"
    settings = get_settings()
    if settings.debug:
        logger.warning("Using non secured protocol")
        protocol = "http"
    url = f"{protocol}://{domain}"
    return f"{url}/graphql/"


def get_executor(host, auth_token=None, timeout=DEFAULT_REQUEST_TIMEOUT):
    async def _execute(query, variables=None):
        return await _execute_query(host, auth_token, timeout, query, variables)

    return _execute


async def _execute_query(host, api_key, timeout, query, variables=None, file=None):
    headers = {"Authorization": "Bearer " + api_key} if api_key else {}

    if not file:
        data = {"query": query}
        if variables is not None:
            data["variables"] = variables
        kwargs = {}
    else:
        variables.update({"file": None})
        data = {
            "operations": json.dumps({"query": query, "variables": variables}),
            "map": json.dumps({"0": ["variables.file"]}),
        }
        kwargs = {"files": {"0": (file.name, file.content)}}

    async with ClientSession() as client:
        try:
            async with client.request(
                "POST", url=host, json=data, headers=headers, timeout=timeout, **kwargs
            ) as response:
                try:
                    result = await response.json()
                    errors = result.get("errors")
                    if errors:
                        logger.warning(
                            "Query to the server has returned an error.", extra=errors
                        )
                except json.JSONDecodeError as e:
                    logger.exception(msg=f"FAILED RESPONSE: {response}", exc_info=e)
                    raise GraphQLError(e)
                return result, errors
        except ClientError as e:
            logger.exception(msg="Connection error", exc_info=e)
            raise GraphQLError(e)
