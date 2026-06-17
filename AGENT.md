# Repository Agent Notes

## Sprint Source Of Truth

This repository has pivoted from the public life-support matching board to the
**AI 반려견 케어 상담 보드** concept.

Current product direction:

> A public pet-care consultation board where users post dog health, growth, and
> disease questions. The AI assistant searches the AIHub dog growth/disease
> corpus with RAG, then returns reference-based advice, action steps, and source
> snippets.

Before planning, implementing, or documenting new work:

1. Treat the AI 반려견 케어 상담 보드 pivot as the current source of truth.
2. Use `docs3/pet-care-pivot/**` for current pivot records.
3. Keep older `docs2/**` and `docs3/pivot-*` records as historical material only.
4. If a user request conflicts with the pet-care pivot, explain the conflict and confirm the scope before changing direction.
5. Do not present AIHub data as public board posts; it is a separate RAG knowledge base.

## Domain Mapping Rule

Interpret existing entities under the pet-care pivot as follows:

1. `Post` means a public pet-care consultation question.
2. `Comment` means a public reply, added experience, or follow-up question on a consultation.
3. `Tag` means practical pet-care metadata such as `기침`, `구토`, `피부`, `안과`, `자견`, `성견`, `노령견`, or `예방접종`.
4. `RAG` means searching AIHub dog Q&A and source corpus chunks, not searching other user posts.
5. `Agent` means generating reference-based advice, hospital-visit criteria, owner action checklists, and follow-up questions.
6. `MCP` means JSON-RPC tools backed by real external pet-care or location providers. The current default is Kakao Local region geocoding and nearby animal-hospital search.

## Safety Rule

Pet-care AI output must be framed as reference information, not a medical
diagnosis.

1. Do not claim a definitive disease diagnosis.
2. Always include a fixed safety note that emergency, worsening, or persistent symptoms require veterinary consultation.
3. Prefer practical next actions: observe, record symptoms, contact a clinic, prepare questions, and bring relevant history.
4. Show the AIHub source snippets used so the user can inspect the basis of the response.

## Implementation Direction Rule

Prefer a fast pivot that reuses the existing application where it still fits:

1. Reuse the current CRUD, Auth, Comment, Tag, Search, Paging, Like, and detail-page structure.
2. Public question posts should use `post_type=case`, `visibility=public`, `comment_policy=public`, and `rag_scope=excluded`.
3. AIHub data must be stored in dedicated knowledge tables, not in `posts`.
4. The AIHub import script should read local zip files directly and must be idempotent.
5. AIHub original data files should not be committed to the repo.
6. Production embedding uses OpenAI; tests use mock embeddings.
7. If embedding fails during import, store the chunk with `status=failed` so it can be retried later.

## UI Direction Rule

The UI should feel like a clean pet-care consultation board:

1. Use `AI 반려견 케어 상담 보드` as the service name.
2. Prefer terms like `상담 질문`, `질문 작성`, `내 질문`, `AI 답변`, `행동 계획`, and `참고 근거`.
3. Remove life-support terms such as `지원 카드`, `시설 카드`, `지원 정보`, and `공공데이터 참고자료` from current UI.
4. Users may browse public questions and AI answers without logging in.
5. Login is required for creating questions, comments, likes, and generating AI advice.

## Learning Record Rule

This repository uses implementation records as study material. When writing or updating implementation records:

1. Mermaid diagram step numbers must match the explanation numbers below the diagram exactly.
2. Do not use Mermaid `autonumber` if the written explanation will group or omit steps.
3. Preserve the requested Mermaid diagram type. If the user asked for a sequence diagram, do not change it to a flowchart.
4. In sequence diagrams, do not number participants/layers. Number only meaningful messages that move between different layers.
5. Do not give numbered steps to self-calls or tiny internal sub-steps unless they are also listed as separate explanation items.
6. Each numbered explanation item must include the file path and function/class the learner should inspect.
7. Keep the flow linear enough that a learner can read the diagram, then open the listed code in the same order.
8. If a diagram has 8 numbered messages, the explanation below it must also have exactly 8 numbered items.
