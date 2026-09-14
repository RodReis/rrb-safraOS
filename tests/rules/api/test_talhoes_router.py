from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from safraos_api.modules.farms.repository import SessionUser
from safraos_api.modules.talhoes.repository import TalhaoRow
from safraos_api.modules.talhoes.router import get_repository, router
from safraos_api.problem_details import ProblemDetailError, install_problem_detail_handler

pytestmark = pytest.mark.rules

_SESSION_COOKIE = "session.hash.token"
_VALID_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [[[-49.0, -16.0], [-49.0, -16.01], [-48.99, -16.01], [-48.99, -16.0], [-49.0, -16.0]]],
}


class FakeTalhoesRepository:
    def __init__(self) -> None:
        self.user = SessionUser(id="user-1", email="dono@example.com")
        self.talhoes: dict[str, TalhaoRow] = {}

    async def session_user(self, session_cookie: str | None) -> SessionUser | None:
        if session_cookie == _SESSION_COOKIE:
            return self.user
        return None

    async def create(
        self, *, user_id: str, organization_id: str, farm_id: str, name: str, geometry: dict, correlation_id: str
    ) -> TalhaoRow:
        talhao_id = f"talhao-{len(self.talhoes) + 1}"
        row = TalhaoRow(
            id=talhao_id, farm_id=farm_id, organization_id=organization_id, name=name,
            area_ha=Decimal("1.2345"), archived_at=None, created_at=datetime.now(UTC),
        )
        self.talhoes[talhao_id] = row
        return row

    async def list(
        self, *, user_id: str, organization_id: str, farm_id: str, include_archived: bool
    ) -> list[TalhaoRow]:
        return [
            t for t in self.talhoes.values()
            if t.organization_id == organization_id and t.farm_id == farm_id
            and (include_archived or t.archived_at is None)
        ]

    async def archive(
        self, *, user_id: str, organization_id: str, talhao_id: str, correlation_id: str
    ) -> TalhaoRow:
        existing = self.talhoes.get(talhao_id)
        if existing is None or existing.organization_id != organization_id:
            raise ProblemDetailError(status=404, title="Talhao nao encontrado.", code="talhoes.not_found")
        archived = TalhaoRow(
            id=talhao_id, farm_id=existing.farm_id, organization_id=organization_id,
            name=existing.name, area_ha=existing.area_ha,
            archived_at=datetime.now(UTC), created_at=existing.created_at,
        )
        self.talhoes[talhao_id] = archived
        return archived


def _build_app(fake_repo: FakeTalhoesRepository) -> FastAPI:
    app = FastAPI()
    install_problem_detail_handler(app)

    @app.middleware("http")
    async def _set_correlation(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.correlation_id = "test-correlation-id"
        return await call_next(request)

    app.include_router(router)
    app.dependency_overrides[get_repository] = lambda: fake_repo
    return app


def test_create_without_session_is_unauthorized() -> None:
    app = _build_app(FakeTalhoesRepository())
    client = TestClient(app)

    response = client.post(
        "/v1/talhoes", json={"farmId": "farm-1", "name": "Talhao 1", "geometry": _VALID_GEOMETRY}
    )
    assert response.status_code == 401


def test_create_requires_active_organization_cookie() -> None:
    app = _build_app(FakeTalhoesRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)

    response = client.post(
        "/v1/talhoes", json={"farmId": "farm-1", "name": "Talhao 1", "geometry": _VALID_GEOMETRY}
    )
    assert response.status_code == 401


def test_create_and_list_talhao() -> None:
    app = _build_app(FakeTalhoesRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    create_response = client.post(
        "/v1/talhoes", json={"farmId": "farm-1", "name": "Talhao 1", "geometry": _VALID_GEOMETRY}
    )
    assert create_response.status_code == 201
    assert create_response.json()["areaHa"] == "1.2345"

    list_response = client.get("/v1/talhoes", params={"farmId": "farm-1"})
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1


def test_list_requires_farm_id_query_param() -> None:
    app = _build_app(FakeTalhoesRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    response = client.get("/v1/talhoes")
    assert response.status_code == 422


def test_archive_talhao() -> None:
    app = _build_app(FakeTalhoesRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    create_response = client.post(
        "/v1/talhoes", json={"farmId": "farm-1", "name": "Talhao 1", "geometry": _VALID_GEOMETRY}
    )
    talhao_id = create_response.json()["id"]

    archive_response = client.post(f"/v1/talhoes/{talhao_id}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["archivedAt"] is not None


def test_archive_of_unknown_talhao_returns_problem_json_404() -> None:
    app = _build_app(FakeTalhoesRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    response = client.post("/v1/talhoes/does-not-exist/archive")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "talhoes.not_found"


def test_create_payload_above_5mb_is_rejected() -> None:
    app = _build_app(FakeTalhoesRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    huge_ring = [[float(i), float(i)] for i in range(400_000)]
    huge_geometry = {"type": "Polygon", "coordinates": [huge_ring]}

    response = client.post(
        "/v1/talhoes", json={"farmId": "farm-1", "name": "Talhao Gigante", "geometry": huge_geometry}
    )
    assert response.status_code == 413
    assert response.json()["code"] == "talhoes.payload_too_large"
