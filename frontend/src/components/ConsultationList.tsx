import type { KeyboardEvent } from "react";

import type { PageMeta, Post } from "../types";
import { excerpt, formatDate } from "../utils/postFormatting";

interface ConsultationCardProps {
  consultation: Post;
  onSelectConsultation: (post: Post) => void;
}

function ConsultationCard({ consultation, onSelectConsultation }: ConsultationCardProps) {
  function handleKeyDown(event: KeyboardEvent<HTMLElement>) {
    if (event.key === "Enter") {
      onSelectConsultation(consultation);
    }
  }

  return (
    <article
      className="consultation-card"
      tabIndex={0}
      onClick={() => onSelectConsultation(consultation)}
      onKeyDown={handleKeyDown}
    >
      <div className="consultation-card-head">
        <div>
          <p className="eyebrow">Private Request</p>
          <h3>{consultation.title}</h3>
        </div>
        <span>비공개</span>
      </div>
      <p>{excerpt(consultation.content, 150)}</p>
      <div className="card-tags">
        {(consultation.tags ?? []).map((tag) => (
          <span key={tag}>#{tag}</span>
        ))}
      </div>
      <div className="card-meta">
        <span>{formatDate(consultation.created_at)}</span>
        <span>{consultation.region || "지역 미입력"}</span>
      </div>
    </article>
  );
}

export function ConsultationList({
  consultations,
  pageMeta,
  onOpenCompose,
  onSelectConsultation,
  onChangePage,
}: {
  consultations: Post[];
  pageMeta: PageMeta;
  onOpenCompose: () => void;
  onSelectConsultation: (post: Post) => void;
  onChangePage: (nextPage: number) => void;
}) {
  return (
    <section className="posts-section consultations-section" aria-label="내 상담 기록">
      <div className="section-heading list-heading">
        <div>
          <p className="eyebrow">My Private Matching Requests</p>
          <h2>내 상담 기록</h2>
        </div>
        <div className="section-actions">
          <span className="count-chip">
            {pageMeta.total}개 · {pageMeta.page}/{pageMeta.total_pages || 1} 페이지
          </span>
          <button className="submit-button compact-button" type="button" onClick={onOpenCompose}>
            상담 등록
          </button>
        </div>
      </div>

      {consultations.length > 0 ? (
        <div className="consultation-grid">
          {consultations.map((consultation) => (
            <ConsultationCard
              key={consultation.id}
              consultation={consultation}
              onSelectConsultation={onSelectConsultation}
            />
          ))}
        </div>
      ) : (
        <div className="empty-state consultation-empty">
          <strong>저장된 상담 기록이 없습니다.</strong>
          <span>상담을 등록하면 이후 Agent가 공공데이터를 기반으로 답변을 도와주는 흐름으로 확장합니다.</span>
          <button className="pill-button highlight" type="button" onClick={onOpenCompose}>
            상담 등록
          </button>
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
