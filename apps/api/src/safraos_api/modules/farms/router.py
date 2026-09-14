"""Rotas HTTP de Farm e Municipio: autorizacao de sessao + tenant ativo + problem+json."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from safraos_api.modules.farms.repository import (
    FarmRepository,
    FarmRow,
    SessionUser,
    build_repository,
)
from safraos_api.problem_details import ProblemDetailError
from safraos_api.settings import Settings

router = APIRouter(prefix="/v1/farms", tags=["farms"])
municipios_router = APIRouter(prefix="/v1/municipios", tags=["municipios"])


def get_repository() -> FarmRepository:
    return build_repository(Settings())


RepositoryDep = Annotated[FarmRepository, Depends(get_repository)]


async def current_user(request: Request, repo: RepositoryDep) -> SessionUser | None:
    return await repo.session_user(request.cookies.get("safraos_session"))


CurrentUserDep = Annotated[SessionUser | None, Depends(current_user)]


class FarmCreateRequest(BaseModel):
    name: str
    uf: str
    municipio_ibge_code: str = Field(alias="municipioIbgeCode")

    model_config = {"populate_by_name": True}


class FarmUpdateRequest(FarmCreateRequest):
    pass


class FarmResponse(BaseModel):
    id: str
    name: str
    uf: str
    municipio_ibge_code: str = Field(alias="municipioIbgeCode")
    municipio_name: str = Field(alias="municipioName")
    archived_at: str | None = Field(alias="archivedAt")

    model_config = {"populate_by_name": True}

    @staticmethod
    def from_row(row: FarmRow) -> "FarmResponse":
        return FarmResponse(
            id=row.id,
            name=row.name,
            uf=row.uf,
            municipioIbgeCode=row.municipio_ibge_code,
            municipioName=row.municipio_name,
            archivedAt=row.archived_at.isoformat() if row.archived_at else None,
        )


class FarmListResponse(BaseModel):
    items: list[FarmResponse]


class MunicipioResponse(BaseModel):
    ibge_code: str = Field(alias="ibgeCode")
    name: str
    uf: str

    model_config = {"populate_by_name": True}


class MunicipioListResponse(BaseModel):
    items: list[MunicipioResponse]


def _require_active_organization(request: Request) -> str:
    organization_id = request.cookies.get("safraos_active_organization")
    if not organization_id:
        raise ProblemDetailError(
            status=401, title="Nenhum tenant ativo.", code="farms.no_active_tenant"
        )
    return organization_id


@router.post("", response_model=FarmResponse, status_code=201)
async def create_farm_endpoint(
    payload: FarmCreateRequest,
    request: Request,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="farms.unauthorized")
    organization_id = _require_active_organization(request)
    row = await repo.create(
        user_id=user.id,
        organization_id=organization_id,
        name=payload.name,
        uf=payload.uf,
        municipio_ibge_code=payload.municipio_ibge_code,
        correlation_id=request.state.correlation_id,
    )
    return FarmResponse.from_row(row)


@router.get("", response_model=FarmListResponse)
async def list_farms_endpoint(
    request: Request,
    user: CurrentUserDep,
    repo: RepositoryDep,
    include_archived: bool = False,
):
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="farms.unauthorized")
    organization_id = _require_active_organization(request)
    rows = await repo.list(
        user_id=user.id, organization_id=organization_id, include_archived=include_archived
    )
    return FarmListResponse(items=[FarmResponse.from_row(r) for r in rows])


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm_endpoint(
    farm_id: str,
    payload: FarmUpdateRequest,
    request: Request,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="farms.unauthorized")
    organization_id = _require_active_organization(request)
    row = await repo.update(
        user_id=user.id,
        organization_id=organization_id,
        farm_id=farm_id,
        name=payload.name,
        uf=payload.uf,
        municipio_ibge_code=payload.municipio_ibge_code,
        correlation_id=request.state.correlation_id,
    )
    return FarmResponse.from_row(row)


@router.post("/{farm_id}/archive", response_model=FarmResponse)
async def archive_farm_endpoint(
    farm_id: str,
    request: Request,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="farms.unauthorized")
    organization_id = _require_active_organization(request)
    row = await repo.archive(
        user_id=user.id,
        organization_id=organization_id,
        farm_id=farm_id,
        correlation_id=request.state.correlation_id,
    )
    return FarmResponse.from_row(row)


@municipios_router.get("", response_model=MunicipioListResponse)
async def list_municipios_endpoint(user: CurrentUserDep, repo: RepositoryDep):
    if user is None:
        raise ProblemDetailError(status=401, title="Sessao invalida.", code="farms.unauthorized")
    rows = await repo.list_municipios()
    return MunicipioListResponse(
        items=[MunicipioResponse(ibgeCode=r.ibge_code, name=r.name, uf=r.uf) for r in rows]
    )
