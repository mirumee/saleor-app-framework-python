import json
import os

from .conf import get_settings

MANIFEST = None


def get_app_manifest():
    global MANIFEST
    settings = get_settings()
    if MANIFEST is not None:
        return MANIFEST
    if not os.path.exists(settings.manifest_path):
        return None
    with open(settings.manifest_path, mode="r") as f:
        MANIFEST = json.load(f)
    return MANIFEST
