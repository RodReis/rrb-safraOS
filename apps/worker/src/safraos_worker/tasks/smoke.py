"""Tarefa de smoke exigida pela SPEC-001: comprova que o worker processa
uma tarefa de fato, sem fingir prova funcional com serviço vazio.

Pura por definição: nenhum efeito externo (sem banco, sem arquivo, sem outra
fila), então rodar duas vezes com o mesmo correlation_id sempre retorna o
mesmo resultado — o requisito de idempotência da SPEC.
"""

from __future__ import annotations

from safraos_worker.app import celery_app


@celery_app.task(name="smoke.ping")
def ping(correlation_id: str) -> dict[str, str]:
    return {"status": "ok", "correlationId": correlation_id}
