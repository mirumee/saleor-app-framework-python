from typing import Callable

from fastapi import HTTPException, Request
from fastapi.routing import APIRoute
from starlette.responses import Response

SALEOR_EVENT_HEADER = "x-saleor-event"


class WebhookRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        async def custom_route_handler(request: Request) -> Response:
            if event_type := request.headers.get("x-saleor-event"):
                route = request.app.webhook_handler_routes[event_type]
                handler = route.get_route_handler()
                response: Response = await handler(request)
                return response

            raise HTTPException(
                status_code=400, detail=f"Missing {SALEOR_EVENT_HEADER.upper()} header."
            )

        return custom_route_handler
