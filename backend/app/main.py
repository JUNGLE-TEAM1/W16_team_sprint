from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.ai_requests import router as ai_requests_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.posts import router as posts_router
from backend.app.core.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.core.rate_limit import LoginRateLimitMiddleware
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.models import ai_request as _ai_request_model
from backend.app.models import post as _post_model
from backend.app.models import user as _user_model


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="W16 Sprint API Auth Security", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoginRateLimitMiddleware)
register_error_handlers(app)
app.include_router(posts_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(ai_requests_router, prefix="/api/v1")
