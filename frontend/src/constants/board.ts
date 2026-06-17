import type { PostType, SearchType, SortType } from "../types";

export const CARD_THEMES = [
  "theme-policy",
  "theme-facility",
  "theme-case",
  "theme-region",
  "theme-source",
  "theme-support",
];

export const POST_TYPE_LABELS: Record<PostType, string> = {
  policy: "참고 문서",
  facility: "보호소 정보",
  case: "상담 질문",
};

export const SEARCH_TYPES: Array<{ value: SearchType; label: string }> = [
  { value: "title_content", label: "제목 + 내용" },
  { value: "title", label: "제목" },
  { value: "content", label: "내용" },
  { value: "author", label: "작성자" },
];

export const SORT_TYPES: Array<{ value: SortType; label: string }> = [
  { value: "latest", label: "최신순" },
  { value: "comment_count", label: "댓글 많은 순" },
  { value: "like_count", label: "관심 많은 순" },
];
