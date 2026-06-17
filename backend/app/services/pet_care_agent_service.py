from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol

from backend.app.core.config import settings
from backend.app.schemas.ai import PetCareAdviceRequest, PetCareHospitalCandidate
from backend.app.services.mcp_service import FIND_NEARBY_ANIMAL_HOSPITALS_TOOL, McpService

HOSPITAL_GUIDANCE_KEYWORDS = (
    "병원",
    "응급",
    "호흡곤란",
    "숨을 못",
    "숨쉬기",
    "출혈",
    "피가",
    "피를",
    "경련",
    "발작",
    "의식",
    "쓰러",
    "반복 구토",
    "구토가 계속",
    "설사가 계속",
    "심한 통증",
    "걷지 못",
    "다리를 못",
)


@dataclass(frozen=True)
class PetCareAgentResult:
    hospital_candidates: list[PetCareHospitalCandidate] = field(default_factory=list)
    hospital_guidance_note: str | None = None


class PetCareAgentDecisionProvider(Protocol):
    def should_search_hospitals(self, payload: PetCareAdviceRequest) -> bool:
        raise NotImplementedError


class OpenAIPetCareAgentDecisionProvider:
    def __init__(
        self,
        api_key: str | None = settings.openai_api_key,
        model: str = settings.pet_care_advice_model,
    ) -> None:
        self.api_key = api_key
        self.model = model

    def should_search_hospitals(self, payload: PetCareAdviceRequest) -> bool:
        if not self.api_key:
            return False

        try:
            from openai import OpenAI
        except ImportError:
            return False

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            input="\n".join(
                [
                    "다음 반려견 상담 질문에 가까운 동물병원 후보 검색이 필요한지 판단한다.",
                    "응급 가능성, 병원 방문 여부 질문, 직접 진료가 필요한 증상일 때만 true다.",
                    '반드시 JSON 객체만 반환한다. 예: {"needs_hospital_search": true}',
                    f"title: {payload.title}",
                    f"content: {payload.content}",
                    f"tags: {', '.join(payload.tags)}",
                ]
            ),
            max_output_tokens=80,
        )
        return self._parse_decision(self._extract_output_text(response))

    @staticmethod
    def _extract_output_text(response: object) -> str:
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

    @staticmethod
    def _parse_decision(output_text: str) -> bool:
        stripped = output_text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        data = json.loads(stripped)
        return bool(data.get("needs_hospital_search")) if isinstance(data, dict) else False


class PetCareAgentService:
    def __init__(
        self,
        mcp_service: McpService | None = None,
        decision_provider: PetCareAgentDecisionProvider | None = None,
    ) -> None:
        self.mcp_service = mcp_service
        self.decision_provider = decision_provider

    def run(self, payload: PetCareAdviceRequest) -> PetCareAgentResult:
        if not self._needs_hospital_guidance(payload):
            if not self._llm_needs_hospital_guidance(payload):
                return PetCareAgentResult()

        location_region = (payload.location_region or "").strip()
        if not location_region:
            return PetCareAgentResult(
                hospital_guidance_note=(
                    "가까운 동물병원 후보가 필요하면 질문에 지역을 추가해 주세요. 예: 서울 마포구"
                )
            )

        if self.mcp_service is None:
            return PetCareAgentResult(
                hospital_guidance_note="현재 주변 동물병원 검색 도구를 사용할 수 없습니다."
            )

        try:
            response = self.mcp_service.handle(
                {
                    "jsonrpc": "2.0",
                    "id": "pet-care-agent-hospital-search",
                    "method": "tools/call",
                    "params": {
                        "name": FIND_NEARBY_ANIMAL_HOSPITALS_TOOL,
                        "arguments": {
                            "region_text": location_region,
                            "radius_meters": 5000,
                            "limit": 3,
                        },
                    },
                }
            )
        except Exception:
            return PetCareAgentResult(
                hospital_guidance_note="주변 동물병원 후보를 불러오지 못했습니다."
            )

        if response.get("error"):
            return PetCareAgentResult(
                hospital_guidance_note="주변 동물병원 후보를 불러오지 못했습니다."
            )

        structured = response.get("result", {}).get("structuredContent", {})
        items = structured.get("items", [])
        if not isinstance(items, list) or not items:
            return PetCareAgentResult(
                hospital_guidance_note="입력한 지역 주변에서 표시할 동물병원 후보를 찾지 못했습니다."
            )

        candidates: list[PetCareHospitalCandidate] = []
        for item in items[:3]:
            if isinstance(item, dict):
                candidates.append(PetCareHospitalCandidate.model_validate(item))

        return PetCareAgentResult(hospital_candidates=candidates)

    @staticmethod
    def _needs_hospital_guidance(payload: PetCareAdviceRequest) -> bool:
        text = " ".join(
            [
                payload.title,
                payload.content,
                " ".join(payload.tags),
                payload.department or "",
            ]
        ).lower()
        return any(keyword.lower() in text for keyword in HOSPITAL_GUIDANCE_KEYWORDS)

    def _llm_needs_hospital_guidance(self, payload: PetCareAdviceRequest) -> bool:
        if self.decision_provider is None:
            return False
        try:
            return self.decision_provider.should_search_hospitals(payload)
        except Exception:
            return False
