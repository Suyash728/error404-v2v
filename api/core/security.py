import logging
import os
from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = logging.getLogger("arohi.auth")
bearer_scheme = HTTPBearer()


@lru_cache
def _jwks() -> dict:
    """Supabase's published signing keys. Supabase issues user session JWTs
    signed with an asymmetric key (ES256) by default on current projects,
    not a shared HS256 secret, so verification has to go through the
    project's public JWKS rather than a static secret.

    Cached for the process lifetime — Supabase key rotation is rare enough
    that "restart the server to pick up a rotated key" is an acceptable
    tradeoff here.
    """
    supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
    response = httpx.get(f"{supabase_url}/auth/v1/.well-known/jwks.json", timeout=5.0)
    response.raise_for_status()
    return response.json()


def _signing_key_for(token: str) -> dict:
    kid = jwt.get_unverified_header(token).get("kid")
    for key in _jwks()["keys"]:
        if key["kid"] == kid:
            return key
    raise JWTError(f"No JWKS key found for kid={kid!r}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Verify a Supabase-issued JWT against Supabase's JWKS and return its
    decoded payload."""
    try:
        key = _signing_key_for(credentials.credentials)
        payload = jwt.decode(
            credentials.credentials, key, algorithms=[key["alg"]], audience="authenticated"
        )
    except JWTError as exc:
        # Logged server-side only (never in the HTTP response) so a 401 can
        # be told apart from "no token sent" vs "bad signature" vs "expired"
        # without needing to inspect the client.
        logger.warning("JWT verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    return payload
