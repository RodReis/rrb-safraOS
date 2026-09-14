from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from safraos.identity import (
    IdentityError,
    PasswordHasher,
    PlainTokenIssuer,
    TokenDigest,
    UserStatus,
    normalize_email,
)

pytestmark = pytest.mark.rules


def test_normalize_email_casefolds_and_trims() -> None:
    assert normalize_email("  Dono@EXEMPLO.COM.BR ") == "dono@exemplo.com.br"


def test_rejects_invalid_email() -> None:
    with pytest.raises(IdentityError, match="E-mail invalido"):
        normalize_email("sem-arroba")


def test_password_hash_uses_argon2id_and_verifies() -> None:
    hasher = PasswordHasher()
    password_hash = hasher.hash("senha-longa-segura")

    assert password_hash.startswith("$argon2id$")
    assert hasher.verify(password_hash, "senha-longa-segura") is True
    assert hasher.verify(password_hash, "senha-errada") is False


def test_token_digest_never_equals_plain_token_and_is_stable() -> None:
    token = "externo"

    digest = TokenDigest.from_plain(token)

    assert digest.value != token
    assert digest == TokenDigest.from_plain(token)


def test_token_issuer_sets_expiration() -> None:
    now = datetime(2026, 9, 14, tzinfo=UTC)

    token, digest, expires_at = PlainTokenIssuer(timedelta(minutes=30)).issue(now)

    assert token
    assert digest == TokenDigest.from_plain(token)
    assert expires_at == now + timedelta(minutes=30)


def test_user_states_contract() -> None:
    assert [state.value for state in UserStatus] == [
        "pending_verification",
        "active",
        "disabled",
    ]
