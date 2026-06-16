import type { FormEventHandler } from "react";
import { Search, X } from "lucide-react";

import type { PostFilters } from "../types";

type SearchToolbarProps = {
  filters: PostFilters;
  hasActiveFilters: boolean;
  onFiltersChange: (filters: PostFilters) => void;
  onSearch: FormEventHandler<HTMLFormElement>;
  onClearFilters: () => void;
};

export function SearchToolbar({
  filters,
  hasActiveFilters,
  onFiltersChange,
  onSearch,
  onClearFilters,
}: SearchToolbarProps) {
  return (
    <section className="toolbarBand">
      <form className="searchForm" onSubmit={onSearch}>
        <Search size={18} />
        <input
          aria-label="지원 카드 검색"
          placeholder="청년월세, 마포구, 취업, 복지시설"
          value={filters.q}
          onChange={(event) => onFiltersChange({ ...filters, q: event.target.value })}
        />
        <button className="searchButton" type="submit">
          검색
        </button>
      </form>
      {hasActiveFilters && (
        <button className="textButton" type="button" onClick={onClearFilters}>
          <X size={15} />
          초기화
        </button>
      )}
    </section>
  );
}
