"""Acesso a dados de Farm: uma transacao por caso de uso, RLS + auditoria."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from safraos.farms.model import FarmError, create_farm
from safraos_api.problem_details import ProblemDetailError
from safraos_api.settings import Settings


@dataclass(frozen=True)
class FarmRow:
    id: str
    organization_id: str
    name: str
    uf: str
    municipio_ibge_code: str
    municipio_name: str
    archived_at: datetime | None
    created_at: datetime


_SELECT_WITH_MUNICIPIO = """
    SELECT f.id, f.organization_id, f.name, f.uf, f.municipio_ibge_code,
           m.name AS municipio_name, f.archived_at, f.created_at
    FROM farms f
    JOIN municipios m ON m.ibge_code = f.municipio_ibge_code
"""


def _row_to_farm(row: RowMapping) -> FarmRow:
    return FarmRow(
        id=str(row["id"]),
        organization_id=str(row["organization_id"]),
        name=row["name"],
        uf=row["uf"],
        municipio_ibge_code=row["municipio_ibge_code"],
        municipio_name=row["municipio_name"],
        archived_at=row["archived_at"],
        created_at=row["created_at"],
    )


class FarmRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create(
        self,
        *,
        user_id: str,
        organization_id: str,
        name: str,
        uf: str,
        municipio_ibge_code: str,
        correlation_id: str,
    ) -> FarmRow:
        try:
            normalized_name, normalized_uf, normalized_ibge = create_farm(
                name, uf, municipio_ibge_code
            )
        except FarmError as error:
            raise ProblemDetailError(status=422, title=str(error), code=error.code) from error

        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user_id)
            farm_id = await conn.scalar(
                text(
                    """
                    INSERT INTO farms (organization_id, name, uf, municipio_ibge_code)
                    VALUES (:organization_id, :name, :uf, :ibge)
                    RETURNING id
                    """
                ),
                {
                    "organization_id": organization_id,
                    "name": normalized_name,
                    "uf": normalized_uf,
                    "ibge": normalized_ibge,
                },
            )
            await self._audit_in_transaction(
                conn,
                actor_user_id=user_id,
                organization_id=organization_id,
                action="farms.create",
                object_type="farm",
                object_id=str(farm_id),
                outcome="allowed",
                correlation_id=correlation_id,
            )
            row = await self._fetch_by_id(conn, farm_id)
            return _row_to_farm(row)

    async def list(
        self, *, user_id: str, organization_id: str, include_archived: bool
    ) -> list[FarmRow]:
        query = _SELECT_WITH_MUNICIPIO + " WHERE f.organization_id = :organization_id"
        if not include_archived:
            query += " AND f.archived_at IS NULL"
        query += " ORDER BY f.name"

        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user_id)
            rows = (
                (await conn.execute(text(query), {"organization_id": organization_id}))
                .mappings()
                .all()
            )
            return [_row_to_farm(row) for row in rows]

    async def update(
        self,
        *,
        user_id: str,
        organization_id: str,
        farm_id: str,
        name: str,
        uf: str,
        municipio_ibge_code: str,
        correlation_id: str,
    ) -> FarmRow:
        try:
            normalized_name, normalized_uf, normalized_ibge = create_farm(
                name, uf, municipio_ibge_code
            )
        except FarmError as error:
            raise ProblemDetailError(status=422, title=str(error), code=error.code) from error

        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user_id)
            updated_id = await conn.scalar(
                text(
                    """
                    UPDATE farms
                    SET name = :name, uf = :uf, municipio_ibge_code = :ibge
                    WHERE id = :id AND organization_id = :organization_id
                    RETURNING id
                    """
                ),
                {
                    "name": normalized_name,
                    "uf": normalized_uf,
                    "ibge": normalized_ibge,
                    "id": farm_id,
                    "organization_id": organization_id,
                },
            )
            if updated_id is None:
                await self._audit_in_transaction(
                    conn,
                    actor_user_id=user_id,
                    organization_id=organization_id,
                    action="farms.update",
                    object_type="farm",
                    object_id=farm_id,
                    outcome="denied",
                    correlation_id=correlation_id,
                )
                raise ProblemDetailError(
                    status=404, title="Fazenda nao encontrada.", code="farms.not_found"
                )

            await self._audit_in_transaction(
                conn,
                actor_user_id=user_id,
                organization_id=organization_id,
                action="farms.update",
                object_type="farm",
                object_id=str(updated_id),
                outcome="allowed",
                correlation_id=correlation_id,
            )
            row = await self._fetch_by_id(conn, updated_id)
            return _row_to_farm(row)

    async def archive(
        self, *, user_id: str, organization_id: str, farm_id: str, correlation_id: str
    ) -> FarmRow:
        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user_id)
            archived_id = await conn.scalar(
                text(
                    """
                    UPDATE farms
                    SET archived_at = now()
                    WHERE id = :id AND organization_id = :organization_id
                      AND archived_at IS NULL
                    RETURNING id
                    """
                ),
                {"id": farm_id, "organization_id": organization_id},
            )
            if archived_id is None:
                await self._audit_in_transaction(
                    conn,
                    actor_user_id=user_id,
                    organization_id=organization_id,
                    action="farms.archive",
                    object_type="farm",
                    object_id=farm_id,
                    outcome="denied",
                    correlation_id=correlation_id,
                )
                raise ProblemDetailError(
                    status=404, title="Fazenda nao encontrada.", code="farms.not_found"
                )

            await self._audit_in_transaction(
                conn,
                actor_user_id=user_id,
                organization_id=organization_id,
                action="farms.archive",
                object_type="farm",
                object_id=str(archived_id),
                outcome="allowed",
                correlation_id=correlation_id,
            )
            row = await self._fetch_by_id(conn, archived_id)
            return _row_to_farm(row)

    async def _fetch_by_id(self, conn: AsyncConnection, farm_id: str) -> RowMapping:
        result = await conn.execute(
            text(_SELECT_WITH_MUNICIPIO + " WHERE f.id = :id"), {"id": farm_id}
        )
        return result.mappings().one()

    async def _audit_in_transaction(
        self,
        conn: AsyncConnection,
        *,
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


def build_repository(settings: Settings) -> FarmRepository:
    engine = create_async_engine(settings.app_database_url, pool_pre_ping=True)
    return FarmRepository(engine)
