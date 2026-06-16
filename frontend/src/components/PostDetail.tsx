import type {
  Comment,
  CommentFormState,
  FieldChangeHandler,
  FormSubmitHandler,
  Post,
  PostFormState,
  RelatedPostsState,
  User,
} from "../types";
import { POST_TYPE_LABELS } from "../constants/board";
import { formatDate } from "../utils/postFormatting";
import { RelatedPostsPanel, shouldShowRelatedPostsPanel } from "./RelatedPostsPanel";

interface PostEditFormProps {
  editForm: PostFormState;
  relatedPosts: RelatedPostsState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onCancel: () => void;
}

function PostEditForm({ editForm, relatedPosts, onChange, onSubmit, onCancel }: PostEditFormProps) {
  const hasRelatedPanel = shouldShowRelatedPostsPanel(relatedPosts);

  return (
    <div className={hasRelatedPanel ? "edit-layout has-related" : "edit-layout"}>
      <form className="stack-form edit-form" onSubmit={onSubmit} aria-label="카드 또는 상담 케이스 수정">
        <label className="field">
          <span>제목 수정</span>
          <input name="title" value={editForm.title} onChange={onChange} />
        </label>
        <label className="field">
          <span>내용 수정</span>
          <textarea name="content" value={editForm.content} onChange={onChange} />
        </label>
        <label className="field">
          <span>지역</span>
          <input name="region" value={editForm.region} onChange={onChange} />
        </label>
        <label className="field">
          <span>태그 수정</span>
          <input name="tags" value={editForm.tags} onChange={onChange} />
        </label>
        <div className="split-actions">
          <button className="submit-button" type="submit">
            수정 완료
          </button>
          <button className="ghost-button" type="button" onClick={onCancel}>
            취소
          </button>
        </div>
      </form>
      <RelatedPostsPanel state={relatedPosts} />
    </div>
  );
}

function CommentsSection({
  comments,
  currentUser,
  commentForm,
  onCommentChange,
  onCreateComment,
  onDeleteComment,
  onShowLogin,
}: {
  comments: Comment[];
  currentUser: User | null;
  commentForm: CommentFormState;
  onCommentChange: FieldChangeHandler;
  onCreateComment: FormSubmitHandler;
  onDeleteComment: (commentId: number) => void;
  onShowLogin: () => void;
}) {
  return (
    <div className="comments-area">
      <div className="comments-head">
        <h3>상담 메모</h3>
        <span>{comments.length}개</span>
      </div>

      {comments.length > 0 ? (
        <div className="comment-list">
          {comments.map((comment) => (
            <article className="comment-item" key={comment.id}>
              <div>
                <strong>{comment.author_display_name}</strong>
                <p>{comment.content}</p>
              </div>
              {currentUser?.id === comment.author_id ? (
                <button className="text-danger" type="button" onClick={() => onDeleteComment(comment.id)}>
                  삭제
                </button>
              ) : null}
            </article>
          ))}
        </div>
      ) : (
        <p className="muted-text">아직 상담 메모가 없습니다.</p>
      )}

      {currentUser ? (
        <form className="comment-form" onSubmit={onCreateComment}>
          <label className="field">
            <span>상담 메모</span>
            <textarea
              name="content"
              value={commentForm.content}
              onChange={onCommentChange}
              maxLength={1000}
              required
            />
          </label>
          <button className="submit-button" type="submit">
            메모 작성
          </button>
        </form>
      ) : (
        <div className="locked-panel compact-lock">
          <span>상담 메모 작성은 로그인이 필요합니다.</span>
          <button className="pill-button" type="button" onClick={onShowLogin}>
            로그인
          </button>
        </div>
      )}
    </div>
  );
}

