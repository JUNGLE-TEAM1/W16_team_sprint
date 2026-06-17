from __future__ import annotations

import json
from typing import Protocol

from fastapi import status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.errors import AppError
from backend.app.repositories.knowledge_repository import KnowledgeRepository, KnowledgeSearchRow
from backend.app.repositories.pet_care_advice_repository import PetCareAdviceRepository
from backend.app.repositories.post_repository import PostRepository
from backend.app.schemas.ai import (
    PetCareAdviceRequest,
    PetCareAdviceResponse,
    PetCareHospitalCandidate,
    PetCareSourceChunk,
)
from backend.app.services.embedding_service import EmbeddingProvider
from backend.app.services.knowledge_rag_index import KnowledgeVectorIndex
from backend.app.services.pet_care_agent_service import PetCareAgentService

PET_CARE_SOURCE_LIMIT = 5
PET_CARE_MIN_SIMILARITY = 0.0
PET_CARE_SAFETY_NOTE = (
    "이 답변은 AIHub 반려견 말뭉치를 바탕으로 한 참고 정보이며 확정 진단이 아닙니다. "
    "호흡곤란, 반복 구토, 경련, 의식 저하, 심한 통증, 출혈, 증상 악화 또는 지속 증상이 있으면 즉시 수의사에게 상담하세요."
)


class PetCareAdviceProvider(Protocol):
    def generate(
        self,
        payload: PetCareAdviceRequest,
        sources: list[KnowledgeSearchRow],
        hospital_candidates: list[PetCareHospitalCandidate],
        hospital_guidance_note: str | None,
    ) -> tuple[str, list[str]]:
        raise NotImplementedError


class OpenAIPetCareAdviceProvider:
    def __init__(
        self,
        api_key: str | None = settings.openai_api_key,
        model: str = settings.pet_care_advice_model,
        max_output_tokens: int = settings.pet_care_advice_max_output_tokens,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.max_output_tokens = max_output_tokens

    def generate(
        self,
        payload: PetCareAdviceRequest,
        sources: list[KnowledgeSearchRow],
        hospital_candidates: list[PetCareHospitalCandidate],
        hospital_guidance_note: str | None,
    ) -> tuple[str, list[str]]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input=self._build_prompt(payload, sources, hospital_candidates, hospital_guidance_note),
            max_output_tokens=self.max_output_tokens,
        )
        return self._parse_output(self._extract_output_text(response))

    def _build_prompt(
        self,
        payload: PetCareAdviceRequest,
        sources: list[KnowledgeSearchRow],
        hospital_candidates: list[PetCareHospitalCandidate],
        hospital_guidance_note: str | None,
    ) -> str:
        source_blocks = []
        for index, source in enumerate(sources, start=1):
            source_blocks.append(
                "\n".join(
                    [
                        f"source_index: {index}",
                        f"source_kind: {source.source_kind}",
                        f"title: {source.title}",
                        f"department: {source.department or ''}",
                        f"disease: {source.disease or ''}",
                        f"life_cycle: {source.life_cycle or ''}",
                        f"question: {source.question or ''}",
                        f"answer: {source.answer or ''}",
                        f"content: {source.content[:1800]}",
                    ]
                )
            )

        return "\n\n".join(
            [
                "너는 반려견 건강/성장/질병 상담 보드의 AI 상담 도우미다.",
                "제공된 AIHub 근거만 바탕으로 한국어 답변과 보호자 행동 계획을 작성한다.",
                "확정 진단, 처방, 약물 용량 지시는 하지 않는다.",
                "응급 증상, 악화, 지속 증상은 수의사 상담을 권장한다.",
                '반드시 JSON 객체만 반환한다. 예: {"answer":"...","action_plan":["..."]}',
                "사용자 질문:",
                f"title: {payload.title}",
                f"content: {payload.content}",
                f"tags: {', '.join(payload.tags)}",
                f"life_cycle: {payload.life_cycle or ''}",
                f"department: {payload.department or ''}",
                f"location_region: {payload.location_region or ''}",
                "검색된 AIHub 근거:",
                "\n\n---\n\n".join(source_blocks),
                "주변 동물병원 후보:",
                self._build_hospital_prompt_block(hospital_candidates, hospital_guidance_note),
            ]
        )

    @staticmethod
    def _build_hospital_prompt_block(
        hospital_candidates: list[PetCareHospitalCandidate],
        hospital_guidance_note: str | None,
    ) -> str:
        if hospital_candidates:
            return "\n".join(
                [
                    f"- {candidate.name} / {candidate.road_address or candidate.address or ''} / "
                    f"{candidate.phone or '전화번호 미상'} / {candidate.distance_meters or ''}m"
                    for candidate in hospital_candidates
                ]
            )
        return hospital_guidance_note or "주변 동물병원 후보 없음"

    def _extract_output_text(self, response: object) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str):
            return output_text

        chunks: list[str] = []
        for output_item in getattr(response, "output", []) or []:
            for content_item in getattr(output_item, "content", []) or []:
                text = getattr(content_item, "text", None)
                if isinstance(text, str):
                    chunks.append(text)
        return "\n".join(chunks)

    def _parse_output(self, output_text: str) -> tuple[str, list[str]]:
        data = json.loads(self._strip_code_fence(output_text))
        if not isinstance(data, dict):
            raise ValueError("pet-care advice output must be a JSON object")
        answer = data.get("answer")
        action_plan = data.get("action_plan")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("answer is required")
        if not isinstance(action_plan, list):
            action_plan = []
        normalized_actions = [
            str(item).strip()
            for item in action_plan
            if str(item).strip()
        ][:8]
        return answer.strip()[:3000], normalized_actions

    @staticmethod
    def _strip_code_fence(value: str) -> str:
        stripped = value.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return stripped


