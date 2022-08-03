import logging
from typing import List

from fastapi import Depends, HTTPException, Query, Request

from saleor_app.schemas.principals import SaleorPrincipal
from saleor_app.security import saleor_user_auth_security

logger = logging.getLogger(__name__)


def require_permission(permissions: List):
    """
    Validates is the requesting principal is authorized for the specified action

    Usage:

    ```
    Depends(require_permission([SaleorPermissions.MANAGE_PRODUCTS]))
    ```
    """

    async def func(
        principal: SaleorPrincipal = Depends(saleor_user_auth_security),
    ):
        if not set([p.value for p in permissions]) - principal.permissions:
            return True
        raise HTTPException(status_code=403, detail="Unauthorized user")

    return func


class ConfigurationFormDeps:
    def __init__(
        self,
        request: Request,
        domain=Query(...),
    ):
        self.request = request
        self.saleor_domain = domain


class ConfigurationDataDeps:
    def __init__(
        self,
        request: Request,
        principal: SaleorPrincipal = Depends(saleor_user_auth_security),
    ):
        self.request = request
        self.saleor_domain = principal.saleor.domain
        self.principal = principal
