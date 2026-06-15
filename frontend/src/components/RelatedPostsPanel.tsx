import type { RelatedPostsState } from "../types";

interface RelatedPostsPanelProps {
  state: RelatedPostsState;
}

export function shouldShowRelatedPostsPanel(state: RelatedPostsState) {
  return state.isLoading || state.items.length > 0;
}

export function RelatedPostsPanel({ state }: RelatedPostsPanelProps) {
  if (!shouldShowRelatedPostsPanel(state)) {
    return null;
  }

  return (
    <aside className="related-panel" aria-label="유사 게시글 추천">
      <div className="related-panel-head">
        <p className="eyebrow">RAG</p>
        <h3>유사 게시글</h3>
      </div>

      {state.isLoading ? <p className="related-loading">유사글 찾는 중</p> : null}

      {state.items.length > 0 ? (
        <div className="related-list">
          {state.items.map((post) => (
            <article className="related-card" key={post.post_id}>
              <div className="related-card-title">
                <strong>{post.title}</strong>
                <span>{Math.round(post.similarity * 100)}%</span>
              </div>
              <p>{post.content_preview}</p>
              {post.tags.length > 0 ? (
                <div className="card-tags">
                  {post.tags.map((tag) => (
                    <span key={tag}>#{tag}</span>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}
    </aside>
  );
}
