from typing import Callable, List

from fastapi import APIRouter, Header, HTTPException, Request, Security
from fastapi.routing import APIRoute
from starlette.responses import Response

from saleor_app.schemas.handlers import (
    SaleorEventType,
    SQSHandler,
    SQSUrl,
    WebHookHandlerSignature,
)
from saleor_app.schemas.webhook import Webhook
from saleor_app.security import saleor_webhook_security

SALEOR_EVENT_HEADER = "x-saleor-event"


class WebhookRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        async def custom_route_handler(request: Request) -> Response:
            if event_type := request.headers.get(SALEOR_EVENT_HEADER):
                route = request.app.webhook_router.http_routes[event_type.upper()]
                handler = route.get_route_handler()
                response: Response = await handler(request)
                return response

            raise HTTPException(
                status_code=400, detail=f"Missing {SALEOR_EVENT_HEADER.upper()} header."
            )

        return custom_route_handler


class WebhookRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_routes = {}
        self.sqs_routes = {}
        self.post("", name="handle-webhook")(self.__handle_webhook_stub)

    async def __handle_webhook_stub(
        request: Request,
        payload: List[Webhook],
        _verify_webhook_signature=Security(saleor_webhook_security),
        _event_type=Header(None, alias=SALEOR_EVENT_HEADER),
    ):
        """
        This definition will never be used, it's here for the sake of the
        OpenAPI spec being complete.
        Endpoints registered by `http_event_route` are invoked in place of this.
        """
        return {}

    def http_event_route(self, event_type: SaleorEventType):
        def decorator(func: WebHookHandlerSignature):
            self.http_routes[event_type] = APIRoute(
                "",
                func,
                dependencies=[
                    Security(saleor_webhook_security),
                ],
            )

        return decorator

    def sqs_event_route(self, target_url: SQSUrl, event_type: SaleorEventType):
        def decorator(func):
            self.sqs_routes[event_type] = SQSHandler(
                target_url=str(target_url), handler=func
            )

        return decorator
