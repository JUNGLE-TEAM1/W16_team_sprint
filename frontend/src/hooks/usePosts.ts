import { useMemo, useState } from "react";
import type { FormEvent } from "react";

import type { FieldChangeEvent, Post, PostFormState, StatusState, User } from "../types";
import { buildPostBody, tagText } from "../utils/postFormatting";
import type { ApiRequest } from "./useApiRequest";

interface UsePostsOptions {
  request: ApiRequest;
  currentUser: User | null;
  onAuthRequired: (message: string) => void;
  setStatus: (status: StatusState) => void;
}

export function usePosts({ request, currentUser, onAuthRequired, setStatus }: UsePostsOptions) {
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [postForm, setPostForm] = useState<PostFormState>({
    title: "Sprint 4 검색과 태그",
    content: "태그, 검색 타입, 페이징 흐름을 정리합니다.",
    tags: "fastapi, sprint",
  });
  const [editForm, setEditForm] = useState<PostFormState>({ title: "", content: "", tags: "" });
  const [isEditingPost, setIsEditingPost] = useState(false);

  const isAuthor = useMemo(
    () => Boolean(currentUser && selectedPost?.author_id === currentUser.id),
    [currentUser, selectedPost],
  );

  function updatePostForm(event: FieldChangeEvent) {
    setPostForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  function updateEditForm(event: FieldChangeEvent) {
    setEditForm((current) => ({
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

  function clearDetail() {
    setSelectedPost(null);
    setIsEditingPost(false);
    setIsComposeOpen(false);
  }

  function openCompose() {
    if (!currentUser) {
      onAuthRequired("게시글 작성은 로그인이 필요합니다.");
      return;
    }
    setIsComposeOpen(true);
  }

  function closeCompose() {
    setIsComposeOpen(false);
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
      return result.data;
    }
    return null;
  }

  async function createPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!currentUser) {
      onAuthRequired("게시글 작성은 로그인이 필요합니다.");
      return null;
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
      setEditForm({
        title: result.data.title,
        content: result.data.content,
        tags: tagText(result.data.tags),
      });
      setIsEditingPost(false);
      return result.data;
    }
    return null;
  }

  async function updatePost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPost) {
      setStatus({ text: "수정할 게시글을 선택하세요.", isError: true });
      return null;
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
      setIsEditingPost(false);
      return result.data;
    }
    return null;
  }

  async function deletePost() {
    if (!selectedPost) {
      setStatus({ text: "삭제할 게시글을 선택하세요.", isError: true });
      return false;
    }
    if (!window.confirm("게시글과 연결된 댓글을 모두 삭제할까요?")) {
      return false;
    }

    const result = await request<Record<string, never>>(`/api/v1/posts/${selectedPost.id}`, {
      method: "DELETE",
      successMessage: "게시글을 삭제했습니다.",
    });
    if (result.ok) {
      setSelectedPost(null);
      setEditForm({ title: "", content: "", tags: "" });
      setIsEditingPost(false);
      return true;
    }
    return false;
  }

  async function likePost() {
    if (!selectedPost) {
      return null;
    }
    if (!currentUser) {
      onAuthRequired("좋아요는 로그인이 필요합니다.");
      return null;
    }

    const result = await request<Post>(`/api/v1/posts/${selectedPost.id}/like`, {
      method: "POST",
      successMessage: "좋아요를 반영했습니다.",
    });
    if (result.ok) {
      setSelectedPost(result.data);
      return result.data;
    }
    return null;
  }

  function applyCommentCount(postId: number, count: number) {
    setSelectedPost((current) =>
      current?.id === postId ? { ...current, comment_count: count } : current,
    );
  }

  return {
    selectedPost,
    isComposeOpen,
    postForm,
    editForm,
    isEditingPost,
    isAuthor,
    updatePostForm,
    updateEditForm,
    openPostEditor,
    closePostEditor,
    clearDetail,
    openCompose,
    closeCompose,
    selectPost,
    createPost,
    updatePost,
    deletePost,
    likePost,
    applyCommentCount,
  };
}
