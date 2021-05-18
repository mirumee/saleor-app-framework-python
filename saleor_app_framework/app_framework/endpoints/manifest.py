from fastapi import APIRouter, HTTPException

from ..core.manifest import get_app_manifest
from ..schemas.manifest import Manifest

router = APIRouter()


@router.get(
    "/manifest",
    response_model=Manifest,
    responses={502: {"description": "Manifest not found"}},
)
async def manifest():
    # TODO Move manifest fields to settings variables
    manifest = get_app_manifest()
    if not manifest:
        raise HTTPException(status_code=502, detail="Missing manifest.")
    return manifest
