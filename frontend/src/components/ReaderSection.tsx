import type { FormEventHandler } from "react";
import { BookOpen, Edit3, MessageCircle, Send, Trash2 } from "lucide-react";

import type { Comment, CurrentUser, Post } from "../types";
import { formatDate, formatFullDate } from "../utils";

type ReaderSectionProps = {
  selectedPost: Post | null;
  comments: Comment[];
  currentUser: CurrentUser | null;
  draftComment: string;
  loadingComments: boolean;
  savingComment: boolean;
  canEditSelectedPost: boolean;
  onApplyTagFilter: (tagName: string) => void;
  onStartEdit: (post: Post) => void;
  onDeletePost: (postId: number) => void;
  onDraftCommentChange: (value: string) => void;
  onSaveComment: FormEventHandler<HTMLFormElement>;
  onDeleteComment: (comment: Comment) => void;
};

export function ReaderSection({
  selectedPost,
  comments,
  currentUser,
  draftComment,
  loadingComments,
  savingComment,
  canEditSelectedPost,
  onApplyTagFilter,
  onStartEdit,
  onDeletePost,
  onDraftCommentChange,
  onSaveComment,
  onDeleteComment,
}: ReaderSectionProps) {
  return (
    <section className="readerWrap">
      {selectedPost ? (
        <article className="readerArticle">
          <div className="readerMeta">
            <span>
              <BookOpen size={15} />
              {selectedPost.author_name}
            </span>
            <time>{formatFullDate(selectedPost.updated_at)}</time>
          </div>
          <h2>{selectedPost.title}</h2>
          <div className="readerTags">
            {selectedPost.tags.map((tagItem) => (
              <button key={tagItem.id} type="button" onClick={() => onApplyTagFilter(tagItem.name)}>
                #{tagItem.name}
              </button>
            ))}
          </div>
          <p className="readerBody">{selectedPost.content}</p>

          {canEditSelectedPost && (
            <div className="articleActions">
              <button className="outlineButton" type="button" onClick={() => onStartEdit(selectedPost)}>
                <Edit3 size={15} />
                수정
              </button>
              <button className="dangerButton" type="button" onClick={() => onDeletePost(selectedPost.id)}>
                <Trash2 size={15} />
                삭제
              </button>
            </div>
          )}

          <section className="commentsBlock" aria-busy={loadingComments}>
            <div className="commentsHeader">
              <strong>
                <MessageCircle size={16} />
                댓글 {comments.length}
              </strong>
            </div>
            <form className="commentForm" onSubmit={onSaveComment}>
              <textarea
                aria-label="댓글"
                placeholder="댓글을 남겨 보세요."
                value={draftComment}
                onChange={(event) => onDraftCommentChange(event.target.value)}
                required
                maxLength={1000}
              />
              <button className="mintButton" type="submit" disabled={savingComment || !currentUser}>
                <Send size={15} />
                {savingComment ? "등록 중" : "등록"}
              </button>
            </form>
            <div className="commentList">
              {comments.map((comment) => {
                const canDeleteComment =
                  Boolean(currentUser) &&
                  (currentUser?.role === "admin" || comment.user_id === currentUser?.id);
                return (
                  <article className="commentItem" key={comment.id}>
                    <div>
                      <strong>{comment.author_name}</strong>
                      <time>{formatDate(comment.created_at)}</time>
                    </div>
                    <p>{comment.content}</p>
                    {canDeleteComment && (
                      <button
                        className="plainIcon dangerIcon"
                        type="button"
                        onClick={() => onDeleteComment(comment)}
                        aria-label="댓글 삭제"
                      >
                        <Trash2 size={15} />
                      </button>
                    )}
                  </article>
                );
              })}
              {!loadingComments && comments.length === 0 && <p className="muted">아직 댓글이 없습니다.</p>}
            </div>
          </section>
        </article>
      ) : (
        <div className="emptyState">
          <MessageCircle size={24} />
          <strong>글을 선택해 주세요</strong>
        </div>
      )}
    </section>
  );
}
