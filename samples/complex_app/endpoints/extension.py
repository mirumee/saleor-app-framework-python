from fastapi import APIRouter, Depends

from saleor_app.deps import ConfigurationDataDeps

router = APIRouter()


@router.get("/", name="custom-add-product")
async def custom_add_product(commons: ConfigurationDataDeps = Depends()):
    return "OK"
