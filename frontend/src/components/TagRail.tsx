import type { Tag } from "../types";

type TagRailProps = {
  tags: Tag[];
  selectedTag: string;
  onClearFilters: () => void;
  onApplyTagFilter: (tagName: string) => void;
};

export function TagRail({ tags, selectedTag, onClearFilters, onApplyTagFilter }: TagRailProps) {
  return (
    <section className="tagRail" aria-label="태그 필터">
      <button className={selectedTag ? "tagButton" : "tagButton active"} type="button" onClick={onClearFilters}>
        전체
      </button>
      {tags.map((tagItem) => (
        <button
          className={selectedTag === tagItem.name ? "tagButton active" : "tagButton"}
          key={tagItem.id}
          type="button"
          onClick={() => onApplyTagFilter(tagItem.name)}
        >
          #{tagItem.name}
        </button>
      ))}
    </section>
  );
}
