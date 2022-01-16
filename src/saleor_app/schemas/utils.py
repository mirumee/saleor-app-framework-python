from functools import cached_property

from fastapi import Request
from starlette.routing import NoMatchFound

from saleor_app.errors import ConfigurationError


class LazyUrl(str):
    def __init__(self, name: str):
        self.name = name

    @cached_property
    def resolve(self):
        return self.request.url_for(self.name)

    def __call__(self, request: Request):
        self.request = request
        try:
            return self.resolve
        except NoMatchFound:
            raise ConfigurationError(
                f"Failed to resolve a lazy url, check if an endpoint named '{self.name}' is defined."
            )
