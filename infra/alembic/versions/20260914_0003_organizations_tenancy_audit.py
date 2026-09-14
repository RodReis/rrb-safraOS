from __future__ import annotations

from alembic import op

revision = "20260914_0003"
down_revision = "20260914_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'safraos_app') THEN
                CREATE ROLE safraos_app LOGIN PASSWORD 'safraos_app_local_dev' NOBYPASSRLS;
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS organizations (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL,
            created_by uuid NOT NULL REFERENCES identity_users(id),
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS organization_memberships (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES identity_users(id) ON DELETE CASCADE,
            organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            role text NOT NULL CHECK (role IN ('owner')),
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (user_id, organization_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            actor_user_id uuid NULL REFERENCES identity_users(id),
            organization_id uuid NULL REFERENCES organizations(id),
            action text NOT NULL,
            object_type text NOT NULL,
            object_id uuid NULL,
            outcome text NOT NULL CHECK (outcome IN ('allowed', 'denied')),
            correlation_id text NOT NULL,
            metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_memberships_user ON organization_memberships(user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_memberships_org ON organization_memberships(organization_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_org_created "
        "ON audit_events(organization_id, created_at)"
    )
    op.execute("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE organizations FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE organization_memberships FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_events FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY organizations_member_select ON organizations
        FOR SELECT TO safraos_app
        USING (
            created_by = current_setting('app.current_user_id', true)::uuid
            OR EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = organizations.id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY organizations_owner_insert ON organizations
        FOR INSERT TO safraos_app
        WITH CHECK (created_by = current_setting('app.current_user_id', true)::uuid)
        """
    )
    op.execute(
        """
        CREATE POLICY memberships_member_select ON organization_memberships
        FOR SELECT TO safraos_app
        USING (user_id = current_setting('app.current_user_id', true)::uuid)
        """
    )
    op.execute(
        """
        CREATE POLICY memberships_self_insert ON organization_memberships
        FOR INSERT TO safraos_app
        WITH CHECK (
            user_id = current_setting('app.current_user_id', true)::uuid
            AND role = 'owner'
        )
        """
    )
    op.execute(
        """
        CREATE POLICY audit_member_select ON audit_events
        FOR SELECT TO safraos_app
        USING (
            organization_id IS NULL
            OR EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = audit_events.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY audit_insert ON audit_events
        FOR INSERT TO safraos_app
        WITH CHECK (
            actor_user_id = current_setting('app.current_user_id', true)::uuid
            OR actor_user_id IS NULL
        )
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION forbid_audit_event_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'audit_events is append-only';
        END;
        $$;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_audit_events_append_only ON audit_events;
        CREATE TRIGGER trg_audit_events_append_only
        BEFORE UPDATE OR DELETE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION forbid_audit_event_mutation();
        """
    )
    op.execute("GRANT USAGE ON SCHEMA public TO safraos_app")
    op.execute("GRANT SELECT ON identity_users TO safraos_app")
    op.execute("GRANT SELECT ON identity_sessions TO safraos_app")
    op.execute("GRANT SELECT, INSERT ON organizations TO safraos_app")
    op.execute("GRANT SELECT, INSERT ON organization_memberships TO safraos_app")
    op.execute("GRANT SELECT, INSERT ON audit_events TO safraos_app")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_append_only ON audit_events")
    op.execute("DROP FUNCTION IF EXISTS forbid_audit_event_mutation")
    op.execute("DROP TABLE IF EXISTS audit_events")
    op.execute("DROP TABLE IF EXISTS organization_memberships")
    op.execute("DROP TABLE IF EXISTS organizations")
    op.execute("DROP ROLE IF EXISTS safraos_app")
