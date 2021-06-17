import json

from .conf import get_settings

MANIFEST = None


def get_app_manifest():
    global MANIFEST
    settings = get_settings()
    if MANIFEST is not None:
        return MANIFEST
    with open(settings.manifest_path, mode="r") as f:
        MANIFEST = json.load(f)
    return MANIFEST
