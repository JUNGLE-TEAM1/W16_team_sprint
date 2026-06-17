import React from "react";
import { createRoot } from "react-dom/client";
import {
  Bot,
  ChevronLeft,
  ChevronRight,
  FileText,
  LogIn,
  LogOut,
  MessageSquare,
  Mic,
  Pencil,
  PhoneOff,
  RefreshCw,
  Save,
  Search,
  Send,
  Trash2,
  UserPlus,
  X,
} from "lucide-react";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function parseSseBlock(block) {
  const lines = block.split("\n");
  const eventLine = lines.find((line) => line.startsWith("event:"));
  const dataLines = lines.filter((line) => line.startsWith("data:"));
  if (!eventLine || dataLines.length === 0) return null;

  return {
    event: eventLine.replace("event:", "").trim(),
    data: JSON.parse(dataLines.map((line) => line.replace("data:", "").trim()).join("\n")),
  };
}

function App() {
  const [posts, setPosts] = React.useState([]);
  const [selectedPost, setSelectedPost] = React.useState(null);
  const [currentUser, setCurrentUser] = React.useState(() => localStorage.getItem("annalsUsername") || "");
  const [authMode, setAuthMode] = React.useState("login");
  const [authForm, setAuthForm] = React.useState({ username: "", password: "" });
  const [authLoading, setAuthLoading] = React.useState(false);
  const [authError, setAuthError] = React.useState("");
  const [postSearch, setPostSearch] = React.useState("");
  const [selectedTag, setSelectedTag] = React.useState("");
  const [postPageInfo, setPostPageInfo] = React.useState({
    total: 0,
    page: 1,
    size: 10,
    pages: 1,
  });
  const [form, setForm] = React.useState({
    title: "태조 즉위 과정은 어떻게 기록되어 있나?",
    question: "태조 이성계가 왕위에 오르는 과정에서 실록은 어떤 명분과 장면을 강조하나요?",
  });
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const loadPost = React.useCallback(async (id) => {
    const response = await fetch(`${API_BASE_URL}/posts/${id}`);
    if (!response.ok) throw new Error("게시글 상세를 불러오지 못했습니다.");
    const data = await response.json();
    setSelectedPost(data);
  }, []);

  const loadPosts = React.useCallback(
    async ({ page = 1, query = postSearch, tag = selectedTag, selectFirst = false, keepSelection = false } = {}) => {
      const params = new URLSearchParams({
        page: String(page),
        size: String(postPageInfo.size),
      });
      const normalizedQuery = query.trim();
      if (normalizedQuery) {
        params.set("q", normalizedQuery);
      }
      const normalizedTag = tag.trim();
      if (normalizedTag) {
        params.set("tag", normalizedTag);
      }

      const response = await fetch(`${API_BASE_URL}/posts?${params.toString()}`);
      if (!response.ok) throw new Error("게시글 목록을 불러오지 못했습니다.");
      const data = await response.json();
      setPosts(data.items);
      setPostPageInfo({
        total: data.total,
        page: data.page,
        size: data.size,
        pages: data.pages,
      });

      if (keepSelection) return;
      if ((selectFirst || !selectedPost) && data.items.length > 0) {
        await loadPost(data.items[0].id);
      }
      if (selectFirst && data.items.length === 0) {
        setSelectedPost(null);
      }
    },
    [loadPost, postPageInfo.size, postSearch, selectedPost, selectedTag],
  );

  React.useEffect(() => {
    loadPosts().catch((err) => setError(err.message));
  }, []);

  const searchPosts = async (event) => {
    event.preventDefault();
    setError("");
    setSelectedTag("");
    try {
      await loadPosts({ page: 1, query: postSearch, tag: "", selectFirst: true });
    } catch (err) {
      setError(err.message);
    }
  };

  const changePostPage = async (nextPage) => {
    setError("");
    try {
      await loadPosts({ page: nextPage, query: postSearch, tag: selectedTag, selectFirst: true });
    } catch (err) {
      setError(err.message);
    }
  };

  const filterByTag = async (tag) => {
    setError("");
    setSelectedTag(tag);
    setPostSearch("");
    try {
      await loadPosts({ page: 1, query: "", tag, selectFirst: true });
    } catch (err) {
      setError(err.message);
    }
  };

  const clearTagFilter = async () => {
    setError("");
    setSelectedTag("");
    try {
      await loadPosts({ page: 1, query: postSearch, tag: "", selectFirst: true });
    } catch (err) {
      setError(err.message);
    }
  };

  const createPost = async (event) => {
    event.preventDefault();
    if (!currentUser) {
      setError("게시글을 작성하려면 먼저 로그인하세요.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/posts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, username: currentUser }),
      });
      if (!response.ok) {
        const detail = await response.json();
        throw new Error(detail.detail || "게시글 생성에 실패했습니다.");
      }
      const data = await response.json();
      setSelectedPost(data);
      setPostSearch("");
      setSelectedTag("");
      await loadPosts({ page: 1, query: "", tag: "", keepSelection: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deletePost = React.useCallback(
    async (postId) => {
      const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        const detail = await response.json();
        throw new Error(detail.detail || "게시글 삭제에 실패했습니다.");
      }
      setSelectedPost(null);
      await loadPosts({ page: postPageInfo.page, query: postSearch, tag: selectedTag, selectFirst: true });
    },
    [loadPosts, postPageInfo.page, postSearch, selectedTag],
  );

  const updatePost = React.useCallback(
    async (postId, payload) => {
      const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const detail = await response.json();
        throw new Error(detail.detail || "게시글 수정에 실패했습니다.");
      }
      const data = await response.json();
      setSelectedPost(data);
      await loadPosts({ page: postPageInfo.page, query: postSearch, tag: selectedTag, keepSelection: true });
      return data;
    },
    [loadPosts, postPageInfo.page, postSearch, selectedTag],
  );

  const submitAuth = async (event) => {
    event.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    try {
      const response = await fetch(`${API_BASE_URL}/auth/${authMode === "login" ? "login" : "register"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: authForm.username.trim(),
          password: authForm.password,
        }),
      });
      if (!response.ok) {
        const detail = await response.json();
        throw new Error(detail.detail || "인증에 실패했습니다.");
      }
      const data = await response.json();
      localStorage.setItem("annalsUsername", data.username);
      setCurrentUser(data.username);
      setAuthForm({ username: data.username, password: "" });
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("annalsUsername");
    setCurrentUser("");
    setAuthForm({ username: "", password: "" });
    setAuthError("");
  };

  return (
    <main className="appShell">
      <section className="composePane">
        <div className="sectionHeader archiveMasthead">
          <div className="archiveSeal" aria-hidden="true">
            <FileText />
          </div>
          <div>
            <span className="sectionKicker">Annals Research Board</span>
            <h1>조선왕조실록 AI 게시판</h1>
            <p>질문을 게시글로 남기면 실록 원문 근거와 AI 초벌 해석이 함께 붙습니다.</p>
            <div className="archiveMeta" aria-label="서비스 핵심 기능">
              <span>원문 근거</span>
              <span>AI 초벌 해석</span>
              <span>토론 기록</span>
            </div>
          </div>
        </div>

        <section className="authPanel">
          {currentUser ? (
            <div className="signedInPanel">
              <div>
                <span>로그인 중</span>
                <strong>{currentUser}</strong>
              </div>
              <button type="button" onClick={logout}>
                <LogOut aria-hidden="true" />
                로그아웃
              </button>
            </div>
          ) : (
            <form className="authForm" onSubmit={submitAuth}>
              <div className="authModeTabs">
                <button type="button" className={authMode === "login" ? "active" : ""} onClick={() => setAuthMode("login")}>
                  <LogIn aria-hidden="true" />
                  로그인
                </button>
                <button type="button" className={authMode === "register" ? "active" : ""} onClick={() => setAuthMode("register")}>
                  <UserPlus aria-hidden="true" />
                  회원가입
                </button>
              </div>
              <label>
                사용자 이름
                <input
                  value={authForm.username}
                  onChange={(event) => setAuthForm({ ...authForm, username: event.target.value })}
                  minLength={2}
                  maxLength={80}
                  required
                />
              </label>
              <label>
                비밀번호
                <input
                  type="password"
                  value={authForm.password}
                  onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
                  minLength={4}
                  maxLength={128}
                  required
                />
              </label>
              <button type="submit" disabled={authLoading || !authForm.username.trim() || !authForm.password}>
                {authLoading ? <RefreshCw className="spin" aria-hidden="true" /> : authMode === "login" ? <LogIn aria-hidden="true" /> : <UserPlus aria-hidden="true" />}
                {authLoading ? "확인 중" : authMode === "login" ? "로그인" : "회원가입"}
              </button>
              {authError && <p className="errorText">{authError}</p>}
            </form>
          )}
        </section>

        <form className="questionForm" onSubmit={createPost}>
          <label>
            제목
            <input
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              maxLength={200}
              required
            />
          </label>
          <label>
            역사 질문
            <textarea
              value={form.question}
              onChange={(event) => setForm({ ...form, question: event.target.value })}
              rows={7}
              required
            />
          </label>
          <button type="submit" disabled={loading || !currentUser}>
            {loading ? <RefreshCw className="spin" aria-hidden="true" /> : <Send aria-hidden="true" />}
            {loading ? "근거 찾는 중" : currentUser ? "AI 근거 게시글 작성" : "로그인 후 작성"}
          </button>
        </form>
      </section>

      <section className="detailPane">
        <section className="postSearchPanel" aria-labelledby="postSearchTitle">
          <div className="postListHeader">
            <div>
              <span className="sectionKicker">기록 검색</span>
              <h2 id="postSearchTitle">조선왕조실록 질문 아카이브</h2>
              <p>실록 원문 근거와 AI 초벌 해석이 연결된 질문 기록을 탐색합니다.</p>
            </div>
            <div className="postListActions">
              <span>총 {postPageInfo.total}개 · {postPageInfo.page}/{postPageInfo.pages}쪽</span>
              <button
                className="iconButton"
                type="button"
                aria-label="게시글 새로고침"
                onClick={() =>
                  loadPosts({ page: postPageInfo.page, query: postSearch, tag: selectedTag, keepSelection: true }).catch((err) => setError(err.message))
                }
              >
                <RefreshCw aria-hidden="true" />
              </button>
            </div>
          </div>
          {error && <p className="errorText">{error}</p>}
          <form className="postSearchForm" onSubmit={searchPosts}>
            <input
              value={postSearch}
              onChange={(event) => setPostSearch(event.target.value)}
              maxLength={100}
              placeholder="제목, 질문, AI 요약 검색"
              aria-label="게시글 검색어"
            />
            <button className="iconButton" type="submit" aria-label="게시글 검색">
              <Search aria-hidden="true" />
            </button>
          </form>
          {selectedTag && (
            <div className="activeFilter">
              <span>태그: {selectedTag}</span>
              <button type="button" onClick={clearTagFilter}>
                <X aria-hidden="true" />
                해제
              </button>
            </div>
          )}
          <div className="postList" aria-live="polite">
            {posts.map((post) => (
              <button
                key={post.id}
                type="button"
                className={`postListItem ${selectedPost?.id === post.id ? "selected" : ""}`}
                onClick={() => loadPost(post.id).catch((err) => setError(err.message))}
              >
                <span className="postListItemMeta">
                  <FileText aria-hidden="true" />
                  질문 기록
                  <time dateTime={post.created_at}>
                    {new Date(post.created_at).toLocaleDateString("ko-KR", {
                      year: "numeric",
                      month: "2-digit",
                      day: "2-digit",
                    })}
                  </time>
                </span>
                <strong>{post.title}</strong>
                <span className="postListItemSummary">{post.ai_summary}</span>
                {post.suggested_tags.length > 0 && (
                  <span className="postListTags">
                    {post.suggested_tags.slice(0, 3).map((tag) => (
                      <span key={tag}>{tag}</span>
                    ))}
                  </span>
                )}
              </button>
            ))}
            {posts.length === 0 && (
              <div className="emptyText">
                <Search aria-hidden="true" />
                <strong>검색 결과가 없습니다.</strong>
                <span>다른 왕대, 사건명, 인물명으로 다시 찾아보세요.</span>
              </div>
            )}
          </div>
          <div className="paginationControls">
            <button type="button" disabled={postPageInfo.page <= 1} onClick={() => changePostPage(postPageInfo.page - 1)}>
              <ChevronLeft aria-hidden="true" />
              이전
            </button>
            <span>{postPageInfo.page}</span>
            <button
              type="button"
              disabled={postPageInfo.page >= postPageInfo.pages}
              onClick={() => changePostPage(postPageInfo.page + 1)}
            >
              다음
              <ChevronRight aria-hidden="true" />
            </button>
          </div>
        </section>

        {selectedPost ? (
          <PostDetail post={selectedPost} currentUser={currentUser} onDelete={deletePost} onUpdate={updatePost} onTagSelect={filterByTag} />
        ) : (
          <div className="emptyDetail">
            <Search aria-hidden="true" />
            <p>첫 질문을 작성하면 실록 근거와 AI 초벌 해석이 여기에 표시됩니다.</p>
          </div>
        )}
      </section>
    </main>
  );
}

function PostDetail({ post, currentUser, onDelete, onUpdate, onTagSelect }) {
  const [comments, setComments] = React.useState(post.comments || []);
  const [commentText, setCommentText] = React.useState("");
  const [commentLoading, setCommentLoading] = React.useState(false);
  const [commentError, setCommentError] = React.useState("");
  const [deleteLoading, setDeleteLoading] = React.useState(false);
  const [deleteError, setDeleteError] = React.useState("");
  const [isEditing, setIsEditing] = React.useState(false);
  const [editForm, setEditForm] = React.useState({
    title: post.title,
  });
  const [editLoading, setEditLoading] = React.useState(false);
  const [editError, setEditError] = React.useState("");
  const [discussionPrompt, setDiscussionPrompt] = React.useState("");
  const [discussionQuestion, setDiscussionQuestion] = React.useState("");
  const [discussionAnswer, setDiscussionAnswer] = React.useState("");
  const [discussionLoading, setDiscussionLoading] = React.useState(false);
  const [discussionError, setDiscussionError] = React.useState("");
  const [voiceStatus, setVoiceStatus] = React.useState("idle");
  const [voiceError, setVoiceError] = React.useState("");
  const [voiceEvents, setVoiceEvents] = React.useState([]);
  const [voiceMessages, setVoiceMessages] = React.useState([]);
  const [voiceLogError, setVoiceLogError] = React.useState("");
  const peerConnectionRef = React.useRef(null);
  const dataChannelRef = React.useRef(null);
  const mediaStreamRef = React.useRef(null);
  const remoteAudioRef = React.useRef(null);
  const voiceSessionIdRef = React.useRef(null);
  const voiceTurnLoadingRef = React.useRef(false);
  const voiceResponseInProgressRef = React.useRef(false);
  const voiceCancelInFlightRef = React.useRef(false);
  const pendingRealtimeEventsRef = React.useRef([]);
  const pendingResponseMetadataRef = React.useRef([]);
  const currentResponseMetadataRef = React.useRef(null);
  const currentAssistantTranscriptRef = React.useRef("");
  const voiceTurnAbortControllerRef = React.useRef(null);
  const voiceTurnIdRef = React.useRef(0);

  const addVoiceEvent = React.useCallback((message) => {
    setVoiceEvents((events) => [message, ...events].slice(0, 5));
  }, []);

  const stopVoiceDiscussion = React.useCallback(() => {
    dataChannelRef.current?.close();
    dataChannelRef.current = null;
    voiceTurnAbortControllerRef.current?.abort();
    voiceTurnAbortControllerRef.current = null;
    voiceTurnIdRef.current += 1;
    voiceTurnLoadingRef.current = false;
    voiceResponseInProgressRef.current = false;
    voiceCancelInFlightRef.current = false;
    pendingRealtimeEventsRef.current = [];
    pendingResponseMetadataRef.current = [];
    currentResponseMetadataRef.current = null;
    currentAssistantTranscriptRef.current = "";
    voiceSessionIdRef.current = null;
    peerConnectionRef.current?.close();
    peerConnectionRef.current = null;
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    mediaStreamRef.current = null;
    if (remoteAudioRef.current) {
      remoteAudioRef.current.srcObject = null;
    }
    setVoiceStatus("idle");
  }, []);

  const loadVoiceMessages = React.useCallback(async () => {
    setVoiceLogError("");
    try {
      const response = await fetch(`${API_BASE_URL}/posts/${post.id}/voice-messages`);
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || "음성 대화 기록을 불러오지 못했습니다.");
      }
      const data = await response.json();
      setVoiceMessages(data);
    } catch (err) {
      setVoiceLogError(err.message);
    }
  }, [post.id]);

  const saveVoiceMessage = React.useCallback(
    async (role, content, metadata = {}) => {
      const trimmedContent = content.trim();
      if (!trimmedContent || !voiceSessionIdRef.current) return null;

      try {
        const response = await fetch(`${API_BASE_URL}/posts/${post.id}/voice-sessions/${voiceSessionIdRef.current}/messages`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            role,
            content: trimmedContent,
            route_action: metadata.route_action || null,
            route_reason: metadata.route_reason || null,
            search_query: metadata.search_query || null,
            evidence_article_ids: metadata.evidence_article_ids || [],
          }),
        });
        if (!response.ok) {
          const detail = await response.json().catch(() => ({}));
          throw new Error(detail.detail || "음성 대화 기록 저장에 실패했습니다.");
        }
        const data = await response.json();
        setVoiceMessages((messages) => [...messages, data].slice(-120));
        return data;
      } catch (err) {
        setVoiceLogError(err.message);
        return null;
      }
    },
    [post.id],
  );

  React.useEffect(() => {
    setComments(post.comments || []);
    setCommentText("");
    setCommentError("");
    setDeleteError("");
    setIsEditing(false);
    setEditForm({
      title: post.title,
    });
    setEditError("");
    setDiscussionPrompt("");
    setDiscussionQuestion("");
    setDiscussionAnswer("");
    setDiscussionError("");
    setVoiceError("");
    setVoiceEvents([]);
    setVoiceMessages([]);
    setVoiceLogError("");
    stopVoiceDiscussion();
    loadVoiceMessages();
  }, [loadVoiceMessages, post.id, post.title, post.comments, stopVoiceDiscussion]);

  React.useEffect(() => {
    return () => stopVoiceDiscussion();
  }, [stopVoiceDiscussion]);

  const updateCurrentPost = async (event) => {
    event.preventDefault();
    setEditLoading(true);
    setEditError("");
    try {
      await onUpdate(post.id, {
        title: editForm.title.trim(),
      });
      setIsEditing(false);
    } catch (err) {
      setEditError(err.message);
    } finally {
      setEditLoading(false);
    }
  };

  const cancelEdit = () => {
    setEditForm({
      title: post.title,
    });
    setEditError("");
    setIsEditing(false);
  };

  const deleteCurrentPost = async () => {
    const confirmed = window.confirm("이 게시글을 삭제할까요? 연결된 댓글도 함께 삭제됩니다.");
    if (!confirmed) return;

    setDeleteLoading(true);
    setDeleteError("");
    try {
      await onDelete(post.id);
    } catch (err) {
      setDeleteError(err.message);
    } finally {
      setDeleteLoading(false);
    }
  };

  const createComment = async (event) => {
    event.preventDefault();
    if (!currentUser) {
      setCommentError("댓글을 작성하려면 먼저 로그인하세요.");
      return;
    }
    const content = commentText.trim();
    if (!content) return;

    setCommentLoading(true);
    setCommentError("");
    try {
      const response = await fetch(`${API_BASE_URL}/posts/${post.id}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: currentUser, content }),
      });
      if (!response.ok) {
        const detail = await response.json();
        throw new Error(detail.detail || "댓글 작성에 실패했습니다.");
      }
      const data = await response.json();
      setComments((currentComments) => [...currentComments, data]);
      setCommentText("");
    } catch (err) {
      setCommentError(err.message);
    } finally {
      setCommentLoading(false);
    }
  };

  const askDiscussionAssistant = async (event) => {
    event.preventDefault();
    const message = discussionPrompt.trim();
    if (!message) return;

    setDiscussionLoading(true);
    setDiscussionError("");
    setDiscussionQuestion(message);
    setDiscussionAnswer("");

    try {
      const response = await fetch(`${API_BASE_URL}/posts/${post.id}/ai-discussion/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!response.ok || !response.body) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || "AI 토론 답변을 불러오지 못했습니다.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let streamDone = false;

      while (!streamDone) {
        const { value, done } = await reader.read();
        streamDone = done;
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
        const blocks = buffer.split("\n\n");
        buffer = blocks.pop() || "";

        for (const block of blocks) {
          if (!block.trim()) continue;
          const parsed = parseSseBlock(block);
          if (!parsed) continue;

          if (parsed.event === "token") {
            setDiscussionAnswer((current) => current + parsed.data.text);
          }
          if (parsed.event === "error") {
            throw new Error(parsed.data.message || "AI 토론 답변 생성 중 오류가 발생했습니다.");
          }
          if (parsed.event === "done") {
            streamDone = true;
          }
        }
      }

      setDiscussionPrompt("");
    } catch (err) {
      setDiscussionError(err.message);
    } finally {
      setDiscussionLoading(false);
    }
  };

  const startVoiceDiscussion = async () => {
    if (!currentUser) {
      setVoiceError("음성 토론은 로그인 후 사용할 수 있습니다.");
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia || !window.RTCPeerConnection) {
      setVoiceError("이 브라우저에서는 실시간 음성 대화를 사용할 수 없습니다.");
      return;
    }

    setVoiceStatus("connecting");
    setVoiceError("");
    setVoiceLogError("");
    setVoiceEvents([]);

    try {
      const sessionResponse = await fetch(`${API_BASE_URL}/posts/${post.id}/voice-sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: currentUser }),
      });
      if (!sessionResponse.ok) {
        const detail = await sessionResponse.json().catch(() => ({}));
        throw new Error(detail.detail || "음성 대화 기록 세션을 만들지 못했습니다.");
      }
      const voiceSession = await sessionResponse.json();
      voiceSessionIdRef.current = voiceSession.id;

      const peerConnection = new RTCPeerConnection();
      peerConnectionRef.current = peerConnection;

      const remoteAudio = remoteAudioRef.current || new Audio();
      remoteAudio.autoplay = true;
      remoteAudio.muted = false;
      remoteAudio.volume = 1;
      remoteAudioRef.current = remoteAudio;
      peerConnection.ontrack = (event) => {
        remoteAudio.srcObject = event.streams[0] || new MediaStream([event.track]);
        addVoiceEvent("AI 음성 트랙 수신됨");
        remoteAudio.play().catch(() => {
          setVoiceError("브라우저가 AI 음성 자동 재생을 막았습니다. 브라우저 소리 권한을 확인한 뒤 다시 시작해 주세요.");
        });
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = mediaStream;
      peerConnection.addTrack(mediaStream.getAudioTracks()[0], mediaStream);

      const dataChannel = peerConnection.createDataChannel("oai-events");
      dataChannelRef.current = dataChannel;
      const sendRealtimeEvents = (events, metadata = {}) => {
        if (dataChannel.readyState !== "open") return;
        if (voiceResponseInProgressRef.current) {
          pendingRealtimeEventsRef.current.push({ events, metadata });
          return;
        }
        events.forEach((realtimeEvent) => {
          if (realtimeEvent.type === "response.create") {
            voiceResponseInProgressRef.current = true;
            pendingResponseMetadataRef.current.push(metadata);
          }
          dataChannel.send(JSON.stringify(realtimeEvent));
        });
      };
      const flushPendingRealtimeEvents = () => {
        if (voiceResponseInProgressRef.current || pendingRealtimeEventsRef.current.length === 0) return;
        const nextGroup = pendingRealtimeEventsRef.current.shift();
        sendRealtimeEvents(nextGroup.events, nextGroup.metadata);
      };
      const interruptActiveVoiceTurn = () => {
        voiceTurnIdRef.current += 1;
        voiceTurnAbortControllerRef.current?.abort();
        voiceTurnAbortControllerRef.current = null;
        voiceTurnLoadingRef.current = false;
        pendingRealtimeEventsRef.current = [];
        pendingResponseMetadataRef.current = [];
        currentResponseMetadataRef.current = { save: false };
        currentAssistantTranscriptRef.current = "";

        if (!voiceResponseInProgressRef.current || voiceCancelInFlightRef.current || dataChannel.readyState !== "open") {
          return;
        }

        voiceCancelInFlightRef.current = true;
        dataChannel.send(JSON.stringify({ type: "response.cancel" }));
        addVoiceEvent("AI 답변 중단");

        window.setTimeout(() => {
          if (!voiceCancelInFlightRef.current) return;
          voiceCancelInFlightRef.current = false;
          voiceResponseInProgressRef.current = false;
          flushPendingRealtimeEvents();
        }, 1500);
      };
      const orchestrateVoiceTurn = async (transcript) => {
        const normalizedTranscript = transcript.trim();
        if (!normalizedTranscript || voiceTurnLoadingRef.current) return;
        voiceTurnLoadingRef.current = true;
        const turnId = voiceTurnIdRef.current + 1;
        voiceTurnIdRef.current = turnId;
        const abortController = new AbortController();
        voiceTurnAbortControllerRef.current = abortController;
        let waitCueTimer = null;
        addVoiceEvent(`사용자: ${normalizedTranscript.slice(0, 40)}`);
        try {
          const routeResponse = await fetch(`${API_BASE_URL}/posts/${post.id}/realtime/turn/route`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript: normalizedTranscript }),
            signal: abortController.signal,
          });
          if (!routeResponse.ok) {
            const detail = await routeResponse.json().catch(() => ({}));
            throw new Error(detail.detail || "음성 질문 라우팅에 실패했습니다.");
          }
          const routePlan = await routeResponse.json();
          if (turnId !== voiceTurnIdRef.current || abortController.signal.aborted) return;
          addVoiceEvent(routePlan.action === "retrieve" ? "추가 실록 검색 필요" : "현재 근거로 답변");

          if (routePlan.action !== "retrieve") {
            sendRealtimeEvents(routePlan.events || [], {
              route_action: routePlan.action,
              route_reason: routePlan.reason,
              search_query: routePlan.search_query || "",
              evidence_article_ids: routePlan.evidence_article_ids || [],
            });
            return;
          }

          if (routePlan.events?.length > 0) {
            waitCueTimer = window.setTimeout(() => {
              if (turnId !== voiceTurnIdRef.current || abortController.signal.aborted) return;
              sendRealtimeEvents(routePlan.events || [], { save: false });
            }, 800);
          }

          const retrieveResponse = await fetch(`${API_BASE_URL}/posts/${post.id}/realtime/turn/retrieve`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              transcript: normalizedTranscript,
              search_query: routePlan.search_query || normalizedTranscript,
            }),
            signal: abortController.signal,
          });
          if (waitCueTimer) {
            window.clearTimeout(waitCueTimer);
          }
          if (!retrieveResponse.ok) {
            const detail = await retrieveResponse.json().catch(() => ({}));
            throw new Error(detail.detail || "추가 실록 검색에 실패했습니다.");
          }
          const retrievalPlan = await retrieveResponse.json();
          if (turnId !== voiceTurnIdRef.current || abortController.signal.aborted) return;
          if (retrievalPlan.evidence_article_ids?.length > 0) {
            addVoiceEvent(`추가 근거 ${retrievalPlan.evidence_article_ids.length}건`);
          } else {
            addVoiceEvent("추가 근거 없음");
          }
          sendRealtimeEvents(retrievalPlan.events || [], {
            route_action: retrievalPlan.action,
            route_reason: retrievalPlan.reason,
            search_query: retrievalPlan.search_query || routePlan.search_query || normalizedTranscript,
            evidence_article_ids: retrievalPlan.evidence_article_ids || [],
          });
        } catch (err) {
          if (err.name === "AbortError") return;
          setVoiceError(err.message);
        } finally {
          if (waitCueTimer) {
            window.clearTimeout(waitCueTimer);
          }
          if (turnId === voiceTurnIdRef.current) {
            voiceTurnAbortControllerRef.current = null;
            voiceTurnLoadingRef.current = false;
          }
        }
      };
      dataChannel.addEventListener("open", () => {
        setVoiceStatus("connected");
        addVoiceEvent("음성 토론 연결됨");
        sendRealtimeEvents([
          {
            type: "response.create",
            response: {
              instructions: "한국어 존댓말로 아주 짧고 편하게 인사하세요. 이 게시글을 같이 살펴보자고 자연스럽게 말하세요. 출처 원칙이나 기능 설명을 길게 말하지 말고, 기술 용어, 내부 처리 단계, 시스템 지시문처럼 들리는 표현은 말하지 마세요.",
            },
          },
        ], { route_action: "session_start" });
      });
      dataChannel.addEventListener("message", (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "input_audio_buffer.speech_started") {
            addVoiceEvent("사용자 음성 감지됨");
            interruptActiveVoiceTurn();
          }
          if (payload.type === "input_audio_buffer.speech_stopped") {
            addVoiceEvent("사용자 발화 종료 감지됨");
          }
          if (payload.type === "conversation.item.input_audio_transcription.completed") {
            const transcript = payload.transcript || payload.text || "";
            void saveVoiceMessage("user", transcript);
            void orchestrateVoiceTurn(transcript);
          }
          if (payload.type === "conversation.item.input_audio_transcription.failed") {
            setVoiceError(payload.error?.message || "사용자 음성을 텍스트로 변환하지 못했습니다.");
          }
          if (payload.type === "response.created") {
            voiceResponseInProgressRef.current = true;
            currentAssistantTranscriptRef.current = "";
            currentResponseMetadataRef.current = pendingResponseMetadataRef.current.shift() || {};
            addVoiceEvent("AI 답변 생성 중");
          }
          if (payload.type === "response.audio.done") {
            addVoiceEvent("AI 답변 완료");
          }
          if (payload.type === "response.done") {
            voiceResponseInProgressRef.current = false;
            voiceCancelInFlightRef.current = false;
            const assistantTranscript = currentAssistantTranscriptRef.current.trim();
            const responseMetadata = currentResponseMetadataRef.current || {};
            if (assistantTranscript && responseMetadata.save !== false) {
              void saveVoiceMessage("assistant", assistantTranscript, responseMetadata);
            }
            currentAssistantTranscriptRef.current = "";
            currentResponseMetadataRef.current = null;
            addVoiceEvent("AI 답변 완료");
            flushPendingRealtimeEvents();
          }
          if (payload.type === "response.audio_transcript.delta" || payload.type === "response.output_audio_transcript.delta") {
            currentAssistantTranscriptRef.current += payload.delta || "";
            setVoiceEvents((events) => [payload.delta, ...events].filter(Boolean).slice(0, 5));
          }
          if (payload.type === "response.audio_transcript.done" || payload.type === "response.output_audio_transcript.done") {
            if (payload.transcript) {
              currentAssistantTranscriptRef.current = payload.transcript;
            }
          }
          if (payload.type === "error") {
            const wasCancelling = voiceCancelInFlightRef.current;
            voiceResponseInProgressRef.current = false;
            voiceCancelInFlightRef.current = false;
            currentAssistantTranscriptRef.current = "";
            currentResponseMetadataRef.current = null;
            flushPendingRealtimeEvents();
            if (!wasCancelling) {
              setVoiceError(payload.error?.message || "Realtime 세션 오류가 발생했습니다.");
            }
          }
        } catch {
          // Realtime event logs are optional UI hints, so malformed events are ignored.
        }
      });

      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      const localSdp = offer.sdp;
      if (!localSdp) {
        throw new Error("브라우저가 WebRTC offer SDP를 만들지 못했습니다.");
      }
      const response = await fetch(`${API_BASE_URL}/posts/${post.id}/realtime/session`, {
        method: "POST",
        headers: { "Content-Type": "application/sdp" },
        body: localSdp,
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || "음성 토론 세션을 만들지 못했습니다.");
      }

      const answer = {
        type: "answer",
        sdp: await response.text(),
      };
      await peerConnection.setRemoteDescription(answer);
    } catch (err) {
      stopVoiceDiscussion();
      setVoiceError(err.message);
    }
  };

  return (
    <article className="postDetail">
      <header>
        <div className="postDetailToolbar">
          <div className="tagRow">
            {post.suggested_tags.map((tag) => (
              <button className="tagButton" type="button" key={tag} onClick={() => onTagSelect(tag)}>
                {tag}
              </button>
            ))}
          </div>
          <div className="postActionRow">
            {!isEditing && (
              <button className="secondaryButton" type="button" onClick={() => setIsEditing(true)}>
                <Pencil aria-hidden="true" />
                수정
              </button>
            )}
            <button className="dangerButton" type="button" disabled={deleteLoading || editLoading} onClick={deleteCurrentPost}>
              {deleteLoading ? <RefreshCw className="spin" aria-hidden="true" /> : <Trash2 aria-hidden="true" />}
              {deleteLoading ? "삭제 중" : "삭제"}
            </button>
          </div>
        </div>
        {isEditing ? (
          <form className="editPostForm" onSubmit={updateCurrentPost}>
            <label>
              제목
              <input
                value={editForm.title}
                onChange={(event) => setEditForm({ ...editForm, title: event.target.value })}
                maxLength={200}
                required
              />
            </label>
            <div className="editActionRow">
              <button type="submit" disabled={editLoading || !editForm.title.trim()}>
                {editLoading ? <RefreshCw className="spin" aria-hidden="true" /> : <Save aria-hidden="true" />}
                {editLoading ? "저장 중" : "저장"}
              </button>
              <button type="button" disabled={editLoading} onClick={cancelEdit}>
                <X aria-hidden="true" />
                취소
              </button>
            </div>
            {editError && <p className="errorText">{editError}</p>}
          </form>
        ) : (
          <>
            <h2>{post.title}</h2>
            <p>{post.question}</p>
          </>
        )}
        {deleteError && <p className="errorText">{deleteError}</p>}
      </header>

      <section>
        <h3>AI 초벌 요약</h3>
        <p>{post.ai_summary}</p>
      </section>

      <section>
        <h3>쉬운 해석</h3>
        <p>{post.ai_interpretation}</p>
      </section>

      <section>
        <h3>실록 원문 근거</h3>
        <div className="evidenceList">
          {post.evidence_articles.map((article) => (
            <a className="evidenceCard" href={article.official_url} target="_blank" rel="noreferrer" key={article.article_id}>
              <strong>{article.title}</strong>
              <span>{article.date || article.reign_date || article.article_id}</span>
              <p>{article.content}</p>
            </a>
          ))}
          {post.evidence_articles.length === 0 && <p className="emptyText">연결된 원문 근거가 없습니다.</p>}
        </div>
      </section>

      <section>
        <h3>Agent 실행 흐름</h3>
        <ol className="traceList">
          {post.agent_trace.map((step, index) => (
            <li key={`${step.step}-${index}`}>{step.step}</li>
          ))}
        </ol>
      </section>

      <section className="voiceDiscussion">
        <div className="discussionHeader">
          <div>
            <h3>음성 토론 모드</h3>
            <p>마이크로 질문하고 AI의 음성 답변을 바로 듣습니다.</p>
          </div>
          <Mic aria-hidden="true" />
        </div>
        <div className="voiceControls">
          <button type="button" disabled={voiceStatus !== "idle" || !currentUser} onClick={startVoiceDiscussion}>
            <Mic aria-hidden="true" />
            {voiceStatus === "connecting" ? "연결 중" : currentUser ? "음성 토론 시작" : "로그인 후 시작"}
          </button>
          <button type="button" disabled={voiceStatus === "idle"} onClick={stopVoiceDiscussion}>
            <PhoneOff aria-hidden="true" />
            종료
          </button>
        </div>
        <div className={`voiceStatus ${voiceStatus}`}>
          {voiceStatus === "idle" && "대기 중"}
          {voiceStatus === "connecting" && "마이크와 Realtime 세션을 연결하는 중입니다."}
          {voiceStatus === "connected" && "연결됨: 마이크로 질문하면 AI가 음성으로 답합니다."}
        </div>
        <audio className="voiceAudioOutput" ref={remoteAudioRef} autoPlay playsInline />
        {voiceEvents.length > 0 && (
          <div className="voiceEvents">
            {voiceEvents.map((event, index) => (
              <span key={`${event}-${index}`}>{event}</span>
            ))}
          </div>
        )}
        <div className="voiceMessageLog">
          <div className="voiceMessageLogHeader">
            <strong>음성 대화 기록</strong>
            <span>{voiceMessages.length}</span>
          </div>
          <div className="voiceMessageList">
            {voiceMessages.map((message) => (
              <article className={`voiceMessage ${message.role}`} key={message.id}>
                <div>
                  <strong>{message.role === "assistant" ? "AI" : message.username}</strong>
                  <time dateTime={message.created_at}>{new Date(message.created_at).toLocaleString("ko-KR")}</time>
                </div>
                <p>{message.content}</p>
                {(message.route_action || (message.evidence_article_ids || []).length > 0) && (
                  <footer>
                    {message.route_action && <span>{message.route_action}</span>}
                    {(message.evidence_article_ids || []).length > 0 && <span>근거 {message.evidence_article_ids.length}건</span>}
                  </footer>
                )}
              </article>
            ))}
            {voiceMessages.length === 0 && <p className="emptyText">아직 저장된 음성 대화가 없습니다.</p>}
          </div>
        </div>
        {voiceLogError && <p className="errorText">{voiceLogError}</p>}
        {voiceError && <p className="errorText">{voiceError}</p>}
      </section>

      <section className="aiDiscussion">
        <div className="discussionHeader">
          <div>
            <h3>AI 토론 도우미</h3>
            <p>이 게시글의 실록 근거와 댓글 맥락을 바탕으로 후속 질문에 답합니다.</p>
          </div>
          <Bot aria-hidden="true" />
        </div>
        <form className="discussionForm" onSubmit={askDiscussionAssistant}>
          <label>
            후속 질문
            <textarea
              value={discussionPrompt}
              onChange={(event) => setDiscussionPrompt(event.target.value)}
              rows={3}
              maxLength={1000}
              placeholder="예: 이 근거에서 정도전의 책임을 어떻게 봐야 해?"
              required
            />
          </label>
          <button type="submit" disabled={discussionLoading || !discussionPrompt.trim()}>
            {discussionLoading ? <RefreshCw className="spin" aria-hidden="true" /> : <Send aria-hidden="true" />}
            {discussionLoading ? "답변 생성 중" : "AI에게 묻기"}
          </button>
        </form>
        {(discussionQuestion || discussionAnswer || discussionLoading) && (
          <div className="discussionResult">
            {discussionQuestion && (
              <div className="discussionQuestion">
                <strong>질문</strong>
                <p>{discussionQuestion}</p>
              </div>
            )}
            <div className="discussionAnswer">
              <strong>AI 답변</strong>
              <p>{discussionAnswer || "답변을 준비하고 있습니다..."}</p>
            </div>
          </div>
        )}
        {discussionError && <p className="errorText">{discussionError}</p>}
      </section>

      <section>
        <div className="commentHeader">
          <h3>토론 댓글</h3>
          <span>{comments.length}</span>
        </div>
        <div className="commentList">
          {comments.map((comment) => (
            <article className="commentItem" key={comment.id}>
              <div>
                <strong>{comment.username}</strong>
                <time dateTime={comment.created_at}>{new Date(comment.created_at).toLocaleString("ko-KR")}</time>
              </div>
              <p>{comment.content}</p>
            </article>
          ))}
          {comments.length === 0 && <p className="emptyText">아직 댓글이 없습니다. 원문 근거를 보고 첫 의견을 남겨보세요.</p>}
        </div>
        <form className="commentForm" onSubmit={createComment}>
          <label>
            댓글
            <textarea
              value={commentText}
              onChange={(event) => setCommentText(event.target.value)}
              rows={3}
              maxLength={2000}
              placeholder="실록 근거를 보고 의견을 남겨보세요."
              required
            />
          </label>
          <button type="submit" disabled={commentLoading || !commentText.trim() || !currentUser}>
            <MessageSquare aria-hidden="true" />
            {commentLoading ? "저장 중" : currentUser ? "댓글 작성" : "로그인 후 댓글 작성"}
          </button>
          {commentError && <p className="errorText">{commentError}</p>}
        </form>
      </section>
    </article>
  );
}

createRoot(document.getElementById("root")).render(<App />);
