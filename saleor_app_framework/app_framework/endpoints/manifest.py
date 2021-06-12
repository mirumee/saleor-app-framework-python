from fastapi import APIRouter, HTTPException
from fastapi.requests import Request

from ..core.manifest import get_app_manifest
from ..schemas.manifest import Manifest

router = APIRouter()


@router.get(
    "/manifest",
    response_model=Manifest,
    responses={502: {"description": "Manifest not found."}},
)
async def manifest(
    request: Request,
):
    token_target_url = request.url_for("app-install")
    configuration_form_url = request.url_for("configuration-form")
    # TODO Move manifest fields to settings variables
    manifest = get_app_manifest()
    if not manifest:
        raise HTTPException(status_code=502, detail="Missing manifest.")
    manifest["tokenTargetUrl"] = token_target_url
    manifest["configurationUrl"] = configuration_form_url
    return manifest
