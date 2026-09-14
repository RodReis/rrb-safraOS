from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response, status
from pydantic import BaseModel

from safraos_api.modules.identity.repository import IdentityRepository, build_repository
from safraos_api.settings import Settings

router = APIRouter(prefix="/v1/auth", tags=["identity"])


class EmailPasswordBody(BaseModel):
    email: str
    password: str


class EmailBody(BaseModel):
    email: str


class TokenBody(BaseModel):
    token: str


class ResetPasswordBody(BaseModel):
    token: str
    password: str


class NeutralMessage(BaseModel):
    message: str


def get_repository() -> IdentityRepository:
    return build_repository(Settings())


RepositoryDep = Annotated[IdentityRepository, Depends(get_repository)]
CsrfHeader = Annotated[str | None, Header()]


@router.post(
    "/register",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=NeutralMessage,
)
async def register(body: EmailPasswordBody, repo: RepositoryDep) -> NeutralMessage:
    await repo.register(body.email, body.password)
    return NeutralMessage(
        message="Se os dados estiverem corretos, enviaremos as proximas instrucoes."
    )


@router.post("/confirm-email", response_model=NeutralMessage)
async def confirm_email(body: TokenBody, repo: RepositoryDep) -> NeutralMessage:
    if not await repo.confirm_email(body.token):
        return NeutralMessage(message="Token invalido ou expirado.")
    return NeutralMessage(message="E-mail confirmado. Entre novamente.")


@router.post("/login", response_model=NeutralMessage)
async def login(
    body: EmailPasswordBody,
    response: Response,
    repo: RepositoryDep,
) -> NeutralMessage:
    result = await repo.login(body.email, body.password)
    if result is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return NeutralMessage(message="Credenciais invalidas ou conta pendente.")
    session_cookie, csrf_token = result
    settings = Settings()
    response.set_cookie(
        "safraos_session",
        session_cookie,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.headers["X-CSRF-Token"] = csrf_token
    return NeutralMessage(message="Sessao iniciada.")


@router.post("/logout", response_model=NeutralMessage)
async def logout(
    request: Request,
    response: Response,
    repo: RepositoryDep,
    x_csrf_token: CsrfHeader = None,
) -> NeutralMessage:
    ok = await repo.logout(request.cookies.get("safraos_session"), x_csrf_token)
    if not ok:
        response.status_code = status.HTTP_403_FORBIDDEN
        return NeutralMessage(message="CSRF ausente ou invalido.")
    response.delete_cookie("safraos_session", path="/")
    return NeutralMessage(message="Sessao encerrada.")


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=NeutralMessage,
)
async def request_password_reset(
    body: EmailBody,
    repo: RepositoryDep,
) -> NeutralMessage:
    await repo.request_password_reset(body.email)
    return NeutralMessage(message="Se a conta existir, enviaremos as proximas instrucoes.")


@router.post("/password-reset/confirm", response_model=NeutralMessage)
async def reset_password(
    body: ResetPasswordBody,
    response: Response,
    repo: RepositoryDep,
) -> NeutralMessage:
    if not await repo.reset_password(body.token, body.password):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return NeutralMessage(message="Token invalido ou expirado.")
    return NeutralMessage(message="Senha redefinida. Entre novamente.")
