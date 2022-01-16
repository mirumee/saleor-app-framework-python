from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.main import Extra


class WebhookV1(BaseModel):
    class Config:
        extra = Extra.allow
        allow_mutation = False


class PrincipalType(str, Enum):
    app = "app"
    user = "user"


class Principal(BaseModel):
    id: str = Field(..., description="Unique identifier of the principal")
    type: PrincipalType = Field(..., description="Defines the principal type")


class WebhookMeta(BaseModel):
    issuing_principal: Principal
    issued_at: datetime
    cipher_spec: Optional[str]
    format: Optional[str]


class WebhookV2(BaseModel):
    meta: WebhookMeta

    class Config:
        extra = Extra.allow
        allow_mutation = False


class WebhookV3(BaseModel):
    meta: WebhookMeta
    payload: Any

    class Config:
        extra = Extra.forbid
        allow_mutation = False


Webhook = Union[WebhookV3, WebhookV2, WebhookV1]
