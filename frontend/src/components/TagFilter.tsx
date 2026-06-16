import type { Tag } from "../types";

interface TagFilterProps {
  tags: Tag[];
  selectedTagName: string;
  selectedTag: string;
  onFilterByTag: (tagName: string) => void;
}

export function TagFilter({ tags, selectedTagName, selectedTag, onFilterByTag }: TagFilterProps) {
  return (
    <section className="tag-filter" aria-label="태그 필터">
      <div className="tag-filter-head">
        <span>대상/분야 태그</span>
        {selectedTagName ? <strong>선택됨: #{selectedTagName}</strong> : null}
      </div>
      <div className="tag-row">
        {tags.length > 0 ? (
          tags.map((tag) => (
            <button
              className={`tag-button ${selectedTag === tag.name ? "is-active" : ""}`}
              key={tag.id}
              type="button"
              onClick={() => onFilterByTag(tag.name)}
            >
              #{tag.name}
            </button>
          ))
        ) : (
          <span className="muted-text">아직 등록된 지원 태그가 없습니다.</span>
        )}
      </div>
    </section>
  );
}
