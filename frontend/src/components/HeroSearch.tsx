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
      <p className="eyebrow">Knowledge Sprint Board</p>
      <h1>AI 지식 공유 게시판</h1>
      <p>태그로 분류하고, 검색 타입을 선택하고, 페이지 단위로 학습 노트를 탐색합니다.</p>
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
          placeholder="검색어를 입력하세요"
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
