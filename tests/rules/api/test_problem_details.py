import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from safraos_api.problem_details import ProblemDetailError, install_problem_detail_handler

pytestmark = pytest.mark.rules


def _build_app() -> FastAPI:
    app = FastAPI()
    install_problem_detail_handler(app)

    @app.middleware("http")
    async def _set_correlation(request, call_next):
        request.state.correlation_id = "test-correlation-id"
        return await call_next(request)

    @app.get("/boom")
    async def boom():
        raise ProblemDetailError(status=422, title="Nome invalido", code="farms.invalid_name")

    return app


def test_problem_detail_error_is_serialized_as_problem_json():
    client = TestClient(_build_app())

    response = client.get("/boom")

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body == {
        "type": "about:blank",
        "title": "Nome invalido",
        "status": 422,
        "code": "farms.invalid_name",
        "correlationId": "test-correlation-id",
    }
