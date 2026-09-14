from __future__ import annotations

from alembic import op

revision = "20260914_0005"
down_revision = "20260914_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS talhoes (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            farm_id uuid NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
            organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            name text NOT NULL,
            geom geometry(MultiPolygon, 4674) NOT NULL,
            area_ha numeric(12,4) NOT NULL,
            archived_at timestamptz NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_talhoes_geom ON talhoes USING GIST (geom)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_talhoes_organization_id ON talhoes(organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_talhoes_farm_id ON talhoes(farm_id)")
    op.execute("ALTER TABLE talhoes ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE talhoes FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY talhoes_member_select ON talhoes
        FOR SELECT TO safraos_app
        USING (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = talhoes.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY talhoes_member_insert ON talhoes
        FOR INSERT TO safraos_app
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = talhoes.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY talhoes_member_update ON talhoes
        FOR UPDATE TO safraos_app
        USING (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = talhoes.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = talhoes.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute("GRANT SELECT, INSERT, UPDATE ON talhoes TO safraos_app")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS talhoes_member_update ON talhoes")
    op.execute("DROP POLICY IF EXISTS talhoes_member_insert ON talhoes")
    op.execute("DROP POLICY IF EXISTS talhoes_member_select ON talhoes")
    op.execute("DROP TABLE IF EXISTS talhoes")
