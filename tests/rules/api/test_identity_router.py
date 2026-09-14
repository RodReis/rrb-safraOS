from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from safraos_api.main import create_app
from safraos_api.modules.identity.router import get_repository


class FakeIdentityRepository:
    async def register(self, email: str, password: str) -> None:
        self.last_register = (email, password)

    async def confirm_email(self, token: str) -> bool:
        return token == "ok"

    async def login(self, email: str, password: str) -> tuple[str, str] | None:
        if email == "ativo@example.com":
            return "session.hash.token", "csrf-token"
        return None

    async def logout(self, session_cookie: str | None, csrf_token: str | None) -> bool:
        return session_cookie == "session.hash.token" and csrf_token == "csrf-token"

    async def request_password_reset(self, email: str) -> None:
        self.last_reset = email

    async def reset_password(self, token: str, password: str) -> bool:
        return token == "ok"


@pytest.fixture
def client() -> TestClient:
    app = create_app(readiness_checker=None)
    fake = FakeIdentityRepository()
    app.dependency_overrides[get_repository] = lambda: fake
    return TestClient(app)


def test_register_returns_neutral_message(client: TestClient) -> None:
    response = client.post(
        "/v1/auth/register",
        json={"email": "x@y.com", "password": "senha-longa"},
    )

    assert response.status_code == 202
    assert "instrucoes" in response.json()["message"]


def test_login_pending_or_unknown_is_denied_without_extra_data(client: TestClient) -> None:
    response = client.post(
        "/v1/auth/login",
        json={"email": "pendente@example.com", "password": "senha-longa"},
    )

    assert response.status_code == 401
    assert "password" not in response.text.lower()
    assert "token" not in response.text.lower()


def test_login_sets_http_only_cookie_and_csrf(client: TestClient) -> None:
    response = client.post(
        "/v1/auth/login",
        json={"email": "ativo@example.com", "password": "senha-longa"},
    )

    assert response.status_code == 200
    assert "httponly" in response.headers["set-cookie"].lower()
    assert response.headers["x-csrf-token"] == "csrf-token"


def test_logout_requires_csrf(client: TestClient) -> None:
    client.cookies.set("safraos_session", "session.hash.token")

    response = client.post("/v1/auth/logout")

    assert response.status_code == 403


def test_password_reset_request_is_neutral(client: TestClient) -> None:
    response = client.post("/v1/auth/password-reset/request", json={"email": "ninguem@example.com"})

    assert response.status_code == 202
    assert "Se a conta existir" in response.json()["message"]
