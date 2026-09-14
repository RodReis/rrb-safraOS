from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260914_0004"
down_revision = "20260914_0003"
branch_labels = None
depends_on = None

_MUNICIPIOS_SEED = [
    ("5208707", "Goiania", "GO"),
    ("5103403", "Cuiaba", "MT"),
    ("5002704", "Campo Grande", "MS"),
    ("5201405", "Aguas Lindas de Goias", "GO"),
    ("5107925", "Sinop", "MT"),
    ("5003207", "Dourados", "MS"),
]


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS municipios (
            ibge_code char(7) PRIMARY KEY,
            name text NOT NULL,
            uf char(2) NOT NULL
        )
        """
    )
    municipios_table = sa.table(
        "municipios",
        sa.column("ibge_code", sa.CHAR(7)),
        sa.column("name", sa.Text()),
        sa.column("uf", sa.CHAR(2)),
    )
    op.bulk_insert(
        municipios_table,
        [
            {"ibge_code": code, "name": name, "uf": uf}
            for code, name, uf in _MUNICIPIOS_SEED
        ],
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS farms (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            name text NOT NULL,
            uf char(2) NOT NULL,
            municipio_ibge_code char(7) NOT NULL REFERENCES municipios(ibge_code),
            archived_at timestamptz NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_farms_organization_id ON farms(organization_id)")
    op.execute("ALTER TABLE farms ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE farms FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY farms_member_select ON farms
        FOR SELECT TO safraos_app
        USING (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = farms.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY farms_member_insert ON farms
        FOR INSERT TO safraos_app
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = farms.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY farms_member_update ON farms
        FOR UPDATE TO safraos_app
        USING (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = farms.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM organization_memberships m
                WHERE m.organization_id = farms.organization_id
                  AND m.user_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        """
    )
    op.execute("GRANT SELECT ON municipios TO safraos_app")
    op.execute("GRANT SELECT, INSERT, UPDATE ON farms TO safraos_app")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS farms_member_update ON farms")
    op.execute("DROP POLICY IF EXISTS farms_member_insert ON farms")
    op.execute("DROP POLICY IF EXISTS farms_member_select ON farms")
    op.execute("DROP TABLE IF EXISTS farms")
    op.execute("DROP TABLE IF EXISTS municipios")
