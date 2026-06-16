import { useState } from "react";

import type { Post, RelatedPostsState } from "../types";

interface RelatedPostsPanelProps {
  state: RelatedPostsState;
}

export function shouldShowRelatedPostsPanel(state: RelatedPostsState) {
  return state.isLoading || state.items.length > 0;
}

export function RelatedPostsPanel({ state }: RelatedPostsPanelProps) {
  const [previewPost, setPreviewPost] = useState<Post | null>(null);
  const [previewStatus, setPreviewStatus] = useState<{
    postId: number | null;
    isLoading: boolean;
    errorText: string;
  }>({
    postId: null,
    isLoading: false,
    errorText: "",
  });

  if (!shouldShowRelatedPostsPanel(state)) {
    return null;
  }

  async function openPostPreview(postId: number) {
    setPreviewPost(null);
    setPreviewStatus({ postId, isLoading: true, errorText: "" });
    try {
      const response = await fetch(`/api/v1/posts/${postId}`, {
        credentials: "include",
      });
      const data = (await response.json()) as Post;
      if (!response.ok) {
        throw new Error("지원 카드 상세를 불러오지 못했습니다.");
      }
      setPreviewPost(data);
      setPreviewStatus({ postId, isLoading: false, errorText: "" });
    } catch {
      setPreviewStatus({
        postId,
        isLoading: false,
        errorText: "지원 카드 상세를 불러오지 못했습니다.",
      });
    }
  }

  function closePostPreview() {
    setPreviewPost(null);
    setPreviewStatus({ postId: null, isLoading: false, errorText: "" });
  }

  const shouldShowPreview = previewPost || previewStatus.isLoading || previewStatus.errorText;

  return (
    <aside className="related-panel" aria-label="관련 지원과 시설 추천">
      <div className="related-panel-head">
        <p className="eyebrow">RAG</p>
        <h3>관련 지원/시설</h3>
      </div>

      {state.isLoading ? <p className="related-loading">관련 지원을 찾는 중</p> : null}

      {state.items.length > 0 ? (
        <div className="related-list">
          {state.items.map((post) => (
            <article
              className="related-card"
              key={post.post_id}
              role="button"
              tabIndex={0}
              onClick={() => void openPostPreview(post.post_id)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  void openPostPreview(post.post_id);
                }
              }}
            >
              <div className="related-card-title">
                <strong>{post.title}</strong>
                <span>{Math.round(post.similarity * 100)}%</span>
              </div>
              <p className={post.summary ? "related-summary" : undefined}>
                {post.summary || post.content_preview}
              </p>
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

      {shouldShowPreview ? (
        <div className="related-preview-backdrop" role="dialog" aria-modal="true">
          <article className="related-preview-modal">
            <div className="section-heading compact-heading">
              <div>
                <p className="eyebrow">Related Support</p>
                <h2>{previewPost?.title || "지원 카드 불러오는 중"}</h2>
              </div>
              <button className="ghost-button" type="button" onClick={closePostPreview}>
                닫기
              </button>
            </div>

            {previewStatus.isLoading ? <p className="muted-text">상세 내용을 불러오는 중입니다.</p> : null}
            {previewStatus.errorText ? <p className="muted-text">{previewStatus.errorText}</p> : null}
            {previewPost ? (
              <div className="related-preview-content">
                <div className="card-tags">
                  {previewPost.tags.map((tag) => (
                    <span key={tag}>#{tag}</span>
                  ))}
                </div>
                <p>{previewPost.content}</p>
                <div className="card-meta">
                  <span>{previewPost.source_name || `by ${previewPost.author_display_name}`}</span>
                  {previewPost.region ? <span>{previewPost.region}</span> : null}
                </div>
              </div>
            ) : null}
          </article>
        </div>
      ) : null}
    </aside>
  );
}
