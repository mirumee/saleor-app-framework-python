import json
import os

from .conf import settings

MANIFEST = None


def get_app_manifest():
    global MANIFEST
    if MANIFEST is not None:
        return MANIFEST
    if not os.path.exists(settings.MANIFEST_PATH):
        return None
    with open(settings.MANIFEST_PATH, mode="r") as f:
        MANIFEST = json.load(f)
    return MANIFEST
