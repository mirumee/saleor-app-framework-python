import pytest
from httpx import AsyncClient

from saleor_app.conf import get_settings


@pytest.mark.asyncio
async def test_manifest(app):
    settings = get_settings()
    manifest = settings.manifest.dict()

    base_url = "http://test"
    manifest["tokenTargetUrl"] = f"{base_url}/configuration/install"
    manifest["configurationUrl"] = f"{base_url}/configuration/"

    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.get("configuration/manifest")
    assert response.status_code == 200
    assert response.json() == manifest
