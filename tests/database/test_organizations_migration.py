from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from safraos_api.settings import Settings

pytestmark = pytest.mark.database


@pytest.mark.asyncio
async def test_membership_is_unique() -> None:
    engine = create_async_engine(Settings().database_url)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                TRUNCATE audit_events, organization_memberships, organizations, identity_users
                RESTART IDENTITY CASCADE
                """
            )
        )
        user_id = await conn.scalar(
            text(
                """
                INSERT INTO identity_users
                    (email, normalized_email, password_hash, password_hash_version, status)
                VALUES ('owner@example.com', 'owner@example.com', 'hash', 'argon2id-v1', 'active')
                RETURNING id
                """
            )
        )
        org_id = await conn.scalar(
            text(
                """
                INSERT INTO organizations (name, created_by)
                VALUES ('Org A', :user_id)
                RETURNING id
                """
            ),
            {"user_id": user_id},
        )
        await conn.execute(
            text(
                """
                INSERT INTO organization_memberships (user_id, organization_id, role)
                VALUES (:user_id, :org_id, 'owner')
                """
            ),
            {"user_id": user_id, "org_id": org_id},
        )
        with pytest.raises(IntegrityError):
            await conn.execute(
                text(
                    """
                    INSERT INTO organization_memberships (user_id, organization_id, role)
                    VALUES (:user_id, :org_id, 'owner')
                    """
                ),
                {"user_id": user_id, "org_id": org_id},
            )
    await engine.dispose()


@pytest.mark.asyncio
async def test_rls_allows_only_member_organizations_through_app_role() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    app_engine = create_async_engine(Settings().app_database_url)
    async with owner_engine.begin() as conn:
        await conn.execute(
            text(
                """
                TRUNCATE audit_events, organization_memberships, organizations, identity_users
                RESTART IDENTITY CASCADE
                """
            )
        )
        user_a = await conn.scalar(
            text(
                """
                INSERT INTO identity_users
                    (email, normalized_email, password_hash, password_hash_version, status)
                VALUES ('a@example.com', 'a@example.com', 'hash', 'argon2id-v1', 'active')
                RETURNING id
                """
            )
        )
        user_b = await conn.scalar(
            text(
                """
                INSERT INTO identity_users
                    (email, normalized_email, password_hash, password_hash_version, status)
                VALUES ('b@example.com', 'b@example.com', 'hash', 'argon2id-v1', 'active')
                RETURNING id
                """
            )
        )
        org_a = await conn.scalar(
            text(
                """
                INSERT INTO organizations (name, created_by)
                VALUES ('Org A', :user_id)
                RETURNING id
                """
            ),
            {"user_id": user_a},
        )
        org_b = await conn.scalar(
            text(
                """
                INSERT INTO organizations (name, created_by)
                VALUES ('Org B', :user_id)
                RETURNING id
                """
            ),
            {"user_id": user_b},
        )
        await conn.execute(
            text(
                """
                INSERT INTO organization_memberships (user_id, organization_id, role)
                VALUES (:user_a, :org_a, 'owner'), (:user_b, :org_b, 'owner')
                """
            ),
            {"user_a": user_a, "org_a": org_a, "user_b": user_b, "org_b": org_b},
        )
    async with app_engine.begin() as conn:
        await conn.execute(
            text("SELECT set_config('app.current_user_id', :user_id, true)"),
            {"user_id": str(user_a)},
        )
        rows = (
            await conn.execute(text("SELECT id, name FROM organizations ORDER BY name"))
        ).mappings().all()

    assert [(str(row["id"]), row["name"]) for row in rows] == [(str(org_a), "Org A")]
    await owner_engine.dispose()
    await app_engine.dispose()


@pytest.mark.asyncio
async def test_app_role_has_no_bypassrls_and_audit_is_append_only() -> None:
    owner_engine = create_async_engine(Settings().database_url)
    app_engine = create_async_engine(Settings().app_database_url)
    async with owner_engine.begin() as conn:
        bypass = await conn.scalar(
            text("SELECT rolbypassrls FROM pg_roles WHERE rolname = 'safraos_app'")
        )
        await conn.execute(
            text(
                """
                TRUNCATE audit_events, organization_memberships, organizations, identity_users
                RESTART IDENTITY CASCADE
                """
            )
        )
        user_id = await conn.scalar(
            text(
                """
                INSERT INTO identity_users
                    (email, normalized_email, password_hash, password_hash_version, status)
                VALUES ('audit@example.com', 'audit@example.com', 'hash', 'argon2id-v1', 'active')
                RETURNING id
                """
            )
        )
        audit_id = await conn.scalar(
            text(
                """
                INSERT INTO audit_events
                    (actor_user_id, action, object_type, outcome, correlation_id)
                VALUES (:user_id, 'tenant.select', 'organization', 'denied', 'corr')
                RETURNING id
                """
            ),
            {"user_id": user_id},
        )
    assert bypass is False
    async with app_engine.begin() as conn:
        await conn.execute(
            text("SELECT set_config('app.current_user_id', :user_id, true)"),
            {"user_id": str(user_id)},
        )
        with pytest.raises(DatabaseError):
            await conn.execute(
                text("UPDATE audit_events SET outcome = 'allowed' WHERE id = :audit_id"),
                {"audit_id": audit_id},
            )
    await owner_engine.dispose()
    await app_engine.dispose()
