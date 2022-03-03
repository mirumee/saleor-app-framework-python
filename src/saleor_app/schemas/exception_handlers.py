from fastapi import Request

from saleor_app.saleor.exceptions import IgnoredPrincipal


class IgnoredIssuingPrincipalChecker:
    def __init__(self, principal_id: str, raise_exception: bool = True):
        self.principal_id = principal_id
        self.raise_exception = raise_exception

    async def __call__(self, request: Request):
        json_data = await request.json()
        for payload in json_data:
            if meta := payload.get("meta"):
                if meta["issuing_principal"]["type"] == self.principal_id:
                    if self.raise_exception:
                        raise IgnoredPrincipal(self.principal_id)
