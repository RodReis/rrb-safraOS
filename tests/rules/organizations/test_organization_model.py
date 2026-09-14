from __future__ import annotations

import pytest

from safraos.organizations import MembershipRole, OrganizationError, create_organization

pytestmark = pytest.mark.rules


def test_create_organization_normalizes_name() -> None:
    organization = create_organization("  Fazenda   Santa   Maria  ")

    assert organization.name == "Fazenda Santa Maria"


def test_create_organization_rejects_empty_name() -> None:
    with pytest.raises(OrganizationError) as error:
        create_organization(" ")

    assert error.value.code == "organizations.invalid_name"


def test_only_owner_role_exists_in_mvp0() -> None:
    assert [role.value for role in MembershipRole] == ["owner"]
