from fastapi import Request
from starlette.routing import NoMatchFound

from saleor_app.errors import ConfigurationError


class LazyUrl(str):
    def __init__(self, name: str):
        self.name = name

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return v

    def resolve(self):
        return self.request.url_for(self.name)

    def __call__(self, request: Request):
        self.request = request
        try:
            return self.resolve()
        except NoMatchFound:
            raise ConfigurationError(
                f"Failed to resolve a lazy url, check if an endpoint named '{self.name}' is defined."
            )

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not (self.name == other.name)

    def __str__(self):
        return f"LazyURL('{self.name}')"

    def __repr__(self):
        return str(self)
