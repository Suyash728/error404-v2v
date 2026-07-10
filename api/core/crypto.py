"""Symmetric encryption for secrets that must be stored at rest (Google
Calendar OAuth refresh tokens) but never need to be read outside the
backend. A single Fernet key (GCAL_TOKEN_ENCRYPTION_KEY) is reused as the
OAuth `state` param's signing key too — Fernet already gives tamper-evident,
authenticated tokens for free, so that doesn't need its own separate secret.
"""

import os
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

__all__ = ["encrypt", "decrypt", "InvalidToken"]


@lru_cache
def _fernet() -> Fernet:
    return Fernet(os.environ["GCAL_TOKEN_ENCRYPTION_KEY"].encode())


def encrypt(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return _fernet().decrypt(ciphertext.encode()).decode()
