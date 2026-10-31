from dataclasses import dataclass
from typing import Any

import jwt
from jwt import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidTokenError,
    PyJWKClient,
)

from app.core.config import settings


MICROSOFT_JWKS_URL = (
    "https://login.microsoftonline.com/"
    "common/discovery/v2.0/keys"
)


class EntraTokenValidationError(Exception):
    pass


@dataclass(frozen=True)
class ValidatedEntraUser:
    tenant_id: str
    object_id: str
    subject: str
    scopes: set[str]
    claims: dict[str, Any]


_jwks_client = PyJWKClient(
    MICROSOFT_JWKS_URL,
    cache_jwk_set=True,
    lifespan=3600,
)


def validate_entra_access_token(
    access_token: str,
) -> ValidatedEntraUser:
    if not settings.entra_api_client_id:
        raise RuntimeError(
            "ENTRA_API_CLIENT_ID is not configured."
        )

    try:
        unverified_claims = jwt.decode(
            access_token,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
            },
        )
    except InvalidTokenError as exc:
        raise EntraTokenValidationError(
            "The access token is not a valid JWT."
        ) from exc

    token_version = str(
        unverified_claims.get("ver", "")
    )

    if token_version != "2.0":
        raise EntraTokenValidationError(
            "Only Microsoft Entra v2.0 access tokens "
            "are currently supported."
        )

    tenant_id = str(
        unverified_claims.get("tid", "")
    ).strip()

    if not tenant_id:
        raise EntraTokenValidationError(
            "The access token does not contain a tenant ID."
        )

    expected_issuer = (
        f"https://login.microsoftonline.com/"
        f"{tenant_id}/v2.0"
    )

    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(
            access_token
        )

        claims = jwt.decode(
            access_token,
            key=signing_key.key,
            algorithms=["RS256"],
            audience=settings.entra_api_client_id,
            issuer=expected_issuer,
            options={
                "require": [
                    "aud",
                    "exp",
                    "iat",
                    "iss",
                    "sub",
                    "tid",
                ],
            },
        )

    except ExpiredSignatureError as exc:
        raise EntraTokenValidationError(
            "The access token has expired."
        ) from exc

    except InvalidAudienceError as exc:
        raise EntraTokenValidationError(
            "The access token was not issued for "
            "the OrderFlow API."
        ) from exc

    except InvalidIssuerError as exc:
        raise EntraTokenValidationError(
            "The access token issuer is not trusted."
        ) from exc

    except InvalidTokenError as exc:
        raise EntraTokenValidationError(
            "The access token could not be validated."
        ) from exc

    verified_tenant_id = str(
        claims.get("tid", "")
    ).strip()

    if verified_tenant_id != tenant_id:
        raise EntraTokenValidationError(
            "The access token tenant is invalid."
        )

    scopes = {
        scope.strip()
        for scope in str(
            claims.get("scp", "")
        ).split()
        if scope.strip()
    }

    required_scope = (
        settings.entra_required_scope.strip()
    )

    if (
        required_scope
        and required_scope not in scopes
    ):
        raise EntraTokenValidationError(
            f"The access token does not contain "
            f"the required '{required_scope}' scope."
        )

    object_id = str(
        claims.get("oid", "")
    ).strip()

    subject = str(
        claims.get("sub", "")
    ).strip()

    if not object_id:
        raise EntraTokenValidationError(
            "The access token does not contain "
            "a user object ID."
        )

    return ValidatedEntraUser(
        tenant_id=verified_tenant_id,
        object_id=object_id,
        subject=subject,
        scopes=scopes,
        claims=claims,
    )