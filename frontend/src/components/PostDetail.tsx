import type {
  Comment,
  CommentFormState,
  FieldChangeHandler,
  FormSubmitHandler,
  PetCareAdviceState,
  Post,
  PostFormState,
  User,
} from "../types";
import { POST_TYPE_LABELS } from "../constants/board";
import { formatDate } from "../utils/postFormatting";

interface PostEditFormProps {
  editForm: PostFormState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onCancel: () => void;
}

function PostEditForm({ editForm, onChange, onSubmit, onCancel }: PostEditFormProps) {
  return (
    <div className="edit-layout">
      <form className="stack-form edit-form" onSubmit={onSubmit} aria-label="상담 질문 수정">
        <label className="field">
          <span>제목 수정</span>
          <input name="title" value={editForm.title} onChange={onChange} />
        </label>
        <label className="field">
          <span>질문 내용 수정</span>
          <textarea name="content" value={editForm.content} onChange={onChange} />
        </label>
        <label className="field">
          <span>지역 (선택)</span>
          <input name="region" value={editForm.region} onChange={onChange} placeholder="예: 서울 마포구" />
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
    </div>
  );
}

function splitAnswerText(text: string) {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (!normalized) {
    return [];
  }

  const sentences = normalized.match(/[^.!?。！？]+[.!?。！？]?/g)?.map((sentence) => sentence.trim()).filter(Boolean);
  if (!sentences || sentences.length <= 1) {
    return [normalized];
  }

  const paragraphs: string[] = [];
  for (let index = 0; index < sentences.length; index += 2) {
    paragraphs.push(sentences.slice(index, index + 2).join(" "));
  }
  return paragraphs;
}

function shortenPreview(text: string | null | undefined) {
  const normalized = (text ?? "").replace(/\s+/g, " ").trim();
  if (normalized.length <= 170) {
    return normalized;
  }
  return `${normalized.slice(0, 170)}...`;
}

function adviceStatusLabel(adviceState: PetCareAdviceState) {
  if (adviceState.isLoading) {
    return "불러오는 중";
  }
  if (!adviceState.advice) {
    return "답변 대기";
  }
  return adviceState.advice.status === "stale" ? "재생성 권장" : "생성 완료";
}

