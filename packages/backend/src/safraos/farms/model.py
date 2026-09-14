"""Regras puras da entidade Farm: sem banco, rede ou relogio."""

import re
from dataclasses import dataclass
from datetime import datetime

BRAZILIAN_UF_CODES: frozenset[str] = frozenset(
    {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    }
)

_IBGE_CODE_PATTERN = re.compile(r"^\d{7}$")


class FarmError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Farm:
    id: str
    organization_id: str
    name: str
    uf: str
    municipio_ibge_code: str
    archived_at: datetime | None


def create_farm(name: str, uf: str, municipio_ibge_code: str) -> tuple[str, str, str]:
    normalized_name = " ".join(name.strip().split())
    if len(normalized_name) < 2:
        raise FarmError("farms.invalid_name", "Nome da fazenda deve ter ao menos 2 caracteres.")

    normalized_uf = uf.strip().upper()
    if normalized_uf not in BRAZILIAN_UF_CODES:
        raise FarmError("farms.invalid_uf", f"UF '{uf}' nao e uma sigla valida.")

    normalized_ibge = municipio_ibge_code.strip()
    if not _IBGE_CODE_PATTERN.match(normalized_ibge):
        raise FarmError(
            "farms.invalid_municipio",
            "Codigo IBGE do municipio deve ter 7 digitos numericos.",
        )

    return normalized_name, normalized_uf, normalized_ibge
