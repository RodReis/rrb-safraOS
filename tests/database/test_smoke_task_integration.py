"""Prova de fila real: worker Celery consumindo do Redis do Compose.

Exige `npm run dev` de pé e um worker `celery -A safraos_worker.app worker`
rodando. Sem eles, falha real de conexão — nunca `not_run` silencioso.
"""

from __future__ import annotations

import pytest

from safraos_worker.app import celery_app
from safraos_worker.tasks.smoke import ping

pytestmark = pytest.mark.database


def test_smoke_ping_processada_pela_fila_real_com_mesmo_correlation_id() -> None:
    celery_app.conf.task_always_eager = False
    correlation_id = "99999999-8888-7777-6666-555555555555"

    async_result = ping.apply_async(kwargs={"correlation_id": correlation_id})
    result = async_result.get(timeout=10)

    assert result == {"status": "ok", "correlationId": correlation_id}
    assert async_result.state == "SUCCESS"
