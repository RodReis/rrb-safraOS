from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from safraos_api.main import create_app
from safraos_api.modules.organizations.repository import OrganizationSummary, SessionUser
from safraos_api.modules.organizations.router import get_repository


class FakeOrganizationRepository:
    def __init__(self) -> None:
        self.user = SessionUser(id="user-1", email="dono@example.com")
        self.organizations = [
            OrganizationSummary(id="org-1", name="Fazenda Santa Maria", role="owner")
        ]

    async def session_user(self, session_cookie: str | None) -> SessionUser | None:
        if session_cookie == "session.hash.token":
            return self.user
        return None

    async def create(
        self,
        user: SessionUser,
        name: str,
        correlation_id: str,
    ) -> OrganizationSummary:
        assert user == self.user
        assert correlation_id
        return OrganizationSummary(id="org-2", name=name.strip(), role="owner")

    async def list_for_user(self, user: SessionUser) -> list[OrganizationSummary]:
        assert user == self.user
        return self.organizations

    async def select_tenant(
        self,
        user: SessionUser,
        organization_id: str,
        correlation_id: str,
    ) -> OrganizationSummary | None:
        assert correlation_id
        if organization_id == "org-1":
            return self.organizations[0]
        return None


@pytest.fixture
def client() -> TestClient:
    app = create_app(readiness_checker=None)
    app.dependency_overrides[get_repository] = lambda: FakeOrganizationRepository()
    test_client = TestClient(app)
    test_client.cookies.set("safraos_session", "session.hash.token")
    return test_client


def test_create_and_list_own_organizations(client: TestClient) -> None:
    created = client.post("/v1/organizations", json={"name": " Fazenda Boa Vista "})
    listed = client.get("/v1/organizations")

    assert created.status_code == 201
    assert created.json() == {"id": "org-2", "name": "Fazenda Boa Vista", "role": "owner"}
    assert listed.json()["organizations"] == [
        {"id": "org-1", "name": "Fazenda Santa Maria", "role": "owner"}
    ]


def test_select_active_tenant_sets_cookie(client: TestClient) -> None:
    response = client.post("/v1/organizations/active", json={"organizationId": "org-1"})

    assert response.status_code == 200
    assert response.json()["activeOrganization"]["id"] == "org-1"
    assert "safraos_active_organization=org-1" in response.headers["set-cookie"]


def test_cross_tenant_selection_does_not_reveal_existence(client: TestClient) -> None:
    response = client.post("/v1/organizations/active", json={"organizationId": "org-other"})

    assert response.status_code == 404
    assert response.json() == {"message": "Organizacao nao encontrada."}


def test_organization_routes_require_session() -> None:
    app = create_app(readiness_checker=None)
    app.dependency_overrides[get_repository] = lambda: FakeOrganizationRepository()
    client = TestClient(app)

    response = client.get("/v1/organizations")

    assert response.status_code == 401
