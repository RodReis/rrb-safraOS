"""Correlação de requisições HTTP (SPEC-001).

`correlationId` recebido no header `X-Correlation-Id` é ecoado; se ausente,
um novo é gerado. Fica disponível em `request.state.correlation_id` para
handlers e logs estruturados.
"""

from __future__ import annotations

import uuid

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

CORRELATION_HEADER = "X-Correlation-Id"


class CorrelationIdMiddleware:
    """Middleware ASGI puro: sem framework de logging acoplado aqui."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        correlation_id = request.headers.get(CORRELATION_HEADER) or str(uuid.uuid4())
        scope.setdefault("state", {})
        scope["state"]["correlation_id"] = correlation_id

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((CORRELATION_HEADER.lower().encode(), correlation_id.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_header)


def get_correlation_id(request: Request) -> str:
    correlation_id = request.state.correlation_id
    assert isinstance(correlation_id, str)
    return correlation_id
