import { useMemo, useState } from "react";
import type { FormEvent } from "react";

import type {
  FieldChangeEvent,
  LoadOptions,
  LoadPostsOptions,
  PageMeta,
  Post,
  PostPage,
  SearchState,
  SortType,
  Tag,
} from "../types";
import { buildPostQuery } from "../utils/postFormatting";
import type { ApiRequest } from "./useApiRequest";

interface UsePostSearchOptions {
  request: ApiRequest;
}

export function usePostSearch({ request }: UsePostSearchOptions) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [search, setSearch] = useState<SearchState>({
    q: "",
    search_type: "title_content",
    tag: "",
    sort: "latest",
    page: 1,
    size: 9,
  });
  const [pageMeta, setPageMeta] = useState<PageMeta>({
    page: 1,
    size: 9,
    total: 0,
    total_pages: 0,
  });

  const selectedTagName = useMemo(
    () => tags.find((tag) => tag.name === search.tag)?.name || "",
    [tags, search.tag],
  );

  function updateSearch(event: FieldChangeEvent) {
    setSearch((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function loadTags(options: LoadOptions = {}) {
    const result = await request<Tag[]>("/api/v1/tags", {
      quiet: options.quiet,
      successMessage: "태그 목록을 불러왔습니다.",
    });
    if (result.ok && Array.isArray(result.data)) {
      setTags(result.data);
    }
  }

  async function loadPosts(options: LoadPostsOptions = {}) {
    const nextSearch = {
      ...search,
      ...(options.filters || {}),
    };
    setSearch(nextSearch);

    const result = await request<PostPage>(`/api/v1/posts?${buildPostQuery(nextSearch)}`, {
      quiet: options.quiet,
      successMessage: "지원 정보 목록을 불러왔습니다.",
    });
    if (result.ok && Array.isArray(result.data.items)) {
      setPosts(result.data.items);
      setPageMeta({
        page: result.data.page,
        size: result.data.size,
        total: result.data.total,
        total_pages: result.data.total_pages,
      });
    }
  }

  async function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadPosts({ filters: { page: 1 } });
  }

  async function filterByTag(tagName: string) {
    await loadPosts({
      filters: {
        tag: search.tag === tagName ? "" : tagName,
        page: 1,
      },
    });
  }

  async function clearFilters() {
    await loadPosts({
      filters: {
        q: "",
        search_type: "title_content",
        tag: "",
        sort: "latest",
        page: 1,
      },
    });
  }

  async function changeSort(event: FieldChangeEvent) {
    await loadPosts({
      filters: {
        sort: event.target.value as SortType,
        page: 1,
      },
    });
  }

  async function changePage(nextPage: number) {
    await loadPosts({ filters: { page: nextPage } });
  }

  return {
    posts,
    tags,
    search,
    pageMeta,
    selectedTagName,
    updateSearch,
    loadTags,
    loadPosts,
    submitSearch,
    filterByTag,
    clearFilters,
    changeSort,
    changePage,
  };
}
