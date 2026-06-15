import type { PostFormState, SearchState } from "../types";

export function formatDate(value?: string) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat("ko-KR", {
    month: "long",
    day: "numeric",
  }).format(new Date(value));
}

export function excerpt(value: string, maxLength = 110) {
  if (!value || value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength).trim()}...`;
}

export function parseTags(value: string) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

export function tagText(tags?: string[]) {
  return Array.isArray(tags) ? tags.join(", ") : "";
}

export function buildPostBody(form: PostFormState) {
  return JSON.stringify({
    title: form.title,
    content: form.content,
    tags: parseTags(form.tags),
  });
}

export function buildPostQuery(nextSearch: SearchState) {
  const params = new URLSearchParams({
    search_type: nextSearch.search_type,
    sort: nextSearch.sort,
    page: String(nextSearch.page),
    size: String(nextSearch.size),
  });
  if (nextSearch.q.trim()) {
    params.set("q", nextSearch.q.trim());
  }
  if (nextSearch.tag) {
    params.set("tag", nextSearch.tag);
  }
  return params.toString();
}
