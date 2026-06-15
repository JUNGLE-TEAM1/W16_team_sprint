from fastapi import APIRouter, Depends, status

from backend.app.api.auth_dependencies import (
    AuthServiceDependency,
    CsrfProtectedContext,
    CurrentAuthContext,
    require_role,
)
from backend.app.core.security import utc_now
from backend.app.schemas.auth import (
    AdminReportResponse,
    CsrfDemoResponse,
    CurrentUserResponse,
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from backend.app.services.auth_service import AuthContext

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, service: AuthServiceDependency) -> UserResponse:
    return service.register(payload)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, service: AuthServiceDependency) -> TokenResponse:
    return service.login(payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, service: AuthServiceDependency) -> TokenResponse:
    return service.refresh(payload.refresh_token)


@router.get("/me", response_model=CurrentUserResponse)
def me(context: CurrentAuthContext) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=context.user.id,
        email=context.user.email,
        role=context.user.role,
        session_id=context.session_id,
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(context: CurrentAuthContext, service: AuthServiceDependency) -> LogoutResponse:
    service.logout(context.session_id)
    return LogoutResponse(revoked=True, session_id=context.session_id)


@router.post("/session-action", response_model=CsrfDemoResponse)
def session_action(context: CsrfProtectedContext) -> CsrfDemoResponse:
    return CsrfDemoResponse(
        message="쿠키 기반 세션이라면 이런 변경 요청에서 CSRF 토큰을 확인합니다.",
        session_id=context.session_id,
        checked_at=utc_now(),
    )


@router.get("/admin/report", response_model=AdminReportResponse)
def admin_report(
    context: AuthContext = Depends(require_role("admin")),
) -> AdminReportResponse:
    return AdminReportResponse(
        message="admin role만 볼 수 있는 보호 리소스입니다.",
        required_role="admin",
        current_role=context.user.role,
    )
