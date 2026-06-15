from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app import models  # noqa: F401
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.comments import router as comments_router
from backend.app.api.v1.posts import router as posts_router
from backend.app.api.v1.tags import router as tags_router
from backend.app.core.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.db.base import Base
from backend.app.db.schema import ensure_development_schema
from backend.app.db.session import engine

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    ensure_development_schema(engine)
    yield


app = FastAPI(title="W16 Team Sprint API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")


@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
