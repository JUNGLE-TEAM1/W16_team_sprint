import { ChevronLeft, ChevronRight, FileText } from "lucide-react";

import type { Post, PostMeta } from "../types";
import { excerpt, formatDate, readingMinutes, sprintNumber } from "../utils";

type FeedColumnProps = {
  posts: Post[];
  postMeta: PostMeta;
  selectedPostId: number | null;
  hasActiveFilters: boolean;
  loadingPosts: boolean;
  onLoadPage: (page: number) => void;
  onSelectPost: (postId: number) => void;
  onClearFilters: () => void;
};

export function FeedColumn({
  posts,
  postMeta,
  selectedPostId,
  hasActiveFilters,
  loadingPosts,
  onLoadPage,
  onSelectPost,
  onClearFilters,
}: FeedColumnProps) {
  return (
    <section className="feedColumn">
      <div className="feedHeader">
        <div>
          <span className="kicker">{hasActiveFilters ? "Filtered" : "Latest"}</span>
          <h2>읽을 글</h2>
        </div>
        <div className="pager">
          <button
            className="plainIcon"
            type="button"
            disabled={postMeta.page <= 1}
            onClick={() => onLoadPage(postMeta.page - 1)}
            aria-label="이전 페이지"
          >
            <ChevronLeft size={18} />
          </button>
          <span>
            {postMeta.pages === 0 ? 0 : postMeta.page} / {postMeta.pages}
          </span>
          <button
            className="plainIcon"
            type="button"
            disabled={postMeta.pages === 0 || postMeta.page >= postMeta.pages}
            onClick={() => onLoadPage(postMeta.page + 1)}
            aria-label="다음 페이지"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      <div className="postList" aria-busy={loadingPosts}>
        {loadingPosts && posts.length === 0 && (
          <>
            <div className="postSkeleton" />
            <div className="postSkeleton" />
            <div className="postSkeleton" />
          </>
        )}

        {posts.map((post) => (
          <button
            className={post.id === selectedPostId ? "postRow selected" : "postRow"}
            key={post.id}
            type="button"
            onClick={() => onSelectPost(post.id)}
          >
            <span className="postRowBody">
              <strong>{post.title}</strong>
              <span className="excerpt">{excerpt(post.content)}</span>
              <span className="metaLine">
                by {post.author_name} · {formatDate(post.created_at)} · 읽기 {readingMinutes(post.content)}분
              </span>
              <span className="tagLine">
                {post.tags.map((tagItem) => (
                  <span key={tagItem.id}>#{tagItem.name}</span>
                ))}
              </span>
            </span>
            <span className="articleThumb">{sprintNumber(post)}</span>
          </button>
        ))}

        {!loadingPosts && posts.length === 0 && (
          <div className="emptyState">
            <FileText size={24} />
            <strong>맞는 글이 없습니다</strong>
            <span>검색어를 바꾸거나 태그 필터를 초기화해 주세요.</span>
            {hasActiveFilters && (
              <button className="outlineButton" type="button" onClick={onClearFilters}>
                초기화
              </button>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
