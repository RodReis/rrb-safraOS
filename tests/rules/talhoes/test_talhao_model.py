import pytest

from safraos.talhoes.model import TalhaoError, normalize_talhao_name, validate_geometry_type

pytestmark = pytest.mark.rules


def test_normalize_talhao_name_trims_and_collapses_spaces() -> None:
    assert normalize_talhao_name("  Talhao   Norte  ") == "Talhao Norte"


def test_normalize_talhao_name_rejects_short_name() -> None:
    with pytest.raises(TalhaoError) as error:
        normalize_talhao_name(" ")

    assert error.value.code == "talhoes.invalid_name"


def test_validate_geometry_type_accepts_polygon() -> None:
    assert validate_geometry_type({"type": "Polygon", "coordinates": []}) == "Polygon"


def test_validate_geometry_type_accepts_multipolygon() -> None:
    assert validate_geometry_type({"type": "MultiPolygon", "coordinates": []}) == "MultiPolygon"


def test_validate_geometry_type_rejects_point() -> None:
    with pytest.raises(TalhaoError) as error:
        validate_geometry_type({"type": "Point", "coordinates": [0, 0]})

    assert error.value.code == "talhoes.invalid_geometry_type"


def test_validate_geometry_type_rejects_non_dict() -> None:
    with pytest.raises(TalhaoError) as error:
        validate_geometry_type("not-a-dict")  # type: ignore[arg-type]

    assert error.value.code == "talhoes.invalid_geometry_type"
