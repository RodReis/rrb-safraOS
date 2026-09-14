from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from safraos.identity import PasswordHasher, PlainTokenIssuer, TokenDigest, normalize_email
from safraos_api.settings import Settings
from safraos_worker.app import celery_app

SESSION_TTL = timedelta(hours=8)
VERIFY_TTL = timedelta(hours=24)
RESET_TTL = timedelta(minutes=30)


class IdentityRepository:
    def __init__(self, engine: AsyncEngine, settings: Settings) -> None:
        self._engine = engine
        self._settings = settings
        self._hasher = PasswordHasher()

    async def register(self, email: str, password: str) -> None:
        normalized = normalize_email(email)
        password_hash = self._hasher.hash(password)
        token, digest, expires_at = PlainTokenIssuer(VERIFY_TTL).issue()
        outbox_id: str | None = None
        async with self._engine.begin() as conn:
            existing = await conn.scalar(
                text("SELECT id FROM identity_users WHERE normalized_email = :email"),
                {"email": normalized},
            )
            if existing is not None:
                return
            user_id = await conn.scalar(
                text(
                    """
                    INSERT INTO identity_users
                        (email, normalized_email, password_hash, password_hash_version, status)
                    VALUES (
                        :email,
                        :normalized_email,
                        :password_hash,
                        :version,
                        'pending_verification'
                    )
                    RETURNING id
                    """
                ),
                {
                    "email": email.strip(),
                    "normalized_email": normalized,
                    "password_hash": password_hash,
                    "version": self._hasher.version,
                },
            )
            await conn.execute(
                text(
                    """
                    INSERT INTO identity_tokens (user_id, kind, token_hash, status, expires_at)
                    VALUES (:user_id, 'email_verification', :token_hash, 'active', :expires_at)
                    """
                ),
                {"user_id": user_id, "token_hash": digest.value, "expires_at": expires_at},
            )
            outbox_id = await self._enqueue(
                conn,
                f"verify:{user_id}",
                "identity.email_verification",
                {
                    "to": normalized,
                    "subject": "Confirme seu e-mail no SafraOS",
                    "url": f"{self._settings.app_origin}/confirmar-email?token={token}",
                },
            )
        if outbox_id is not None:
            celery_app.send_task("safraos_worker.tasks.email.send_identity_email", args=[outbox_id])

    async def confirm_email(self, token: str) -> bool:
        digest = TokenDigest.from_plain(token).value
        async with self._engine.begin() as conn:
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT id, user_id, expires_at, status
                        FROM identity_tokens
                        WHERE token_hash = :token_hash AND kind = 'email_verification'
                        FOR UPDATE
                        """
                    ),
                    {"token_hash": digest},
                )
            ).mappings().first()
            if row is None or row["status"] != "active" or row["expires_at"] <= datetime.now(UTC):
                return False
            await conn.execute(
                text(
                    """
                    UPDATE identity_tokens
                    SET status = 'consumed', consumed_at = now()
                    WHERE id = :id
                    """
                ),
                {"id": row["id"]},
            )
            await conn.execute(
                text(
                    """
                    UPDATE identity_users
                    SET status = 'active', verified_at = COALESCE(verified_at, now())
                    WHERE id = :user_id AND status = 'pending_verification'
                    """
                ),
                {"user_id": row["user_id"]},
            )
            return True

    async def login(self, email: str, password: str) -> tuple[str, str] | None:
        normalized = normalize_email(email)
        async with self._engine.begin() as conn:
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT id, password_hash, status
                        FROM identity_users
                        WHERE normalized_email = :email
                        """
                    ),
                    {"email": normalized},
                )
            ).mappings().first()
            if row is None or row["status"] != "active":
                return None
            if not self._hasher.verify(row["password_hash"], password):
                return None
            session_token, session_hash, expires_at = PlainTokenIssuer(SESSION_TTL).issue()
            csrf_token, csrf_hash, _ = PlainTokenIssuer(SESSION_TTL).issue()
            await conn.execute(
                text(
                    """
                    INSERT INTO identity_sessions (user_id, csrf_token_hash, status, expires_at)
                    VALUES (:user_id, :csrf_hash, 'active', :expires_at)
                    """
                ),
                {"user_id": row["id"], "csrf_hash": csrf_hash.value, "expires_at": expires_at},
            )
            await conn.execute(
                text(
                    """
                    UPDATE identity_sessions
                    SET csrf_token_hash = :csrf_hash
                    WHERE id = (
                        SELECT id FROM identity_sessions
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC
                        LIMIT 1
                    )
                    """
                ),
                {"user_id": row["id"], "csrf_hash": csrf_hash.value},
            )
            session_id = await conn.scalar(
                text(
                    """
                    SELECT id FROM identity_sessions
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                    LIMIT 1
                    """
                ),
                {"user_id": row["id"]},
            )
            return f"{session_id}.{session_hash.value}.{session_token}", csrf_token

    async def logout(self, session_cookie: str | None, csrf_token: str | None) -> bool:
        session_id = self._parse_session_id(session_cookie)
        if session_id is None or csrf_token is None:
            return False
        async with self._engine.begin() as conn:
            valid = await self._check_csrf(conn, session_id, csrf_token)
            if not valid:
                return False
            await conn.execute(
                text(
                    """
                    UPDATE identity_sessions
                    SET status = 'revoked', revoked_at = now()
                    WHERE id = :id
                    """
                ),
                {"id": session_id},
            )
            return True

    async def request_password_reset(self, email: str) -> None:
        normalized = normalize_email(email)
        token, digest, expires_at = PlainTokenIssuer(RESET_TTL).issue()
        outbox_id: str | None = None
        async with self._engine.begin() as conn:
            user_id = await conn.scalar(
                text("SELECT id FROM identity_users WHERE normalized_email = :email"),
                {"email": normalized},
            )
            if user_id is None:
                return
            await conn.execute(
                text(
                    """
                    INSERT INTO identity_tokens (user_id, kind, token_hash, status, expires_at)
                    VALUES (:user_id, 'password_reset', :token_hash, 'active', :expires_at)
                    """
                ),
                {"user_id": user_id, "token_hash": digest.value, "expires_at": expires_at},
            )
            outbox_id = await self._enqueue(
                conn,
                f"reset:{user_id}:{digest.value}",
                "identity.password_reset",
                {
                    "to": normalized,
                    "subject": "Redefina sua senha no SafraOS",
                    "url": f"{self._settings.app_origin}/redefinir-senha?token={token}",
                },
            )
        if outbox_id is not None:
            celery_app.send_task("safraos_worker.tasks.email.send_identity_email", args=[outbox_id])

    async def reset_password(self, token: str, password: str) -> bool:
        digest = TokenDigest.from_plain(token).value
        password_hash = self._hasher.hash(password)
        async with self._engine.begin() as conn:
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT id, user_id, expires_at, status
                        FROM identity_tokens
                        WHERE token_hash = :token_hash AND kind = 'password_reset'
                        FOR UPDATE
                        """
                    ),
                    {"token_hash": digest},
                )
            ).mappings().first()
            if row is None or row["status"] != "active" or row["expires_at"] <= datetime.now(UTC):
                return False
            await conn.execute(
                text(
                    """
                    UPDATE identity_users
                    SET password_hash = :password_hash, password_hash_version = :version
                    WHERE id = :user_id
                    """
                ),
                {
                    "password_hash": password_hash,
                    "version": self._hasher.version,
                    "user_id": row["user_id"],
                },
            )
            await conn.execute(
                text(
                    """
                    UPDATE identity_sessions
                    SET status = 'revoked', revoked_at = now()
                    WHERE user_id = :user_id
                    """
                ),
                {"user_id": row["user_id"]},
            )
            await conn.execute(
                text(
                    """
                    UPDATE identity_tokens
                    SET status = 'consumed', consumed_at = now()
                    WHERE id = :id
                    """
                ),
                {"id": row["id"]},
            )
            await conn.execute(
                text(
                    """
                    UPDATE identity_tokens
                    SET status = 'expired'
                    WHERE user_id = :user_id AND kind = 'password_reset' AND status = 'active'
                    """
                ),
                {"user_id": row["user_id"]},
            )
            return True

    async def _enqueue(
        self,
        conn: AsyncConnection,
        event_key: str,
        event_type: str,
        payload: dict[str, str],
    ) -> str | None:
        await conn.execute(
            text(
                """
                INSERT INTO identity_outbox (event_key, event_type, payload, status)
                VALUES (:event_key, :event_type, CAST(:payload AS jsonb), 'pending')
                ON CONFLICT (event_key) DO NOTHING
                """
            ),
            {"event_key": event_key, "event_type": event_type, "payload": json.dumps(payload)},
        )
        outbox_id = await conn.scalar(
            text("SELECT id FROM identity_outbox WHERE event_key = :event_key"),
            {"event_key": event_key},
        )
        return str(outbox_id) if outbox_id is not None else None

    def _parse_session_id(self, session_cookie: str | None) -> str | None:
        if not session_cookie or "." not in session_cookie:
            return None
        return session_cookie.split(".", maxsplit=1)[0]

    async def _check_csrf(
        self,
        conn: AsyncConnection,
        session_id: str,
        csrf_token: str,
    ) -> bool:
        row = (
            await conn.execute(
                text(
                    """
                    SELECT csrf_token_hash, status, expires_at
                    FROM identity_sessions
                    WHERE id = :id
                    """
                ),
                {"id": session_id},
            )
        ).mappings().first()
        return bool(
            row
            and row["status"] == "active"
            and row["expires_at"] > datetime.now(UTC)
            and row["csrf_token_hash"] == TokenDigest.from_plain(csrf_token).value
        )


def build_repository(settings: Settings) -> IdentityRepository:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    return IdentityRepository(engine, settings)
