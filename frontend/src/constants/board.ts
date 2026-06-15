import type { SearchType, SortType } from "../types";

export const CARD_THEMES = [
  "theme-code",
  "theme-data",
  "theme-agent",
  "theme-fastapi",
  "theme-react",
  "theme-db",
  "theme-rag",
  "theme-auth",
  "theme-note",
];

export const SEARCH_TYPES: Array<{ value: SearchType; label: string }> = [
  { value: "title_content", label: "제목 + 내용" },
  { value: "title", label: "제목" },
  { value: "content", label: "내용" },
  { value: "author", label: "작성자" },
];

export const SORT_TYPES: Array<{ value: SortType; label: string }> = [
  { value: "latest", label: "최신순" },
  { value: "comment_count", label: "댓글 많은 순" },
  { value: "like_count", label: "좋아요 많은 순" },
];
