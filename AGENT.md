# Repository Agent Notes

## Sprint Source Of Truth

This repository's sprint work is based on `docs2/ai_knowledge_board_sprint_plan.md`.

Before planning, implementing, or documenting any sprint task:

1. Read `docs2/ai_knowledge_board_sprint_plan.md` first.
2. Treat that document as the current source of truth for sprint scope, order, and intent.
3. If the user request appears to conflict with that plan, explain the conflict and confirm the decision before changing scope.
4. Keep sprint implementation records aligned with the plan's terminology and sprint boundaries.
5. Prefer `docs2/**` as the current sprint documentation area unless the user explicitly asks for another location.

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
