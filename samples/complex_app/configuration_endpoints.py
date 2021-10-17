from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from saleor_app.deps import ConfigurationDataDeps
from saleor_app.endpoints import get_public_form


class ConfigurationData(BaseModel):
    public_api_token: str
    private_api_key: int


router = APIRouter()


router.get("/", response_class=HTMLResponse, name="configuration-form")(get_public_form)


@router.get("/data")
async def get_configuration_data(commons: ConfigurationDataDeps = Depends()):
    return ConfigurationData(public_api_token="api_token", private_api_key=1)
