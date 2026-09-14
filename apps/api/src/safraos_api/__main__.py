"""Entrypoint `python -m safraos_api`.

Aplica a política de event loop compatível com psycopg async antes de
inicializar o uvicorn — necessário no Windows, onde o loop padrão
(`ProactorEventLoop`) não é suportado pelo psycopg em modo assíncrono.
"""

from __future__ import annotations

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore[attr-defined]

import uvicorn


def main() -> None:
    uvicorn.run("safraos_api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
