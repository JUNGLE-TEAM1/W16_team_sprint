import { useState } from "react";

import type { PetCareAdvice, PetCareAdviceState, Post } from "../types";
import type { ApiRequest } from "./useApiRequest";

interface UsePetCareAdviceOptions {
  request: ApiRequest;
  isAuthenticated: boolean;
  onAuthRequired: (message: string) => void;
}

function emptyAdviceState(): PetCareAdviceState {
  return {
    advice: null,
    isLoading: false,
    errorText: "",
  };
}

export function usePetCareAdvice({ request, isAuthenticated, onAuthRequired }: UsePetCareAdviceOptions) {
  const [adviceByPostId, setAdviceByPostId] = useState<Record<number, PetCareAdviceState>>({});

  function getAdviceState(postId: number | null): PetCareAdviceState {
    if (!postId) {
      return emptyAdviceState();
    }
    return adviceByPostId[postId] ?? emptyAdviceState();
  }

  function clearAdvice(postId: number | null) {
    if (!postId) {
      return;
    }
    setAdviceByPostId((current) => {
      const next = { ...current };
      delete next[postId];
      return next;
    });
  }

  async function loadForPost(post: Post) {
    setAdviceByPostId((current) => ({
      ...current,
      [post.id]: { advice: current[post.id]?.advice ?? null, isLoading: true, errorText: "" },
    }));

    const result = await request<PetCareAdvice | null>(`/api/v1/ai/pet-care/posts/${post.id}/advice`, {
      quiet: true,
    });

    if (result.ok) {
      setAdviceByPostId((current) => ({
        ...current,
        [post.id]: { advice: result.data, isLoading: false, errorText: "" },
      }));
      return result.data;
    }

    setAdviceByPostId((current) => ({
      ...current,
      [post.id]: {
        advice: current[post.id]?.advice ?? null,
        isLoading: false,
        errorText: "저장된 AI 답변을 불러오지 못했습니다.",
      },
    }));
    return null;
  }

  async function generateForPost(post: Post) {
    if (!isAuthenticated) {
      onAuthRequired("AI 답변 생성은 로그인이 필요합니다.");
      return null;
    }

    setAdviceByPostId((current) => ({
      ...current,
      [post.id]: { advice: current[post.id]?.advice ?? null, isLoading: true, errorText: "" },
    }));

    const result = await request<PetCareAdvice>(`/api/v1/ai/pet-care/posts/${post.id}/advice`, {
      method: "POST",
      quiet: true,
    });

    if (result.ok) {
      setAdviceByPostId((current) => ({
        ...current,
        [post.id]: { advice: result.data, isLoading: false, errorText: "" },
      }));
      return result.data;
    }

    const errorText = "AI 답변을 생성하지 못했습니다.";
    setAdviceByPostId((current) => ({
      ...current,
      [post.id]: { advice: current[post.id]?.advice ?? null, isLoading: false, errorText },
    }));
    return null;
  }

  async function generateForCreatedPost(post: Post) {
    if (!isAuthenticated) {
      return null;
    }
    setAdviceByPostId((current) => ({
      ...current,
      [post.id]: { advice: null, isLoading: true, errorText: "" },
    }));
    const result = await request<PetCareAdvice>(`/api/v1/ai/pet-care/posts/${post.id}/advice`, {
      method: "POST",
      quiet: true,
    });
    if (result.ok) {
      setAdviceByPostId((current) => ({
        ...current,
        [post.id]: { advice: result.data, isLoading: false, errorText: "" },
      }));
      return result.data;
    }
    setAdviceByPostId((current) => ({
      ...current,
      [post.id]: { advice: null, isLoading: false, errorText: "AI 답변을 생성하지 못했습니다." },
    }));
    return null;
  }

  return {
    getAdviceState,
    loadForPost,
    clearAdvice,
    generateForPost,
    generateForCreatedPost,
  };
}
