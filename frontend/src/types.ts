export type Tag = {
  id: number;
  name: string;
};

export type Post = {
  id: number;
  user_id: number | null;
  title: string;
  content: string;
  author_name: string;
  created_at: string;
  updated_at: string;
  tags: Tag[];
};

export type PostListResponse = {
  items: Post[];
  page: number;
  size: number;
  total: number;
  pages: number;
};

export type Comment = {
  id: number;
  post_id: number;
  user_id: number | null;
  content: string;
  author_name: string;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  csrf_token: string;
  session_id: string;
};

export type CurrentUser = {
  id: number;
  email: string;
  role: string;
  session_id: string;
};

export type RagMatch = {
  post_id: number;
  title: string;
  excerpt: string;
  score: number;
  duplicate_risk: "low" | "medium" | "high";
  summary: string;
  tags: Tag[];
};

export type RagReference = {
  title: string;
  url: string;
  source: string;
  excerpt: string;
};

export type RagAssistResponse = {
  embedding_dimensions: number;
  embedding_provider: string;
  embedding_model: string;
  llm_provider: string;
  llm_model: string;
  llm_used: boolean;
  stored_vectors: number;
  duplicate_warning: boolean;
  recommendation: string;
  matches: RagMatch[];
  references: RagReference[];
};

export type AgentWritingAssistResponse = {
  provider: string;
  model: string;
  mvp_highlight: {
    title: string;
    why_it_fits: string;
    why_highlight: string;
  };
  suggested_title: string;
  suggested_content: string;
  suggested_tag_names: string[];
  outline: string[];
  next_questions: string[];
  agent_steps: string[];
  confidence: number;
};

export type ApiError = {
  error?: {
    code?: string;
    message?: string;
  };
};

export type AuthMode = "login" | "signup";

export type AuthForm = {
  email: string;
  password: string;
};

export type DraftPost = {
  title: string;
  content: string;
  tagNames: string;
  referenceUrls: string;
};

export type PostFilters = {
  q: string;
  tag: string;
};

export type PostMeta = {
  page: number;
  size: number;
  total: number;
  pages: number;
};
