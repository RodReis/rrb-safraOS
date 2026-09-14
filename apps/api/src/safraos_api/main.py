"""Composition root da API (SPEC-001).

`create_app` aceita um `readiness_checker` injetável para permitir testes
puros da rota de health sem dependência real de banco/Redis; produção e
`uvicorn safraos_api.main:app` usam a implementação real por padrão.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine

from safraos_api.correlation import CorrelationIdMiddleware
from safraos_api.modules.health.checker import SqlAlchemyRedisReadinessChecker
from safraos_api.modules.health.ports import ReadinessChecker
from safraos_api.modules.health.router import build_ready_route
from safraos_api.modules.health.router import router as health_router
from safraos_api.modules.farms.router import municipios_router
from safraos_api.modules.farms.router import router as farms_router
from safraos_api.modules.identity.router import router as identity_router
from safraos_api.modules.organizations.router import router as organizations_router
from safraos_api.problem_details import install_problem_detail_handler
from safraos_api.settings import Settings


def _default_readiness_checker(settings: Settings) -> ReadinessChecker:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    return SqlAlchemyRedisReadinessChecker(engine, settings.redis_url)


def create_app(*, readiness_checker: ReadinessChecker | None = None) -> FastAPI:
    settings = Settings()
    checker = readiness_checker or _default_readiness_checker(settings)

    app = FastAPI(title="SafraOS API")
    install_problem_detail_handler(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.web_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(health_router)
    app.include_router(build_ready_route(checker))
    app.include_router(identity_router)
    app.include_router(organizations_router)
    app.include_router(farms_router)
    app.include_router(municipios_router)

    return app


app = create_app()
