import logging

import aiohttp
from aiohttp.client import ClientTimeout

from saleor_app.saleor.exceptions import GraphQLError

logger = logging.getLogger("saleor.client")


class SaleorClient:
    def __init__(self, saleor_url, user_agent, auth_token=None, timeout=15):
        headers = {"User-Agent": user_agent}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self.session = aiohttp.ClientSession(
            base_url=saleor_url,
            headers=headers,
            raise_for_status=True,
            timeout=ClientTimeout(total=timeout),
        )

    async def close(self):
        await self.session.close()

    async def __aenter__(self) -> aiohttp.ClientSession:
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        await self.close()

    async def execute(self, query, variables=None):
        async with self.session.post(
            url="/graphql/", json={"query": query, "variables": variables}
        ) as resp:
            response_data = await resp.json()
            if errors := response_data.get("errors"):
                exc = GraphQLError(
                    errors=errors, response_data=response_data.get("data")
                )
                logger.error("Error when executing a GraphQL call to Saleor")
                logger.debug(str(exc))
                raise exc
            return response_data.get("data")
