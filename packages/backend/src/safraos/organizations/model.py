from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OrganizationError(ValueError):
    code: str

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class MembershipRole(StrEnum):
    OWNER = "owner"


class AuditOutcome(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"


@dataclass(frozen=True)
class Organization:
    name: str


def create_organization(name: str) -> Organization:
    normalized = " ".join(name.strip().split())
    if len(normalized) < 2:
        raise OrganizationError(
            "organizations.invalid_name",
            "Nome da organizacao deve ter ao menos 2 caracteres.",
        )
    return Organization(name=normalized)
