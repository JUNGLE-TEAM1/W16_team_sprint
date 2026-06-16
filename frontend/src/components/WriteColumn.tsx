import { ArrowRight, BadgeCheck, Bot, Check, ExternalLink, Plus, Sparkles, Tag, X } from "lucide-react";

import type { AgentWritingAssistResponse, DraftPost, RagAssistResponse } from "../types";
import { riskText } from "../utils";

type WriteColumnProps = {
  showComposer: boolean;
  editingPostId: number | null;
  draftPost: DraftPost;
  agentResult: AgentWritingAssistResponse | null;
  ragResult: RagAssistResponse | null;
  runningAgent: boolean;
  runningRag: boolean;
  onOpenComposer: () => void;
  onCancelEdit: () => void;
  onDraftPostChange: (draftPost: DraftPost) => void;
  onWritingAgent: () => void;
  onApplyAgentSuggestion: () => void;
  onRagAssist: () => void;
  onOpenMatchedPost: (postId: number) => void;
};

export function WriteColumn({
  showComposer,
  editingPostId,
  draftPost,
  agentResult,
  ragResult,
  runningAgent,
  runningRag,
  onOpenComposer,
  onCancelEdit,
  onDraftPostChange,
  onWritingAgent,
  onApplyAgentSuggestion,
  onRagAssist,
  onOpenMatchedPost,
}: WriteColumnProps) {
  return (
    <aside className="writeColumn">
      {!showComposer && !editingPostId ? (
        <section className="quietPanel">
          <div className="panelTop">
            <Sparkles size={18} />
            <span>상담 케이스</span>
          </div>
          <button className="wideGhostButton" type="button" onClick={onOpenComposer}>
            <Plus size={16} />
            내 상황 입력
          </button>
        </section>
      ) : (
        <section className="composerPanel">
          <div className="panelHeader">
            <div>
              <span className="kicker">{editingPostId ? "Editing" : "Consulting"}</span>
              <strong>{editingPostId ? "상담 케이스 수정" : "내 상황 입력"}</strong>
            </div>
            <button className="plainIcon" type="button" onClick={onCancelEdit} aria-label="상담 작성 취소">
              <X size={17} />
            </button>
          </div>

          <form className="composerForm" onSubmit={(event) => event.preventDefault()}>
            <input
              aria-label="상담 제목"
              placeholder="예: 수원시 24세 청년 월세 지원 상담"
              value={draftPost.title}
              onChange={(event) => onDraftPostChange({ ...draftPost, title: event.target.value })}
              required
              maxLength={120}
            />
            <textarea
              aria-label="상담 내용"
              placeholder="수원시 거주 여부, 나이, 소득, 고용 상태, 필요한 지원을 적어 주세요."
              value={draftPost.content}
              onChange={(event) => onDraftPostChange({ ...draftPost, content: event.target.value })}
              required
            />
            <label className="fieldWithIcon">
              <Tag size={15} />
              <input
                aria-label="태그"
                placeholder="수원시, 청년, 월세"
                value={draftPost.tagNames}
                onChange={(event) => onDraftPostChange({ ...draftPost, tagNames: event.target.value })}
              />
            </label>
            <label className="fieldWithIcon">
              <ExternalLink size={15} />
              <input
                aria-label="참고 URL"
                placeholder="정책/공공데이터 URL, 쉼표로 여러 개"
                value={draftPost.referenceUrls}
                onChange={(event) =>
                  onDraftPostChange({ ...draftPost, referenceUrls: event.target.value })
                }
              />
            </label>
            <div className="buttonRow">
              <button className="outlineButton" type="button" onClick={onWritingAgent} disabled={runningAgent}>
                <Bot size={15} />
                {runningAgent ? "정리 중" : "상담 초안 추천"}
              </button>
              <button className="outlineButton" type="button" onClick={onRagAssist} disabled={runningRag}>
                <Sparkles size={15} />
                {runningRag ? "매칭 중" : "AI 매칭"}
              </button>
            </div>
            <p className="panelHint">입력한 상황은 저장되지 않고, AI 매칭 요청에만 일회성으로 사용됩니다.</p>
          </form>
        </section>
      )}

      {agentResult && (
        <section className="agentPanel">
          <div className="panelHeader">
            <div>
              <span className="kicker">Agent</span>
              <strong>상담 초안과 태그 추천</strong>
            </div>
            <span className="softPill">{Math.round(agentResult.confidence * 100)}%</span>
          </div>
          <strong className="agentTitle">{agentResult.suggested_title}</strong>
          <p>{agentResult.suggested_content}</p>
          <div className="agentTags">
            {agentResult.suggested_tag_names.map((tagName) => (
              <span key={tagName}>#{tagName}</span>
            ))}
          </div>
          <div className="agentList">
            {agentResult.outline.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
          <button className="wideGhostButton" type="button" onClick={onApplyAgentSuggestion}>
            <Check size={15} />
            제안 적용
          </button>
        </section>
      )}

      {ragResult && (
        <section className={ragResult.duplicate_warning ? "ragPanel warning" : "ragPanel"}>
          <div className="panelHeader">
            <div>
              <span className="kicker">RAG</span>
              <strong>{ragResult.duplicate_warning ? "관련도 높은 카드 있음" : "지원 카드 매칭"}</strong>
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
          {ragResult.mvp_highlight && (
            <button
              className="mvpHighlight ragHighlight"
              type="button"
              onClick={() => onOpenMatchedPost(ragResult.mvp_highlight!.post_id)}
              aria-label={`${ragResult.mvp_highlight.title} 상세 보기`}
            >
              <span className="mvpHighlightHeader">
                <BadgeCheck size={15} />
                <span>MVP 하이라이트</span>
              </span>
              <strong>{ragResult.mvp_highlight.title}</strong>
              <span className="mvpHighlightText">
                <b>왜 맞나</b>
                {ragResult.mvp_highlight.why_it_fits}
              </span>
              <span className="mvpHighlightText">
                <b>왜 하이라이트</b>
                {ragResult.mvp_highlight.why_highlight}
              </span>
              <span className="ragMatchAction">
                상세 보기
                <ArrowRight size={13} />
              </span>
            </button>
          )}
          <div className="ragMatches">
            {ragResult.matches.map((match) => (
              <button
                className="ragMatch"
                key={match.post_id}
                type="button"
                onClick={() => onOpenMatchedPost(match.post_id)}
                aria-label={`${match.title} 상세 보기`}
              >
                <strong>{match.title}</strong>
                <span>
                  {Math.round(match.score * 100)}% · {riskText(match.duplicate_risk)}
                </span>
                <p>{match.summary}</p>
                <span className="ragMatchAction">
                  상세 보기
                  <ArrowRight size={13} />
                </span>
              </button>
            ))}
            {ragResult.matches.length === 0 && <p className="muted">가까운 수원시 청년정책 카드가 없습니다.</p>}
          </div>
          {ragResult.references.length > 0 && (
            <div className="ragReferences">
              <span className="kicker">Suwon Policy References</span>
              {ragResult.references.map((reference) => (
                <a href={reference.url} key={reference.url} target="_blank" rel="noreferrer">
                  <span>
                    <strong>{reference.title}</strong>
                    <small>{reference.source}</small>
                  </span>
                  <ExternalLink size={14} />
                  <p>{reference.excerpt}</p>
                </a>
              ))}
            </div>
          )}
        </section>
      )}
    </aside>
  );
}