export function PostDetail({
  selectedPost,
  comments,
  currentUser,
  isAuthor,
  isEditingPost,
  editForm,
  editRelatedPosts,
  commentForm,
  onBackToList,
  onRefreshComments,
  onLikePost,
  onOpenEditor,
  onDeletePost,
  onUpdatePost,
  onEditChange,
  onCancelEdit,
  onCommentChange,
  onCreateComment,
  onDeleteComment,
  onShowLogin,
}: {
  selectedPost: Post;
  comments: Comment[];
  currentUser: User | null;
  isAuthor: boolean | null;
  isEditingPost: boolean;
  editForm: PostFormState;
  editRelatedPosts: RelatedPostsState;
  commentForm: CommentFormState;
  onBackToList: () => void;
  onRefreshComments: () => void;
  onLikePost: () => void;
  onOpenEditor: () => void;
  onDeletePost: () => void;
  onUpdatePost: FormSubmitHandler;
  onEditChange: FieldChangeHandler;
  onCancelEdit: () => void;
  onCommentChange: FieldChangeHandler;
  onCreateComment: FormSubmitHandler;
  onDeleteComment: (commentId: number) => void;
  onShowLogin: () => void;
}) {
  const canComment = selectedPost.comment_policy !== "none";
  const isPrivateCase = selectedPost.post_type === "case";
  const showInterest = selectedPost.visibility === "public";

  return (
    <section className="detail-page" aria-label="지원 정보와 상담 요청 상세">
      <article className="panel detail-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow">{isPrivateCase ? "Private Matching Request" : "Support Information"}</p>
            <h2>{selectedPost.title}</h2>
          </div>
          <div className="section-actions">
            <button className="ghost-button" type="button" onClick={onBackToList}>
              목록으로
            </button>
            {canComment ? (
              <button className="ghost-button" type="button" onClick={onRefreshComments}>
                메모 새로고침
              </button>
            ) : null}
          </div>
        </div>

        <div className="post-detail">
          <div className="detail-badges">
            <span>{POST_TYPE_LABELS[selectedPost.post_type]}</span>
            {selectedPost.region ? <span>{selectedPost.region}</span> : null}
            {selectedPost.source_name ? <span>{selectedPost.source_name}</span> : null}
            {selectedPost.visibility === "private" ? <span>비공개</span> : null}
            {selectedPost.rag_scope === "excluded" ? <span>RAG 제외</span> : null}
          </div>
          <p>{selectedPost.content}</p>
          <div className="card-tags">
            {(selectedPost.tags ?? []).map((tag) => (
              <span key={tag}>#{tag}</span>
            ))}
          </div>
          <div className="card-meta">
            <span>{formatDate(selectedPost.created_at)}</span>
            <span>by {selectedPost.author_display_name}</span>
          </div>
          {selectedPost.source_url ? (
            <a className="reference-link" href={selectedPost.source_url} target="_blank" rel="noreferrer">
              원문 출처 열기
            </a>
          ) : null}
          <div className="card-stats detail-stats">
            {canComment ? <span>상담 메모 {selectedPost.comment_count ?? comments.length}개</span> : null}
            {showInterest ? <span>관심 {selectedPost.like_count ?? 0}개</span> : null}
          </div>
          {showInterest ? (
            <div className="like-actions">
              <button className="like-button" type="button" onClick={onLikePost}>
                관심 등록
              </button>
            </div>
          ) : null}
          {isAuthor ? (
            <div className="detail-actions" aria-label="카드 또는 상담 케이스 관리">
              <button className="ghost-button" type="button" onClick={onOpenEditor}>
                수정
              </button>
              <button className="danger-button" type="button" onClick={onDeletePost}>
                삭제
              </button>
            </div>
          ) : null}
        </div>

        {isAuthor && isEditingPost ? (
          <PostEditForm
            editForm={editForm}
            relatedPosts={editRelatedPosts}
            onChange={onEditChange}
            onSubmit={onUpdatePost}
            onCancel={onCancelEdit}
          />
        ) : null}

        {canComment ? (
          <CommentsSection
            comments={comments}
            currentUser={currentUser}
            commentForm={commentForm}
            onCommentChange={onCommentChange}
            onCreateComment={onCreateComment}
            onDeleteComment={onDeleteComment}
            onShowLogin={onShowLogin}
          />
        ) : (
          <div className="locked-panel inline-empty">
            <strong>{isPrivateCase ? "이 상담 요청은 본인만 확인할 수 있습니다." : "지원 정보에는 상담 메모를 받지 않습니다."}</strong>
            <span>
              {isPrivateCase
                ? "개인정보 보호를 위해 공용 RAG 지식베이스에도 저장하지 않습니다."
                : "공식 정보와 개인 의견이 섞이지 않도록 출처 확인과 관심 등록만 제공합니다."}
            </span>
          </div>
        )}
      </article>
    </section>
  );
}
