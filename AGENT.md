# Repository Agent Notes

## Sprint Source Of Truth

This repository has pivoted from the original AI knowledge-board concept to the
**AI 생활지원 매칭 보드** concept.

Current product direction:

> A public-data based public support-information board plus a private AI
> matching flow. Users can browse support/facility cards publicly, then enter
> their own situation privately to find relevant welfare policies, youth
> support, public facilities, and living-support infrastructure.

`docs2/ai_knowledge_board_sprint_plan.md` remains useful as the historical
sprint-operation document, but new implementation and documentation decisions
should prioritize the AI 생활지원 매칭 보드 pivot.

Before planning, implementing, or documenting any sprint task:

1. Read `docs3/pivot-3/mvp-direction-and-data-plan.md` first for current product direction.
2. Treat the AI 생활지원 매칭 보드 pivot as the current product source of truth.
3. Use `docs2/ai_knowledge_board_sprint_plan.md` only for historical sprint order and learning context, not as the current product domain.
4. If a user request conflicts with the pivot direction, explain the conflict and confirm the decision before changing scope.
5. Keep sprint implementation records aligned with the active pivot terminology and sprint boundaries.
6. Use `docs3/**` for pivot implementation/decision records unless the user explicitly asks for another location. Keep older `docs2/**` sprint records as historical learning material.

## Domain Mapping Rule

When working on this repository after the pivot, interpret existing board
entities as follows:

1. Public `Post` means a support card, public facility card, or AI/admin-curated public information card.
2. Private `Post` with `post_type=case` means a saved private matching request, not a public board article.
3. `Comment` is disabled by default for both public cards and private matching requests. Re-enable it only after an explicit product decision.
4. `Tag` means practical matching metadata such as `청년`, `주거`, `취업`, `서울`, `마포구`, `저소득`, `장애`, or `노인`.
5. `RAG` means using the user's private situation as a query to search only public support/facility cards. Do not put private consultation text into the shared vector index.
6. `MCP` means retrieving public-data or policy-source references.
7. `Agent` means generating application-likelihood notes, missing conditions, checklists, and follow-up questions from private user input plus public data.

## Implementation Direction Rule

Prefer a fast pivot that reuses the existing application structure:

1. Reuse the current CRUD, Auth, Comment, Tag, Search, Paging, RAG, and MCP structure as much as possible.
2. Do not introduce dedicated policy/facility tables first unless the user explicitly asks for that larger redesign.
3. The default data-model direction is to add minimal fields to `Post`, such as `post_type`, `region`, `source_name`, `source_url`, and `source_external_id`.
4. Public-data import should use a `data-bot` author plus an import script as the default approach. Imported rows should default to `post_type=policy` or `post_type=facility`, `visibility=public`, `comment_policy=none`, and `rag_scope=public`.
5. Stack Overflow MCP search is no longer the default product direction after the pivot; replace it with a public-data or policy-source provider when implementing MCP work.
6. For bulk public-data loading, avoid creating posts one-by-one through the normal UI flow if that would trigger slow per-row work unnecessarily; prefer import/batch-oriented code with clear embedding behavior.
7. Private matching requests should default to `post_type=case`, `visibility=private`, `comment_policy=none`, and `rag_scope=excluded`.

## UI Direction Rule

The UI should feel like a practical public-service portal rather than a dark
blog-style developer board:

1. Prefer a bright government/public-institution tone with white or light-gray surfaces and restrained blue/teal accents.
2. Prefer terms like `지원 정보`, `지원 카드`, `시설 카드`, `AI 지원 찾기`, `내 상담 기록`, `공공데이터 참고자료`, and `관련 지원/시설` over generic `게시글` wording.
3. Users may browse support/facility cards without logging in.
4. Login is still required for saving private matching requests, viewing `내 상담 기록`, likes, and AI assistance flows that call protected APIs.
5. The primary MVP navigation should distinguish `지원 정보`, `AI 지원 찾기`, and `내 상담 기록` so users do not confuse public cards with private requests.

## Learning Record Rule

This repository uses implementation records as study material. When writing or updating `docs2/**/implementation-record.md` or step-specific implementation records:

1. Mermaid diagram step numbers must match the explanation numbers below the diagram exactly.
2. Do not use Mermaid `autonumber` if the written explanation will group or omit steps.
3. Preserve the requested Mermaid diagram type. If the user asked for a sequence diagram, do not change it to a flowchart.
4. In sequence diagrams, do not number participants/layers. Number only meaningful messages that move between different layers.
5. Do not give numbered steps to self-calls or tiny internal sub-steps unless they are also listed as separate explanation items.
6. Each numbered explanation item must include the file path and function/class the learner should inspect.
7. Keep the flow linear enough that a learner can read the diagram, then open the listed code in the same order.
8. If a diagram has 8 numbered messages, the explanation below it must also have exactly 8 numbered items.
