import type { Post, RagMatch } from "./types";

export function formatDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

export function formatFullDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function parseTags(value: string) {
  return value
    .split(",")
    .map((tagName) => tagName.trim().replace(/^#/, "").toLowerCase())
    .filter(Boolean);
}

export function excerpt(value: string, maxLength = 146) {
  const normalized = value.replace(/\s+/g, " ").trim();
  return normalized.length > maxLength ? `${normalized.slice(0, maxLength)}...` : normalized;
}

export function readingMinutes(value: string) {
  return Math.max(1, Math.ceil(value.length / 520));
}

export function sprintNumber(post: Post) {
  const match = post.title.match(/Sprint\s+(\d+)/i);
  return match ? `S${match[1]}` : "글";
}

export function riskText(risk: RagMatch["duplicate_risk"]) {
  if (risk === "high") return "중복 위험 높음";
  if (risk === "medium") return "관련 글";
  return "느슨한 연결";
}
