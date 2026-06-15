import type { FormEventHandler } from "react";
import { Plus, Sparkles, Tag, X } from "lucide-react";

import type { CurrentUser, DraftPost, RagAssistResponse } from "../types";
import { riskText } from "../utils";

type WriteColumnProps = {
  showComposer: boolean;
  editingPostId: number | null;
  currentUser: CurrentUser | null;
  draftPost: DraftPost;
  ragResult: RagAssistResponse | null;
  runningRag: boolean;
  savingPost: boolean;
  onOpenComposer: () => void;
  onCancelEdit: () => void;
  onDraftPostChange: (draftPost: DraftPost) => void;
  onRagAssist: () => void;
  onSavePost: FormEventHandler<HTMLFormElement>;
};

export function WriteColumn({
  showComposer,
  editingPostId,
  currentUser,
  draftPost,
  ragResult,
  runningRag,
  savingPost,
  onOpenComposer,
  onCancelEdit,
  onDraftPostChange,
  onRagAssist,
  onSavePost,
}: WriteColumnProps) {
  return (
    <aside className="writeColumn">
      {!showComposer && !editingPostId ? (
        <section className="quietPanel">
          <div className="panelTop">
            <Sparkles size={18} />
            <span>새 기록</span>
          </div>
          <button className="wideGhostButton" type="button" onClick={onOpenComposer}>
            <Plus size={16} />
            글쓰기
          </button>
        </section>
      ) : (
        <section className="composerPanel">
          <div className="panelHeader">
            <div>
              <span className="kicker">{editingPostId ? "Editing" : "Writing"}</span>
              <strong>{editingPostId ? "글 수정" : "새 글"}</strong>
            </div>
            <button className="plainIcon" type="button" onClick={onCancelEdit} aria-label="작성 취소">
              <X size={17} />
            </button>
          </div>

          <form className="composerForm" onSubmit={onSavePost}>
            <input
              aria-label="글 제목"
              placeholder="제목"
              value={draftPost.title}
              onChange={(event) => onDraftPostChange({ ...draftPost, title: event.target.value })}
              required
              maxLength={120}
            />
            <textarea
              aria-label="글 내용"
              placeholder="내용"
              value={draftPost.content}
              onChange={(event) => onDraftPostChange({ ...draftPost, content: event.target.value })}
              required
            />
            <label className="fieldWithIcon">
              <Tag size={15} />
              <input
                aria-label="태그"
                placeholder="sprint, rag"
                value={draftPost.tagNames}
                onChange={(event) => onDraftPostChange({ ...draftPost, tagNames: event.target.value })}
              />
            </label>
            <div className="buttonRow">
              <button className="outlineButton" type="button" onClick={onRagAssist} disabled={runningRag}>
                <Sparkles size={15} />
                {runningRag ? "검사 중" : "RAG 검사"}
              </button>
              <button className="mintButton" type="submit" disabled={savingPost || !currentUser}>
                <Plus size={15} />
                {savingPost ? "저장 중" : editingPostId ? "수정" : "발행"}
              </button>
            </div>
            {!currentUser && <p className="panelHint">로그인 후 발행할 수 있습니다.</p>}
          </form>
        </section>
      )}

      {ragResult && (
        <section className={ragResult.duplicate_warning ? "ragPanel warning" : "ragPanel"}>
          <div className="panelHeader">
            <div>
              <span className="kicker">RAG</span>
              <strong>{ragResult.duplicate_warning ? "비슷한 글이 있습니다" : "관련 글"}</strong>
            </div>
            <div className="ragPills">
              <span className={ragResult.llm_used ? "softPill active" : "softPill"}>
                {ragResult.llm_used ? `LLM ${ragResult.llm_model}` : "rule fallback"}
              </span>
              <span className="softPill">
                {ragResult.embedding_provider} · {ragResult.embedding_dimensions}d
              </span>
            </div>
          </div>
          <p>{ragResult.recommendation}</p>
          <div className="ragMatches">
            {ragResult.matches.map((match) => (
              <article className="ragMatch" key={match.post_id}>
                <strong>{match.title}</strong>
                <span>
                  {Math.round(match.score * 100)}% · {riskText(match.duplicate_risk)}
                </span>
                <p>{match.summary}</p>
              </article>
            ))}
            {ragResult.matches.length === 0 && <p className="muted">가까운 글이 없습니다.</p>}
          </div>
        </section>
      )}
    </aside>
  );
}
