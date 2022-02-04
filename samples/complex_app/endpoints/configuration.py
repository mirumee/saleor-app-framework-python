import json

from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from saleor_app.deps import ConfigurationDataDeps, ConfigurationFormDeps


class ConfigurationData(BaseModel):
    public_api_token: str
    private_api_key: int


router = APIRouter()


@router.get("/", response_class=PlainTextResponse, name="configuration-form")
async def get_public_form(commons: ConfigurationFormDeps = Depends()):
    context = {
        "request": str(commons.request),
        "form_url": str(commons.request.url),
        "saleor_domain": commons.saleor_domain,
    }
    return PlainTextResponse(json.dumps(context, indent=4))


@router.get("/data")
async def get_configuration_data(commons: ConfigurationDataDeps = Depends()):
    return ConfigurationData(public_api_token="api_token", private_api_key=1)
