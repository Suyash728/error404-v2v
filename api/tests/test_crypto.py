import pytest
from cryptography.fernet import Fernet, InvalidToken

from core import crypto


def test_encrypt_decrypt_round_trip(monkeypatch):
    monkeypatch.setenv("GCAL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    ciphertext = crypto.encrypt("a-refresh-token")
    assert crypto.decrypt(ciphertext) == "a-refresh-token"


def test_ciphertext_does_not_contain_the_plaintext(monkeypatch):
    monkeypatch.setenv("GCAL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    ciphertext = crypto.encrypt("a-refresh-token")
    assert "a-refresh-token" not in ciphertext


def test_decrypt_with_wrong_key_raises(monkeypatch):
    monkeypatch.setenv("GCAL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    ciphertext = crypto.encrypt("a-refresh-token")

    crypto._fernet.cache_clear()
    monkeypatch.setenv("GCAL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())

    with pytest.raises(InvalidToken):
        crypto.decrypt(ciphertext)


def test_decrypt_tampered_ciphertext_raises(monkeypatch):
    monkeypatch.setenv("GCAL_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    ciphertext = crypto.encrypt("a-refresh-token")

    last_char = ciphertext[-1]
    flipped = "A" if last_char != "A" else "B"
    tampered = ciphertext[:-1] + flipped

    with pytest.raises(InvalidToken):
        crypto.decrypt(tampered)
