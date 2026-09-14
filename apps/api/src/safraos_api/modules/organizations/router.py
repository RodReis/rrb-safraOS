from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel

from safraos_api.modules.organizations.repository import (
    OrganizationRepository,
    OrganizationSummary,
    SessionUser,
    build_repository,
)
from safraos_api.settings import Settings

router = APIRouter(prefix="/v1/organizations", tags=["organizations"])


class CreateOrganizationBody(BaseModel):
    name: str


class SelectTenantBody(BaseModel):
    organizationId: str


class OrganizationResponse(BaseModel):
    id: str
    name: str
    role: str


class TenantResponse(BaseModel):
    activeOrganization: OrganizationResponse


class OrganizationListResponse(BaseModel):
    organizations: list[OrganizationResponse]


class MessageResponse(BaseModel):
    message: str


def get_repository() -> OrganizationRepository:
    return build_repository(Settings())


RepositoryDep = Annotated[OrganizationRepository, Depends(get_repository)]


async def current_user(request: Request, repo: RepositoryDep) -> SessionUser | None:
    return await repo.session_user(request.cookies.get("safraos_session"))


CurrentUserDep = Annotated[SessionUser | None, Depends(current_user)]


def _response(summary: OrganizationSummary) -> OrganizationResponse:
    return OrganizationResponse(id=summary.id, name=summary.name, role=summary.role)


@router.get("", response_model=OrganizationListResponse | MessageResponse)
async def list_organizations(
    response: Response,
    user: CurrentUserDep,
    repo: RepositoryDep,
) -> OrganizationListResponse | MessageResponse:
    if user is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MessageResponse(message="Sessao ausente ou expirada.")
    organizations = await repo.list_for_user(user)
    return OrganizationListResponse(organizations=[_response(org) for org in organizations])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationResponse | MessageResponse,
)
async def create_organization(
    body: CreateOrganizationBody,
    request: Request,
    response: Response,
    user: CurrentUserDep,
    repo: RepositoryDep,
) -> OrganizationResponse | MessageResponse:
    if user is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MessageResponse(message="Sessao ausente ou expirada.")
    organization = await repo.create(user, body.name, request.state.correlation_id)
    return _response(organization)


@router.post("/active", response_model=TenantResponse | MessageResponse)
async def select_active_tenant(
    body: SelectTenantBody,
    request: Request,
    response: Response,
    user: CurrentUserDep,
    repo: RepositoryDep,
) -> TenantResponse | MessageResponse:
    if user is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MessageResponse(message="Sessao ausente ou expirada.")
    organization = await repo.select_tenant(user, body.organizationId, request.state.correlation_id)
    if organization is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return MessageResponse(message="Organizacao nao encontrada.")
    response.set_cookie(
        "safraos_active_organization",
        organization.id,
        httponly=True,
        secure=Settings().cookie_secure,
        samesite="lax",
        path="/",
    )
    return TenantResponse(activeOrganization=_response(organization))
