from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.main import Extra


class OldStyleWebhook(BaseModel):
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


class WebhookWithMeta(BaseModel):
    meta: WebhookMeta

    class Config:
        extra = Extra.allow
        allow_mutation = False


class NewStyleWebhook(BaseModel):
    meta: WebhookMeta
    payload: Any

    class Config:
        extra = Extra.forbid
        allow_mutation = False


Webhook = Union[NewStyleWebhook, WebhookWithMeta, OldStyleWebhook]
