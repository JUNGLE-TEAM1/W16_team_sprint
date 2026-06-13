from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.v1.posts import router as posts_router
from backend.app.core.errors import register_error_handlers
from backend.app.db.base import Base
from backend.app.db.session import engine


def create_lifespan(database_engine=engine):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        Base.metadata.create_all(bind=database_engine)
        yield

    return lifespan


def create_app(database_engine=engine) -> FastAPI:
    app = FastAPI(
        title="Sprint 1 API Data Flow",
        lifespan=create_lifespan(database_engine),
    )
    register_error_handlers(app)
    app.include_router(posts_router, prefix="/api/v1")
    return app


app = create_app()
