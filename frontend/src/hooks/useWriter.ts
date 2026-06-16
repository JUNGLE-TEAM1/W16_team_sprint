import { useState } from "react";

import { deletePost, runRagAssist, runWritingAgent } from "../services/boardApi";
import type {
  AgentWritingAssistResponse,
  DraftPost,
  Post,
  PostFilters,
  PostMeta,
  RagAssistResponse,
  TokenResponse,
} from "../types";

const EMPTY_DRAFT: DraftPost = { title: "", content: "", tagNames: "", referenceUrls: "" };

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
  const [runningAgent, setRunningAgent] = useState(false);
  const [runningRag, setRunningRag] = useState(false);

  async function handleWritingAgent() {
    setRunningAgent(true);
    setError(null);
    try {
      setAgentResult(await runWritingAgent(draftPost));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "상담 초안 추천을 완료하지 못했습니다.");
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
      referenceUrls: draftPost.referenceUrls,
    });
  }

  async function handleRagAssist() {
    if (!draftPost.title.trim() && !draftPost.content.trim()) {
      setError("AI 매칭을 하려면 상담 제목이나 현재 상황을 먼저 입력해 주세요.");
      return;
    }

    setRunningRag(true);
    setError(null);
    try {
      setRagResult(await runRagAssist(draftPost));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "AI 매칭을 완료하지 못했습니다.");
    } finally {
      setRunningRag(false);
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
      referenceUrls: "",
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
      setError("상담 케이스를 삭제하려면 먼저 로그인해 주세요.");
      setShowAuthPanel(true);
      return;
    }

    if (!window.confirm("이 상담 케이스를 삭제할까요? 되돌릴 수 없습니다.")) {
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
      setError(requestError instanceof Error ? requestError.message : "상담 케이스를 삭제하지 못했습니다.");
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
    handleWritingAgent,
    ragResult,
    runningAgent,
    runningRag,
    setDraftPost,
    setShowComposer,
    showComposer,
    startEdit,
  };
}
