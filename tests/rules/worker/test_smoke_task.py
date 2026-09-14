"""Contrato da tarefa smoke.ping (SPEC-001).

`task_always_eager` roda a tarefa no processo de teste, sem broker real —
suficiente para provar o contrato do payload. Prova de fila real (Celery
+ Redis de verdade) fica em tests/database/test_smoke_task_integration.py.
"""

from __future__ import annotations

from safraos_worker.app import celery_app
from safraos_worker.tasks.smoke import ping


def test_smoke_ping_eco_o_correlation_id_recebido() -> None:
    celery_app.conf.task_always_eager = True
    correlation_id = "11111111-2222-3333-4444-555555555555"

    result = ping.apply(kwargs={"correlation_id": correlation_id})

    assert result.successful()
    assert result.result == {"status": "ok", "correlationId": correlation_id}


def test_smoke_ping_e_idempotente_sem_efeito_colateral_observavel() -> None:
    # A tarefa não escreve em banco/arquivo/fila própria: rodar duas vezes com
    # o mesmo correlationId produz exatamente o mesmo resultado, sem estado
    # acumulado — é a garantia mínima de "sem efeito externo" da SPEC.
    celery_app.conf.task_always_eager = True
    correlation_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    first = ping.apply(kwargs={"correlation_id": correlation_id}).result
    second = ping.apply(kwargs={"correlation_id": correlation_id}).result

    assert first == second == {"status": "ok", "correlationId": correlation_id}
