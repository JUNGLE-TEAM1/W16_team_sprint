import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import status

from backend.app.core.config import settings
from backend.app.core.errors import AppError


def utc_now() -> datetime:
    return datetime.utcnow()


def random_token() -> str:
    return secrets.token_urlsafe(32)


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = "sprint-demo-salt"
    return hash_secret(f"{salt}:{password}")


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def _base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def create_jwt(
    *,
    subject: int,
    role: str,
    token_type: str,
    session_id: str,
    expires_delta: timedelta,
    jwt_id: str | None = None,
) -> str:
    now = int(time.time())
    payload = {
        "sub": str(subject),
        "role": role,
        "type": token_type,
        "sid": session_id,
        "jti": jwt_id or str(uuid4()),
        "iat": now,
        "exp": now + int(expires_delta.total_seconds()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    header_part = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_part = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        f"{header_part}.{payload_part}".encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{header_part}.{payload_part}.{_base64url_encode(signature)}"


def decode_jwt(token: str, *, expected_type: str) -> dict[str, Any]:
    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:
        raise AppError(
            code="INVALID_TOKEN",
            message="토큰 형식이 올바르지 않습니다.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc

    expected_signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        f"{header_part}.{payload_part}".encode("ascii"),
        hashlib.sha256,
    ).digest()
    actual_signature = _base64url_decode(signature_part)

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise AppError(
            code="INVALID_TOKEN",
            message="토큰 서명이 올바르지 않습니다.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload = json.loads(_base64url_decode(payload_part))

    if payload.get("exp", 0) < int(time.time()):
        raise AppError(
            code="TOKEN_EXPIRED",
            message="토큰이 만료되었습니다.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if payload.get("type") != expected_type:
        raise AppError(
            code="INVALID_TOKEN_TYPE",
            message="토큰 타입이 올바르지 않습니다.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return payload
