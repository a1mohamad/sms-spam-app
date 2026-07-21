"""ASGI middleware that rejects oversized HTTP request bodies early."""

import json
from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestBodyLimitMiddleware:
    """Bound request-body memory use before application-level validation."""

    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        """Initialize the middleware with a positive byte limit.

        Args:
            app: Next ASGI application in the middleware chain.
            max_body_bytes: Maximum accepted HTTP request-body size in bytes.

        Raises:
            ValueError: If the configured byte limit is not positive.
        """
        if max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive.")

        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Reject declared or streamed bodies that exceed the configured cap.

        Args:
            scope: ASGI connection metadata and shared request state.
            receive: Callable used to receive ASGI request messages.
            send: Callable used to send ASGI response messages.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_length = self._content_length(scope)

        # Reject a declared oversized body before reading it into memory.
        if content_length is not None and content_length > self.max_body_bytes:
            await self._send_too_large(scope, send)
            return

        # Content-Length can be absent for streamed requests, so buffer only up
        # to the limit and replay the messages for FastAPI after validation.
        buffered_messages: list[Message] = []
        total_bytes = 0

        while True:
            message = await receive()
            buffered_messages.append(message)

            if message["type"] != "http.request":
                break

            total_bytes += len(message.get("body", b""))
            if total_bytes > self.max_body_bytes:
                await self._send_too_large(scope, send)
                return

            if not message.get("more_body", False):
                break

        async def replay_receive() -> Message:
            """Replay validated messages before returning to the live stream.

            Returns:
                Next buffered or newly received ASGI message.
            """
            if buffered_messages:
                return buffered_messages.pop(0)
            return await receive()

        await self.app(scope, replay_receive, send)

    @staticmethod
    def _content_length(scope: Scope) -> int | None:
        """Extract a valid Content-Length header when one is present.

        Args:
            scope: ASGI connection metadata containing raw request headers.

        Returns:
            Parsed byte length, or None when the header is absent or invalid.
        """
        for name, value in scope.get("headers", []):
            if name.lower() == b"content-length":
                try:
                    return int(value)
                except ValueError:
                    # The streamed-byte check remains authoritative when a
                    # malformed Content-Length cannot be parsed.
                    return None
        return None

    async def _send_too_large(self, scope: Scope, send: Send) -> None:
        """Return the standard API error shape for an oversized body.

        Args:
            scope: ASGI connection metadata containing the request ID.
            send: Callable used to send ASGI response messages.
        """
        request_id = scope.get("state", {}).get("request_id") or str(uuid4())
        body = json.dumps(
            {
                "error": {
                    "code": "request_too_large",
                    "message": "The request body is too large.",
                    "request_id": request_id,
                }
            }
        ).encode("utf-8")

        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})
