"""Porta de readiness: a rota depende desta interface, não de driver concreto."""

from __future__ import annotations

from typing import Protocol


class ReadinessChecker(Protocol):
    async def check_database(self) -> bool: ...

    async def check_redis(self) -> bool: ...
