import pytest

from safraos.farms.model import BRAZILIAN_UF_CODES, FarmError, create_farm

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
