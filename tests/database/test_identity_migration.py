from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from safraos_api.settings import Settings

pytestmark = pytest.mark.database


@pytest.mark.asyncio
async def test_identity_tables_have_unique_normalized_email() -> None:
    engine = create_async_engine(Settings().database_url)
    async with engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE audit_events, identity_users RESTART IDENTITY CASCADE")
        )
        await conn.execute(
            text(
                """
                INSERT INTO identity_users
                    (email, normalized_email, password_hash, password_hash_version, status)
                VALUES (
                    'A@EXEMPLO.COM',
                    'a@exemplo.com',
                    '$argon2id$fake',
                    'argon2id-v1',
                    'pending_verification'
                )
                """
            )
        )
        with pytest.raises(IntegrityError):
            await conn.execute(
                text(
                    """
                    INSERT INTO identity_users
                        (email, normalized_email, password_hash, password_hash_version, status)
                    VALUES (
                        'a@exemplo.com',
                        'a@exemplo.com',
                        '$argon2id$fake',
                        'argon2id-v1',
                        'pending_verification'
                    )
                    """
                )
            )
    await engine.dispose()
