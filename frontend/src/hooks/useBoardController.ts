import { useEffect, useMemo, useRef, useState } from "react";
import type { Dispatch, FormEvent, SetStateAction } from "react";

import type {
  ApiErrorResponse,
  ApiResult,
  AuthFormState,
  AuthView,
  Comment,
  CommentFormState,
  FieldChangeEvent,
  LoadOptions,
  LoadPostsOptions,
  LoginResponse,
  PageMeta,
  Post,
  PostFormState,
  PostPage,
  RelatedPostsResponse,
  RelatedPostsState,
  RequestOptions,
  SearchState,
  SortType,
  StatusState,
  Tag,
  User,
} from "../types";
import {
  buildPostBody,
  buildPostQuery,
  buildRelatedPostsPayload,
  tagText,
} from "../utils/postFormatting";

const RELATED_POSTS_DEBOUNCE_MS = 3000;
const RELATED_POSTS_MIN_QUERY_LENGTH = 20;

type RelatedPostsScope = "compose" | "edit";

function emptyRelatedPostsState(): RelatedPostsState {
  return {
    items: [],
    isLoading: false,
    errorText: "",
  };
}

export function useBoardController() {
  const [authView, setAuthView] = useState<AuthView>(null);
  const [authForm, setAuthForm] = useState<AuthFormState>({
    username: "team1",
    password: "password123",
    display_name: "Team One",
  });
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [search, setSearch] = useState<SearchState>({
    q: "",
    search_type: "title_content",
    tag: "",
    sort: "latest",
    page: 1,
    size: 9,
  });
  const [pageMeta, setPageMeta] = useState<PageMeta>({
    page: 1,
    size: 9,
    total: 0,
    total_pages: 0,
  });
  const [postForm, setPostForm] = useState<PostFormState>({
    title: "Sprint 4 검색과 태그",
    content: "태그, 검색 타입, 페이징 흐름을 정리합니다.",
    tags: "fastapi, sprint",
  });
  const [editForm, setEditForm] = useState<PostFormState>({ title: "", content: "", tags: "" });
  const [composeRelatedPosts, setComposeRelatedPosts] = useState<RelatedPostsState>(
    emptyRelatedPostsState,
  );
  const [editRelatedPosts, setEditRelatedPosts] = useState<RelatedPostsState>(
    emptyRelatedPostsState,
  );
  const [isEditingPost, setIsEditingPost] = useState(false);
  const [commentForm, setCommentForm] = useState<CommentFormState>({ content: "좋은 정리입니다." });
  const [status, setStatus] = useState<StatusState>({
    text: "게시글을 불러오는 중",
    isError: false,
  });
  const relatedRequestIds = useRef<Record<RelatedPostsScope, number>>({ compose: 0, edit: 0 });
  const relatedRequestKeys = useRef<Record<RelatedPostsScope, string>>({ compose: "", edit: "" });

  const isAuthor = Boolean(currentUser && selectedPost?.author_id === currentUser.id);
  const selectedTagName = useMemo(
    () => tags.find((tag) => tag.name === search.tag)?.name || "",
    [tags, search.tag],
  );

  useEffect(() => {
    loadPosts({ quiet: true });
    loadTags({ quiet: true });
    loadMe({ quiet: true });
  }, []);

  useEffect(() => {
    return scheduleRelatedPosts("compose", postForm, null, isComposeOpen && Boolean(currentUser));
  }, [currentUser, isComposeOpen, postForm.content, postForm.tags, postForm.title]);

  useEffect(() => {
    return scheduleRelatedPosts(
      "edit",
      editForm,
      selectedPost?.id ?? null,
      isEditingPost && Boolean(currentUser) && Boolean(selectedPost),
    );
  }, [
    currentUser,
    editForm.content,
    editForm.tags,
    editForm.title,
    isEditingPost,
    selectedPost?.id,
  ]);

  function showLogin() {
    setAuthView("login");
  }

  function showRegister() {
    setAuthView("register");
  }

  function hideAuth() {
    setAuthView(null);
  }

  function updateAuthForm(event: FieldChangeEvent) {
    updateForm(setAuthForm, event);
  }

  function updatePostForm(event: FieldChangeEvent) {
    updateForm(setPostForm, event);
  }

  function updateEditForm(event: FieldChangeEvent) {
    updateForm(setEditForm, event);
  }

  function updateCommentForm(event: FieldChangeEvent) {
    updateForm(setCommentForm, event);
  }

  function updateSearch(event: FieldChangeEvent) {
    updateForm(setSearch, event);
  }

  function updateForm<T extends object>(
    setter: Dispatch<SetStateAction<T>>,
    event: FieldChangeEvent,
  ) {
    setter((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }) as T);
  }

  function setRelatedPostsState(scope: RelatedPostsScope, state: RelatedPostsState) {
    if (scope === "compose") {
      setComposeRelatedPosts(state);
      return;
    }
    setEditRelatedPosts(state);
  }

  function resetRelatedPosts(scope: RelatedPostsScope) {
    relatedRequestIds.current[scope] += 1;
    relatedRequestKeys.current[scope] = "";
    setRelatedPostsState(scope, emptyRelatedPostsState());
  }

  function buildRelatedRequestKey(form: PostFormState, excludePostId?: number | null) {
    const queryText = `${form.title.trim()} ${form.content.trim()}`.trim();
    if (queryText.length < RELATED_POSTS_MIN_QUERY_LENGTH) {
      return "";
    }
    return JSON.stringify(buildRelatedPostsPayload(form, excludePostId));
  }

  function scheduleRelatedPosts(
    scope: RelatedPostsScope,
    form: PostFormState,
    excludePostId: number | null,
    enabled: boolean,
  ) {
    if (!enabled) {
      resetRelatedPosts(scope);
      return;
    }

    const requestKey = buildRelatedRequestKey(form, excludePostId);
    if (!requestKey) {
      resetRelatedPosts(scope);
      return;
    }

    if (relatedRequestKeys.current[scope] === requestKey) {
      return;
    }

    const requestId = relatedRequestIds.current[scope] + 1;
    relatedRequestIds.current[scope] = requestId;
    relatedRequestKeys.current[scope] = "";
    setRelatedPostsState(scope, emptyRelatedPostsState());

    const timer = window.setTimeout(() => {
      void loadRelatedPosts(scope, form, excludePostId, requestKey, requestId);
    }, RELATED_POSTS_DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  }

  async function loadRelatedPosts(
    scope: RelatedPostsScope,
    form: PostFormState,
    excludePostId: number | null,
    requestKey: string,
    requestId: number,
  ) {
    setRelatedPostsState(scope, {
      items: [],
      isLoading: true,
      errorText: "",
    });

    try {
      const result = await request<RelatedPostsResponse>("/api/v1/ai/rag/related-posts", {
        method: "POST",
        body: JSON.stringify(buildRelatedPostsPayload(form, excludePostId)),
        quiet: true,
      });

      if (requestId !== relatedRequestIds.current[scope]) {
        return;
      }

      if (result.ok && Array.isArray(result.data.items)) {
        relatedRequestKeys.current[scope] = requestKey;
        setRelatedPostsState(scope, {
          items: result.data.items,
          isLoading: false,
          errorText: "",
        });
        return;
      }
    } catch {
      // Recommendation errors should not interrupt the writing flow.
    }

    if (requestId === relatedRequestIds.current[scope]) {
      relatedRequestKeys.current[scope] = requestKey;
      setRelatedPostsState(scope, {
        items: [],
        isLoading: false,
        errorText: "유사 게시글을 불러오지 못했습니다.",
      });
    }
  }

  function openPostEditor() {
    if (!selectedPost) {
      return;
    }
    setEditForm({
      title: selectedPost.title,
      content: selectedPost.content,
      tags: tagText(selectedPost.tags),
    });
    resetRelatedPosts("edit");
    setIsEditingPost(true);
  }

  function closePostEditor() {
    if (selectedPost) {
      setEditForm({
        title: selectedPost.title,
        content: selectedPost.content,
        tags: tagText(selectedPost.tags),
      });
    }
    resetRelatedPosts("edit");
    setIsEditingPost(false);
  }

  async function goToList() {
    setSelectedPost(null);
    setComments([]);
    setIsEditingPost(false);
    setIsComposeOpen(false);
    resetRelatedPosts("compose");
    resetRelatedPosts("edit");
    await loadPosts({ quiet: true });
  }

  function openCompose() {
    if (!currentUser) {
      showLogin();
      setStatus({ text: "게시글 작성은 로그인이 필요합니다.", isError: true });
      return;
    }
    resetRelatedPosts("compose");
    setIsComposeOpen(true);
  }

  function closeCompose() {
    resetRelatedPosts("compose");
    setIsComposeOpen(false);
  }

  async function register(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await request<User>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(authForm),
      successMessage: "계정 생성 완료. 로그인해주세요.",
    });
    if (result.ok) {
      showLogin();
    }
  }

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await request<LoginResponse>("/api/v1/auth/session/login", {
      method: "POST",
      body: JSON.stringify({
        username: authForm.username,
        password: authForm.password,
      }),
      successMessage: "로그인되었습니다.",
    });
    if (result.ok) {
      setCurrentUser(result.data.user);
      hideAuth();
      await loadPosts({ quiet: true });
    }
  }

  async function loadMe(options: LoadOptions = {}) {
    const result = await request<User>("/api/v1/auth/session/me", {
      quiet: options.quiet,
      successMessage: "현재 사용자 정보를 확인했습니다.",
    });
    if (result.ok) {
      setCurrentUser(result.data);
    }
  }

  async function logout() {
    const result = await request<Record<string, never>>("/api/v1/auth/session/logout", {
      method: "POST",
      successMessage: "로그아웃되었습니다.",
    });
    if (result.ok) {
      setCurrentUser(null);
      hideAuth();
      setIsEditingPost(false);
      setIsComposeOpen(false);
      resetRelatedPosts("compose");
      resetRelatedPosts("edit");
    }
  }

  async function loadTags(options: LoadOptions = {}) {
    const result = await request<Tag[]>("/api/v1/tags", {
      quiet: options.quiet,
      successMessage: "태그 목록을 불러왔습니다.",
    });
    if (result.ok && Array.isArray(result.data)) {
      setTags(result.data);
    }
  }

  async function loadPosts(options: LoadPostsOptions = {}) {
    const nextSearch = {
      ...search,
      ...(options.filters || {}),
    };
    setSearch(nextSearch);

    const result = await request<PostPage>(`/api/v1/posts?${buildPostQuery(nextSearch)}`, {
      quiet: options.quiet,
      successMessage: "게시글 목록을 불러왔습니다.",
    });
    if (result.ok && Array.isArray(result.data.items)) {
      setPosts(result.data.items);
      setPageMeta({
        page: result.data.page,
        size: result.data.size,
        total: result.data.total,
        total_pages: result.data.total_pages,
      });
    }
  }

  async function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadPosts({ filters: { page: 1 } });
  }

  async function filterByTag(tagName: string) {
    await loadPosts({
      filters: {
        tag: search.tag === tagName ? "" : tagName,
        page: 1,
      },
    });
  }

  async function clearFilters() {
    await loadPosts({
      filters: {
        q: "",
        search_type: "title_content",
        tag: "",
        sort: "latest",
        page: 1,
      },
    });
  }

  async function changeSort(event: FieldChangeEvent) {
    await loadPosts({
      filters: {
        sort: event.target.value as SortType,
        page: 1,
      },
    });
  }

  async function changePage(nextPage: number) {
    await loadPosts({ filters: { page: nextPage } });
  }

  async function selectPost(post: Post) {
    const result = await request<Post>(`/api/v1/posts/${post.id}`, {
      successMessage: "게시글 상세를 불러왔습니다.",
    });
    if (result.ok) {
      setSelectedPost(result.data);
      setEditForm({
        title: result.data.title,
        content: result.data.content,
        tags: tagText(result.data.tags),
      });
      setIsEditingPost(false);
      setIsComposeOpen(false);
      resetRelatedPosts("compose");
      resetRelatedPosts("edit");
      await loadComments(result.data.id, { quiet: true });
    }
  }

  async function createPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!currentUser) {
      showLogin();
      setStatus({ text: "게시글 작성은 로그인이 필요합니다.", isError: true });
      return;
    }

    const result = await request<Post>("/api/v1/posts", {
      method: "POST",
      body: buildPostBody(postForm),
      successMessage: "게시글을 작성했습니다.",
    });
    if (result.ok) {
      setPostForm({ title: "", content: "", tags: "" });
      setSelectedPost(result.data);
      setIsComposeOpen(false);
      resetRelatedPosts("compose");
      setEditForm({
        title: result.data.title,
        content: result.data.content,
        tags: tagText(result.data.tags),
      });
      setIsEditingPost(false);
      await loadTags({ quiet: true });
      await loadPosts({ quiet: true, filters: { page: 1 } });
      await loadComments(result.data.id, { quiet: true });
    }
  }

  async function updatePost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPost) {
      setStatus({ text: "수정할 게시글을 선택하세요.", isError: true });
      return;
    }

    const result = await request<Post>(`/api/v1/posts/${selectedPost.id}`, {
      method: "PATCH",
      body: buildPostBody(editForm),
      successMessage: "게시글을 수정했습니다.",
    });
    if (result.ok) {
      setSelectedPost(result.data);
      setEditForm({
        title: result.data.title,
        content: result.data.content,
        tags: tagText(result.data.tags),
      });
      resetRelatedPosts("edit");
      setIsEditingPost(false);
      await loadTags({ quiet: true });
      await loadPosts({ quiet: true });
    }
  }

  async function deletePost() {
    if (!selectedPost) {
      setStatus({ text: "삭제할 게시글을 선택하세요.", isError: true });
      return;
    }
    if (!window.confirm("게시글과 연결된 댓글을 모두 삭제할까요?")) {
      return;
    }

    const result = await request<Record<string, never>>(`/api/v1/posts/${selectedPost.id}`, {
      method: "DELETE",
      successMessage: "게시글을 삭제했습니다.",
    });
    if (result.ok) {
      setSelectedPost(null);
      setComments([]);
      setEditForm({ title: "", content: "", tags: "" });
      setIsEditingPost(false);
      resetRelatedPosts("edit");
      await loadTags({ quiet: true });
      await loadPosts({ quiet: true });
    }
  }

  async function loadComments(postId = selectedPost?.id, options: LoadOptions = {}) {
    if (!postId) {
      return;
    }
    const result = await request<Comment[]>(`/api/v1/posts/${postId}/comments`, {
      quiet: options.quiet,
      successMessage: "댓글을 불러왔습니다.",
    });
    if (result.ok && Array.isArray(result.data)) {
      setComments(result.data);
      setSelectedPost((current) =>
        current?.id === postId ? { ...current, comment_count: result.data.length } : current,
      );
    }
  }

  async function createComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!currentUser) {
      showLogin();
      setStatus({ text: "댓글 작성은 로그인이 필요합니다.", isError: true });
      return;
    }
    if (!selectedPost) {
      setStatus({ text: "댓글을 작성할 게시글을 선택하세요.", isError: true });
      return;
    }

    const result = await request<Comment>(`/api/v1/posts/${selectedPost.id}/comments`, {
      method: "POST",
      body: JSON.stringify(commentForm),
      successMessage: "댓글을 작성했습니다.",
    });
    if (result.ok) {
      setCommentForm({ content: "" });
      await loadComments(selectedPost.id, { quiet: true });
    }
  }

  async function likePost() {
    if (!selectedPost) {
      return;
    }
    if (!currentUser) {
      showLogin();
      setStatus({ text: "좋아요는 로그인이 필요합니다.", isError: true });
      return;
    }

    const result = await request<Post>(`/api/v1/posts/${selectedPost.id}/like`, {
      method: "POST",
      successMessage: "좋아요를 반영했습니다.",
    });
    if (result.ok) {
      setSelectedPost(result.data);
      await loadPosts({ quiet: true });
    }
  }

  async function deleteComment(commentId: number) {
    const result = await request<Record<string, never>>(`/api/v1/comments/${commentId}`, {
      method: "DELETE",
      successMessage: "댓글을 삭제했습니다.",
    });
    if (result.ok && selectedPost) {
      await loadComments(selectedPost.id, { quiet: true });
    }
  }

  async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
    if (!options.quiet) {
      setStatus({ text: "요청 중", isError: false });
    }

    const response = await fetch(endpoint, {
      method: options.method ?? "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
      },
      body: options.body,
    });

    const text = await response.text();
    const data = (text ? JSON.parse(text) : {}) as T & ApiErrorResponse;
    if (!options.quiet) {
      const message = response.ok
        ? options.successMessage || "완료"
        : data.error?.message || "요청에 실패했습니다.";
      setStatus({ text: message, isError: !response.ok });
    }
    return { ok: response.ok, status: response.status, data };
  }

  return {
    authView,
    authForm,
    currentUser,
    posts,
    tags,
    selectedPost,
    isComposeOpen,
    comments,
    search,
    pageMeta,
    postForm,
    editForm,
    composeRelatedPosts,
    editRelatedPosts,
    isEditingPost,
    commentForm,
    status,
    isAuthor,
    selectedTagName,
    showLogin,
    showRegister,
    hideAuth,
    updateAuthForm,
    updatePostForm,
    updateEditForm,
    updateCommentForm,
    updateSearch,
    openPostEditor,
    closePostEditor,
    goToList,
    openCompose,
    closeCompose,
    register,
    login,
    logout,
    submitSearch,
    filterByTag,
    clearFilters,
    changeSort,
    changePage,
    selectPost,
    createPost,
    updatePost,
    deletePost,
    loadComments,
    createComment,
    likePost,
    deleteComment,
  };
}
