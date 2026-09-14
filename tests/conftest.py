"""Configuração global de testes.

Windows usa `ProactorEventLoop` por padrão; psycopg em modo assíncrono só
funciona com `SelectorEventLoop` (documentado pelo próprio psycopg —
https://www.psycopg.org/psycopg3/docs/advanced/async.html). Sem isso, todo
teste que abre conexão async ao Postgres falha com `psycopg.InterfaceError`.
"""

from __future__ import annotations

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[attr-defined]
