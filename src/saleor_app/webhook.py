from typing import Any, Callable, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.routing import APIRoute
from starlette.responses import Response

from saleor_app.deps import (
    saleor_domain_header,
    verify_saleor_domain,
    verify_webhook_signature,
)
from saleor_app.schemas.handlers import (
    SaleorEventType,
    SQSHandler,
    SQSUrl,
    WebHookHandlerSignature,
)
from saleor_app.schemas.webhook import Webhook

SALEOR_EVENT_HEADER = "x-saleor-event"


class WebhookAPIRoute(APIRoute):

    def __init__(self, 
        path: str,
        endpoint: Callable[..., Any],
        subscription_query: Optional[str] = None,
        *args, 
        **kwargs
    ):
        super().__init__(path=path, endpoint=endpoint, *args, **kwargs)
        self.subscription_query = subscription_query


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
        payload: List[Webhook],  # FIXME provide a way to proper define payload types
        saleor_domain=Depends(saleor_domain_header),
        _verify_saleor_domain=Depends(verify_saleor_domain),
        _verify_webhook_signature=Depends(verify_webhook_signature),
        _event_type=Header(None, alias=SALEOR_EVENT_HEADER),
    ):
        """
        This definition will never be used, it's here for the sake of the
        OpenAPI spec being complete.
        Endpoints registered by `http_event_route` are invoked in place of this.
        """
        return {}

    def http_event_route(self, event_type: SaleorEventType, subscription_query: Optional[str] = None):
        def decorator(func: WebHookHandlerSignature):
            self.http_routes[event_type] = WebhookAPIRoute(
                "",
                func,
                subscription_query=subscription_query,
                dependencies=[
                    Depends(verify_saleor_domain),
                    Depends(verify_webhook_signature),
                ],
            )

        return decorator

    def sqs_event_route(self, target_url: SQSUrl, event_type: SaleorEventType):
        def decorator(func):
            self.sqs_routes[event_type] = SQSHandler(
                target_url=str(target_url), handler=func
            )

        return decorator
