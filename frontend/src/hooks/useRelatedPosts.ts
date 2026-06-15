import { useEffect, useRef, useState } from "react";

import type {
  ApiResult,
  PostFormState,
  RelatedPostsResponse,
  RelatedPostsState,
  RequestOptions,
} from "../types";
import { buildRelatedPostsPayload } from "../utils/postFormatting";

const RELATED_POSTS_DEBOUNCE_MS = 3000;
const RELATED_POSTS_MIN_QUERY_LENGTH = 20;

type RelatedPostsScope = "compose" | "edit";
type RequestFunction = <T>(endpoint: string, options?: RequestOptions) => Promise<ApiResult<T>>;

interface UseRelatedPostsOptions {
  isAuthenticated: boolean;
  isComposeOpen: boolean;
  postForm: PostFormState;
  isEditingPost: boolean;
  editForm: PostFormState;
  selectedPostId: number | null;
  request: RequestFunction;
}

function emptyRelatedPostsState(): RelatedPostsState {
  return {
    items: [],
    isLoading: false,
    errorText: "",
  };
}

export function useRelatedPosts({
  isAuthenticated,
  isComposeOpen,
  postForm,
  isEditingPost,
  editForm,
  selectedPostId,
  request,
}: UseRelatedPostsOptions) {
  const [composeRelatedPosts, setComposeRelatedPosts] = useState<RelatedPostsState>(
    emptyRelatedPostsState,
  );
  const [editRelatedPosts, setEditRelatedPosts] = useState<RelatedPostsState>(
    emptyRelatedPostsState,
  );
  const requestRef = useRef(request);
  const relatedRequestIds = useRef<Record<RelatedPostsScope, number>>({ compose: 0, edit: 0 });
  const relatedRequestKeys = useRef<Record<RelatedPostsScope, string>>({ compose: "", edit: "" });

  useEffect(() => {
    requestRef.current = request;
  }, [request]);

  useEffect(() => {
    return scheduleRelatedPosts("compose", postForm, null, isComposeOpen && isAuthenticated);
  }, [isAuthenticated, isComposeOpen, postForm.content, postForm.tags, postForm.title]);

  useEffect(() => {
    return scheduleRelatedPosts(
      "edit",
      editForm,
      selectedPostId,
      isEditingPost && isAuthenticated && Boolean(selectedPostId),
    );
  }, [
    editForm.content,
    editForm.tags,
    editForm.title,
    isAuthenticated,
    isEditingPost,
    selectedPostId,
  ]);

  function resetComposeRelatedPosts() {
    resetRelatedPosts("compose");
  }

  function resetEditRelatedPosts() {
    resetRelatedPosts("edit");
  }

  function setRelatedPostsState(scope: RelatedPostsScope, state: RelatedPostsState) {
    if (scope === "compose") {
      setComposeRelatedPosts(state);
      return;
    }
    setEditRelatedPosts(state);
  }

  function resetRelatedPosts(scope: RelatedPostsScope) {
    relatedRequestIds.current[scope] += 1;
    relatedRequestKeys.current[scope] = "";
    setRelatedPostsState(scope, emptyRelatedPostsState());
  }

  function buildRelatedRequestKey(form: PostFormState, excludePostId?: number | null) {
    const queryText = `${form.title.trim()} ${form.content.trim()}`.trim();
    if (queryText.length < RELATED_POSTS_MIN_QUERY_LENGTH) {
      return "";
    }
    return JSON.stringify(buildRelatedPostsPayload(form, excludePostId));
  }

  function scheduleRelatedPosts(
    scope: RelatedPostsScope,
    form: PostFormState,
    excludePostId: number | null,
    enabled: boolean,
  ) {
    if (!enabled) {
      resetRelatedPosts(scope);
      return;
    }

    const requestKey = buildRelatedRequestKey(form, excludePostId);
    if (!requestKey) {
      resetRelatedPosts(scope);
      return;
    }

    if (relatedRequestKeys.current[scope] === requestKey) {
      return;
    }

    const requestId = relatedRequestIds.current[scope] + 1;
    relatedRequestIds.current[scope] = requestId;
    relatedRequestKeys.current[scope] = "";
    setRelatedPostsState(scope, emptyRelatedPostsState());

    const timer = window.setTimeout(() => {
      void loadRelatedPosts(scope, form, excludePostId, requestKey, requestId);
    }, RELATED_POSTS_DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  }

  async function loadRelatedPosts(
    scope: RelatedPostsScope,
    form: PostFormState,
    excludePostId: number | null,
    requestKey: string,
    requestId: number,
  ) {
    setRelatedPostsState(scope, {
      items: [],
      isLoading: true,
      errorText: "",
    });

    try {
      const result = await requestRef.current<RelatedPostsResponse>("/api/v1/ai/rag/related-posts", {
        method: "POST",
        body: JSON.stringify(buildRelatedPostsPayload(form, excludePostId)),
        quiet: true,
      });

      if (requestId !== relatedRequestIds.current[scope]) {
        return;
      }

      if (result.ok && Array.isArray(result.data.items)) {
        relatedRequestKeys.current[scope] = requestKey;
        setRelatedPostsState(scope, {
          items: result.data.items,
          isLoading: false,
          errorText: "",
        });
        return;
      }
    } catch {
      // Recommendation errors should not interrupt the writing flow.
    }

    if (requestId === relatedRequestIds.current[scope]) {
      relatedRequestKeys.current[scope] = requestKey;
      setRelatedPostsState(scope, {
        items: [],
        isLoading: false,
        errorText: "유사 게시글을 불러오지 못했습니다.",
      });
    }
  }

  return {
    composeRelatedPosts,
    editRelatedPosts,
    resetComposeRelatedPosts,
    resetEditRelatedPosts,
  };
}
