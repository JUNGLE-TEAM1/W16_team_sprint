import { CARD_THEMES, SORT_TYPES } from "../constants/board";
import type { KeyboardEvent } from "react";
import type { FieldChangeHandler, PageMeta, Post, SearchState } from "../types";
import { excerpt, formatDate } from "../utils/postFormatting";

interface PostCardProps {
  post: Post;
  index: number;
  pageMeta: PageMeta;
  onSelectPost: (post: Post) => void;
}

function PostCard({ post, index, pageMeta, onSelectPost }: PostCardProps) {
  const cardNumber = String((pageMeta.page - 1) * pageMeta.size + index + 1).padStart(2, "0");

  function handleKeyDown(event: KeyboardEvent<HTMLElement>) {
    if (event.key === "Enter") {
      onSelectPost(post);
    }
  }

  return (
    <article
      className="post-card"
      tabIndex={0}
      onClick={() => onSelectPost(post)}
      onKeyDown={handleKeyDown}
    >
      <div className={`card-visual ${CARD_THEMES[index % CARD_THEMES.length]}`}>
        <span>{cardNumber}</span>
        <strong>{post.title.slice(0, 1).toUpperCase()}</strong>
      </div>
      <div className="card-body">
        <h3>{post.title}</h3>
        <p>{excerpt(post.content)}</p>
        <div className="card-tags">
          {(post.tags ?? []).map((tag) => (
            <span key={tag}>#{tag}</span>
          ))}
        </div>
        <div className="card-stats">
          <span>댓글 {post.comment_count ?? 0}개</span>
          <span>좋아요 {post.like_count ?? 0}개</span>
        </div>
        <div className="card-meta">
          <span>{formatDate(post.created_at)}</span>
          <span>by {post.author_display_name}</span>
        </div>
      </div>
    </article>
  );
}

export function PostList({
  posts,
  pageMeta,
  search,
  onSortChange,
  onOpenCompose,
  onSelectPost,
  onChangePage,
}: {
  posts: Post[];
  pageMeta: PageMeta;
  search: SearchState;
  onSortChange: FieldChangeHandler;
  onOpenCompose: () => void;
  onSelectPost: (post: Post) => void;
  onChangePage: (nextPage: number) => void;
}) {
  return (
    <section className="posts-section" aria-label="게시글 목록">
      <div className="section-heading list-heading">
        <div>
          <p className="eyebrow">Latest Posts</p>
          <h2>현재까지 작성된 게시글</h2>
        </div>
        <div className="section-actions">
          <span className="count-chip">
            {pageMeta.total}개 · {pageMeta.page}/{pageMeta.total_pages || 1} 페이지
          </span>
          <label className="sort-control">
            <span>정렬</span>
            <select name="sort" value={search.sort} onChange={onSortChange}>
              {SORT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>
          <button className="submit-button compact-button" type="button" onClick={onOpenCompose}>
            새 글 작성
          </button>
        </div>
      </div>

      {posts.length > 0 ? (
        <div className="post-grid">
          {posts.map((post, index) => (
            <PostCard
              key={post.id}
              post={post}
              index={index}
              pageMeta={pageMeta}
              onSelectPost={onSelectPost}
            />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <strong>조건에 맞는 게시글이 없습니다.</strong>
          <span>검색어 또는 태그 필터를 조정해보세요.</span>
        </div>
      )}

      <div className="pagination">
        <button
          className="pill-button"
          type="button"
          disabled={pageMeta.page <= 1}
          onClick={() => onChangePage(pageMeta.page - 1)}
        >
          이전
        </button>
        <span>
          page {pageMeta.page} / {pageMeta.total_pages || 1}
        </span>
        <button
          className="pill-button"
          type="button"
          disabled={pageMeta.total_pages === 0 || pageMeta.page >= pageMeta.total_pages}
          onClick={() => onChangePage(pageMeta.page + 1)}
        >
          다음
        </button>
      </div>
    </section>
  );
}
