from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.comment_repository import CommentRepository
from backend.app.repositories.embedding_repository import PostEmbeddingRepository
from backend.app.repositories.knowledge_repository import KnowledgeRepository
from backend.app.repositories.pet_care_advice_repository import PetCareAdviceRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.repositories.tag_repository import TagRepository
from backend.app.services.comment_service import CommentService
from backend.app.services.embedding_service import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    PostEmbeddingService,
)
from backend.app.services.kakao_local_service import KakaoLocalProvider, LocationSearchProvider
from backend.app.services.langchain_rag_index import LangChainPostVectorIndex
from backend.app.services.knowledge_rag_index import KnowledgeVectorIndex
from backend.app.services.mcp_service import McpService
from backend.app.services.pet_care_agent_service import (
    OpenAIPetCareAgentDecisionProvider,
    PetCareAgentService,
)
from backend.app.services.pet_care_advice_service import (
    OpenAIPetCareAdviceProvider,
    PetCareAdviceProvider,
    PetCareAdviceService,
)
from backend.app.services.post_service import PostService
from backend.app.services.rag_service import RagService
from backend.app.services.rag_summary_service import OpenAIRagSummaryProvider, RagSummaryProvider


def get_embedding_provider() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider()


def get_rag_summary_provider() -> RagSummaryProvider:
    return OpenAIRagSummaryProvider()


def get_pet_care_advice_provider() -> PetCareAdviceProvider:
    return OpenAIPetCareAdviceProvider()


def get_pet_care_agent_decision_provider() -> OpenAIPetCareAgentDecisionProvider:
    return OpenAIPetCareAgentDecisionProvider()


def get_location_search_provider() -> LocationSearchProvider:
    return KakaoLocalProvider()


def get_post_service(
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
) -> PostService:
    posts = PostRepository(db)
    tags = TagRepository(db)
    embeddings = PostEmbeddingRepository(db)
    pet_care_advices = PetCareAdviceRepository(db)
    embedding_service = PostEmbeddingService(embedding_provider)
    rag_index = LangChainPostVectorIndex(db=db, embedding_provider=embedding_provider)
    return PostService(
        db=db,
        posts=posts,
        tags=tags,
        embeddings=embeddings,
        pet_care_advices=pet_care_advices,
        embedding_service=embedding_service,
        rag_index=rag_index,
    )


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    posts = PostRepository(db)
    comments = CommentRepository(db)
    return CommentService(db=db, posts=posts, comments=comments)


def get_rag_service(
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
    summary_provider: RagSummaryProvider = Depends(get_rag_summary_provider),
) -> RagService:
    embedding_service = PostEmbeddingService(embedding_provider)
    rag_index = LangChainPostVectorIndex(db=db, embedding_provider=embedding_provider)
    return RagService(
        rag_index=rag_index,
        embedding_service=embedding_service,
        summary_provider=summary_provider,
    )


def get_mcp_service(
    location_search: LocationSearchProvider = Depends(get_location_search_provider),
) -> McpService:
    return McpService(location_search=location_search)


def get_pet_care_advice_service(
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
    advice_provider: PetCareAdviceProvider = Depends(get_pet_care_advice_provider),
    mcp_service: McpService = Depends(get_mcp_service),
    agent_decision_provider: OpenAIPetCareAgentDecisionProvider = Depends(get_pet_care_agent_decision_provider),
) -> PetCareAdviceService:
    repository = KnowledgeRepository(db)
    posts = PostRepository(db)
    advices = PetCareAdviceRepository(db)
    rag_index = KnowledgeVectorIndex(db=db, embedding_provider=embedding_provider)
    return PetCareAdviceService(
        db=db,
        repository=repository,
        rag_index=rag_index,
        embedding_provider=embedding_provider,
        posts=posts,
        advices=advices,
        advice_provider=advice_provider,
        agent=PetCareAgentService(
            mcp_service=mcp_service,
            decision_provider=agent_decision_provider,
        ),
    )
