from pydantic import BaseModel, Field


class AgentWritingAssistRequest(BaseModel):
    title: str = Field(default="", max_length=120)
    content: str = Field(default="", max_length=5000)
    tag_names: list[str] = Field(default_factory=list, max_length=8)
    intent: str = Field(default="생활지원 상담 케이스와 태그를 추천해 주세요.", max_length=200)


class AgentWritingAssistResponse(BaseModel):
    provider: str
    model: str
    suggested_title: str
    suggested_content: str
    suggested_tag_names: list[str]
    outline: list[str]
    next_questions: list[str]
    agent_steps: list[str]
    confidence: float
