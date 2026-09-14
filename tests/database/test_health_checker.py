"""Prova de integração real do readiness contra Postgres e Redis do Compose.

Exige `npm run dev` de pé. Sem os serviços, o teste falha de propósito — nunca
vira `not_run` silencioso; ausência de infra é sinalizada como falha real de
setup, não como sucesso.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from safraos_api.modules.health.checker import SqlAlchemyRedisReadinessChecker
from safraos_api.settings import Settings

pytestmark = pytest.mark.database


@pytest.fixture
def checker() -> SqlAlchemyRedisReadinessChecker:
    settings = Settings()
    engine = create_async_engine(settings.database_url)
    return SqlAlchemyRedisReadinessChecker(engine, settings.redis_url)


@pytest.mark.asyncio
async def test_check_database_true_contra_postgres_real(
    checker: SqlAlchemyRedisReadinessChecker,
) -> None:
    assert await checker.check_database() is True


@pytest.mark.asyncio
async def test_check_redis_true_contra_redis_real(
    checker: SqlAlchemyRedisReadinessChecker,
) -> None:
    assert await checker.check_redis() is True


@pytest.mark.asyncio
async def test_check_database_false_quando_url_aponta_para_porta_fechada() -> None:
    engine = create_async_engine("postgresql+psycopg://safraos:x@localhost:1/safraos")
    checker = SqlAlchemyRedisReadinessChecker(engine, "redis://localhost:6383/0")

    assert await checker.check_database() is False


@pytest.mark.asyncio
async def test_check_redis_false_quando_url_aponta_para_porta_fechada() -> None:
    settings = Settings()
    engine = create_async_engine(settings.database_url)
    checker = SqlAlchemyRedisReadinessChecker(engine, "redis://localhost:1/0")

    assert await checker.check_redis() is False
