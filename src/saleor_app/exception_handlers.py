from typing import List

from fastapi import Request

from saleor_app.saleor.exceptions import IgnoredPrincipal


class IgnoredIssuingPrincipalChecker:
    def __init__(self, principal_ids: List[str], raise_exception: bool = True):
        self.principal_ids = principal_ids
        self.raise_exception = raise_exception

    async def __call__(self, request: Request):
        json_data = await request.json()
        for payload in json_data:
            if meta := payload.get("meta"):
                if meta["issuing_principal"]["id"] in self.principal_ids:
                    if self.raise_exception:
                        raise IgnoredPrincipal(self.principal_ids)