class PetCareAdviceService:
    def __init__(
        self,
        db: Session,
        repository: KnowledgeRepository,
        rag_index: KnowledgeVectorIndex,
        embedding_provider: EmbeddingProvider,
        posts: PostRepository | None = None,
        advices: PetCareAdviceRepository | None = None,
        advice_provider: PetCareAdviceProvider | None = None,
        agent: PetCareAgentService | None = None,
        limit: int = PET_CARE_SOURCE_LIMIT,
        min_similarity: float = PET_CARE_MIN_SIMILARITY,
    ) -> None:
        self.db = db
        self.repository = repository
        self.rag_index = rag_index
        self.embedding_provider = embedding_provider
        self.posts = posts
        self.advices = advices
        self.advice_provider = advice_provider
        self.agent = agent
        self.limit = limit
        self.min_similarity = min_similarity

    def create_advice(self, payload: PetCareAdviceRequest) -> PetCareAdviceResponse:
        query_text = self._build_query_text(payload)
        try:
            sources = self.rag_index.find_related_chunks(
                query_text=query_text,
                repository=self.repository,
                limit=self.limit,
                min_similarity=self.min_similarity,
            )
        except Exception as exc:
            raise AppError(
                code="PET_CARE_RAG_FAILED",
                message="반려견 케어 지식 검색에 실패했습니다.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details={},
            ) from exc
        sources = self._prioritize_sources(payload, sources)
        agent_result = self.agent.run(payload) if self.agent is not None else None
        hospital_candidates = agent_result.hospital_candidates if agent_result else []
        hospital_guidance_note = agent_result.hospital_guidance_note if agent_result else None

        answer: str
        action_plan: list[str]
        if self.advice_provider is not None and sources:
            try:
                answer, action_plan = self.advice_provider.generate(
                    payload,
                    sources,
                    hospital_candidates,
                    hospital_guidance_note,
                )
            except Exception:
                answer, action_plan = self._fallback_advice(sources, hospital_candidates, hospital_guidance_note)
        else:
            answer, action_plan = self._fallback_advice(sources, hospital_candidates, hospital_guidance_note)

        return PetCareAdviceResponse(
            answer=answer,
            action_plan=action_plan,
            safety_note=PET_CARE_SAFETY_NOTE,
            sources=[self._to_source_chunk(source) for source in sources],
            hospital_candidates=hospital_candidates,
        )

    def get_stored_advice(self, post_id: int, viewer_id: int | None = None) -> PetCareAdviceResponse | None:
        self._get_viewable_post(post_id, viewer_id)
        if self.advices is None:
            return None
        advice = self.advices.get_by_post_id(post_id)
        if advice is None:
            return None
        return self._stored_to_response(advice)

    def create_advice_for_post(self, post_id: int, viewer_id: int) -> PetCareAdviceResponse:
        post = self._get_viewable_post(post_id, viewer_id)
        if self.advices is None:
            raise AppError(
                code="PET_CARE_ADVICE_STORAGE_UNAVAILABLE",
                message="AI 답변 저장소를 사용할 수 없습니다.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details={},
            )

        existing = self.advices.get_by_post_id(post.id)
        if existing is not None and existing.status != "stale":
            return self._stored_to_response(existing)

        response = self.create_advice(
            PetCareAdviceRequest(
                title=post.title,
                content=post.content,
                tags=post.tags,
                location_region=post.region,
            )
        )
        saved = self.advices.upsert_completed(post_id=post.id, response=response)
        self.db.commit()
        return self._stored_to_response(saved)

    def _build_query_text(self, payload: PetCareAdviceRequest) -> str:
        return "\n".join(
            [
                f"title: {payload.title}",
                f"content: {payload.content}",
                f"tags: {', '.join(payload.tags)}",
                f"life_cycle: {payload.life_cycle or ''}",
                f"department: {payload.department or ''}",
                f"location_region: {payload.location_region or ''}",
            ]
        )

    def _fallback_advice(
        self,
        sources: list[KnowledgeSearchRow],
        hospital_candidates: list[PetCareHospitalCandidate],
        hospital_guidance_note: str | None,
    ) -> tuple[str, list[str]]:
        hospital_sentence = self._hospital_sentence(hospital_candidates, hospital_guidance_note)
        if not sources:
            return (
                "현재 질문과 충분히 유사한 AIHub 근거를 찾지 못했습니다. 증상, 기간, 나이, 식욕, 활력, 배변 상태를 더 구체적으로 기록한 뒤 다시 질문해 주세요."
                + hospital_sentence,
                [
                    "증상이 언제 시작됐는지와 얼마나 자주 반복되는지 기록하세요.",
                    "식욕, 활력, 구토, 설사, 기침, 호흡 상태 변화를 함께 관찰하세요.",
                    "증상이 심하거나 지속되면 수의사에게 상담하세요.",
                ],
            )

        primary = sources[0]
        basis = primary.answer or primary.content[:600]
        answer = (
            f"가장 가까운 AIHub 근거는 '{primary.title}'입니다. "
            f"해당 근거에서는 다음 내용을 참고할 수 있습니다: {basis[:900]}"
            + hospital_sentence
        )
        return (
            answer,
            [
                "현재 증상과 기간, 반복 빈도, 식욕과 활력 변화를 기록하세요.",
                "관련 근거와 비교해 악화되거나 새 증상이 생기는지 확인하세요.",
                "호흡곤란, 반복 구토, 무기력, 통증 등 위험 신호가 있으면 병원에 문의하세요.",
            ],
        )

    @staticmethod
    def _hospital_sentence(
        hospital_candidates: list[PetCareHospitalCandidate],
        hospital_guidance_note: str | None,
    ) -> str:
        if hospital_candidates:
            return " 가까운 동물병원 후보도 함께 확인해 주세요."
        if hospital_guidance_note:
            return f" {hospital_guidance_note}"
        return ""

    def _prioritize_sources(
        self,
        payload: PetCareAdviceRequest,
        sources: list[KnowledgeSearchRow],
    ) -> list[KnowledgeSearchRow]:
        if not sources:
            return sources

        requested_department = (payload.department or "").strip()
        requested_life_cycle = (payload.life_cycle or "").strip()
        tags = [tag.strip() for tag in payload.tags if tag.strip()]

        if not requested_department and not requested_life_cycle and not tags:
            return sources

        def score(source: KnowledgeSearchRow) -> tuple[float, float]:
            metadata_score = 0.0
            if requested_department and source.department == requested_department:
                metadata_score += 3.0
            if requested_life_cycle and source.life_cycle == requested_life_cycle:
                metadata_score += 2.0

            searchable_text = " ".join(
                [
                    source.title,
                    source.question or "",
                    source.answer or "",
                    source.content,
                    source.disease or "",
                    source.department or "",
                    source.life_cycle or "",
                ]
            )
            metadata_score += sum(0.25 for tag in tags if tag in searchable_text)
            return metadata_score, source.similarity

        return sorted(sources, key=score, reverse=True)

    def _to_source_chunk(self, source: KnowledgeSearchRow) -> PetCareSourceChunk:
        return PetCareSourceChunk(
            chunk_id=source.chunk_id,
            document_id=source.document_id,
            title=source.title,
            content_preview=source.content[:500],
            question=source.question,
            answer_preview=source.answer[:500] if source.answer else None,
            department=source.department,
            disease=source.disease,
            life_cycle=source.life_cycle,
            source_kind=source.source_kind,
            split=source.split,
            similarity=source.similarity,
        )

    def _get_viewable_post(self, post_id: int, viewer_id: int | None):
        if self.posts is None:
            raise AppError(
                code="POST_REPOSITORY_UNAVAILABLE",
                message="상담 질문을 확인할 수 없습니다.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details={},
            )
        post = self.posts.get(post_id)
        if post is None or not self._can_view(post, viewer_id):
            raise AppError(
                code="POST_NOT_FOUND",
                message="상담 질문을 찾을 수 없습니다.",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"post_id": post_id},
            )
        return post

    @staticmethod
    def _can_view(post, viewer_id: int | None) -> bool:  # noqa: ANN001
        if post.visibility == "public":
            return True
        return viewer_id is not None and post.author_id == viewer_id

    @staticmethod
    def _stored_to_response(advice) -> PetCareAdviceResponse:  # noqa: ANN001
        return PetCareAdviceResponse(
            id=advice.id,
            post_id=advice.post_id,
            status=advice.status,
            generated_at=advice.generated_at,
            answer=advice.answer,
            action_plan=list(advice.action_plan or []),
            safety_note=advice.safety_note,
            sources=[PetCareSourceChunk(**source) for source in advice.sources or []],
            hospital_candidates=[
                PetCareHospitalCandidate(**hospital)
                for hospital in advice.hospital_candidates or []
            ],
        )
