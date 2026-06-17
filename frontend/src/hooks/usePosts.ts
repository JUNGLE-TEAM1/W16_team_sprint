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
    title: "강아지가 켁켁 기침을 반복합니다",
    content: "5개월 된 말티푸가 최근 켁켁거리는 기침을 반복합니다. 식욕은 조금 줄었고 활력은 평소와 비슷합니다. 병원에 바로 가야 하는지 궁금합니다.",
    tags: "기침, 자견, 내과",
    region: "서울 마포구",
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
      onAuthRequired("질문 작성은 로그인이 필요합니다.");
      return;
    }
    setIsComposeOpen(true);
  }

  function closeCompose() {
    setIsComposeOpen(false);
  }

  async function selectPost(post: Post) {
    const result = await request<Post>(`/api/v1/posts/${post.id}`, {
      successMessage: "상담 질문 상세를 불러왔습니다.",
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
      onAuthRequired("질문 작성은 로그인이 필요합니다.");
      return null;
    }

    const result = await request<Post>("/api/v1/posts", {
      method: "POST",
      body: buildPostBody(postForm),
      successMessage: "질문을 등록했습니다.",
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
      setStatus({ text: "수정할 상담 질문을 선택하세요.", isError: true });
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
      setStatus({ text: "삭제할 상담 질문을 선택하세요.", isError: true });
      return false;
    }
    const message = "상담 질문을 삭제할까요? 화면에 표시된 AI 답변도 함께 사라집니다.";
    if (!window.confirm(message)) {
      return false;
    }

    const result = await request<Record<string, never>>(`/api/v1/posts/${selectedPost.id}`, {
      method: "DELETE",
      successMessage: "상담 질문을 삭제했습니다.",
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
