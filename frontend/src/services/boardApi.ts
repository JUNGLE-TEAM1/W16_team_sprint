import { PAGE_SIZE, request } from "../api";
import type {
  AuthForm,
  AuthMode,
  Comment,
  CurrentUser,
  AgentWritingAssistResponse,
  DraftPost,
  Post,
  PostFilters,
  PostListResponse,
  RagAssistResponse,
  Tag,
  TokenResponse,
} from "../types";
import { parseTags } from "../utils";

export function fetchCurrentUser(token: string) {
  return request<CurrentUser>("/api/v1/auth/me", {}, token);
}

export function submitAuth(mode: AuthMode, form: AuthForm) {
  return request<TokenResponse>(`/api/v1/auth/${mode}`, {
    method: "POST",
    body: JSON.stringify(form),
  });
}

export function logout(token: string) {
  return request("/api/v1/auth/logout", { method: "POST" }, token);
}

export function fetchTags() {
  return request<Tag[]>("/api/v1/tags");
}

export function fetchPosts(page: number, filters: PostFilters) {
  const params = new URLSearchParams({
    page: String(page),
    size: String(PAGE_SIZE),
  });
  if (filters.q.trim()) params.set("q", filters.q.trim());
  if (filters.tag.trim()) params.set("tag", filters.tag.trim());

  return request<PostListResponse>(`/api/v1/posts?${params.toString()}`);
}

export function fetchPost(postId: number) {
  return request<Post>(`/api/v1/posts/${postId}`);
}

export function fetchComments(postId: number) {
  return request<Comment[]>(`/api/v1/posts/${postId}/comments`);
}

export function runRagAssist(draftPost: DraftPost) {
  const referenceUrls = parseReferenceUrls(draftPost.referenceUrls);
  return request<RagAssistResponse>("/api/v1/rag/assist", {
    method: "POST",
    body: JSON.stringify({
      title: draftPost.title,
      content: draftPost.content,
      top_k: 5,
      include_references: referenceUrls.length > 0,
      reference_urls: referenceUrls,
    }),
  });
}

export function runWritingAgent(draftPost: DraftPost) {
  return request<AgentWritingAssistResponse>("/api/v1/agent/writing-assist", {
    method: "POST",
    body: JSON.stringify({
      title: draftPost.title,
      content: draftPost.content,
      tag_names: parseTags(draftPost.tagNames),
    }),
  });
}

export function savePost(draftPost: DraftPost, token: string, editingPostId: number | null) {
  const payload = {
    title: draftPost.title,
    content: draftPost.content,
    tag_names: parseTags(draftPost.tagNames),
  };

  if (editingPostId) {
    return request<Post>(
      `/api/v1/posts/${editingPostId}`,
      { method: "PATCH", body: JSON.stringify(payload) },
      token,
    );
  }

  return request<Post>("/api/v1/posts", { method: "POST", body: JSON.stringify(payload) }, token);
}

export function deletePost(postId: number, token: string) {
  return request<void>(`/api/v1/posts/${postId}`, { method: "DELETE" }, token);
}

export function saveComment(postId: number, content: string, token: string) {
  return request<Comment>(
    `/api/v1/posts/${postId}/comments`,
    { method: "POST", body: JSON.stringify({ content }) },
    token,
  );
}

export function deleteComment(commentId: number, token: string) {
  return request<void>(`/api/v1/comments/${commentId}`, { method: "DELETE" }, token);
}

function parseReferenceUrls(value: string) {
  return Array.from(
    new Set(
      value
        .split(/[\s,]+/)
        .map((url) => url.trim())
        .filter(Boolean),
    ),
  ).slice(0, 5);
}
