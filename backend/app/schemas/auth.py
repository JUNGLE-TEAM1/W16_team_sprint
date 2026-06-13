from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(examples=["member@sprint.local"])
    password: str = Field(examples=["password123"])


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_expires_in: int
    session_id: str
    csrf_token: str


class CurrentUserResponse(BaseModel):
    id: int
    email: str
    role: str
    session_id: str


class LogoutResponse(BaseModel):
    revoked: bool
    session_id: str


class AdminReportResponse(BaseModel):
    message: str
    required_role: str
    current_role: str


class CsrfDemoResponse(BaseModel):
    message: str
    session_id: str
    checked_at: datetime
