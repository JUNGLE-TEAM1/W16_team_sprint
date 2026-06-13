import base64
import hashlib
import hmac
import json
import secrets
from datetime import timedelta
from typing import Any

from backend.app.core.config import settings
from backend.app.core.time import utc_now


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}:{digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt, expected = password_hash.split(":", 1)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return hmac.compare_digest(digest.hex(), expected)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_opaque_token() -> str:
    return secrets.token_urlsafe(32)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64url(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: int, role: str, expires_delta: timedelta | None = None) -> str:
    expires = utc_now() + (expires_delta or timedelta(seconds=settings.access_token_seconds))
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": str(user_id), "role": role, "type": "access", "exp": int(expires.timestamp())}
    signing_input = ".".join(
        [
            _b64url(json.dumps(header, separators=(",", ":")).encode()),
            _b64url(json.dumps(payload, separators=(",", ":")).encode()),
        ]
    )
    signature = hmac.new(settings.auth_secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        expected = hmac.new(settings.auth_secret.encode(), signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url(expected), signature_b64):
            return None
        payload = json.loads(_unb64url(payload_b64))
        if payload.get("type") != "access":
            return None
        if int(payload.get("exp", 0)) < int(utc_now().timestamp()):
            return None
        return payload
    except Exception:
        return None
