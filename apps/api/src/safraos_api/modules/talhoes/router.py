"""Rotas HTTP de Talhao: autorizacao de sessao + tenant ativo + problem+json."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from safraos_api.modules.farms.repository import SessionUser
from safraos_api.modules.talhoes.repository import (
    TalhaoRow,
    TalhoesRepository,
    build_repository,
)
from safraos_api.problem_details import ProblemDetailError
from safraos_api.settings import Settings

router = APIRouter(prefix="/v1/talhoes", tags=["talhoes"])

_MAX_PAYLOAD_BYTES = 5 * 1024 * 1024


def get_repository() -> TalhoesRepository:
    return build_repository(Settings())


RepositoryDep = Annotated[TalhoesRepository, Depends(get_repository)]


async def current_user(request: Request, repo: RepositoryDep) -> SessionUser | None:
    return await repo.session_user(request.cookies.get("safraos_session"))


CurrentUserDep = Annotated[SessionUser | None, Depends(current_user)]


class TalhaoCreateRequest(BaseModel):
    farm_id: str = Field(alias="farmId")
    name: str
    geometry: dict[str, Any]

    model_config = {"populate_by_name": True}


class TalhaoResponse(BaseModel):
    id: str
    farm_id: str = Field(alias="farmId")
    name: str
    area_ha: str = Field(alias="areaHa")
    archived_at: str | None = Field(alias="archivedAt")

    model_config = {"populate_by_name": True}

    @staticmethod
    def from_row(row: TalhaoRow) -> TalhaoResponse:
        return TalhaoResponse(
            id=row.id,
            farmId=row.farm_id,
            name=row.name,
            areaHa=str(row.area_ha),
            archivedAt=row.archived_at.isoformat() if row.archived_at else None,
        )


class TalhaoListResponse(BaseModel):
    items: list[TalhaoResponse]


def _require_active_organization(request: Request) -> str:
    organization_id = request.cookies.get("safraos_active_organization")
    if not organization_id:
        raise ProblemDetailError(
            status=401, title="Nenhum tenant ativo.", code="talhoes.no_active_tenant"
        )
    return organization_id


@router.post("", response_model=TalhaoResponse, status_code=201)
async def create_talhao_endpoint(
    payload: TalhaoCreateRequest,
    request: Request,
    user: CurrentUserDep,
    repo: RepositoryDep,
) -> TalhaoResponse:
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="talhoes.unauthorized")

    body = await request.body()
    if len(body) > _MAX_PAYLOAD_BYTES:
        raise ProblemDetailError(
            status=413, title="Arquivo GeoJSON acima de 5 MB.", code="talhoes.payload_too_large"
        )

    organization_id = _require_active_organization(request)
    row = await repo.create(
        user_id=user.id,
        organization_id=organization_id,
        farm_id=payload.farm_id,
        name=payload.name,
        geometry=payload.geometry,
        correlation_id=request.state.correlation_id,
    )
    return TalhaoResponse.from_row(row)


@router.get("", response_model=TalhaoListResponse)
async def list_talhoes_endpoint(
    request: Request,
    user: CurrentUserDep,
    repo: RepositoryDep,
    farm_id: Annotated[str, Query(alias="farmId")],
    include_archived: bool = False,
) -> TalhaoListResponse:
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="talhoes.unauthorized")
    organization_id = _require_active_organization(request)
    rows = await repo.list(
        user_id=user.id,
        organization_id=organization_id,
        farm_id=farm_id,
        include_archived=include_archived,
    )
    return TalhaoListResponse(items=[TalhaoResponse.from_row(r) for r in rows])


@router.post("/{talhao_id}/archive", response_model=TalhaoResponse)
async def archive_talhao_endpoint(
    talhao_id: str,
    request: Request,
    user: CurrentUserDep,
    repo: RepositoryDep,
) -> TalhaoResponse:
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="talhoes.unauthorized")
    organization_id = _require_active_organization(request)
    row = await repo.archive(
        user_id=user.id,
        organization_id=organization_id,
        talhao_id=talhao_id,
        correlation_id=request.state.correlation_id,
    )
    return TalhaoResponse.from_row(row)
