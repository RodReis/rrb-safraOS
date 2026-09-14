from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from safraos.organizations import create_organization
from safraos_api.settings import Settings


@dataclass(frozen=True)
class SessionUser:
    id: str
    email: str


@dataclass(frozen=True)
class OrganizationSummary:
    id: str
    name: str
    role: str


class OrganizationRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def session_user(self, session_cookie: str | None) -> SessionUser | None:
        session_id = _parse_session_id(session_cookie)
        if session_id is None:
            return None
        async with self._engine.begin() as conn:
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT u.id, u.email
                        FROM identity_sessions s
                        JOIN identity_users u ON u.id = s.user_id
                        WHERE s.id = :session_id
                          AND s.status = 'active'
                          AND s.expires_at > now()
                          AND u.status = 'active'
                        """
                    ),
                    {"session_id": session_id},
                )
            ).mappings().first()
            if row is None:
                return None
            return SessionUser(id=str(row["id"]), email=str(row["email"]))

    async def create(
        self,
        user: SessionUser,
        name: str,
        correlation_id: str,
    ) -> OrganizationSummary:
        organization = create_organization(name)
        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user.id)
            org_id = await conn.scalar(
                text(
                    """
                    INSERT INTO organizations (name, created_by)
                    VALUES (:name, :user_id)
                    RETURNING id
                    """
                ),
                {"name": organization.name, "user_id": user.id},
            )
            await conn.execute(
                text(
                    """
                    INSERT INTO organization_memberships (user_id, organization_id, role)
                    VALUES (:user_id, :organization_id, 'owner')
                    """
                ),
                {"user_id": user.id, "organization_id": org_id},
            )
            await self._audit_in_transaction(
                conn,
                user.id,
                str(org_id),
                "organization.create",
                "organization",
                str(org_id),
                "allowed",
                correlation_id,
            )
            return OrganizationSummary(id=str(org_id), name=organization.name, role="owner")

    async def list_for_user(self, user: SessionUser) -> list[OrganizationSummary]:
        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user.id)
            rows = (
                await conn.execute(
                    text(
                        """
                        SELECT o.id, o.name, m.role
                        FROM organization_memberships m
                        JOIN organizations o ON o.id = m.organization_id
                        WHERE m.user_id = :user_id
                        ORDER BY o.created_at, o.name
                        """
                    ),
                    {"user_id": user.id},
                )
            ).mappings().all()
            return [
                OrganizationSummary(id=str(row["id"]), name=str(row["name"]), role=str(row["role"]))
                for row in rows
            ]

    async def select_tenant(
        self,
        user: SessionUser,
        organization_id: str,
        correlation_id: str,
    ) -> OrganizationSummary | None:
        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user.id)
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT o.id, o.name, m.role
                        FROM organization_memberships m
                        JOIN organizations o ON o.id = m.organization_id
                        WHERE m.user_id = :user_id
                          AND m.organization_id = :organization_id
                        """
                    ),
                    {"user_id": user.id, "organization_id": organization_id},
                )
            ).mappings().first()
            if row is None:
                await self._audit_in_transaction(
                    conn,
                    user.id,
                    None,
                    "tenant.select",
                    "organization",
                    None,
                    "denied",
                    correlation_id,
                )
                return None
            await self._audit_in_transaction(
                conn,
                user.id,
                str(row["id"]),
                "tenant.select",
                "organization",
                str(row["id"]),
                "allowed",
                correlation_id,
            )
            return OrganizationSummary(
                id=str(row["id"]),
                name=str(row["name"]),
                role=str(row["role"]),
            )

    async def _audit_in_transaction(
        self,
        conn: AsyncConnection,
        actor_user_id: str | None,
        organization_id: str | None,
        action: str,
        object_type: str,
        object_id: str | None,
        outcome: str,
        correlation_id: str,
    ) -> None:
        await conn.execute(
            text(
                """
                INSERT INTO audit_events
                    (
                        actor_user_id,
                        organization_id,
                        action,
                        object_type,
                        object_id,
                        outcome,
                        correlation_id
                    )
                VALUES
                    (
                        :actor_user_id,
                        :organization_id,
                        :action,
                        :object_type,
                        :object_id,
                        :outcome,
                        :correlation_id
                    )
                """
            ),
            {
                "actor_user_id": actor_user_id,
                "organization_id": organization_id,
                "action": action,
                "object_type": object_type,
                "object_id": object_id,
                "outcome": outcome,
                "correlation_id": correlation_id,
            },
        )

    async def _set_tenant_context(self, conn: AsyncConnection, user_id: str) -> None:
        await conn.execute(
            text("SELECT set_config('app.current_user_id', :user_id, true)"),
            {"user_id": user_id},
        )


def _parse_session_id(session_cookie: str | None) -> str | None:
    if not session_cookie or "." not in session_cookie:
        return None
    return session_cookie.split(".", maxsplit=1)[0]


def build_repository(settings: Settings) -> OrganizationRepository:
    engine = create_async_engine(settings.app_database_url, pool_pre_ping=True)
    return OrganizationRepository(engine)
