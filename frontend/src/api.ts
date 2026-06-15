const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const TOKEN_KEY = "sprint2_access_token";

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  refresh_expires_in: number;
  session_id: string;
  csrf_token: string;
};

export type Post = {
  id: number;
  title: string;
  content: string;
  created_at: string;
  tags: string[];
};

export type PostListResponse = {
  items: Post[];
  total: number;
  page: number;
  size: number;
  pages: number;
};

export type PostListParams = {
  tag?: string;
  q?: string;
  page?: number;
  size?: number;
};

export type SimilarityLevel = "high" | "medium" | "low";

export type SimilarPostItem = {
  post_id: number;
  title: string;
  preview: string;
  similarity: number;
  similarity_level: SimilarityLevel;
  tags: string[];
};

export type SimilarPostsResponse = {
  summary: string;
  summary_error: string | null;
  items: SimilarPostItem[];
  message: string;
};

export type Comment = {
  id: number;
  post_id: number;
  content: string;
  created_at: string;
  updated_at: string;
};

export type ApiError = {
  error?: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
};

export function getStoredToken(): string {
  return localStorage.getItem(TOKEN_KEY) ?? "";
}

export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }
  const body = (await response.json()) as T & ApiError;
  if (!response.ok) {
    throw new Error(body.error?.message ?? "요청을 처리하지 못했습니다.");
  }
  return body;
}

function authHeaders(token: string): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return parseResponse<TokenResponse>(response);
}

export async function listPosts(params: PostListParams = {}): Promise<PostListResponse> {
  const searchParams = new URLSearchParams();
  if (params.tag?.trim()) {
    searchParams.set("tag", params.tag.trim());
  }
  if (params.q?.trim()) {
    searchParams.set("q", params.q.trim());
  }
  searchParams.set("page", String(params.page ?? 1));
  searchParams.set("size", String(params.size ?? 10));
  const query = searchParams.toString();
  const response = await fetch(`${API_BASE_URL}/posts?${query}`);
  return parseResponse<PostListResponse>(response);
}

export async function createPost(
  token: string,
  title: string,
  content: string,
  tags: string[],
): Promise<Post> {
  const response = await fetch(`${API_BASE_URL}/posts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ title, content, tags }),
  });
  return parseResponse<Post>(response);
}

export async function updatePost(
  token: string,
  postId: number,
  title: string,
  content: string,
  tags: string[],
): Promise<Post> {
  const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ title, content, tags }),
  });
  return parseResponse<Post>(response);
}

export async function deletePost(token: string, postId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  return parseResponse<void>(response);
}

export async function findSimilarPosts(
  token: string,
  title: string,
  content: string,
  tags: string[],
  limit = 3,
): Promise<SimilarPostsResponse> {
  const response = await fetch(`${API_BASE_URL}/ai/similar-posts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ title, content, tags, limit }),
  });
  return parseResponse<SimilarPostsResponse>(response);
}

export async function listComments(postId: number): Promise<Comment[]> {
  const response = await fetch(`${API_BASE_URL}/posts/${postId}/comments`);
  return parseResponse<Comment[]>(response);
}

export async function createComment(
  token: string,
  postId: number,
  content: string,
): Promise<Comment> {
  const response = await fetch(`${API_BASE_URL}/posts/${postId}/comments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ content }),
  });
  return parseResponse<Comment>(response);
}

export async function updateComment(
  token: string,
  postId: number,
  commentId: number,
  content: string,
): Promise<Comment> {
  const response = await fetch(`${API_BASE_URL}/posts/${postId}/comments/${commentId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify({ content }),
  });
  return parseResponse<Comment>(response);
}

export async function deleteComment(
  token: string,
  postId: number,
  commentId: number,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/posts/${postId}/comments/${commentId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  return parseResponse<void>(response);
}
