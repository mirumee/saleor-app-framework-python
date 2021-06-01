from typing import Optional, Type

from pydantic import BaseModel

ConfigurationDataClass = Type[BaseModel]
ConfigurationDataUpdateClass = Type[BaseModel]
ConfigurationData = BaseModel
ConfigurationDataUpdate = BaseModel


class FailedResponse(BaseModel):
    message: str
    exc_info: Optional[str] = None
