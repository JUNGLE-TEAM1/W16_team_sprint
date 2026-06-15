import { useEffect, useMemo, useState } from "react";

const CARD_THEMES = [
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

const SEARCH_TYPES = [
  { value: "title_content", label: "제목 + 내용" },
  { value: "title", label: "제목" },
  { value: "content", label: "내용" },
  { value: "author", label: "작성자" },
];

const SORT_TYPES = [
  { value: "latest", label: "최신순" },
  { value: "comment_count", label: "댓글 많은 순" },
  { value: "like_count", label: "좋아요 많은 순" },
];

function formatDate(value) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat("ko-KR", {
    month: "long",
    day: "numeric",
  }).format(new Date(value));
}

function excerpt(value, maxLength = 110) {
  if (!value || value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength).trim()}...`;
}

function parseTags(value) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function tagText(tags) {
  return Array.isArray(tags) ? tags.join(", ") : "";
}

export default function App() {
  const [authView, setAuthView] = useState(null);
  const [authForm, setAuthForm] = useState({
    username: "team1",
    password: "password123",
    display_name: "Team One",
  });
  const [currentUser, setCurrentUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [tags, setTags] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [comments, setComments] = useState([]);
  const [search, setSearch] = useState({
    q: "",
    search_type: "title_content",
    tag: "",
    sort: "latest",
    page: 1,
    size: 9,
  });
  const [pageMeta, setPageMeta] = useState({
    page: 1,
    size: 9,
    total: 0,
    total_pages: 0,
  });
  const [postForm, setPostForm] = useState({
    title: "Sprint 4 검색과 태그",
    content: "태그, 검색 타입, 페이징 흐름을 정리합니다.",
    tags: "fastapi, sprint",
  });
  const [editForm, setEditForm] = useState({ title: "", content: "", tags: "" });
  const [isEditingPost, setIsEditingPost] = useState(false);
  const [commentForm, setCommentForm] = useState({ content: "좋은 정리입니다." });
  const [status, setStatus] = useState({ text: "게시글을 불러오는 중", isError: false });

  const isAuthor = currentUser && selectedPost?.author_id === currentUser.id;
  const selectedTagName = useMemo(
    () => tags.find((tag) => tag.name === search.tag)?.name || "",
    [tags, search.tag],
  );

  useEffect(() => {
    loadPosts({ quiet: true });
    loadTags({ quiet: true });
    loadMe({ quiet: true });
  }, []);

  function updateAuthForm(event) {
    setAuthForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  function updatePostForm(event) {
    setPostForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  function updateEditForm(event) {
    setEditForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  function updateCommentForm(event) {
    setCommentForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
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
    setIsEditingPost(false);
  }

  async function goToList() {
    setSelectedPost(null);
    setComments([]);
    setIsEditingPost(false);
    setIsComposeOpen(false);
    await loadPosts({ quiet: true });
  }

  function openCompose() {
    if (!currentUser) {
      setAuthView("login");
      setStatus({ text: "게시글 작성은 로그인이 필요합니다.", isError: true });
      return;
    }
    setIsComposeOpen(true);
  }

  function closeCompose() {
    setIsComposeOpen(false);
  }

  function updateSearch(event) {
    setSearch((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  function buildPostBody(form) {
    return JSON.stringify({
      title: form.title,
      content: form.content,
      tags: parseTags(form.tags),
    });
  }

  function postQuery(nextSearch) {
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

  async function register(event) {
    event.preventDefault();
    const result = await request("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(authForm),
      successMessage: "계정 생성 완료. 로그인해주세요.",
    });
    if (result.ok) {
      setAuthView("login");
    }
  }

  async function login(event) {
    event.preventDefault();
    const result = await request("/api/v1/auth/session/login", {
      method: "POST",
      body: JSON.stringify({
        username: authForm.username,
        password: authForm.password,
      }),
      successMessage: "로그인되었습니다.",
    });
    if (result.ok) {
      setCurrentUser(result.data.user);
      setAuthView(null);
      await loadPosts({ quiet: true });
    }
  }

  async function loadMe(options = {}) {
    const result = await request("/api/v1/auth/session/me", {
      quiet: options.quiet,
      successMessage: "현재 사용자 정보를 확인했습니다.",
    });
    if (result.ok) {
      setCurrentUser(result.data);
    }
  }

  async function logout() {
    const result = await request("/api/v1/auth/session/logout", {
      method: "POST",
      successMessage: "로그아웃되었습니다.",
    });
    if (result.ok) {
      setCurrentUser(null);
      setAuthView(null);
      setIsEditingPost(false);
      setIsComposeOpen(false);
    }
  }

  async function loadTags(options = {}) {
    const result = await request("/api/v1/tags", {
      quiet: options.quiet,
      successMessage: "태그 목록을 불러왔습니다.",
    });
    if (result.ok && Array.isArray(result.data)) {
      setTags(result.data);
    }
  }

  async function loadPosts(options = {}) {
    const nextSearch = {
      ...search,
      ...(options.filters || {}),
    };
    setSearch(nextSearch);

    const result = await request(`/api/v1/posts?${postQuery(nextSearch)}`, {
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

  async function submitSearch(event) {
    event.preventDefault();
    await loadPosts({ filters: { page: 1 } });
  }

  async function filterByTag(tagName) {
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

  async function changeSort(event) {
    await loadPosts({
      filters: {
        sort: event.target.value,
        page: 1,
      },
    });
  }

  async function changePage(nextPage) {
    await loadPosts({ filters: { page: nextPage } });
  }

  async function selectPost(post) {
    const result = await request(`/api/v1/posts/${post.id}`, {
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
      await loadComments(result.data.id, { quiet: true });
    }
  }

  async function createPost(event) {
    event.preventDefault();
    if (!currentUser) {
      setAuthView("login");
      setStatus({ text: "게시글 작성은 로그인이 필요합니다.", isError: true });
      return;
    }

    const result = await request("/api/v1/posts", {
      method: "POST",
      body: buildPostBody(postForm),
      successMessage: "게시글을 작성했습니다.",
    });
    if (result.ok) {
      setPostForm({ title: "", content: "", tags: "" });
      setSelectedPost(result.data);
      setIsComposeOpen(false);
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

  async function updatePost(event) {
    event.preventDefault();
    if (!selectedPost) {
      setStatus({ text: "수정할 게시글을 선택하세요.", isError: true });
      return;
    }

    const result = await request(`/api/v1/posts/${selectedPost.id}`, {
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

    const result = await request(`/api/v1/posts/${selectedPost.id}`, {
      method: "DELETE",
      successMessage: "게시글을 삭제했습니다.",
    });
    if (result.ok) {
      setSelectedPost(null);
      setComments([]);
      setEditForm({ title: "", content: "", tags: "" });
      setIsEditingPost(false);
      await loadTags({ quiet: true });
      await loadPosts({ quiet: true });
    }
  }

  async function loadComments(postId = selectedPost?.id, options = {}) {
    if (!postId) {
      return;
    }
    const result = await request(`/api/v1/posts/${postId}/comments`, {
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

  async function createComment(event) {
    event.preventDefault();
    if (!currentUser) {
      setAuthView("login");
      setStatus({ text: "댓글 작성은 로그인이 필요합니다.", isError: true });
      return;
    }
    if (!selectedPost) {
      setStatus({ text: "댓글을 작성할 게시글을 선택하세요.", isError: true });
      return;
    }

    const result = await request(`/api/v1/posts/${selectedPost.id}/comments`, {
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
      setAuthView("login");
      setStatus({ text: "좋아요는 로그인이 필요합니다.", isError: true });
      return;
    }

    const result = await request(`/api/v1/posts/${selectedPost.id}/like`, {
      method: "POST",
      successMessage: "좋아요를 반영했습니다.",
    });
    if (result.ok) {
      setSelectedPost(result.data);
      await loadPosts({ quiet: true });
    }
  }

  async function deleteComment(commentId) {
    const result = await request(`/api/v1/comments/${commentId}`, {
      method: "DELETE",
      successMessage: "댓글을 삭제했습니다.",
    });
    if (result.ok) {
      await loadComments(selectedPost.id, { quiet: true });
    }
  }

  async function request(endpoint, options = {}) {
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
    const data = text ? JSON.parse(text) : {};
    if (!options.quiet) {
      const message = response.ok
        ? options.successMessage || "완료"
        : data.error?.message || "요청에 실패했습니다.";
      setStatus({ text: message, isError: !response.ok });
    }
    return { ok: response.ok, status: response.status, data };
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand-button" type="button" onClick={goToList}>
          <span className="brand-symbol">AI</span>
          <span>지식 공유 게시판</span>
        </button>

        <nav className="top-actions" aria-label="계정 메뉴">
          {currentUser ? (
            <>
              <span className="user-chip">{currentUser.display_name}</span>
              <button className="nav-button" type="button" onClick={logout}>
                로그아웃
              </button>
            </>
          ) : (
            <>
              <button className="nav-button" type="button" onClick={() => setAuthView("login")}>
                로그인
              </button>
              <button
                className="nav-button primary-nav"
                type="button"
                onClick={() => setAuthView("register")}
              >
                회원가입
              </button>
            </>
          )}
        </nav>
      </header>

      {authView ? (
        <section className="auth-card" aria-label={authView === "login" ? "로그인" : "회원가입"}>
          <div className="section-heading compact-heading">
            <div>
              <p className="eyebrow">Account</p>
              <h2>{authView === "login" ? "로그인" : "회원가입"}</h2>
            </div>
            <button className="ghost-button" type="button" onClick={() => setAuthView(null)}>
              닫기
            </button>
          </div>

          <form className="inline-form" onSubmit={authView === "login" ? login : register}>
            <label className="field">
              <span>Username</span>
              <input
                name="username"
                autoComplete="username"
                value={authForm.username}
                onChange={updateAuthForm}
                required
              />
            </label>

            <label className="field">
              <span>Password</span>
              <input
                name="password"
                type="password"
                autoComplete={authView === "login" ? "current-password" : "new-password"}
                value={authForm.password}
                onChange={updateAuthForm}
                required
              />
            </label>

            {authView === "register" ? (
              <label className="field">
                <span>Display name</span>
                <input
                  name="display_name"
                  autoComplete="name"
                  value={authForm.display_name}
                  onChange={updateAuthForm}
                  required
                />
              </label>
            ) : null}

            <button className="submit-button" type="submit">
              {authView === "login" ? "로그인" : "계정 생성"}
            </button>
          </form>
        </section>
      ) : null}

      <main>
        {selectedPost ? (
          <>
            <div className={`status ${status.isError ? "is-error" : ""}`} role="status">
              <span className="status-dot" aria-hidden="true" />
              <span>{status.text}</span>
            </div>

            <section className="detail-page" aria-label="게시글 상세">
              <article className="panel detail-panel">
                <div className="section-heading compact-heading">
                  <div>
                    <p className="eyebrow">Read</p>
                    <h2>{selectedPost.title}</h2>
                  </div>
                  <div className="section-actions">
                    <button className="ghost-button" type="button" onClick={goToList}>
                      목록으로
                    </button>
                    <button className="ghost-button" type="button" onClick={() => loadComments()}>
                      댓글 새로고침
                    </button>
                  </div>
                </div>

                <div className="post-detail">
                  <p>{selectedPost.content}</p>
                  <div className="card-tags">
                    {(selectedPost.tags ?? []).map((tag) => (
                      <span key={tag}>#{tag}</span>
                    ))}
                  </div>
                  <div className="card-meta">
                    <span>{formatDate(selectedPost.created_at)}</span>
                    <span>by {selectedPost.author_display_name}</span>
                  </div>
                  <div className="card-stats detail-stats">
                    <span>댓글 {selectedPost.comment_count ?? comments.length}개</span>
                    <span>좋아요 {selectedPost.like_count ?? 0}개</span>
                  </div>
                  <div className="like-actions">
                    <button className="like-button" type="button" onClick={likePost}>
                      좋아요
                    </button>
                  </div>
                  {isAuthor ? (
                    <div className="detail-actions" aria-label="게시글 관리">
                      <button className="ghost-button" type="button" onClick={openPostEditor}>
                        수정
                      </button>
                      <button className="danger-button" type="button" onClick={deletePost}>
                        삭제
                      </button>
                    </div>
                  ) : null}
                </div>

                {isAuthor && isEditingPost ? (
                  <form className="stack-form edit-form" onSubmit={updatePost} aria-label="게시글 수정">
                    <label className="field">
                      <span>Edit title</span>
                      <input name="title" value={editForm.title} onChange={updateEditForm} />
                    </label>
                    <label className="field">
                      <span>Edit content</span>
                      <textarea name="content" value={editForm.content} onChange={updateEditForm} />
                    </label>
                    <label className="field">
                      <span>Edit tags</span>
                      <input name="tags" value={editForm.tags} onChange={updateEditForm} />
                    </label>
                    <div className="split-actions">
                      <button className="submit-button" type="submit">
                        수정 완료
                      </button>
                      <button className="ghost-button" type="button" onClick={closePostEditor}>
                        취소
                      </button>
                    </div>
                  </form>
                ) : null}

                <div className="comments-area">
                  <div className="comments-head">
                    <h3>댓글</h3>
                    <span>{comments.length}개</span>
                  </div>

                  {comments.length > 0 ? (
                    <div className="comment-list">
                      {comments.map((comment) => (
                        <article className="comment-item" key={comment.id}>
                          <div>
                            <strong>{comment.author_display_name}</strong>
                            <p>{comment.content}</p>
                          </div>
                          {currentUser?.id === comment.author_id ? (
                            <button
                              className="text-danger"
                              type="button"
                              onClick={() => deleteComment(comment.id)}
                            >
                              삭제
                            </button>
                          ) : null}
                        </article>
                      ))}
                    </div>
                  ) : (
                    <p className="muted-text">아직 댓글이 없습니다.</p>
                  )}

                  {currentUser ? (
                    <form className="comment-form" onSubmit={createComment}>
                      <label className="field">
                        <span>Comment</span>
                        <textarea
                          name="content"
                          value={commentForm.content}
                          onChange={updateCommentForm}
                          maxLength={1000}
                          required
                        />
                      </label>
                      <button className="submit-button" type="submit">
                        댓글 작성
                      </button>
                    </form>
                  ) : (
                    <div className="locked-panel compact-lock">
                      <span>댓글 작성은 로그인이 필요합니다.</span>
                      <button className="pill-button" type="button" onClick={() => setAuthView("login")}>
                        로그인
                      </button>
                    </div>
                  )}
                </div>
              </article>
            </section>
          </>
        ) : (
          <>
            <section className="hero" aria-label="서비스 소개">
              <p className="eyebrow">Knowledge Sprint Board</p>
              <h1>AI 지식 공유 게시판</h1>
              <p>
                태그로 분류하고, 검색 타입을 선택하고, 페이지 단위로 학습 노트를 탐색합니다.
              </p>
              <form className="search-bar" onSubmit={submitSearch}>
                <select name="search_type" value={search.search_type} onChange={updateSearch}>
                  {SEARCH_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                <input
                  name="q"
                  value={search.q}
                  onChange={updateSearch}
                  placeholder="검색어를 입력하세요"
                />
                <button className="submit-button" type="submit">
                  검색
                </button>
              </form>
              <div className="hero-actions">
                <button className="pill-button" type="button" onClick={clearFilters}>
                  필터 초기화
                </button>
              </div>
            </section>

            <div className={`status ${status.isError ? "is-error" : ""}`} role="status">
              <span className="status-dot" aria-hidden="true" />
              <span>{status.text}</span>
            </div>

            <section className="tag-filter" aria-label="태그 필터">
              <div className="tag-filter-head">
                <span>태그 필터</span>
                {selectedTagName ? <strong>선택됨: #{selectedTagName}</strong> : null}
              </div>
              <div className="tag-row">
                {tags.length > 0 ? (
                  tags.map((tag) => (
                    <button
                      className={`tag-button ${search.tag === tag.name ? "is-active" : ""}`}
                      key={tag.id}
                      type="button"
                      onClick={() => filterByTag(tag.name)}
                    >
                      #{tag.name}
                    </button>
                  ))
                ) : (
                  <span className="muted-text">아직 등록된 태그가 없습니다.</span>
                )}
              </div>
            </section>

            <section className="posts-section" aria-label="게시글 목록">
              <div className="section-heading list-heading">
                <div>
                  <p className="eyebrow">Latest Posts</p>
                  <h2>현재까지 작성된 게시글</h2>
                </div>
                <div className="section-actions">
                  <span className="count-chip">
                    {pageMeta.total}개 · {pageMeta.page}/{pageMeta.total_pages || 1} 페이지
                  </span>
                  <label className="sort-control">
                    <span>정렬</span>
                    <select name="sort" value={search.sort} onChange={changeSort}>
                      {SORT_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button className="submit-button compact-button" type="button" onClick={openCompose}>
                    새 글 작성
                  </button>
                </div>
              </div>

              {posts.length > 0 ? (
                <div className="post-grid">
                  {posts.map((post, index) => (
                    <article
                      className="post-card"
                      key={post.id}
                      tabIndex={0}
                      onClick={() => selectPost(post)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter") {
                          selectPost(post);
                        }
                      }}
                    >
                      <div className={`card-visual ${CARD_THEMES[index % CARD_THEMES.length]}`}>
                        <span>{String((pageMeta.page - 1) * pageMeta.size + index + 1).padStart(2, "0")}</span>
                        <strong>{post.title.slice(0, 1).toUpperCase()}</strong>
                      </div>
                      <div className="card-body">
                        <h3>{post.title}</h3>
                        <p>{excerpt(post.content)}</p>
                        <div className="card-tags">
                          {(post.tags ?? []).map((tag) => (
                            <span key={tag}>#{tag}</span>
                          ))}
                        </div>
                        <div className="card-stats">
                          <span>댓글 {post.comment_count ?? 0}개</span>
                          <span>좋아요 {post.like_count ?? 0}개</span>
                        </div>
                        <div className="card-meta">
                          <span>{formatDate(post.created_at)}</span>
                          <span>by {post.author_display_name}</span>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <strong>조건에 맞는 게시글이 없습니다.</strong>
                  <span>검색어 또는 태그 필터를 조정해보세요.</span>
                </div>
              )}

              <div className="pagination">
                <button
                  className="pill-button"
                  type="button"
                  disabled={pageMeta.page <= 1}
                  onClick={() => changePage(pageMeta.page - 1)}
                >
                  이전
                </button>
                <span>
                  page {pageMeta.page} / {pageMeta.total_pages || 1}
                </span>
                <button
                  className="pill-button"
                  type="button"
                  disabled={pageMeta.total_pages === 0 || pageMeta.page >= pageMeta.total_pages}
                  onClick={() => changePage(pageMeta.page + 1)}
                >
                  다음
                </button>
              </div>
            </section>

            {isComposeOpen ? (
              <div className="modal-backdrop">
                <section
                  className="modal-panel"
                  role="dialog"
                  aria-modal="true"
                  aria-label="새 게시글 작성"
                >
                  <div className="section-heading compact-heading">
                    <div>
                      <p className="eyebrow">Write</p>
                      <h2>새 게시글 작성</h2>
                    </div>
                    <button className="ghost-button" type="button" onClick={closeCompose}>
                      닫기
                    </button>
                  </div>

                  <form className="stack-form" onSubmit={createPost}>
                    <label className="field">
                      <span>Title</span>
                      <input
                        name="title"
                        value={postForm.title}
                        onChange={updatePostForm}
                        maxLength={120}
                        required
                      />
                    </label>
                    <label className="field">
                      <span>Content</span>
                      <textarea
                        name="content"
                        value={postForm.content}
                        onChange={updatePostForm}
                        maxLength={10000}
                        required
                      />
                    </label>
                    <label className="field">
                      <span>Tags</span>
                      <input
                        name="tags"
                        value={postForm.tags}
                        onChange={updatePostForm}
                        placeholder="fastapi, auth, sprint"
                      />
                    </label>
                    <button className="submit-button" type="submit">
                      게시글 작성
                    </button>
                  </form>
                </section>
              </div>
            ) : null}
          </>
        )}
      </main>
    </div>
  );
}
