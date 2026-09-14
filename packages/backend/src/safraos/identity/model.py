from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import VerifyMismatchError


class IdentityError(ValueError):
    code: str

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class UserStatus(StrEnum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    DISABLED = "disabled"


def normalize_email(value: str) -> str:
    normalized = value.strip().casefold()
    if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
        raise IdentityError("identity.invalid_email", "E-mail invalido.")
    return normalized


@dataclass(frozen=True)
class EmailAddress:
    value: str

    @classmethod
    def parse(cls, value: str) -> EmailAddress:
        return cls(normalize_email(value))


class PasswordHasher:
    version = "argon2id-v1"

    def __init__(self) -> None:
        self._hasher = Argon2PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )

    def hash(self, password: str) -> str:
        self._validate_password(password)
        return self._hasher.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except VerifyMismatchError:
            return False

    def _validate_password(self, password: str) -> None:
        if len(password) < 12:
            raise IdentityError("identity.weak_password", "Senha deve ter ao menos 12 caracteres.")


@dataclass(frozen=True)
class TokenDigest:
    value: str

    @classmethod
    def from_plain(cls, token: str) -> TokenDigest:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return cls(digest)


@dataclass(frozen=True)
class PlainTokenIssuer:
    ttl: timedelta

    def issue(self, now: datetime | None = None) -> tuple[str, TokenDigest, datetime]:
        instant = now or datetime.now(UTC)
        token = secrets.token_urlsafe(32)
        return token, TokenDigest.from_plain(token), instant + self.ttl
