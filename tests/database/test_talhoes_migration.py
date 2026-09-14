from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from safraos_api.settings import Settings

pytestmark = pytest.mark.database

_VALID_MULTIPOLYGON_GEOJSON = (
    '{"type":"MultiPolygon","coordinates":[[[[-49.0,-16.0],[-49.0,-16.01],'
    "[-48.99,-16.01],[-48.99,-16.0],[-49.0,-16.0]]]]}"
)
_SELF_INTERSECTING_POLYGON_GEOJSON = (
    '{"type":"Polygon","coordinates":[[[-49.0,-16.0],[-48.99,-16.0],'
    "[-49.0,-16.01],[-48.99,-16.01],[-49.0,-16.0]]]}"
)
_OUT_OF_BRAZIL_POLYGON_GEOJSON = (
    '{"type":"Polygon","coordinates":[[[10.0,10.0],[10.0,10.01],'
    "[10.01,10.01],[10.01,10.0],[10.0,10.0]]]}"
)


async def _truncate_all(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE talhoes, farms, audit_events, organization_memberships, "
                "organizations, identity_users RESTART IDENTITY CASCADE"
            )
        )


async def _insert_user(conn: AsyncConnection, user_id: str) -> None:
    await conn.execute(
        text(
            """
            INSERT INTO identity_users
                (id, email, normalized_email, password_hash, password_hash_version, status)
            VALUES (:id, :email, :email, 'hash', 'argon2id-v1', 'active')
            """
        ),
        {"id": user_id, "email": f"{user_id}@example.com"},
    )


async def _insert_org(conn: AsyncConnection, org_id: str, created_by: str) -> None:
    await conn.execute(
        text(
            "INSERT INTO organizations (id, name, created_by) "
            "VALUES (:id, 'Org Teste', :created_by)"
        ),
        {"id": org_id, "created_by": created_by},
    )


async def _insert_membership(conn: AsyncConnection, user_id: str, org_id: str) -> None:
    await conn.execute(
        text(
            """
            INSERT INTO organization_memberships (user_id, organization_id, role)
            VALUES (:user_id, :org_id, 'owner')
            """
        ),
        {"user_id": user_id, "org_id": org_id},
    )


async def _insert_farm(conn: AsyncConnection, farm_id: str, org_id: str) -> None:
    await conn.execute(
        text(
            "INSERT INTO farms (id, organization_id, name, uf, municipio_ibge_code) "
            "VALUES (:id, :org_id, 'Fazenda Teste', 'GO', '5208707')"
        ),
        {"id": farm_id, "org_id": org_id},
    )


@pytest.mark.asyncio
async def test_polygon_is_normalized_to_multipolygon_with_correct_srid() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    try:
        await _truncate_all(owner_engine)
        user_id, org_id, farm_id = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
        async with owner_engine.begin() as conn:
            await _insert_user(conn, user_id)
            await _insert_org(conn, org_id, user_id)
            await _insert_farm(conn, farm_id, org_id)
            talhao_id = await conn.scalar(
                text(
                    """
                    INSERT INTO talhoes (farm_id, organization_id, name, geom, area_ha)
                    VALUES (
                        :farm_id, :org_id, 'Talhao 1',
                        ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674)),
                        ST_Area(geography(ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674))) / 10000
                    )
                    RETURNING id
                    """
                ),
                {"farm_id": farm_id, "org_id": org_id, "geojson": _VALID_MULTIPOLYGON_GEOJSON},
            )
            row = (
                (
                    await conn.execute(
                        text(
                            "SELECT ST_GeometryType(geom) AS geom_type, ST_SRID(geom) AS srid, "
                            "area_ha FROM talhoes WHERE id = :id"
                        ),
                        {"id": talhao_id},
                    )
                )
                .mappings()
                .one()
            )
            assert row["geom_type"] == "ST_MultiPolygon"
            assert row["srid"] == 4674
            assert row["area_ha"] > 0
    finally:
        await owner_engine.dispose()


@pytest.mark.asyncio
async def test_self_intersecting_geometry_is_invalid() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    try:
        async with owner_engine.begin() as conn:
            result = await conn.execute(
                text("SELECT ST_IsValid(ST_GeomFromGeoJSON(:geojson)) AS is_valid"),
                {"geojson": _SELF_INTERSECTING_POLYGON_GEOJSON},
            )
            assert result.scalar() is False
    finally:
        await owner_engine.dispose()


@pytest.mark.asyncio
async def test_geometry_out_of_brazil_bbox_is_rejected() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    try:
        async with owner_engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT ST_Within(
                        ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674),
                        ST_MakeEnvelope(-74.0, -34.0, -32.0, 6.0, 4674)
                    ) AS within_brazil
                    """
                ),
                {"geojson": _OUT_OF_BRAZIL_POLYGON_GEOJSON},
            )
            assert result.scalar() is False
    finally:
        await owner_engine.dispose()


@pytest.mark.asyncio
async def test_rls_allows_only_member_organization_talhoes_through_app_role() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    app_engine = create_async_engine(Settings().app_database_url)
    try:
        await _truncate_all(owner_engine)
        user_a, user_b = str(uuid.uuid4()), str(uuid.uuid4())
        org_a, org_b = str(uuid.uuid4()), str(uuid.uuid4())
        farm_a, farm_b = str(uuid.uuid4()), str(uuid.uuid4())

        async with owner_engine.begin() as conn:
            await _insert_user(conn, user_a)
            await _insert_user(conn, user_b)
            await _insert_org(conn, org_a, user_a)
            await _insert_org(conn, org_b, user_b)
            await _insert_membership(conn, user_a, org_a)
            await _insert_membership(conn, user_b, org_b)
            await _insert_farm(conn, farm_a, org_a)
            await _insert_farm(conn, farm_b, org_b)
            for farm_id, org_id, name in [(farm_a, org_a, "Talhao A"), (farm_b, org_b, "Talhao B")]:
                await conn.execute(
                    text(
                        """
                        INSERT INTO talhoes (farm_id, organization_id, name, geom, area_ha)
                        VALUES (
                            :farm_id, :org_id, :name,
                            ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674)),
                            1.2345
                        )
                        """
                    ),
                    {
                        "farm_id": farm_id,
                        "org_id": org_id,
                        "name": name,
                        "geojson": _VALID_MULTIPOLYGON_GEOJSON,
                    },
                )

        async with app_engine.begin() as conn:
            await conn.execute(
                text("SELECT set_config('app.current_user_id', :uid, true)"),
                {"uid": user_a},
            )
            result = await conn.execute(text("SELECT name FROM talhoes"))
            names = {row.name for row in result}
            assert names == {"Talhao A"}
    finally:
        await owner_engine.dispose()
        await app_engine.dispose()


@pytest.mark.asyncio
async def test_talhao_rejects_unknown_farm_via_fk() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    try:
        await _truncate_all(owner_engine)
        user_id, org_id = str(uuid.uuid4()), str(uuid.uuid4())
        async with owner_engine.begin() as conn:
            await _insert_user(conn, user_id)
            await _insert_org(conn, org_id, user_id)
            with pytest.raises(IntegrityError):
                await conn.execute(
                    text(
                        """
                        INSERT INTO talhoes (farm_id, organization_id, name, geom, area_ha)
                        VALUES (
                            :farm_id, :org_id, 'Talhao X',
                            ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4674)), 1.0
                        )
                        """
                    ),
                    {
                        "farm_id": str(uuid.uuid4()),
                        "org_id": org_id,
                        "geojson": _VALID_MULTIPOLYGON_GEOJSON,
                    },
                )
    finally:
        await owner_engine.dispose()
