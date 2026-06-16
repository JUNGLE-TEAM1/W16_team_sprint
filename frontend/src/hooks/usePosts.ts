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

function emptyConsultationForm(): PostFormState {
  return {
    title: "",
    content: "",
    tags: "",
    post_type: "case",
    region: "",
    source_name: "",
    source_url: "",
    source_external_id: "",
  };
}

function postToForm(post: Post): PostFormState {
  return {
    title: post.title,
    content: post.content,
    tags: tagText(post.tags),
    post_type: post.post_type,
    region: post.region ?? "",
    source_name: post.source_name ?? "",
    source_url: post.source_url ?? "",
    source_external_id: post.source_external_id ?? "",
  };
}

export function usePosts({ request, currentUser, onAuthRequired, setStatus }: UsePostsOptions) {
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [postForm, setPostForm] = useState<PostFormState>({
    ...emptyConsultationForm(),
    title: "서울 거주 24세 취준생 지원 찾기",
    content: "서울에 거주하는 24세 취업준비생입니다. 월세 부담이 크고 소득이 없어 받을 수 있는 청년 주거, 취업, 상담 지원을 찾고 싶습니다.",
    tags: "청년, 주거, 취업, 서울",
    region: "서울",
  });
  const [editForm, setEditForm] = useState<PostFormState>(emptyConsultationForm);
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
    setEditForm(postToForm(selectedPost));
    setIsEditingPost(true);
  }

  function closePostEditor() {
    if (selectedPost) {
      setEditForm(postToForm(selectedPost));
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
      onAuthRequired("상담 등록은 로그인이 필요합니다.");
      return;
    }
    setIsComposeOpen(true);
  }

  function closeCompose() {
    setIsComposeOpen(false);
  }

  async function selectPost(post: Post) {
    const result = await request<Post>(`/api/v1/posts/${post.id}`, {
      successMessage: "지원 카드 상세를 불러왔습니다.",
    });
    if (result.ok) {
      setSelectedPost(result.data);
      setEditForm(postToForm(result.data));
      setIsEditingPost(false);
      setIsComposeOpen(false);
      return result.data;
    }
    return null;
  }

  async function createPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!currentUser) {
      onAuthRequired("상담 등록은 로그인이 필요합니다.");
      return null;
    }

    const result = await request<Post>("/api/v1/posts", {
      method: "POST",
      body: buildPostBody(postForm),
      successMessage: "상담을 등록했습니다.",
    });
    if (result.ok) {
      setPostForm(emptyConsultationForm());
      setSelectedPost(result.data);
      setIsComposeOpen(false);
      setEditForm(postToForm(result.data));
      setIsEditingPost(false);
      return result.data;
    }
    return null;
  }

  async function updatePost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPost) {
      setStatus({ text: "수정할 지원 카드나 상담 요청을 선택하세요.", isError: true });
      return null;
    }

    const result = await request<Post>(`/api/v1/posts/${selectedPost.id}`, {
      method: "PATCH",
      body: buildPostBody(editForm),
      successMessage: "내용을 수정했습니다.",
    });
    if (result.ok) {
      setSelectedPost(result.data);
      setEditForm(postToForm(result.data));
      setIsEditingPost(false);
      return result.data;
    }
    return null;
  }

  async function deletePost() {
    if (!selectedPost) {
      setStatus({ text: "삭제할 지원 카드나 상담 요청을 선택하세요.", isError: true });
      return false;
    }
    const message =
      selectedPost.post_type === "case"
        ? "상담 기록을 삭제할까요? 이후 연결될 AI 답변도 함께 삭제되는 흐름으로 처리합니다."
        : "이 지원 카드를 삭제할까요?";
    if (!window.confirm(message)) {
      return false;
    }

    const result = await request<Record<string, never>>(`/api/v1/posts/${selectedPost.id}`, {
      method: "DELETE",
      successMessage: selectedPost.post_type === "case" ? "상담 기록을 삭제했습니다." : "카드를 삭제했습니다.",
    });
    if (result.ok) {
      setSelectedPost(null);
      setEditForm(emptyConsultationForm());
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
      onAuthRequired("관심 등록은 로그인이 필요합니다.");
      return null;
    }

    const result = await request<Post>(`/api/v1/posts/${selectedPost.id}/like`, {
      method: "POST",
      successMessage: "관심 등록을 반영했습니다.",
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
