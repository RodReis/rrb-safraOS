"""Acesso a dados de Talhao: geometria/area via PostGIS, RLS + auditoria."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from safraos.talhoes.model import TalhaoError, normalize_talhao_name, validate_geometry_type
from safraos_api.modules.farms.repository import SessionUser
from safraos_api.problem_details import ProblemDetailError
from safraos_api.settings import Settings


def _parse_session_id(session_cookie: str | None) -> str | None:
    if not session_cookie or "." not in session_cookie:
        return None
    return session_cookie.split(".", maxsplit=1)[0]


@dataclass(frozen=True)
class TalhaoRow:
    id: str
    farm_id: str
    organization_id: str
    name: str
    area_ha: Decimal
    archived_at: datetime | None
    created_at: datetime
    geometry: dict[str, Any]


_SELECT_TALHAO = """
    SELECT id, farm_id, organization_id, name, area_ha, archived_at, created_at,
           ST_AsGeoJSON(geom)::json AS geometry
    FROM talhoes
"""


def _row_to_talhao(row: RowMapping) -> TalhaoRow:
    return TalhaoRow(
        id=str(row["id"]),
        farm_id=str(row["farm_id"]),
        organization_id=str(row["organization_id"]),
        name=row["name"],
        area_ha=row["area_ha"],
        archived_at=row["archived_at"],
        created_at=row["created_at"],
        geometry=row["geometry"],
    )


class TalhoesRepository:
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
        *,
        user_id: str,
        organization_id: str,
        farm_id: str,
        name: str,
        geometry: dict[str, object],
        correlation_id: str,
    ) -> TalhaoRow:
        try:
            normalized_name = normalize_talhao_name(name)
            validate_geometry_type(geometry)
        except TalhaoError as error:
            raise ProblemDetailError(status=422, title=str(error), code=error.code) from error

        geojson_text = json.dumps(geometry)

        try:
            async with self._engine.begin() as conn:
                await self._set_tenant_context(conn, user_id)

                farm_owned_by_org = await conn.scalar(
                    text(
                        """
                        SELECT 1 FROM farms
                        WHERE id = :farm_id AND organization_id = :organization_id
                          AND archived_at IS NULL
                        """
                    ),
                    {"farm_id": farm_id, "organization_id": organization_id},
                )
                if farm_owned_by_org is None:
                    raise ProblemDetailError(
                        status=404,
                        title="Fazenda nao encontrada.",
                        code="talhoes.farm_not_found",
                    )

                validity = (
                    (
                        await conn.execute(
                            text(
                                """
                                SELECT
                                    ST_IsValid(
                                        ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674)
                                    ) AS is_valid,
                                    ST_Within(
                                        ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674),
                                        ST_MakeEnvelope(-74.0, -34.0, -32.0, 6.0, 4674)
                                    ) AS within_brazil
                                """
                            ),
                            {"geojson": geojson_text},
                        )
                    )
                    .mappings()
                    .one()
                )

                if not validity["is_valid"]:
                    raise ProblemDetailError(
                        status=422,
                        title="Geometria invalida (vazia, autointersectada ou aneis invalidos).",
                        code="talhoes.invalid_geometry",
                    )
                if not validity["within_brazil"]:
                    raise ProblemDetailError(
                        status=422,
                        title="Geometria fora dos limites do Brasil.",
                        code="talhoes.out_of_bounds",
                    )

                talhao_id = await conn.scalar(
                    text(
                        """
                        INSERT INTO talhoes (farm_id, organization_id, name, geom, area_ha)
                        VALUES (
                            :farm_id, :organization_id, :name,
                            ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674)),
                            ROUND(
                                (
                                    ST_Area(
                                        geography(ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674))
                                    ) / 10000
                                )::numeric,
                                4
                            )
                        )
                        RETURNING id
                        """
                    ),
                    {
                        "farm_id": farm_id,
                        "organization_id": organization_id,
                        "name": normalized_name,
                        "geojson": geojson_text,
                    },
                )
                await self._audit_in_transaction(
                    conn,
                    actor_user_id=user_id,
                    organization_id=organization_id,
                    action="talhoes.create",
                    object_type="talhao",
                    object_id=str(talhao_id),
                    outcome="allowed",
                    correlation_id=correlation_id,
                )
                row = await self._fetch_by_id(conn, talhao_id)
                return _row_to_talhao(row)
        except DBAPIError as error:
            async with self._engine.begin() as audit_conn:
                await self._set_tenant_context(audit_conn, user_id)
                await self._audit_in_transaction(
                    audit_conn,
                    actor_user_id=user_id,
                    organization_id=organization_id,
                    action="talhoes.create",
                    object_type="talhao",
                    object_id=None,
                    outcome="denied",
                    correlation_id=correlation_id,
                )
            raise ProblemDetailError(
                status=403,
                title="Organizacao ou fazenda nao autorizada.",
                code="talhoes.forbidden_organization",
            ) from error

    async def list(
        self, *, user_id: str, organization_id: str, farm_id: str, include_archived: bool
    ) -> list[TalhaoRow]:
        query = _SELECT_TALHAO + " WHERE organization_id = :organization_id AND farm_id = :farm_id"
        if not include_archived:
            query += " AND archived_at IS NULL"
        query += " ORDER BY name"

        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user_id)
            rows = (
                (
                    await conn.execute(
                        text(query), {"organization_id": organization_id, "farm_id": farm_id}
                    )
                )
                .mappings()
                .all()
            )
            return [_row_to_talhao(row) for row in rows]

    async def archive(
        self, *, user_id: str, organization_id: str, talhao_id: str, correlation_id: str
    ) -> TalhaoRow:
        async with self._engine.begin() as conn:
            await self._set_tenant_context(conn, user_id)
            archived_id = await conn.scalar(
                text(
                    """
                    UPDATE talhoes
                    SET archived_at = now()
                    WHERE id = :id AND organization_id = :organization_id
                      AND archived_at IS NULL
                    RETURNING id
                    """
                ),
                {"id": talhao_id, "organization_id": organization_id},
            )
            if archived_id is None:
                await self._audit_in_transaction(
                    conn,
                    actor_user_id=user_id,
                    organization_id=organization_id,
                    action="talhoes.archive",
                    object_type="talhao",
                    object_id=talhao_id,
                    outcome="denied",
                    correlation_id=correlation_id,
                )
                raise ProblemDetailError(
                    status=404, title="Talhao nao encontrado.", code="talhoes.not_found"
                )

            await self._audit_in_transaction(
                conn,
                actor_user_id=user_id,
                organization_id=organization_id,
                action="talhoes.archive",
                object_type="talhao",
                object_id=str(archived_id),
                outcome="allowed",
                correlation_id=correlation_id,
            )
            row = await self._fetch_by_id(conn, archived_id)
            return _row_to_talhao(row)

    async def _fetch_by_id(self, conn: AsyncConnection, talhao_id: str) -> RowMapping:
        result = await conn.execute(text(_SELECT_TALHAO + " WHERE id = :id"), {"id": talhao_id})
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
                        actor_user_id, organization_id, action,
                        object_type, object_id, outcome, correlation_id
                    )
                VALUES
                    (
                        :actor_user_id, :organization_id, :action,
                        :object_type, :object_id, :outcome, :correlation_id
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


def build_repository(settings: Settings) -> TalhoesRepository:
    engine = create_async_engine(settings.app_database_url, pool_pre_ping=True)
    return TalhoesRepository(engine)
