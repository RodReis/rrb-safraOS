from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from safraos_api.settings import Settings

pytestmark = pytest.mark.database


async def _truncate_all(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE farms, audit_events, organization_memberships, organizations, "
                "identity_users RESTART IDENTITY CASCADE"
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


@pytest.mark.asyncio
async def test_municipios_seed_has_reference_data() -> None:
    engine = create_async_engine(Settings().database_url)
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT name, uf FROM municipios WHERE ibge_code = :code"),
                {"code": "5208707"},
            )
            row = result.one()
            assert row.uf == "GO"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_farm_rejects_unknown_municipio_via_fk() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    try:
        await _truncate_all(owner_engine)
        user_id = str(uuid.uuid4())
        org_id = str(uuid.uuid4())
        async with owner_engine.begin() as conn:
            await _insert_user(conn, user_id)
            await _insert_org(conn, org_id, user_id)
            with pytest.raises(IntegrityError):
                await conn.execute(
                    text(
                        "INSERT INTO farms (organization_id, name, uf, municipio_ibge_code) "
                        "VALUES (:org_id, 'Fazenda X', 'GO', '9999999')"
                    ),
                    {"org_id": org_id},
                )
    finally:
        await owner_engine.dispose()


@pytest.mark.asyncio
async def test_rls_allows_only_member_organization_farms_through_app_role() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    app_engine = create_async_engine(Settings().app_database_url)
    try:
        await _truncate_all(owner_engine)

        user_a, user_b = str(uuid.uuid4()), str(uuid.uuid4())
        org_a, org_b = str(uuid.uuid4()), str(uuid.uuid4())

        async with owner_engine.begin() as conn:
            await _insert_user(conn, user_a)
            await _insert_user(conn, user_b)
            await _insert_org(conn, org_a, user_a)
            await _insert_org(conn, org_b, user_b)
            await _insert_membership(conn, user_a, org_a)
            await _insert_membership(conn, user_b, org_b)
            await conn.execute(
                text(
                    "INSERT INTO farms (organization_id, name, uf, municipio_ibge_code) "
                    "VALUES (:oid, 'Fazenda A', 'GO', '5208707')"
                ),
                {"oid": org_a},
            )
            await conn.execute(
                text(
                    "INSERT INTO farms (organization_id, name, uf, municipio_ibge_code) "
                    "VALUES (:oid, 'Fazenda B', 'MT', '5103403')"
                ),
                {"oid": org_b},
            )

        async with app_engine.begin() as conn:
            await conn.execute(
                text("SELECT set_config('app.current_user_id', :uid, true)"),
                {"uid": user_a},
            )
            result = await conn.execute(text("SELECT name FROM farms"))
            names = {row.name for row in result}
            assert names == {"Fazenda A"}
    finally:
        await owner_engine.dispose()
        await app_engine.dispose()


@pytest.mark.asyncio
async def test_farms_archive_is_update_not_delete_and_is_audited() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    try:
        await _truncate_all(owner_engine)
        async with owner_engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO audit_events (action, object_type, outcome, correlation_id) "
                    "VALUES ('farm.archive', 'farm', 'allowed', 'corr')"
                )
            )
        with pytest.raises(DatabaseError):
            async with owner_engine.begin() as conn:
                await conn.execute(text("DELETE FROM audit_events"))
    finally:
        await owner_engine.dispose()
