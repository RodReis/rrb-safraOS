"""SPEC-001 — GET /health/live e GET /health/ready."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from safraos_api.correlation import get_correlation_id
from safraos_api.modules.health.ports import ReadinessChecker

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live(request: Request) -> dict[str, str]:
    # Liveness só prova que o processo responde: nunca consulta dependência
    # externa, senão uma falha de banco derrubaria o próprio processo.
    return {"status": "alive", "correlationId": get_correlation_id(request)}


def build_ready_route(checker: ReadinessChecker) -> APIRouter:
    """Fecha a rota sobre o checker escolhido em `create_app` (composition root)."""
    ready_router = APIRouter(prefix="/health")

    @ready_router.get("/ready")
    async def ready(request: Request, response: Response) -> dict[str, object]:
        database_ok = await checker.check_database()
        redis_ok = await checker.check_redis()
        checks = {
            "database": "ok" if database_ok else "fail",
            "redis": "ok" if redis_ok else "fail",
        }
        healthy = database_ok and redis_ok
        response.status_code = (
            status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return {
            "status": "ready" if healthy else "unhealthy",
            "checks": checks,
            "correlationId": get_correlation_id(request),
        }

    return ready_router
