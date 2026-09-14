"""Entrypoint `python -m safraos_api`.

Aplica a política de event loop compatível com psycopg async antes de
inicializar o uvicorn — necessário no Windows, onde `uvicorn.run()` em modo
single-process força `ProactorEventLoop` mesmo com a policy global já
trocada (documentado pelo próprio uvicorn: "On Windows, the asyncio
implementation uses the standard ProactorEventLoop in single-process mode").
Rodar via `server.serve()` dentro de `asyncio.run(main())` — em vez de
`uvicorn.run()` — usa o loop já criado por `asyncio.run`, que respeita a
policy setada antes dele.
"""

from __future__ import annotations

import asyncio
import os
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[attr-defined]

import uvicorn


async def main() -> None:
    port = int(os.environ.get("SAFRAOS_API_PORT", "5183"))
    config = uvicorn.Config("safraos_api.main:app", host="0.0.0.0", port=port, reload=False)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
