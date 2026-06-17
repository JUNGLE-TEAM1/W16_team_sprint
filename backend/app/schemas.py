from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AnnalsArticleOut(BaseModel):
    article_id: str
    title: str
    king: str | None
    reign_date: str | None
    date: str | None
    content: str
    official_url: str
    subject_classes: list[str]

    model_config = ConfigDict(from_attributes=True)


class AuthRequest(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=4, max_length=128)


class AuthUserOut(BaseModel):
    username: str


class PostCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    question: str = Field(min_length=5)
    username: str = Field(default="demo")


class PostUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=200)


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    username: str = Field(default="demo")


class DiscussionPrompt(BaseModel):
    message: str = Field(min_length=2, max_length=1000)


class RealtimeTurnRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=1000)
    search_query: str | None = Field(default=None, max_length=200)


class RealtimeTurnPlan(BaseModel):
    action: str
    reason: str
    search_query: str = ""
    events: list[dict] = Field(default_factory=list)
    evidence_article_ids: list[str] = Field(default_factory=list)


class VoiceSessionCreate(BaseModel):
    username: str = Field(default="demo", min_length=2, max_length=80)


class VoiceSessionOut(BaseModel):
    id: int
    post_id: int
    username: str
    created_at: datetime


class VoiceMessageCreate(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)
    route_action: str | None = Field(default=None, max_length=40)
    route_reason: str | None = Field(default=None, max_length=500)
    search_query: str | None = Field(default=None, max_length=240)
    evidence_article_ids: list[str] = Field(default_factory=list, max_length=20)


class VoiceMessageOut(BaseModel):
    id: int
    session_id: int
    post_id: int
    username: str
    role: str
    content: str
    route_action: str | None
    route_reason: str | None
    search_query: str | None
    evidence_article_ids: list[str]
    created_at: datetime


class CommentOut(BaseModel):
    id: int
    post_id: int
    username: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeleteResult(BaseModel):
    deleted_id: int


class PostListItem(BaseModel):
    id: int
    title: str
    question: str
    ai_summary: str
    suggested_tags: list[str]
    evidence_article_ids: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostListPage(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    size: int
    pages: int


class PostDetail(PostListItem):
    ai_interpretation: str
    agent_trace: list[dict]
    evidence_articles: list[AnnalsArticleOut]
    comments: list[CommentOut]


class SearchResult(BaseModel):
    query: str
    articles: list[AnnalsArticleOut]
