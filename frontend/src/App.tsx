import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  LogIn,
  LogOut,
  MessageSquarePlus,
  PenLine,
  RefreshCcw,
  Search,
  Send,
  Sparkles,
  Trash2,
} from "lucide-react";

import {
  clearToken,
  Comment,
  createComment,
  createPost,
  deleteComment,
  deletePost,
  findSimilarPosts,
  getStoredToken,
  listComments,
  listPosts,
  login,
  Post,
  PostListResponse,
  SimilarPostsResponse,
  storeToken,
  updateComment,
  updatePost,
} from "./api";

type PostForm = {
  title: string;
  content: string;
  tagsText: string;
};

const emptyPostForm: PostForm = { title: "", content: "", tagsText: "" };
const defaultPostList: PostListResponse = { items: [], total: 0, page: 1, size: 10, pages: 0 };
const emptySimilarPosts: SimilarPostsResponse = {
  summary: "",
  summary_error: null,
  items: [],
  message: "",
};

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function App() {
  const [token, setToken] = useState(getStoredToken);
  const [email, setEmail] = useState("member@sprint.local");
  const [password, setPassword] = useState("password123");
  const [posts, setPosts] = useState<Post[]>([]);
  const [postList, setPostList] = useState<PostListResponse>(defaultPostList);
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [postForm, setPostForm] = useState<PostForm>(emptyPostForm);
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [commentText, setCommentText] = useState("");
  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [searchText, setSearchText] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [page, setPage] = useState(1);
  const [message, setMessage] = useState("API 서버가 켜져 있으면 게시글을 불러옵니다.");
  const [isBusy, setIsBusy] = useState(false);
  const [similarPosts, setSimilarPosts] = useState<SimilarPostsResponse>(emptySimilarPosts);

  const selectedPost = useMemo(
    () => posts.find((post) => post.id === selectedPostId) ?? posts[0] ?? null,
    [posts, selectedPostId],
  );

  async function run(label: string, action: () => Promise<void>) {
    setIsBusy(true);
    setMessage(label);
    try {
      await action();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "요청 중 오류가 발생했습니다.");
    } finally {
      setIsBusy(false);
    }
  }

  function parseTags(value: string): string[] {
    const tags = value
      .split(",")
      .map((tag) => tag.trim().toLowerCase())
      .filter(Boolean);
    return [...new Set(tags)];
  }

  async function refreshPosts(nextSelectedId?: number, nextPage = page) {
    const nextPostList = await listPosts({
      page: nextPage,
      size: postList.size,
      q: searchText,
      tag: tagFilter,
    });
    setPostList(nextPostList);
    setPosts(nextPostList.items);
    setPage(nextPostList.page);
    setSelectedPostId(nextSelectedId ?? nextPostList.items[0]?.id ?? null);
  }

  async function refreshComments(postId: number | null) {
    if (postId === null) {
      setComments([]);
      return;
    }
    setComments(await listComments(postId));
  }

  useEffect(() => {
    void run("게시글을 불러오는 중입니다.", async () => {
      await refreshPosts(undefined, 1);
      setMessage("게시글 목록을 불러왔습니다.");
    });
  }, []);

  useEffect(() => {
    void refreshComments(selectedPost?.id ?? null);
  }, [selectedPost?.id]);

  function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void run("로그인 중입니다.", async () => {
      const tokens = await login(email, password);
      storeToken(tokens.access_token);
      setToken(tokens.access_token);
      setMessage("로그인했습니다.");
    });
  }

  function handleLogout() {
    clearToken();
    setToken("");
    setMessage("로컬 token을 지웠습니다.");
  }

  function handleSubmitPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void run(editingPostId ? "게시글을 수정하는 중입니다." : "게시글을 작성하는 중입니다.", async () => {
      const savedPost = editingPostId
        ? await updatePost(token, editingPostId, postForm.title, postForm.content, parseTags(postForm.tagsText))
        : await createPost(token, postForm.title, postForm.content, parseTags(postForm.tagsText));
      setPostForm(emptyPostForm);
      setEditingPostId(null);
      await refreshPosts(savedPost.id, page);
      setMessage(editingPostId ? "게시글을 수정했습니다." : "게시글을 작성했습니다.");
    });
  }

  function handleFindSimilarPosts() {
    void run("유사 게시글을 찾는 중입니다.", async () => {
      const result = await findSimilarPosts(
        token,
        postForm.title,
        postForm.content,
        parseTags(postForm.tagsText),
        3,
      );
      setSimilarPosts(result);
      setMessage(result.message);
    });
  }

  function startEditPost(post: Post) {
    setEditingPostId(post.id);
    setPostForm({ title: post.title, content: post.content, tagsText: post.tags.join(", ") });
    setSelectedPostId(post.id);
  }

  function handleDeletePost(postId: number) {
    void run("게시글을 삭제하는 중입니다.", async () => {
      await deletePost(token, postId);
      await refreshPosts(undefined, page);
      setMessage("게시글을 삭제했습니다.");
    });
  }

  function handleSubmitFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void run("검색 조건을 적용합니다.", async () => {
      await refreshPosts(undefined, 1);
      setMessage("검색 조건을 적용했습니다.");
    });
  }

  function movePage(nextPage: number) {
    void run(`${nextPage}페이지를 불러옵니다.`, async () => {
      await refreshPosts(undefined, nextPage);
      setMessage(`${nextPage}페이지를 불러왔습니다.`);
    });
  }

  function handleSubmitComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPost) {
      return;
    }
    void run(editingCommentId ? "댓글을 수정하는 중입니다." : "댓글을 작성하는 중입니다.", async () => {
      if (editingCommentId) {
        await updateComment(token, selectedPost.id, editingCommentId, commentText);
      } else {
        await createComment(token, selectedPost.id, commentText);
      }
      setCommentText("");
      setEditingCommentId(null);
      await refreshComments(selectedPost.id);
      setMessage(editingCommentId ? "댓글을 수정했습니다." : "댓글을 작성했습니다.");
    });
  }

  function startEditComment(comment: Comment) {
    setEditingCommentId(comment.id);
    setCommentText(comment.content);
  }

  function handleDeleteComment(commentId: number) {
    if (!selectedPost) {
      return;
    }
    void run("댓글을 삭제하는 중입니다.", async () => {
      await deleteComment(token, selectedPost.id, commentId);
      if (editingCommentId === commentId) {
        setEditingCommentId(null);
        setCommentText("");
      }
      await refreshComments(selectedPost.id);
      setMessage("댓글을 삭제했습니다.");
    });
  }

  return (
    <main className="shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Sprint 4 Board</p>
          <h1>RAG 유사 글 추천</h1>
        </div>
        <form className="login-panel" onSubmit={handleLogin}>
          <input
            aria-label="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="email"
            type="email"
          />
          <input
            aria-label="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="password"
            type="password"
          />
          <button type="submit" disabled={isBusy}>
            <LogIn size={16} />
            로그인
          </button>
          <button type="button" className="ghost" onClick={handleLogout}>
            <LogOut size={16} />
            로그아웃
          </button>
        </form>
      </section>

      <div className="status-row">
        <span className={token ? "status-dot active" : "status-dot"} />
        <span>{token ? "Bearer token 저장됨" : "로그인 필요"}</span>
        <button
          className="icon-button"
          type="button"
          title="게시글 새로고침"
          onClick={() => void run("게시글을 새로고침합니다.", () => refreshPosts(selectedPost?.id, page))}
        >
          <RefreshCcw size={16} />
        </button>
        <span className="message">{message}</span>
      </div>

      <section className="workspace">
        <aside className="post-list">
          <div className="section-heading">
            <h2>게시글 목록</h2>
            <span>{postList.total}</span>
          </div>
          <form className="filter-form" onSubmit={handleSubmitFilters}>
            <input
              aria-label="검색어"
              value={searchText}
              onChange={(event) => setSearchText(event.target.value)}
              placeholder="제목/본문 검색"
            />
            <input
              aria-label="태그 필터"
              value={tagFilter}
              onChange={(event) => setTagFilter(event.target.value)}
              placeholder="태그"
            />
            <button type="submit" disabled={isBusy}>
              <Search size={16} />
              검색
            </button>
          </form>
          <div className="list-scroll">
            {posts.map((post) => (
              <button
                key={post.id}
                className={selectedPost?.id === post.id ? "post-item selected" : "post-item"}
                type="button"
                onClick={() => setSelectedPostId(post.id)}
              >
                <strong>{post.title}</strong>
                {post.tags.length > 0 && (
                  <span className="tag-row">
                    {post.tags.map((tag) => (
                      <span className="tag-pill" key={tag}>
                        {tag}
                      </span>
                    ))}
                  </span>
                )}
                <span>{formatDate(post.created_at)}</span>
              </button>
            ))}
            {posts.length === 0 && <p className="empty">검색 결과가 없습니다.</p>}
          </div>
          <div className="pagination">
            <button
              className="icon-button"
              type="button"
              title="이전 페이지"
              disabled={page <= 1 || isBusy}
              onClick={() => movePage(page - 1)}
            >
              <ChevronLeft size={16} />
            </button>
            <span>
              {postList.pages === 0 ? 0 : page} / {postList.pages}
            </span>
            <button
              className="icon-button"
              type="button"
              title="다음 페이지"
              disabled={page >= postList.pages || isBusy}
              onClick={() => movePage(page + 1)}
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </aside>

        <section className="editor">
          <div className="section-heading">
            <h2>{editingPostId ? "게시글 수정" : "게시글 작성"}</h2>
            {editingPostId && (
              <button className="text-button" type="button" onClick={() => setEditingPostId(null)}>
                취소
              </button>
            )}
          </div>
          <form onSubmit={handleSubmitPost} className="stack-form">
            <input
              value={postForm.title}
              onChange={(event) => setPostForm({ ...postForm, title: event.target.value })}
              placeholder="제목"
              maxLength={120}
            />
            <textarea
              value={postForm.content}
              onChange={(event) => setPostForm({ ...postForm, content: event.target.value })}
              placeholder="내용"
              rows={8}
            />
            <input
              value={postForm.tagsText}
              onChange={(event) => setPostForm({ ...postForm, tagsText: event.target.value })}
              placeholder="태그, 쉼표로 구분"
            />
            <button type="submit" disabled={!token || isBusy}>
              <PenLine size={16} />
              {editingPostId ? "수정" : "작성"}
            </button>
          </form>
          <div className="rag-panel">
            <button
              className="ghost"
              type="button"
              disabled={!token || isBusy || !postForm.title.trim() || !postForm.content.trim()}
              onClick={handleFindSimilarPosts}
            >
              <Sparkles size={16} />
              유사 글 찾기
            </button>
            {similarPosts.summary && (
              <div className="rag-summary">
                <strong>AI 요약</strong>
                <p>{similarPosts.summary}</p>
                {similarPosts.summary_error && <span>요약 provider 오류: {similarPosts.summary_error}</span>}
              </div>
            )}
            {similarPosts.items.length > 0 && (
              <div className="similar-list">
                {similarPosts.items.map((item) => (
                  <button
                    key={item.post_id}
                    className={`similar-item ${item.similarity_level}`}
                    type="button"
                    onClick={() => setSelectedPostId(item.post_id)}
                  >
                    <span className="similar-score">{Math.round(item.similarity * 100)}%</span>
                    <strong>{item.title}</strong>
                    <p>{item.preview}</p>
                    {item.tags.length > 0 && (
                      <span className="tag-row">
                        {item.tags.map((tag) => (
                          <span className="tag-pill" key={tag}>
                            {tag}
                          </span>
                        ))}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
            {similarPosts.message && similarPosts.items.length === 0 && <p className="empty">{similarPosts.message}</p>}
          </div>
        </section>

        <section className="detail">
          <div className="section-heading">
            <h2>게시글 상세</h2>
            {selectedPost && (
              <div className="toolbar">
                <button className="icon-button" type="button" title="게시글 수정" onClick={() => startEditPost(selectedPost)}>
                  <PenLine size={16} />
                </button>
                <button
                  className="icon-button danger"
                  type="button"
                  title="게시글 삭제"
                  onClick={() => handleDeletePost(selectedPost.id)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            )}
          </div>
          {selectedPost ? (
            <>
              <article className="post-detail">
                <h3>{selectedPost.title}</h3>
                <time>{formatDate(selectedPost.created_at)}</time>
                {selectedPost.tags.length > 0 && (
                  <div className="tag-row">
                    {selectedPost.tags.map((tag) => (
                      <span className="tag-pill" key={tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                <p>{selectedPost.content}</p>
              </article>
              <div className="comments">
                <div className="section-heading compact">
                  <h2>댓글</h2>
                  <span>{comments.length}</span>
                </div>
                <form className="comment-form" onSubmit={handleSubmitComment}>
                  <input
                    value={commentText}
                    onChange={(event) => setCommentText(event.target.value)}
                    placeholder={editingCommentId ? "댓글 수정" : "댓글 입력"}
                  />
                  <button type="submit" disabled={!token || isBusy || !commentText.trim()}>
                    <Send size={16} />
                  </button>
                  {editingCommentId && (
                    <button
                      className="ghost"
                      type="button"
                      onClick={() => {
                        setEditingCommentId(null);
                        setCommentText("");
                      }}
                    >
                      취소
                    </button>
                  )}
                </form>
                <div className="comment-list">
                  {comments.map((comment) => (
                    <div className="comment-item" key={comment.id}>
                      <MessageSquarePlus size={16} />
                      <p>{comment.content}</p>
                      <time>{formatDate(comment.updated_at)}</time>
                      <div className="comment-actions">
                        <button
                          className="icon-button"
                          type="button"
                          title="댓글 수정"
                          onClick={() => startEditComment(comment)}
                        >
                          <PenLine size={14} />
                        </button>
                        <button
                          className="icon-button danger"
                          type="button"
                          title="댓글 삭제"
                          onClick={() => handleDeleteComment(comment.id)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                  {comments.length === 0 && <p className="empty">댓글이 없습니다.</p>}
                </div>
              </div>
            </>
          ) : (
            <p className="empty">게시글을 선택하거나 새로 작성하세요.</p>
          )}
        </section>
      </section>
    </main>
  );
}
