import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError

from safraos.farms.model import BRAZILIAN_UF_CODES, Farm, FarmError, create_farm

pytestmark = pytest.mark.rules


def test_create_farm_normalizes_name_and_accepts_valid_uf_and_ibge() -> None:
    name, uf, ibge = create_farm("  Fazenda   Boa   Vista  ", "GO", "5208707")

    assert name == "Fazenda Boa Vista"
    assert uf == "GO"
    assert ibge == "5208707"


def test_create_farm_rejects_empty_name() -> None:
    with pytest.raises(FarmError) as error:
        create_farm("   ", "GO", "5208707")

    assert error.value.code == "farms.invalid_name"


def test_create_farm_rejects_unknown_uf() -> None:
    with pytest.raises(FarmError) as error:
        create_farm("Fazenda Teste", "XX", "5208707")

    assert error.value.code == "farms.invalid_uf"


def test_create_farm_uf_is_case_insensitive_and_normalized_to_upper() -> None:
    _, uf, _ = create_farm("Fazenda Teste", "go", "5208707")

    assert uf == "GO"


@pytest.mark.parametrize("bad_code", ["123", "abcdefg", "12345678", ""])
def test_create_farm_rejects_malformed_ibge_code(bad_code: str) -> None:
    with pytest.raises(FarmError) as error:
        create_farm("Fazenda Teste", "GO", bad_code)

    assert error.value.code == "farms.invalid_municipio"


def test_brazilian_uf_codes_has_27_entries() -> None:
    assert len(BRAZILIAN_UF_CODES) == 27
    assert "GO" in BRAZILIAN_UF_CODES
    assert "MT" in BRAZILIAN_UF_CODES
    assert "MS" in BRAZILIAN_UF_CODES


def test_farm_dataclass_is_constructed_with_all_fields() -> None:
    now = datetime.now()
    farm = Farm(
        id="farm-001",
        organization_id="org-001",
        name="Fazenda Boa Vista",
        uf="GO",
        municipio_ibge_code="5208707",
        archived_at=None,
    )

    assert farm.id == "farm-001"
    assert farm.organization_id == "org-001"
    assert farm.name == "Fazenda Boa Vista"
    assert farm.uf == "GO"
    assert farm.municipio_ibge_code == "5208707"
    assert farm.archived_at is None


def test_farm_dataclass_is_frozen() -> None:
    farm = Farm(
        id="farm-001",
        organization_id="org-001",
        name="Fazenda Boa Vista",
        uf="GO",
        municipio_ibge_code="5208707",
        archived_at=None,
    )

    with pytest.raises(FrozenInstanceError):
        farm.name = "Fazenda Nova"  # type: ignore[misc]  # mypy: campo frozen, mutação é o comportamento testado
