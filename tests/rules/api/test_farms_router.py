from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from safraos_api.modules.farms.repository import FarmRow, MunicipioRow, SessionUser
from safraos_api.modules.farms.router import get_repository, municipios_router, router
from safraos_api.problem_details import install_problem_detail_handler

pytestmark = pytest.mark.rules

_SESSION_COOKIE = "session.hash.token"


class FakeFarmRepository:
    def __init__(self) -> None:
        self.user = SessionUser(id="user-1", email="dono@example.com")
        self.farms: dict[str, FarmRow] = {}
        self.municipios = [
            MunicipioRow(ibge_code="5208707", name="Goiania", uf="GO"),
        ]

    async def session_user(self, session_cookie: str | None) -> SessionUser | None:
        if session_cookie == _SESSION_COOKIE:
            return self.user
        return None

    async def list_municipios(self) -> list[MunicipioRow]:
        return self.municipios

    async def create(self, *, user_id, organization_id, name, uf, municipio_ibge_code, correlation_id):
        farm_id = f"farm-{len(self.farms) + 1}"
        row = FarmRow(
            id=farm_id,
            organization_id=organization_id,
            name=name,
            uf=uf,
            municipio_ibge_code=municipio_ibge_code,
            municipio_name="Goiania",
            archived_at=None,
            created_at=datetime.now(timezone.utc),
        )
        self.farms[farm_id] = row
        return row

    async def list(self, *, user_id, organization_id, include_archived):
        return [
            f
            for f in self.farms.values()
            if f.organization_id == organization_id and (include_archived or f.archived_at is None)
        ]

    async def update(self, *, user_id, organization_id, farm_id, name, uf, municipio_ibge_code, correlation_id):
        from safraos_api.problem_details import ProblemDetailError

        existing = self.farms.get(farm_id)
        if existing is None or existing.organization_id != organization_id:
            raise ProblemDetailError(status=404, title="Fazenda nao encontrada.", code="farms.not_found")
        updated = FarmRow(
            id=farm_id,
            organization_id=organization_id,
            name=name,
            uf=uf,
            municipio_ibge_code=municipio_ibge_code,
            municipio_name=existing.municipio_name,
            archived_at=existing.archived_at,
            created_at=existing.created_at,
        )
        self.farms[farm_id] = updated
        return updated

    async def archive(self, *, user_id, organization_id, farm_id, correlation_id):
        from safraos_api.problem_details import ProblemDetailError

        existing = self.farms.get(farm_id)
        if existing is None or existing.organization_id != organization_id:
            raise ProblemDetailError(status=404, title="Fazenda nao encontrada.", code="farms.not_found")
        archived = FarmRow(
            id=farm_id,
            organization_id=organization_id,
            name=existing.name,
            uf=existing.uf,
            municipio_ibge_code=existing.municipio_ibge_code,
            municipio_name=existing.municipio_name,
            archived_at=datetime.now(timezone.utc),
            created_at=existing.created_at,
        )
        self.farms[farm_id] = archived
        return archived


def _build_app(fake_repo: FakeFarmRepository) -> FastAPI:
    app = FastAPI()
    install_problem_detail_handler(app)

    @app.middleware("http")
    async def _set_correlation(request, call_next):
        request.state.correlation_id = "test-correlation-id"
        return await call_next(request)

    app.include_router(router)
    app.include_router(municipios_router)
    app.dependency_overrides[get_repository] = lambda: fake_repo
    return app


def test_create_requires_active_organization_cookie():
    app = _build_app(FakeFarmRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)

    response = client.post(
        "/v1/farms", json={"name": "Fazenda X", "uf": "GO", "municipioIbgeCode": "5208707"}
    )

    assert response.status_code == 401


def test_create_without_session_is_unauthorized():
    app = _build_app(FakeFarmRepository())
    client = TestClient(app)

    response = client.post(
        "/v1/farms", json={"name": "Fazenda X", "uf": "GO", "municipioIbgeCode": "5208707"}
    )

    assert response.status_code == 401


def test_create_and_list_farm():
    app = _build_app(FakeFarmRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    create_response = client.post(
        "/v1/farms", json={"name": "Fazenda X", "uf": "GO", "municipioIbgeCode": "5208707"}
    )
    assert create_response.status_code == 201

    list_response = client.get("/v1/farms")
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1


def test_update_and_archive_farm():
    app = _build_app(FakeFarmRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    create_response = client.post(
        "/v1/farms", json={"name": "Fazenda X", "uf": "GO", "municipioIbgeCode": "5208707"}
    )
    farm_id = create_response.json()["id"]

    update_response = client.put(
        f"/v1/farms/{farm_id}",
        json={"name": "Fazenda Y", "uf": "GO", "municipioIbgeCode": "5208707"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Fazenda Y"

    archive_response = client.post(f"/v1/farms/{farm_id}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["archivedAt"] is not None


def test_archive_of_unknown_farm_returns_problem_json_404():
    app = _build_app(FakeFarmRepository())
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)
    client.cookies.set("safraos_active_organization", "org-1")

    response = client.post("/v1/farms/does-not-exist/archive")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "farms.not_found"


def test_list_municipios_does_not_require_active_organization():
    fake_repo = FakeFarmRepository()
    app = _build_app(fake_repo)
    client = TestClient(app)
    client.cookies.set("safraos_session", _SESSION_COOKIE)

    response = client.get("/v1/municipios")

    assert response.status_code == 200
    assert response.json()["items"][0]["ibgeCode"] == "5208707"


def test_list_municipios_requires_session():
    fake_repo = FakeFarmRepository()
    app = _build_app(fake_repo)
    client = TestClient(app)

    response = client.get("/v1/municipios")

    assert response.status_code == 401
