import { FormEvent, useState } from "react";

import { deletePost, runRagAssist, runWritingAgent, savePost } from "../services/boardApi";
import type {
  AgentWritingAssistResponse,
  DraftPost,
  Post,
  PostFilters,
  PostMeta,
  RagAssistResponse,
  TokenResponse,
} from "../types";

const EMPTY_DRAFT: DraftPost = { title: "", content: "", tagNames: "" };

type UseWriterOptions = {
  filters: PostFilters;
  loadPosts: (page?: number, nextFilters?: PostFilters, nextSelectedId?: number) => Promise<void>;
  loadTags: () => Promise<void>;
  postMeta: PostMeta;
  session: TokenResponse | null;
  setError: (message: string | null) => void;
  setShowAuthPanel: (value: boolean) => void;
};

export function useWriter({
  filters,
  loadPosts,
  loadTags,
  postMeta,
  session,
  setError,
  setShowAuthPanel,
}: UseWriterOptions) {
  const [showComposer, setShowComposer] = useState(false);
  const [draftPost, setDraftPost] = useState<DraftPost>(EMPTY_DRAFT);
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [agentResult, setAgentResult] = useState<AgentWritingAssistResponse | null>(null);
  const [ragResult, setRagResult] = useState<RagAssistResponse | null>(null);
  const [savingPost, setSavingPost] = useState(false);
  const [runningAgent, setRunningAgent] = useState(false);
  const [runningRag, setRunningRag] = useState(false);

  async function handleWritingAgent() {
    setRunningAgent(true);
    setError(null);
    try {
      setAgentResult(await runWritingAgent(draftPost));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Agent 추천을 완료하지 못했습니다.");
    } finally {
      setRunningAgent(false);
    }
  }

  function applyAgentSuggestion() {
    if (!agentResult) return;
    setDraftPost({
      title: agentResult.suggested_title,
      content: agentResult.suggested_content,
      tagNames: agentResult.suggested_tag_names.join(", "),
    });
  }

  async function handleRagAssist() {
    if (!draftPost.title.trim() && !draftPost.content.trim()) {
      setError("RAG 검사를 하려면 제목이나 초안을 먼저 입력해 주세요.");
      return;
    }

    setRunningRag(true);
    setError(null);
    try {
      setRagResult(await runRagAssist(draftPost));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "RAG 검사를 완료하지 못했습니다.");
    } finally {
      setRunningRag(false);
    }
  }

  async function handleSavePost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session) {
      setError("글을 저장하려면 먼저 로그인해 주세요.");
      setShowAuthPanel(true);
      return;
    }

    setSavingPost(true);
    setError(null);
    try {
      const savedPost = await savePost(draftPost, session.access_token, editingPostId);
      setDraftPost(EMPTY_DRAFT);
      setEditingPostId(null);
      setAgentResult(null);
      setRagResult(null);
      setShowComposer(false);
      await loadTags();
      await loadPosts(editingPostId ? postMeta.page : 1, filters, savedPost.id);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "글을 저장하지 못했습니다.");
    } finally {
      setSavingPost(false);
    }
  }

  function startEdit(post: Post) {
    setEditingPostId(post.id);
    setShowComposer(true);
    setAgentResult(null);
    setRagResult(null);
    setDraftPost({
      title: post.title,
      content: post.content,
      tagNames: post.tags.map((tagItem) => tagItem.name).join(", "),
    });
  }

  function cancelEdit() {
    setEditingPostId(null);
    setShowComposer(false);
    setAgentResult(null);
    setRagResult(null);
    setDraftPost(EMPTY_DRAFT);
  }

  async function handleDeletePost(postId: number) {
    if (!session) {
      setError("글을 삭제하려면 먼저 로그인해 주세요.");
      setShowAuthPanel(true);
      return;
    }

    if (!window.confirm("이 글을 삭제할까요? 되돌릴 수 없습니다.")) {
      return;
    }

    setError(null);
    try {
      await deletePost(postId, session.access_token);
      setEditingPostId(null);
      setAgentResult(null);
      setRagResult(null);
      setDraftPost(EMPTY_DRAFT);
      await loadTags();
      await loadPosts(postMeta.page, filters);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "글을 삭제하지 못했습니다.");
    }
  }

  return {
    agentResult,
    applyAgentSuggestion,
    cancelEdit,
    draftPost,
    editingPostId,
    handleDeletePost,
    handleRagAssist,
    handleSavePost,
    handleWritingAgent,
    ragResult,
    runningAgent,
    runningRag,
    savingPost,
    setDraftPost,
    setShowComposer,
    showComposer,
    startEdit,
  };
}
