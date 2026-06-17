import type { ChangeEvent, FormEvent } from "react";

export type AuthView = "login" | "register" | null;
export type BoardView = "support" | "consultations";
export type SearchType = "title_content" | "title" | "content" | "author";
export type SortType = "latest" | "comment_count" | "like_count";
export type PostType = "policy" | "facility" | "case";
export type PostVisibility = "public" | "private";
export type PostCommentPolicy = "none" | "public" | "private";
export type PostRagScope = "public" | "excluded";

export interface AuthFormState {
  username: string;
  password: string;
  display_name: string;
}

export interface PostFormState {
  title: string;
  content: string;
  tags: string;
  post_type: PostType;
  region: string;
  source_name: string;
  source_url: string;
  source_external_id: string;
}

export interface CommentFormState {
  content: string;
}

export interface SearchState {
  q: string;
  search_type: SearchType;
  tag: string;
  sort: SortType;
  page: number;
  size: number;
}

export interface PageMeta {
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

export interface StatusState {
  text: string;
  isError: boolean;
}

export interface User {
  id: number;
  username?: string;
  display_name: string;
  created_at?: string;
}

export interface Tag {
  id: number;
  name: string;
  created_at?: string;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_display_name: string;
  post_type: PostType;
  visibility: PostVisibility;
  comment_policy: PostCommentPolicy;
  rag_scope: PostRagScope;
  region: string | null;
  source_name: string | null;
  source_url: string | null;
  source_external_id: string | null;
  comment_count: number;
  like_count: number;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  post_id: number;
  author_id: number;
  author_display_name: string;
  content: string;
  created_at?: string;
}

export interface PostPage {
  items: Post[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

export interface RelatedPost {
  post_id: number;
  title: string;
  content_preview: string;
  tags: string[];
  similarity: number;
  summary: string | null;
}

export interface RelatedPostsResponse {
  items: RelatedPost[];
}

export interface RelatedPostsState {
  items: RelatedPost[];
  isLoading: boolean;
  errorText: string;
}

export interface PetCareSource {
  chunk_id: number;
  document_id: number;
  title: string;
  content_preview: string;
  question: string | null;
  answer_preview: string | null;
  department: string | null;
  disease: string | null;
  life_cycle: string | null;
  source_kind: string;
  split: string;
  similarity: number;
}

export interface PetCareAdvice {
  id: number | null;
  post_id: number | null;
  status: "completed" | "stale";
  generated_at: string | null;
  answer: string;
  action_plan: string[];
  safety_note: string;
  sources: PetCareSource[];
  hospital_candidates: PetCareHospitalCandidate[];
}

export interface PetCareHospitalCandidate {
  name: string;
  address: string | null;
  road_address: string | null;
  phone: string | null;
  distance_meters: number | null;
  place_url: string | null;
  source: string;
}

export interface PetCareAdviceState {
  advice: PetCareAdvice | null;
  isLoading: boolean;
  errorText: string;
}

export interface LoginResponse {
  user: User;
}

export interface ApiErrorResponse {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
}

export interface ApiResult<T> {
  ok: boolean;
  status: number;
  data: T;
}

export interface RequestOptions {
  method?: string;
  body?: BodyInit | null;
  headers?: HeadersInit;
  quiet?: boolean;
  successMessage?: string;
}

export interface LoadOptions {
  quiet?: boolean;
}

export interface LoadPostsOptions extends LoadOptions {
  filters?: Partial<SearchState>;
}

export type FieldChangeEvent = ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>;
export type FieldChangeHandler = (event: FieldChangeEvent) => void;
export type FormSubmitHandler = (event: FormEvent<HTMLFormElement>) => void | Promise<void>;
