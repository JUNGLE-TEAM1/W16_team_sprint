from fastapi import APIRouter

from backend.app.api.dependencies import TagServiceDependency
from backend.app.schemas.tag import TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(service: TagServiceDependency) -> list[TagRead]:
    return service.list()
