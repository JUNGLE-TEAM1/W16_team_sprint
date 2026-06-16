import { FormEvent, useEffect, useState } from "react";

import { deleteComment, fetchComments, saveComment } from "../services/boardApi";
import type { Comment, TokenResponse } from "../types";

type UseCommentsOptions = {
  selectedPostId: number | null;
  session: TokenResponse | null;
  setError: (message: string | null) => void;
  setShowAuthPanel: (value: boolean) => void;
};

export function useComments({ selectedPostId, session, setError, setShowAuthPanel }: UseCommentsOptions) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [draftComment, setDraftComment] = useState("");
  const [loadingComments, setLoadingComments] = useState(false);
  const [savingComment, setSavingComment] = useState(false);

  async function loadComments(postId: number) {
    setLoadingComments(true);
    setError(null);
    try {
      setComments(await fetchComments(postId));
    } catch (requestError) {
      setComments([]);
      setError(requestError instanceof Error ? requestError.message : "상담 메모를 불러오지 못했습니다.");
    } finally {
      setLoadingComments(false);
    }
  }

  useEffect(() => {
    if (selectedPostId === null) {
      setComments([]);
      return;
    }
    void loadComments(selectedPostId);
  }, [selectedPostId]);

  async function handleSaveComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session || selectedPostId === null) {
      setError("상담 메모를 남기려면 먼저 로그인해 주세요.");
      setShowAuthPanel(true);
      return;
    }

    setSavingComment(true);
    setError(null);
    try {
      await saveComment(selectedPostId, draftComment, session.access_token);
      setDraftComment("");
      await loadComments(selectedPostId);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "상담 메모를 저장하지 못했습니다.");
    } finally {
      setSavingComment(false);
    }
  }

  async function handleDeleteComment(comment: Comment) {
    if (!session || selectedPostId === null) {
      setError("상담 메모를 삭제하려면 먼저 로그인해 주세요.");
      setShowAuthPanel(true);
      return;
    }

    if (!window.confirm("이 상담 메모를 삭제할까요?")) {
      return;
    }

    setError(null);
    try {
      await deleteComment(comment.id, session.access_token);
      await loadComments(selectedPostId);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "상담 메모를 삭제하지 못했습니다.");
    }
  }

  return {
    comments,
    draftComment,
    handleDeleteComment,
    handleSaveComment,
    loadingComments,
    savingComment,
    setDraftComment,
  };
}
