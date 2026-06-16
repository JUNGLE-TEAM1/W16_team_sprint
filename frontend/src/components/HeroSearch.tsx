import { SEARCH_TYPES } from "../constants/board";
import type { FieldChangeHandler, FormSubmitHandler, SearchState } from "../types";

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
    <section className="hero" aria-label="서비스 소개">
      <p className="eyebrow">Public Support Matching</p>
      <h1>AI 생활지원 매칭 보드</h1>
      <p>공공데이터 기반 복지정책, 청년지원, 공공시설을 찾고 내 상황은 비공개 요청으로 매칭합니다.</p>
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
          placeholder="예: 서울 청년 월세, 취업 준비, 마포구 상담"
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
    </section>
  );
}
