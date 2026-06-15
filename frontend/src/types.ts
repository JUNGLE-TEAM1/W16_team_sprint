import type { ChangeEvent, FormEvent } from "react";

export type AuthView = "login" | "register" | null;
export type SearchType = "title_content" | "title" | "content" | "author";
export type SortType = "latest" | "comment_count" | "like_count";

export interface AuthFormState {
  username: string;
  password: string;
  display_name: string;
}

export interface PostFormState {
  title: string;
  content: string;
  tags: string;
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
