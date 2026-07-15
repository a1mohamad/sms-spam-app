"""ASGI middleware for correlating HTTP responses with server logs."""

from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestIDMiddleware:
    """Attach a unique correlation ID to each HTTP request and response."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the middleware.

        Args:
            app: Next ASGI application in the middleware chain.
        """
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Add a request ID to HTTP request state and response headers.

        Args:
            scope: ASGI connection metadata and shared request state.
            receive: Callable used to receive ASGI request messages.
            send: Callable used to send ASGI response messages.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_request_id(message: Message) -> None:
            # ASGI headers can only be changed before the response body starts.
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Error responses may already include the correlation header.
                if not any(
                    name.lower() == b"x-request-id"
                    for name, _ in headers
                ):
                    headers.append(
                        (b"x-request-id", request_id.encode("ascii"))
                    )
                message["headers"] = headers

            await send(message)

        # Wrapping send lets the middleware modify all outgoing HTTP responses.
        await self.app(scope, receive, send_with_request_id)

