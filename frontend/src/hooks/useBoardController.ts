import { useEffect } from "react";
import type { FormEvent } from "react";

import type { Post } from "../types";
import { useApiRequest } from "./useApiRequest";
import { useAuth } from "./useAuth";
import { useComments } from "./useComments";
import { useExternalReferences } from "./useExternalReferences";
import { usePostSearch } from "./usePostSearch";
import { usePosts } from "./usePosts";
import { useRelatedPosts } from "./useRelatedPosts";

export function useBoardController() {
  const { status, setStatus, request } = useApiRequest();
  const auth = useAuth({ request });
  const postSearch = usePostSearch({ request });

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

  const relatedPosts = useRelatedPosts({
    isAuthenticated: Boolean(auth.currentUser),
    isComposeOpen: postActions.isComposeOpen,
    postForm: postActions.postForm,
    isEditingPost: postActions.isEditingPost,
    editForm: postActions.editForm,
    selectedPostId: postActions.selectedPost?.id ?? null,
    request,
  });

  const externalReferences = useExternalReferences({ request });

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
    }
  }

  async function logout() {
    const ok = await auth.logout();
    if (ok) {
      postActions.clearDetail();
      comments.resetComments();
      relatedPosts.resetComposeRelatedPosts();
      relatedPosts.resetEditRelatedPosts();
      externalReferences.resetComposeExternalReferences();
    }
  }

  async function goToList() {
    postActions.clearDetail();
    comments.resetComments();
    relatedPosts.resetComposeRelatedPosts();
    relatedPosts.resetEditRelatedPosts();
    externalReferences.resetComposeExternalReferences();
    await postSearch.loadPosts({ quiet: true });
  }

  function openPostEditor() {
    postActions.openPostEditor();
    relatedPosts.resetEditRelatedPosts();
  }

  function closePostEditor() {
    postActions.closePostEditor();
    relatedPosts.resetEditRelatedPosts();
  }

  function openCompose() {
    if (auth.currentUser) {
      relatedPosts.resetComposeRelatedPosts();
      externalReferences.resetComposeExternalReferences();
    }
    postActions.openCompose();
  }

  function closeCompose() {
    postActions.closeCompose();
    relatedPosts.resetComposeRelatedPosts();
    externalReferences.resetComposeExternalReferences();
  }

  async function selectPost(post: Post) {
    const selectedPost = await postActions.selectPost(post);
    if (selectedPost) {
      relatedPosts.resetComposeRelatedPosts();
      relatedPosts.resetEditRelatedPosts();
      externalReferences.resetComposeExternalReferences();
      await comments.loadComments(selectedPost.id, { quiet: true });
    }
  }

  async function createPost(event: FormEvent<HTMLFormElement>) {
    const createdPost = await postActions.createPost(event);
    if (createdPost) {
      relatedPosts.resetComposeRelatedPosts();
      externalReferences.resetComposeExternalReferences();
      await postSearch.loadTags({ quiet: true });
      await postSearch.loadPosts({ quiet: true, filters: { page: 1 } });
      await comments.loadComments(createdPost.id, { quiet: true });
    }
  }

  async function updatePost(event: FormEvent<HTMLFormElement>) {
    const updatedPost = await postActions.updatePost(event);
    if (updatedPost) {
      relatedPosts.resetEditRelatedPosts();
      await postSearch.loadTags({ quiet: true });
      await postSearch.loadPosts({ quiet: true });
    }
  }

  async function deletePost() {
    const deleted = await postActions.deletePost();
    if (deleted) {
      comments.resetComments();
      relatedPosts.resetEditRelatedPosts();
      await postSearch.loadTags({ quiet: true });
      await postSearch.loadPosts({ quiet: true });
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

  async function findComposeExternalReferences() {
    if (!auth.currentUser) {
      handleAuthRequired("외부 참고자료 찾기는 로그인이 필요합니다.");
      return;
    }
    await externalReferences.findComposeExternalReferences(postActions.postForm);
  }

  return {
    authView: auth.authView,
    authForm: auth.authForm,
    currentUser: auth.currentUser,
    posts: postSearch.posts,
    tags: postSearch.tags,
    selectedPost: postActions.selectedPost,
    isComposeOpen: postActions.isComposeOpen,
    comments: comments.comments,
    search: postSearch.search,
    pageMeta: postSearch.pageMeta,
    postForm: postActions.postForm,
    editForm: postActions.editForm,
    composeRelatedPosts: relatedPosts.composeRelatedPosts,
    editRelatedPosts: relatedPosts.editRelatedPosts,
    composeExternalReferences: externalReferences.composeExternalReferences,
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
    findComposeExternalReferences,
    openPostEditor,
    closePostEditor,
    goToList,
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
