from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.app.api.v1.ai import router as ai_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.posts import router as posts_router
from backend.app.api.v1.security import router as security_router
from backend.app import models
from backend.app.core.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.core.rate_limit import SimpleRateLimitMiddleware
from backend.app.db.base import Base
from backend.app.db.seeds import seed_demo_users
from backend.app.db.session import engine


def create_lifespan(database_engine=engine):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if database_engine.dialect.name == "postgresql":
            with database_engine.begin() as connection:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=database_engine)
        seed_demo_users(database_engine)
        yield

    return lifespan


def create_app(database_engine=engine) -> FastAPI:
    app = FastAPI(
        title="Sprint 1 API Data Flow",
        lifespan=create_lifespan(database_engine),
    )
    register_error_handlers(app)
    app.add_middleware(SimpleRateLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(ai_router, prefix="/api/v1")
    app.include_router(posts_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(security_router, prefix="/api/v1")
    return app


app = create_app()
