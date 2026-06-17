import { useState } from "react";
import type { FormEvent } from "react";

import type {
  Comment,
  CommentFormState,
  FieldChangeEvent,
  LoadOptions,
  StatusState,
  User,
} from "../types";
import type { ApiRequest } from "./useApiRequest";

interface UseCommentsOptions {
  request: ApiRequest;
  currentUser: User | null;
  selectedPostId: number | null;
  onAuthRequired: (message: string) => void;
  setStatus: (status: StatusState) => void;
  onCommentsLoaded: (postId: number, count: number) => void;
}

export function useComments({
  request,
  currentUser,
  selectedPostId,
  onAuthRequired,
  setStatus,
  onCommentsLoaded,
}: UseCommentsOptions) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentForm, setCommentForm] = useState<CommentFormState>({
    content: "추가로 확인하면 좋을 점을 남깁니다.",
  });

  function updateCommentForm(event: FieldChangeEvent) {
    setCommentForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  function resetComments() {
    setComments([]);
  }

  async function loadComments(postId = selectedPostId, options: LoadOptions = {}) {
    if (!postId) {
      return false;
    }
    const result = await request<Comment[]>(`/api/v1/posts/${postId}/comments`, {
      quiet: options.quiet,
      successMessage: "댓글을 불러왔습니다.",
    });
    if (result.ok && Array.isArray(result.data)) {
      setComments(result.data);
      onCommentsLoaded(postId, result.data.length);
      return true;
    }
    return false;
  }

  async function createComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!currentUser) {
      onAuthRequired("댓글 작성은 로그인이 필요합니다.");
      return false;
    }
    if (!selectedPostId) {
      setStatus({ text: "댓글을 작성할 상담 질문을 선택하세요.", isError: true });
      return false;
    }

    const result = await request<Comment>(`/api/v1/posts/${selectedPostId}/comments`, {
      method: "POST",
      body: JSON.stringify(commentForm),
      successMessage: "댓글을 작성했습니다.",
    });
    if (result.ok) {
      setCommentForm({ content: "" });
      await loadComments(selectedPostId, { quiet: true });
      return true;
    }
    return false;
  }

  async function deleteComment(commentId: number) {
    const result = await request<Record<string, never>>(`/api/v1/comments/${commentId}`, {
      method: "DELETE",
      successMessage: "댓글을 삭제했습니다.",
    });
    if (result.ok && selectedPostId) {
      await loadComments(selectedPostId, { quiet: true });
      return true;
    }
    return false;
  }

  return {
    comments,
    commentForm,
    updateCommentForm,
    resetComments,
    loadComments,
    createComment,
    deleteComment,
  };
}
