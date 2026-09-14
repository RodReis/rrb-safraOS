from __future__ import annotations

from alembic import op

revision = "20260914_0002"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS identity_users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            email text NOT NULL,
            normalized_email text NOT NULL UNIQUE,
            password_hash text NOT NULL,
            password_hash_version text NOT NULL,
            status text NOT NULL CHECK (status IN ('pending_verification', 'active', 'disabled')),
            created_at timestamptz NOT NULL DEFAULT now(),
            verified_at timestamptz NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS identity_sessions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES identity_users(id) ON DELETE CASCADE,
            csrf_token_hash text NOT NULL,
            status text NOT NULL CHECK (status IN ('active', 'revoked', 'expired')),
            created_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL,
            revoked_at timestamptz NULL
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_identity_sessions_user ON identity_sessions(user_id)")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS identity_tokens (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES identity_users(id) ON DELETE CASCADE,
            kind text NOT NULL CHECK (kind IN ('email_verification', 'password_reset')),
            token_hash text NOT NULL UNIQUE,
            status text NOT NULL CHECK (status IN ('active', 'consumed', 'expired')),
            created_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL,
            consumed_at timestamptz NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_identity_tokens_user_kind ON identity_tokens(user_id, kind)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS identity_outbox (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            event_key text NOT NULL UNIQUE,
            event_type text NOT NULL,
            payload jsonb NOT NULL,
            status text NOT NULL CHECK (status IN ('pending', 'processing', 'sent', 'failed')),
            attempts integer NOT NULL DEFAULT 0,
            created_at timestamptz NOT NULL DEFAULT now(),
            sent_at timestamptz NULL
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS identity_outbox")
    op.execute("DROP TABLE IF EXISTS identity_tokens")
    op.execute("DROP TABLE IF EXISTS identity_sessions")
    op.execute("DROP TABLE IF EXISTS identity_users")
