import json
import logging

from aiohttp import ClientError, ClientSession

from .conf import settings

DEFAULT_REQUEST_TIMEOUT = 10

logger = logging.getLogger("graphql")


class GraphqlError(Exception):
    pass


def get_saleor_api_url(domain: str) -> str:
    protocol = "https"
    if settings.DEBUG:
        logger.warning("Using non secured protocol.")
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
            response = await client.request(
                "POST",
                url=host,
                json=data,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )
        except ClientError as e:
            logger.exception(msg="Connection error", exc_info=e)
            raise GraphqlError(e)

    try:
        result = await response.json()
        if result.get("errors"):
            logger.error("Query to the server has returned an error.", extra=result)
    except json.JSONDecodeError as e:
        logger.exception(msg=f"FAILED RESPONSE: {response}", exc_info=e)
        raise GraphqlError(e)
    return result
