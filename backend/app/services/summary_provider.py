from __future__ import annotations

from typing import Protocol

import httpx

from backend.app.core.config import settings


class SummaryProvider(Protocol):
    def summarize(self, *, query: str, contexts: list[dict]) -> str:
        pass


class OllamaSummaryProvider:
    def __init__(
        self,
        *,
        base_url: str = settings.ollama_base_url,
        model: str = settings.ollama_model,
        timeout_seconds: float = settings.ollama_timeout_seconds,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def summarize(self, *, query: str, contexts: list[dict]) -> str:
        prompt = self._build_prompt(query=query, contexts=contexts)
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        summary = str(body.get("response", "")).strip()
        if not summary:
            raise RuntimeError("Ollama returned an empty summary")
        return summary

    def _build_prompt(self, *, query: str, contexts: list[dict]) -> str:
        context_lines = []
        for index, item in enumerate(contexts, start=1):
            context_lines.append(
                "\n".join(
                    [
                        f"{index}. 제목: {item['title']}",
                        f"   태그: {', '.join(item['tags']) if item['tags'] else '없음'}",
                        f"   유사도: {item['similarity']:.2f}",
                        f"   내용: {item['preview']}",
                    ]
                )
            )
        context_text = "\n".join(context_lines) if context_lines else "유사 게시글 없음"
        return (
            "너는 게시글 작성 중 중복 가능성을 알려주는 한국어 도우미다.\n"
            "입력 중인 글과 유사 게시글 목록을 보고 2문장 이내로 요약해라.\n"
            "유사도가 높은 글이 있으면 사용자가 확인해야 한다고 말해라.\n\n"
            f"입력 글:\n{query}\n\n"
            f"유사 게시글:\n{context_text}\n"
        )


class FakeSummaryProvider:
    def __init__(self, summary: str = "유사 게시글 요약입니다.") -> None:
        self.summary = summary

    def summarize(self, *, query: str, contexts: list[dict]) -> str:
        if not contexts:
            return "비슷한 게시글을 찾지 못했습니다."
        return self.summary
