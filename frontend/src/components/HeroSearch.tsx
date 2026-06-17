import { SEARCH_TYPES } from "../constants/board";
import type { FieldChangeHandler, FormSubmitHandler, SearchState } from "../types";
import petCareHero from "../../assets/pet-care-hero.svg";

interface HeroSearchProps {
  search: SearchState;
  onSearchChange: FieldChangeHandler;
  onSubmitSearch: FormSubmitHandler;
  onClearFilters: () => void;
}

export function HeroSearch({
  search,
  onSearchChange,
  onSubmitSearch,
  onClearFilters,
}: HeroSearchProps) {
  return (
    <section className="hero pet-hero" aria-label="서비스 소개">
      <div className="hero-copy">
        <p className="eyebrow">Pet Care RAG Board</p>
        <h1>AI 반려견 케어 상담 보드</h1>
        <p>반려견 건강, 성장, 질병 질문을 올리면 AIHub 말뭉치 기반으로 참고 답변과 행동 계획을 제공합니다.</p>
        <form className="search-bar" onSubmit={onSubmitSearch}>
          <select name="search_type" value={search.search_type} onChange={onSearchChange}>
            {SEARCH_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          <input
            name="q"
            value={search.q}
            onChange={onSearchChange}
            placeholder="예: 기침, 구토, 피부 가려움, 자견 예방접종"
          />
          <button className="submit-button" type="submit">
            검색
          </button>
        </form>
        <div className="hero-actions">
          <button className="pill-button" type="button" onClick={onClearFilters}>
            필터 초기화
          </button>
        </div>
      </div>
      <div className="hero-visual" aria-hidden="true">
        <img src={petCareHero} alt="" />
      </div>
    </section>
  );
}