function AiAnswerSection({
  adviceState,
  currentUser,
  onGenerateAdvice,
}: {
  adviceState: PetCareAdviceState;
  currentUser: User | null;
  onGenerateAdvice: () => void;
}) {
  const canGenerateAdvice = !adviceState.advice || adviceState.advice.status === "stale";
  const hospitalCandidates = adviceState.advice?.hospital_candidates ?? [];
  const generateButtonLabel = !adviceState.advice
    ? "AI 답변 생성"
    : adviceState.advice.status === "stale"
      ? "AI 답변 다시 생성"
      : "AI 답변 생성 완료";

  return (
    <section className="ai-answer-card" aria-label="AI 답변">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow">RAG Advice</p>
          <h3>AI 답변</h3>
        </div>
        <span className={adviceState.advice?.status === "stale" ? "answer-status is-stale" : "answer-status"}>
          {adviceStatusLabel(adviceState)}
        </span>
      </div>

      {adviceState.advice ? (
        <>
          {adviceState.advice.status === "stale" ? (
            <div className="answer-policy warning">
              <strong>질문 수정 이후의 이전 답변입니다.</strong>
              <span>제목, 내용, 태그 또는 지역이 바뀌었기 때문에 현재 질문에 맞게 다시 생성하는 것이 좋습니다.</span>
            </div>
          ) : null}
          <div className="answer-layout">
            <div className="answer-main">
              <section className="answer-block answer-summary">
                <div className="answer-block-head">
                  <span>AI</span>
                  <strong>답변 요약</strong>
                </div>
                <div className="answer-copy">
                  {splitAnswerText(adviceState.advice.answer).map((paragraph, index) => (
                    <p key={`${paragraph}-${index}`}>{paragraph}</p>
                  ))}
                </div>
              </section>

              <section className="answer-block answer-warning">
                <div className="answer-block-head">
                  <span>SAFE</span>
                  <strong>안전 안내</strong>
                </div>
                <p>{adviceState.advice.safety_note}</p>
              </section>
            </div>

            <section className="answer-block action-plan-block">
              <div className="answer-block-head">
                <span>CHECK</span>
                <strong>보호자 행동 계획</strong>
              </div>
              <ol className="action-steps">
                {adviceState.advice.action_plan.map((item, index) => (
                  <li key={`${item}-${index}`}>
                    <span>{index + 1}</span>
                    <p>{item}</p>
                  </li>
                ))}
              </ol>
            </section>
          </div>
          {hospitalCandidates.length > 0 ? (
            <section className="hospital-list">
              <div className="source-list-head">
                <strong>주변 동물병원 후보</strong>
                <span>{hospitalCandidates.length}곳</span>
              </div>
              <div className="hospital-grid">
                {hospitalCandidates.map((hospital) => (
                  <article className="hospital-card" key={`${hospital.name}-${hospital.place_url ?? hospital.address ?? ""}`}>
                    <div>
                      <strong>{hospital.name}</strong>
                      {hospital.distance_meters !== null ? <span>{hospital.distance_meters}m</span> : null}
                    </div>
                    <p>{hospital.road_address || hospital.address || "주소 정보 없음"}</p>
                    <div className="hospital-meta">
                      {hospital.phone ? <span>{hospital.phone}</span> : <span>전화번호 미상</span>}
                      {hospital.place_url ? (
                        <a href={hospital.place_url} target="_blank" rel="noreferrer">
                          Kakao 지도
                        </a>
                      ) : null}
                    </div>
                  </article>
                ))}
              </div>
            </section>
          ) : null}
          <section className="source-list">
            <div className="source-list-head">
              <strong>참고 근거</strong>
              <span>{adviceState.advice.sources.length}개 문서</span>
            </div>
            {adviceState.advice.sources.length > 0 ? (
              adviceState.advice.sources.map((source) => (
                <article className="source-item" key={source.chunk_id}>
                  <div>
                    <span className="source-kind">{source.source_kind === "qa" ? "Q&A" : "원천 말뭉치"}</span>
                    <strong>{source.title}</strong>
                  </div>
                  <p>{shortenPreview(source.answer_preview || source.content_preview)}</p>
                  <div className="source-meta">
                    <span>{source.department || "진료과 미상"}</span>
                    {source.life_cycle ? <span>{source.life_cycle}</span> : null}
                    {source.disease ? <span>{source.disease}</span> : null}
                    <span>유사도 {Math.round(source.similarity * 100)}%</span>
                  </div>
                </article>
              ))
            ) : (
              <span className="muted-text">표시할 참고 근거가 없습니다.</span>
            )}
          </section>
        </>
      ) : (
        <div className="answer-policy">
          <strong>AIHub 기반 답변 생성</strong>
          <span>질문과 비슷한 AIHub 반려견 Q&A/말뭉치를 검색해 참고 답변과 행동 계획을 만듭니다.</span>
        </div>
      )}

      {adviceState.errorText ? <p className="status-text error">{adviceState.errorText}</p> : null}
      {currentUser ? (
        <button
          className="submit-button compact-button"
          type="button"
          disabled={adviceState.isLoading || !canGenerateAdvice}
          onClick={onGenerateAdvice}
        >
          {generateButtonLabel}
        </button>
      ) : (
        <p className="muted-text">AI 답변 생성은 로그인이 필요합니다.</p>
      )}
    </section>
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
            <span>댓글</span>
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
  adviceState,
  commentForm,
  onBackToList,
  onRefreshComments,
  onGenerateAdvice,
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
  adviceState: PetCareAdviceState;
  commentForm: CommentFormState;
  onBackToList: () => void;
  onRefreshComments: () => void;
  onGenerateAdvice: () => void;
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
  const showInterest = selectedPost.visibility === "public";

  return (
    <section
      className="detail-page"
      role="dialog"
      aria-modal="true"
      aria-label="반려견 상담 질문 상세"
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          onBackToList();
        }
      }}
    >
      <article className="panel detail-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow">Pet Care Question</p>
            <h2>{selectedPost.title}</h2>
          </div>
          <div className="section-actions">
            <button className="ghost-button" type="button" onClick={onBackToList}>
              닫기
            </button>
            {canComment ? (
              <button className="ghost-button" type="button" onClick={onRefreshComments}>
                댓글 새로고침
              </button>
            ) : null}
          </div>
        </div>

        <div className="post-detail">
          <div className="detail-badges">
            <span>{POST_TYPE_LABELS[selectedPost.post_type]}</span>
            {selectedPost.region ? <span>{selectedPost.region}</span> : null}
            {selectedPost.source_name ? <span>{selectedPost.source_name}</span> : null}
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
            {canComment ? <span>댓글 {selectedPost.comment_count ?? comments.length}개</span> : null}
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
            <div className="detail-actions" aria-label="상담 질문 관리">
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

        <AiAnswerSection
          adviceState={adviceState}
          currentUser={currentUser}
          onGenerateAdvice={onGenerateAdvice}
        />

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
            <strong>이 상담 질문에는 댓글을 받지 않습니다.</strong>
            <span>댓글 정책이 닫힌 질문입니다.</span>
          </div>
        )}
      </article>
    </section>
  );
}
