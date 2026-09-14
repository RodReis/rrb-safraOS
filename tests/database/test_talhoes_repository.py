from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from safraos_api.modules.talhoes.repository import TalhoesRepository
from safraos_api.problem_details import ProblemDetailError
from safraos_api.settings import Settings

pytestmark = pytest.mark.database

_VALID_POLYGON: dict[str, object] = {
    "type": "Polygon",
    "coordinates": [
        [[-49.0, -16.0], [-49.0, -16.01], [-48.99, -16.01], [-48.99, -16.0], [-49.0, -16.0]]
    ],
}
_SELF_INTERSECTING: dict[str, object] = {
    "type": "Polygon",
    "coordinates": [
        [[-49.0, -16.0], [-48.99, -16.0], [-49.0, -16.01], [-48.99, -16.01], [-49.0, -16.0]]
    ],
}
_OUT_OF_BRAZIL: dict[str, object] = {
    "type": "Polygon",
    "coordinates": [[[10.0, 10.0], [10.0, 10.01], [10.01, 10.01], [10.01, 10.0], [10.0, 10.0]]],
}


async def _truncate_all(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE talhoes, farms, audit_events, organization_memberships, "
                "organizations, identity_users RESTART IDENTITY CASCADE"
            )
        )


async def _seed_farm(conn: AsyncConnection) -> tuple[str, str, str]:
    user_id, org_id, farm_id = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    await conn.execute(
        text(
            "INSERT INTO identity_users (id, email, normalized_email, password_hash, "
            "password_hash_version, status) "
            "VALUES (:id, :email, :email, 'hash', 'argon2id-v1', 'active')"
        ),
        {"id": user_id, "email": f"{user_id}@example.com"},
    )
    await conn.execute(
        text("INSERT INTO organizations (id, name, created_by) VALUES (:id, 'Org Teste', :uid)"),
        {"id": org_id, "uid": user_id},
    )
    await conn.execute(
        text(
            "INSERT INTO organization_memberships (user_id, organization_id, role) "
            "VALUES (:uid, :oid, 'owner')"
        ),
        {"uid": user_id, "oid": org_id},
    )
    await conn.execute(
        text(
            "INSERT INTO farms (id, organization_id, name, uf, municipio_ibge_code) "
            "VALUES (:id, :oid, 'Fazenda Teste', 'GO', '5208707')"
        ),
        {"id": farm_id, "oid": org_id},
    )
    return user_id, org_id, farm_id


@pytest.mark.asyncio
async def test_create_calculates_area_and_normalizes_polygon_to_multipolygon() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    repo = TalhoesRepository(create_async_engine(Settings().app_database_url))
    try:
        await _truncate_all(owner_engine)
        async with owner_engine.begin() as conn:
            user_id, org_id, farm_id = await _seed_farm(conn)

        row = await repo.create(
            user_id=user_id,
            organization_id=org_id,
            farm_id=farm_id,
            name="  Talhao   Norte  ",
            geometry=_VALID_POLYGON,
            correlation_id="corr-1",
        )

        assert row.name == "Talhao Norte"
        assert row.area_ha > 0
        assert row.farm_id == farm_id
        assert row.geometry["type"] == "MultiPolygon"
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()  # noqa: SLF001


@pytest.mark.asyncio
async def test_create_rejects_self_intersecting_geometry() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    repo = TalhoesRepository(create_async_engine(Settings().app_database_url))
    try:
        await _truncate_all(owner_engine)
        async with owner_engine.begin() as conn:
            user_id, org_id, farm_id = await _seed_farm(conn)

        with pytest.raises(ProblemDetailError) as error:
            await repo.create(
                user_id=user_id,
                organization_id=org_id,
                farm_id=farm_id,
                name="Talhao Invalido",
                geometry=_SELF_INTERSECTING,
                correlation_id="corr-1",
            )

        assert error.value.code == "talhoes.invalid_geometry"
        assert error.value.status == 422
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()  # noqa: SLF001


@pytest.mark.asyncio
async def test_create_rejects_geometry_out_of_brazil_bbox() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    repo = TalhoesRepository(create_async_engine(Settings().app_database_url))
    try:
        await _truncate_all(owner_engine)
        async with owner_engine.begin() as conn:
            user_id, org_id, farm_id = await _seed_farm(conn)

        with pytest.raises(ProblemDetailError) as error:
            await repo.create(
                user_id=user_id,
                organization_id=org_id,
                farm_id=farm_id,
                name="Talhao Fora",
                geometry=_OUT_OF_BRAZIL,
                correlation_id="corr-1",
            )

        assert error.value.code == "talhoes.out_of_bounds"
        assert error.value.status == 422
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()  # noqa: SLF001


@pytest.mark.asyncio
async def test_create_rejects_farm_id_from_another_organization() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    repo = TalhoesRepository(create_async_engine(Settings().app_database_url))
    try:
        await _truncate_all(owner_engine)
        async with owner_engine.begin() as conn:
            user_a, org_a, _farm_a = await _seed_farm(conn)
            _user_b, _org_b, farm_b = await _seed_farm(conn)

        with pytest.raises(ProblemDetailError) as error:
            await repo.create(
                user_id=user_a,
                organization_id=org_a,
                farm_id=farm_b,
                name="Talhao Cross Tenant",
                geometry=_VALID_POLYGON,
                correlation_id="corr-1",
            )

        assert error.value.code == "talhoes.farm_not_found"
        assert error.value.status == 404
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()  # noqa: SLF001


@pytest.mark.asyncio
async def test_list_returns_only_talhoes_of_given_farm() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    repo = TalhoesRepository(create_async_engine(Settings().app_database_url))
    try:
        await _truncate_all(owner_engine)
        async with owner_engine.begin() as conn:
            user_id, org_id, farm_id = await _seed_farm(conn)

        await repo.create(
            user_id=user_id,
            organization_id=org_id,
            farm_id=farm_id,
            name="Talhao 1",
            geometry=_VALID_POLYGON,
            correlation_id="corr-1",
        )
        rows = await repo.list(
            user_id=user_id, organization_id=org_id, farm_id=farm_id, include_archived=False
        )

        assert len(rows) == 1
        assert rows[0].name == "Talhao 1"
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()  # noqa: SLF001


@pytest.mark.asyncio
async def test_archive_marks_archived_at_and_excludes_from_default_list() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    repo = TalhoesRepository(create_async_engine(Settings().app_database_url))
    try:
        await _truncate_all(owner_engine)
        async with owner_engine.begin() as conn:
            user_id, org_id, farm_id = await _seed_farm(conn)

        created = await repo.create(
            user_id=user_id,
            organization_id=org_id,
            farm_id=farm_id,
            name="Talhao 1",
            geometry=_VALID_POLYGON,
            correlation_id="corr-1",
        )
        archived = await repo.archive(
            user_id=user_id, organization_id=org_id, talhao_id=created.id, correlation_id="corr-2"
        )

        assert archived.archived_at is not None
        rows = await repo.list(
            user_id=user_id, organization_id=org_id, farm_id=farm_id, include_archived=False
        )
        assert rows == []
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()  # noqa: SLF001
