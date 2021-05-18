from typing import Type

from pydantic import BaseModel

ConfigurationDataClass = Type[BaseModel]
ConfigurationDataUpdateClass = Type[BaseModel]
ConfigurationData = BaseModel
ConfigurationDataUpdate = BaseModel
DomainName = str
