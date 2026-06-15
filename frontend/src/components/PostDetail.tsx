import type {
  Comment,
  CommentFormState,
  FieldChangeHandler,
  FormSubmitHandler,
  Post,
  PostFormState,
  User,
} from "../types";
import { formatDate } from "../utils/postFormatting";

interface PostEditFormProps {
  editForm: PostFormState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onCancel: () => void;
}

function PostEditForm({ editForm, onChange, onSubmit, onCancel }: PostEditFormProps) {
  return (
    <form className="stack-form edit-form" onSubmit={onSubmit} aria-label="게시글 수정">
      <label className="field">
        <span>Edit title</span>
        <input name="title" value={editForm.title} onChange={onChange} />
      </label>
      <label className="field">
        <span>Edit content</span>
        <textarea name="content" value={editForm.content} onChange={onChange} />
      </label>
      <label className="field">
        <span>Edit tags</span>
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
        <h3>댓글</h3>
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
        <p className="muted-text">아직 댓글이 없습니다.</p>
      )}

      {currentUser ? (
        <form className="comment-form" onSubmit={onCreateComment}>
          <label className="field">
            <span>Comment</span>
            <textarea
              name="content"
              value={commentForm.content}
              onChange={onCommentChange}
              maxLength={1000}
              required
            />
          </label>
          <button className="submit-button" type="submit">
            댓글 작성
          </button>
        </form>
      ) : (
        <div className="locked-panel compact-lock">
          <span>댓글 작성은 로그인이 필요합니다.</span>
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
  return (
    <section className="detail-page" aria-label="게시글 상세">
      <article className="panel detail-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow">Read</p>
            <h2>{selectedPost.title}</h2>
          </div>
          <div className="section-actions">
            <button className="ghost-button" type="button" onClick={onBackToList}>
              목록으로
            </button>
            <button className="ghost-button" type="button" onClick={onRefreshComments}>
              댓글 새로고침
            </button>
          </div>
        </div>

        <div className="post-detail">
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
          <div className="card-stats detail-stats">
            <span>댓글 {selectedPost.comment_count ?? comments.length}개</span>
            <span>좋아요 {selectedPost.like_count ?? 0}개</span>
          </div>
          <div className="like-actions">
            <button className="like-button" type="button" onClick={onLikePost}>
              좋아요
            </button>
          </div>
          {isAuthor ? (
            <div className="detail-actions" aria-label="게시글 관리">
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
            onChange={onEditChange}
            onSubmit={onUpdatePost}
            onCancel={onCancelEdit}
          />
        ) : null}

        <CommentsSection
          comments={comments}
          currentUser={currentUser}
          commentForm={commentForm}
          onCommentChange={onCommentChange}
          onCreateComment={onCreateComment}
          onDeleteComment={onDeleteComment}
          onShowLogin={onShowLogin}
        />
      </article>
    </section>
  );
}
