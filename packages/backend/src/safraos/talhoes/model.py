"""Regras puras da entidade Talhao: sem banco, rede ou relogio."""

from __future__ import annotations

_VALID_GEOMETRY_TYPES = frozenset({"Polygon", "MultiPolygon"})


class TalhaoError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def normalize_talhao_name(name: str) -> str:
    normalized = " ".join(name.strip().split())
    if len(normalized) < 2:
        raise TalhaoError("talhoes.invalid_name", "Nome do talhao deve ter ao menos 2 caracteres.")
    return normalized


def validate_geometry_type(geometry: object) -> str:
    if not isinstance(geometry, dict):
        raise TalhaoError(
            "talhoes.invalid_geometry_type", "Geometria deve ser um objeto GeoJSON."
        )
    geometry_type = geometry.get("type")
    if geometry_type not in _VALID_GEOMETRY_TYPES:
        raise TalhaoError(
            "talhoes.invalid_geometry_type",
            "Geometria deve ser do tipo Polygon ou MultiPolygon.",
        )
    return str(geometry_type)
