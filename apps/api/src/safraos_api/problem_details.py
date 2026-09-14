"""Handler de erro no formato application/problem+json (RFC 9457)."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ProblemDetailError(Exception):
    def __init__(self, status: int, title: str, code: str) -> None:
        super().__init__(title)
        self.status = status
        self.title = title
        self.code = code


def install_problem_detail_handler(app: FastAPI) -> None:
    @app.exception_handler(ProblemDetailError)
    async def _handle_problem_detail(request: Request, exc: ProblemDetailError) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", None)
        return JSONResponse(
            status_code=exc.status,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": exc.title,
                "status": exc.status,
                "code": exc.code,
                "correlationId": correlation_id,
            },
        )
