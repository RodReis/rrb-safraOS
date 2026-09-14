from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from safraos_api.modules.farms.repository import FarmRepository
from safraos_api.problem_details import ProblemDetailError
from safraos_api.settings import Settings

pytestmark = [pytest.mark.database, pytest.mark.asyncio]


async def _seed_user_and_org(owner_engine: AsyncEngine) -> tuple[str, str]:
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    async with owner_engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE farms, organization_memberships, organizations, "
                "identity_users, audit_events RESTART IDENTITY CASCADE"
            )
        )
        await conn.execute(
            text(
                "INSERT INTO identity_users "
                "(id, email, normalized_email, password_hash, password_hash_version, status) "
                "VALUES (:id, :email, :email, 'hash', 'argon2id-v1', 'active')"
            ),
            {"id": user_id, "email": f"{user_id}@example.com"},
        )
        await conn.execute(
            text(
                "INSERT INTO organizations (id, name, created_by) "
                "VALUES (:id, 'Org Teste', :uid)"
            ),
            {"id": org_id, "uid": user_id},
        )
        await conn.execute(
            text(
                "INSERT INTO organization_memberships (id, user_id, organization_id, role) "
                "VALUES (gen_random_uuid(), :uid, :oid, 'owner')"
            ),
            {"uid": user_id, "oid": org_id},
        )
    return user_id, org_id


async def test_create_list_update_archive_round_trip() -> None:
    settings = Settings()
    owner_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    repo = FarmRepository(create_async_engine(settings.app_database_url, pool_pre_ping=True))
    try:
        user_id, org_id = await _seed_user_and_org(owner_engine)

        created = await repo.create(
            user_id=user_id,
            organization_id=org_id,
            name="Fazenda Boa Vista",
            uf="GO",
            municipio_ibge_code="5208707",
            correlation_id="corr-1",
        )
        assert created.name == "Fazenda Boa Vista"
        assert created.archived_at is None
        assert created.municipio_name == "Goiania"

        listed = await repo.list(
            user_id=user_id, organization_id=org_id, include_archived=False
        )
        assert [f.id for f in listed] == [created.id]

        updated = await repo.update(
            user_id=user_id,
            organization_id=org_id,
            farm_id=created.id,
            name="Fazenda Boa Vista II",
            uf="GO",
            municipio_ibge_code="5208707",
            correlation_id="corr-2",
        )
        assert updated.name == "Fazenda Boa Vista II"

        archived = await repo.archive(
            user_id=user_id,
            organization_id=org_id,
            farm_id=created.id,
            correlation_id="corr-3",
        )
        assert archived.archived_at is not None

        active_only = await repo.list(
            user_id=user_id, organization_id=org_id, include_archived=False
        )
        assert active_only == []

        with_archived = await repo.list(
            user_id=user_id, organization_id=org_id, include_archived=True
        )
        assert len(with_archived) == 1

        async with owner_engine.begin() as conn:
            audit_actions = (
                await conn.execute(
                    text(
                        "SELECT action, outcome FROM audit_events "
                        "WHERE object_id = :id ORDER BY created_at"
                    ),
                    {"id": created.id},
                )
            ).all()
        assert [(row.action, row.outcome) for row in audit_actions] == [
            ("farms.create", "allowed"),
            ("farms.update", "allowed"),
            ("farms.archive", "allowed"),
        ]
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()


async def test_create_rejects_invalid_uf_before_hitting_database() -> None:
    settings = Settings()
    owner_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    repo = FarmRepository(create_async_engine(settings.app_database_url, pool_pre_ping=True))
    try:
        user_id, org_id = await _seed_user_and_org(owner_engine)

        with pytest.raises(ProblemDetailError) as error:
            await repo.create(
                user_id=user_id,
                organization_id=org_id,
                name="Fazenda X",
                uf="ZZ",
                municipio_ibge_code="5208707",
                correlation_id="corr-1",
            )
        assert error.value.code == "farms.invalid_uf"
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()


async def test_update_of_foreign_organization_farm_raises_not_found() -> None:
    settings = Settings()
    owner_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    repo = FarmRepository(create_async_engine(settings.app_database_url, pool_pre_ping=True))
    try:
        user_a, org_a = await _seed_user_and_org(owner_engine)
        user_b_id = str(uuid.uuid4())
        org_b_id = str(uuid.uuid4())
        async with owner_engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO identity_users "
                    "(id, email, normalized_email, password_hash, password_hash_version, status) "
                    "VALUES (:id, :email, :email, 'hash', 'argon2id-v1', 'active')"
                ),
                {"id": user_b_id, "email": f"{user_b_id}@example.com"},
            )
            await conn.execute(
                text(
                    "INSERT INTO organizations (id, name, created_by) "
                    "VALUES (:id, 'Org B', :uid)"
                ),
                {"id": org_b_id, "uid": user_b_id},
            )
            await conn.execute(
                text(
                    "INSERT INTO organization_memberships (id, user_id, organization_id, role) "
                    "VALUES (gen_random_uuid(), :uid, :oid, 'owner')"
                ),
                {"uid": user_b_id, "oid": org_b_id},
            )

        farm_a = await repo.create(
            user_id=user_a,
            organization_id=org_a,
            name="Fazenda A",
            uf="GO",
            municipio_ibge_code="5208707",
            correlation_id="corr-1",
        )

        with pytest.raises(ProblemDetailError) as error:
            await repo.update(
                user_id=user_b_id,
                organization_id=org_b_id,
                farm_id=farm_a.id,
                name="Hackeada",
                uf="GO",
                municipio_ibge_code="5208707",
                correlation_id="corr-2",
            )
        assert error.value.status == 404

        # Tenant B nunca le a fazenda do tenant A, mesmo listando.
        listed_by_b = await repo.list(
            user_id=user_b_id, organization_id=org_b_id, include_archived=True
        )
        assert listed_by_b == []

        # Tenant B nunca arquiva a fazenda do tenant A.
        with pytest.raises(ProblemDetailError) as archive_error:
            await repo.archive(
                user_id=user_b_id,
                organization_id=org_b_id,
                farm_id=farm_a.id,
                correlation_id="corr-3",
            )
        assert archive_error.value.status == 404

        # A fazenda de A continua intacta e nao arquivada.
        still_active = await repo.list(
            user_id=user_a, organization_id=org_a, include_archived=False
        )
        assert [f.id for f in still_active] == [farm_a.id]
    finally:
        await owner_engine.dispose()
        await repo._engine.dispose()
