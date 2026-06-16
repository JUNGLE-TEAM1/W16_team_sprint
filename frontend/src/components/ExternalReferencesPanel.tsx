import type { ExternalReferencesState } from "../types";

interface ExternalReferencesPanelProps {
  state: ExternalReferencesState;
}

export function shouldShowExternalReferencesPanel(state: ExternalReferencesState) {
  return state.isLoading || state.errorText || state.items.length > 0;
}

export function ExternalReferencesPanel({ state }: ExternalReferencesPanelProps) {
  if (!shouldShowExternalReferencesPanel(state)) {
    return null;
  }

  return (
    <aside className="reference-panel" aria-label="외부 참고자료">
      <div className="related-panel-head">
        <p className="eyebrow">MCP</p>
        <h3>외부 참고자료</h3>
      </div>

      {state.isLoading ? <p className="related-loading">참고자료 찾는 중</p> : null}
      {state.errorText ? <p className="reference-status">{state.errorText}</p> : null}

      {state.items.length > 0 ? (
        <div className="related-list">
          {state.items.map((reference) => (
            <article className="reference-card" key={reference.url || reference.title}>
              <div className="related-card-title">
                <strong>{reference.title}</strong>
                <span>{reference.source}</span>
              </div>
              <p>{reference.summary}</p>
              <div className="reference-meta">
                {typeof reference.answer_count === "number" ? (
                  <span>답변 {reference.answer_count}</span>
                ) : null}
                {typeof reference.score === "number" ? <span>점수 {reference.score}</span> : null}
                {reference.is_answered ? <span>채택 답변 있음</span> : null}
              </div>
              {reference.tags.length > 0 ? (
                <div className="card-tags">
                  {reference.tags.map((tag) => (
                    <span key={tag}>#{tag}</span>
                  ))}
                </div>
              ) : null}
              {reference.url ? (
                <a className="reference-link" href={reference.url} target="_blank" rel="noreferrer">
                  원문 열기
                </a>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}
    </aside>
  );
}
