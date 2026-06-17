import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import type { BoardView, Post } from "../types";
import { useApiRequest } from "./useApiRequest";
import { useAuth } from "./useAuth";
import { useComments } from "./useComments";
import { useConsultations } from "./useConsultations";
import { usePetCareAdvice } from "./usePetCareAdvice";
import { usePostSearch } from "./usePostSearch";
import { usePosts } from "./usePosts";

export function useBoardController() {
  const { status, setStatus, request } = useApiRequest();
  const [activeView, setActiveView] = useState<BoardView>("support");
  const auth = useAuth({ request });
  const postSearch = usePostSearch({ request });
  const consultations = useConsultations({ request });

  function handleAuthRequired(message: string) {
    auth.showLogin();
    setStatus({ text: message, isError: true });
  }

  const postActions = usePosts({
    request,
    currentUser: auth.currentUser,
    onAuthRequired: handleAuthRequired,
    setStatus,
  });

  const petCareAdvice = usePetCareAdvice({
    request,
    isAuthenticated: Boolean(auth.currentUser),
    onAuthRequired: handleAuthRequired,
  });

  const comments = useComments({
    request,
    currentUser: auth.currentUser,
    selectedPostId: postActions.selectedPost?.id ?? null,
    onAuthRequired: handleAuthRequired,
    setStatus,
    onCommentsLoaded: postActions.applyCommentCount,
  });

  useEffect(() => {
    void postSearch.loadPosts({ quiet: true });
    void postSearch.loadTags({ quiet: true });
    void auth.loadMe({ quiet: true });
  }, []);

  async function register(event: FormEvent<HTMLFormElement>) {
    await auth.register(event);
  }

  async function login(event: FormEvent<HTMLFormElement>) {
    const ok = await auth.login(event);
    if (ok) {
      await postSearch.loadPosts({ quiet: true });
      if (activeView === "consultations") {
        await consultations.loadConsultations({ quiet: true, page: 1 });
      }
    }
  }

  async function logout() {
    const ok = await auth.logout();
    if (ok) {
      setActiveView("support");
      postActions.clearDetail();
      comments.resetComments();
      consultations.resetConsultations();
    }
  }

  async function goToList() {
    postActions.clearDetail();
    comments.resetComments();
    if (activeView === "consultations") {
      await consultations.loadConsultations({ quiet: true });
    } else {
      await postSearch.loadPosts({ quiet: true });
    }
  }

  async function showSupportInfo() {
    setActiveView("support");
    postActions.clearDetail();
    comments.resetComments();
    await postSearch.loadPosts({ quiet: true });
  }

  async function showConsultations() {
    setActiveView("consultations");
    postActions.clearDetail();
    comments.resetComments();

    if (!auth.currentUser) {
      consultations.resetConsultations();
      handleAuthRequired("내 질문은 로그인이 필요합니다.");
      return;
    }
    await consultations.loadConsultations({ page: 1 });
  }

  function openPostEditor() {
    postActions.openPostEditor();
  }

  function closePostEditor() {
    postActions.closePostEditor();
  }

  function openCompose() {
    postActions.openCompose();
  }

  function closeCompose() {
    postActions.closeCompose();
  }

  async function selectPost(post: Post) {
    const selectedPost = await postActions.selectPost(post);
    if (selectedPost) {
      await petCareAdvice.loadForPost(selectedPost);
      if (selectedPost.comment_policy !== "none") {
        await comments.loadComments(selectedPost.id, { quiet: true });
      } else {
        comments.resetComments();
      }
    }
  }

  async function createPost(event: FormEvent<HTMLFormElement>) {
    const createdPost = await postActions.createPost(event);
    if (createdPost) {
      setActiveView("support");
      await postSearch.loadTags({ quiet: true });
      await postSearch.loadPosts({ quiet: true });
      if (createdPost.comment_policy !== "none") {
        await comments.loadComments(createdPost.id, { quiet: true });
      }
      await petCareAdvice.generateForCreatedPost(createdPost);
    }
  }

  async function updatePost(event: FormEvent<HTMLFormElement>) {
    const updatedPost = await postActions.updatePost(event);
    if (updatedPost) {
      await petCareAdvice.loadForPost(updatedPost);
      await postSearch.loadTags({ quiet: true });
      await postSearch.loadPosts({ quiet: true });
    }
  }

  async function deletePost() {
    const selectedId = postActions.selectedPost?.id ?? null;
    const deleted = await postActions.deletePost();
    if (deleted) {
      petCareAdvice.clearAdvice(selectedId);
      comments.resetComments();
      await postSearch.loadTags({ quiet: true });
      if (activeView === "consultations") {
        await consultations.loadConsultations({ quiet: true });
      } else {
        await postSearch.loadPosts({ quiet: true });
      }
    }
  }

  async function likePost() {
    const likedPost = await postActions.likePost();
    if (likedPost) {
      await postSearch.loadPosts({ quiet: true });
    }
  }

  async function createComment(event: FormEvent<HTMLFormElement>) {
    await comments.createComment(event);
  }

  async function generateAdviceForSelectedPost() {
    if (!postActions.selectedPost) {
      return;
    }
    await petCareAdvice.generateForPost(postActions.selectedPost);
  }

  async function changeConsultationPage(nextPage: number) {
    await consultations.loadConsultations({ page: nextPage });
  }

  return {
    activeView,
    authView: auth.authView,
    authForm: auth.authForm,
    currentUser: auth.currentUser,
    posts: postSearch.posts,
    consultations: consultations.consultations,
    tags: postSearch.tags,
    selectedPost: postActions.selectedPost,
    isComposeOpen: postActions.isComposeOpen,
    comments: comments.comments,
    search: postSearch.search,
    pageMeta: postSearch.pageMeta,
    consultationPageMeta: consultations.consultationPageMeta,
    postForm: postActions.postForm,
    editForm: postActions.editForm,
    petCareAdviceState: petCareAdvice.getAdviceState(postActions.selectedPost?.id ?? null),
    isEditingPost: postActions.isEditingPost,
    commentForm: comments.commentForm,
    status,
    isAuthor: postActions.isAuthor,
    selectedTagName: postSearch.selectedTagName,
    showLogin: auth.showLogin,
    showRegister: auth.showRegister,
    hideAuth: auth.hideAuth,
    updateAuthForm: auth.updateAuthForm,
    updatePostForm: postActions.updatePostForm,
    updateEditForm: postActions.updateEditForm,
    updateCommentForm: comments.updateCommentForm,
    updateSearch: postSearch.updateSearch,
    generateAdviceForSelectedPost,
    openPostEditor,
    closePostEditor,
    goToList,
    showSupportInfo,
    showConsultations,
    openCompose,
    closeCompose,
    register,
    login,
    logout,
    submitSearch: postSearch.submitSearch,
    filterByTag: postSearch.filterByTag,
    clearFilters: postSearch.clearFilters,
    changeSort: postSearch.changeSort,
    changePage: postSearch.changePage,
    changeConsultationPage,
    selectPost,
    createPost,
    updatePost,
    deletePost,
    loadComments: comments.loadComments,
    createComment,
    likePost,
    deleteComment: comments.deleteComment,
  };
}
