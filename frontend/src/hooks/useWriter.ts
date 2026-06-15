import { FormEvent, useState } from "react";

import { deletePost, runRagAssist, savePost } from "../services/boardApi";
import type { DraftPost, Post, PostFilters, PostMeta, RagAssistResponse, TokenResponse } from "../types";

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
  const [ragResult, setRagResult] = useState<RagAssistResponse | null>(null);
  const [savingPost, setSavingPost] = useState(false);
  const [runningRag, setRunningRag] = useState(false);

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
      setRagResult(null);
      setDraftPost(EMPTY_DRAFT);
      await loadTags();
      await loadPosts(postMeta.page, filters);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "글을 삭제하지 못했습니다.");
    }
  }

  return {
    cancelEdit,
    draftPost,
    editingPostId,
    handleDeletePost,
    handleRagAssist,
    handleSavePost,
    ragResult,
    runningRag,
    savingPost,
    setDraftPost,
    setShowComposer,
    showComposer,
    startEdit,
  };
}
