from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AiRequestCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class AiRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_id: int
    prompt: str
    result: str
    status: str
    created_at: datetime
