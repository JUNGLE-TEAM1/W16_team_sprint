import { useState } from "react";

import type { LoadOptions, PageMeta, Post, PostPage } from "../types";
import type { ApiRequest } from "./useApiRequest";

interface LoadConsultationsOptions extends LoadOptions {
  page?: number;
}

interface UseConsultationsOptions {
  request: ApiRequest;
}

export function useConsultations({ request }: UseConsultationsOptions) {
  const [consultations, setConsultations] = useState<Post[]>([]);
  const [consultationPageMeta, setConsultationPageMeta] = useState<PageMeta>({
    page: 1,
    size: 9,
    total: 0,
    total_pages: 0,
  });

  async function loadConsultations(options: LoadConsultationsOptions = {}) {
    const page = options.page ?? consultationPageMeta.page;
    const result = await request<PostPage>(`/api/v1/posts/my-consultations?page=${page}&size=9`, {
      quiet: options.quiet,
      successMessage: "내 상담 기록을 불러왔습니다.",
    });

    if (result.ok && Array.isArray(result.data.items)) {
      setConsultations(result.data.items);
      setConsultationPageMeta({
        page: result.data.page,
        size: result.data.size,
        total: result.data.total,
        total_pages: result.data.total_pages,
      });
    }

    return result.ok;
  }

  function resetConsultations() {
    setConsultations([]);
    setConsultationPageMeta({
      page: 1,
      size: 9,
      total: 0,
      total_pages: 0,
    });
  }

  return {
    consultations,
    consultationPageMeta,
    loadConsultations,
    resetConsultations,
  };
}
