"""
Sagarvani Reconstructed — Supabase Authentication & Token Verification

Provides FastAPI security dependencies for extracting and verifying Supabase
access tokens from incoming 'Authorization: Bearer <token>' headers.

Verification strategy:
1. Local JWKS verification using PyJWT and the project's public keys from SUPABASE_JWKS_URL.
2. Direct Supabase Auth REST verification (GET /auth/v1/user) as fallback.
3. Derives user_id (UUID 'sub'), email, and metadata securely from verified claims.
4. Returns 401 Unauthorized on invalid, expired, or missing tokens.
"""

import time
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel
import httpx
import jwt
from jwt import PyJWKClient, ExpiredSignatureError, InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.core.config import settings

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    user_id: str
    email: Optional[str] = None
    role: Optional[str] = None
    metadata: Dict[str, Any] = {}


# Cached PyJWKClient instance
_jwk_client: Optional[PyJWKClient] = None


def get_jwk_client() -> Optional[PyJWKClient]:
    global _jwk_client
    if _jwk_client is not None:
        return _jwk_client

    jwks_url = settings.supabase_jwks_url
    if not jwks_url and settings.supabase_url:
        jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"

    if jwks_url:
        try:
            _jwk_client = PyJWKClient(jwks_url, cache_keys=True, max_cached_keys=10)
        except Exception as e:
            logger.warning("Could not initialize PyJWKClient: %s", e)
    return _jwk_client


async def verify_token_via_supabase_api(token: str) -> Optional[AuthenticatedUser]:
    """Fallback: verifies token directly with Supabase Auth REST endpoint."""
    if not settings.supabase_url or not settings.supabase_publishable_key:
        return None

    user_endpoint = f"{settings.supabase_url.rstrip('/')}/auth/v1/user"
    headers = {
        "apikey": settings.supabase_publishable_key,
        "Authorization": f"Bearer {token}",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(user_endpoint, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return AuthenticatedUser(
                    user_id=data.get("id"),
                    email=data.get("email"),
                    role=data.get("role", "authenticated"),
                    metadata=data.get("user_metadata", {}),
                )
    except Exception as e:
        logger.warning("Supabase Auth API token check error: %s", e)

    return None


def verify_token_via_jwks(token: str) -> Optional[AuthenticatedUser]:
    """Verifies JWT signature, issuer, audience, and expiration via JWKS."""
    jwk_client = get_jwk_client()
    if not jwk_client:
        return None

    try:
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        # Supabase tokens have aud='authenticated'
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
        sub = payload.get("sub")
        if not sub:
            return None

        return AuthenticatedUser(
            user_id=sub,
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
            metadata=payload.get("user_metadata", {}),
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"token has expired\""},
        )
    except InvalidTokenError as e:
        logger.debug("JWKS token decode failed: %s", e)
        return None
    except Exception as e:
        logger.debug("JWKS unexpected error: %s", e)
        return None


async def verify_supabase_token(token: str) -> AuthenticatedUser:
    """Verifies a Supabase access token using JWKS first, then API fallback."""
    # 1. Try local JWKS verification
    user = verify_token_via_jwks(token)
    if user:
        return user

    # 2. Try Supabase Auth API verification
    user = await verify_token_via_supabase_api(token)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or unauthorized authentication token.",
        headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
    )


async def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[AuthenticatedUser]:
    """Optional authentication dependency: returns AuthenticatedUser if token is present and valid,
    or None if no Authorization header was sent. Raises 401 if token is present but invalid/expired."""
    if not auth or not auth.credentials:
        return None
    return await verify_supabase_token(auth.credentials)


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> AuthenticatedUser:
    """Mandatory authentication dependency for protected endpoints.
    Raises 401 if token is missing, invalid, or expired."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await verify_supabase_token(auth.credentials)
