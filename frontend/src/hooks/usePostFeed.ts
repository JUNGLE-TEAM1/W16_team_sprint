import { FormEvent, useEffect, useMemo, useState } from "react";

import { PAGE_SIZE } from "../api";
import { fetchPost, fetchPosts, fetchTags } from "../services/boardApi";
import type { Post, PostFilters, PostMeta, Tag } from "../types";

type UsePostFeedOptions = {
  setError: (message: string | null) => void;
};

export function usePostFeed({ setError }: UsePostFeedOptions) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [postMeta, setPostMeta] = useState<PostMeta>({
    page: 1,
    size: PAGE_SIZE,
    total: 0,
    pages: 0,
  });
  const [selectedPostId, setSelectedPostId] = useState<number | null>(null);
  const [selectedPostOverride, setSelectedPostOverride] = useState<Post | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const [filters, setFilters] = useState<PostFilters>({ q: "", tag: "" });
  const [loadingPosts, setLoadingPosts] = useState(false);

  const selectedPost = useMemo(
    () =>
      posts.find((post) => post.id === selectedPostId) ??
      (selectedPostOverride?.id === selectedPostId ? selectedPostOverride : null),
    [posts, selectedPostId, selectedPostOverride],
  );
  const hasActiveFilters = Boolean(filters.q.trim() || filters.tag.trim());
  const selectedTag = filters.tag.trim();

  async function loadTags() {
    try {
      setTags(await fetchTags());
    } catch {
      setTags([]);
    }
  }

  async function loadPosts(page = postMeta.page, nextFilters = filters, nextSelectedId?: number) {
    setLoadingPosts(true);
    setError(null);
    try {
      const body = await fetchPosts(page, nextFilters);
      setPosts(body.items);
      setPostMeta({ page: body.page, size: body.size, total: body.total, pages: body.pages });
      const fallbackId = nextSelectedId ?? selectedPostId ?? body.items[0]?.id ?? null;
      setSelectedPostId(body.items.some((post) => post.id === fallbackId) ? fallbackId : body.items[0]?.id ?? null);
      if (body.items.some((post) => post.id === fallbackId)) {
        setSelectedPostOverride(null);
      }
    } catch (requestError) {
      setPosts([]);
      setSelectedPostId(null);
      setError(requestError instanceof Error ? requestError.message : "지원 카드를 불러오지 못했습니다.");
    } finally {
      setLoadingPosts(false);
    }
  }

  async function clearFilters() {
    const nextFilters = { q: "", tag: "" };
    setFilters(nextFilters);
    await loadPosts(1, nextFilters);
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadPosts(1, filters);
  }

  async function applyTagFilter(tagName: string) {
    const nextFilters = { ...filters, tag: filters.tag === tagName ? "" : tagName };
    setFilters(nextFilters);
    await loadPosts(1, nextFilters);
  }

  async function selectPost(postId: number) {
    setSelectedPostId(postId);
    const listedPost = posts.find((post) => post.id === postId);
    if (listedPost) {
      setSelectedPostOverride(null);
      return listedPost;
    }

    try {
      const post = await fetchPost(postId);
      setSelectedPostOverride(post);
      return post;
    } catch (requestError) {
      setSelectedPostId(selectedPostId);
      setError(requestError instanceof Error ? requestError.message : "지원 카드 상세를 불러오지 못했습니다.");
      return null;
    }
  }

  useEffect(() => {
    void loadPosts(1);
    void loadTags();
  }, []);

  return {
    applyTagFilter,
    clearFilters,
    filters,
    handleSearch,
    hasActiveFilters,
    loadPosts,
    loadTags,
    loadingPosts,
    postMeta,
    posts,
    selectedPost,
    selectedPostId,
    selectedTag,
    selectPost,
    setFilters,
    setSelectedPostId,
    tags,
  };
}
