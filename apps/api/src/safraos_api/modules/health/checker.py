"""Implementação real da porta ReadinessChecker: consulta Postgres e Redis."""

from __future__ import annotations

import asyncio

import redis.asyncio as redis_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine

# Sem timeout, um host inalcançável (porta filtrada/firewall) prende a conexão
# TCP por dezenas de segundos — inaceitável numa rota de readiness, que existe
# justamente para responder rápido quando a dependência está fora do ar.
_CHECK_TIMEOUT_SECONDS = 3.0


class SqlAlchemyRedisReadinessChecker:
    def __init__(self, database_engine: AsyncEngine, redis_url: str) -> None:
        self._engine = database_engine
        self._redis_url = redis_url

    async def check_database(self) -> bool:
        try:
            async with asyncio.timeout(_CHECK_TIMEOUT_SECONDS):
                async with self._engine.connect() as connection:
                    await connection.exec_driver_sql("SELECT 1")
            return True
        except Exception:  # noqa: BLE001 — readiness nunca deve propagar, só reportar
            return False

    async def check_redis(self) -> bool:
        client = redis_asyncio.from_url(self._redis_url)
        try:
            async with asyncio.timeout(_CHECK_TIMEOUT_SECONDS):
                return bool(await client.ping())
        except Exception:  # noqa: BLE001
            return False
        finally:
            await client.aclose()
