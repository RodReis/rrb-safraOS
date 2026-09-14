"""Contrato de health check e correlação (SPEC-001).

Testes puros: readiness usa dependências fake, sem tocar banco/Redis real.
Prova de integração real (banco/Redis de verdade) fica em tests/database/.
"""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from safraos_api.main import create_app

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


class AlwaysHealthy:
    async def check_database(self) -> bool:
        return True

    async def check_redis(self) -> bool:
        return True


class DatabaseDown:
    async def check_database(self) -> bool:
        return False

    async def check_redis(self) -> bool:
        return True


class RedisDown:
    async def check_database(self) -> bool:
        return True

    async def check_redis(self) -> bool:
        return False


@pytest.fixture
def client() -> TestClient:
    app = create_app(readiness_checker=AlwaysHealthy())
    return TestClient(app)


def test_live_sempre_responde_200_mesmo_com_dependencias_fora(client: TestClient) -> None:
    app = create_app(readiness_checker=DatabaseDown())
    response = TestClient(app).get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_ready_200_quando_banco_e_redis_disponiveis(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"] == {"database": "ok", "redis": "ok"}


def test_ready_503_quando_banco_indisponivel() -> None:
    app = create_app(readiness_checker=DatabaseDown())
    response = TestClient(app).get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unhealthy"
    assert body["checks"]["database"] == "fail"


def test_ready_503_quando_redis_indisponivel() -> None:
    app = create_app(readiness_checker=RedisDown())
    response = TestClient(app).get("/health/ready")

    assert response.status_code == 503
    assert response.json()["checks"]["redis"] == "fail"


def test_falha_de_banco_nao_derruba_liveness_mas_derruba_readiness() -> None:
    # Critério de aceite explícito da SPEC-001: liveness e readiness têm
    # semânticas diferentes e não podem colapsar numa única falha.
    app = create_app(readiness_checker=DatabaseDown())
    tc = TestClient(app)

    assert tc.get("/health/live").status_code == 200
    assert tc.get("/health/ready").status_code == 503


def test_correlation_id_recebido_e_ecoado_no_header_e_no_corpo(client: TestClient) -> None:
    sent = "11111111-2222-3333-4444-555555555555"
    response = client.get("/health/live", headers={"X-Correlation-Id": sent})

    assert response.headers["x-correlation-id"] == sent
    assert response.json()["correlationId"] == sent


def test_correlation_id_gerado_quando_ausente(client: TestClient) -> None:
    response = client.get("/health/live")

    generated = response.headers["x-correlation-id"]
    assert UUID_RE.match(generated)
    assert response.json()["correlationId"] == generated
