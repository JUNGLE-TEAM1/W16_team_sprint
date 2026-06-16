import { useCallback, useState } from "react";

import type { ApiErrorResponse, ApiResult, RequestOptions, StatusState } from "../types";

export type ApiRequest = <T>(
  endpoint: string,
  options?: RequestOptions,
) => Promise<ApiResult<T>>;

export function useApiRequest() {
  const [status, setStatus] = useState<StatusState>({
    text: "지원 정보를 탐색하거나 내 상황으로 지원을 찾아보세요.",
    isError: false,
  });

  const request = useCallback(
    async <T,>(endpoint: string, options: RequestOptions = {}): Promise<ApiResult<T>> => {
    if (!options.quiet) {
      setStatus({ text: "요청 중", isError: false });
    }

    const response = await fetch(endpoint, {
      method: options.method ?? "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
      },
      body: options.body,
    });

    const text = await response.text();
    const data = (text ? JSON.parse(text) : {}) as T & ApiErrorResponse;
    if (!options.quiet) {
      const message = response.ok
        ? options.successMessage || "완료"
        : data.error?.message || "요청에 실패했습니다.";
      setStatus({ text: message, isError: !response.ok });
    }
      return { ok: response.ok, status: response.status, data };
    },
    [],
  );

  return {
    status,
    setStatus,
    request,
  };
}
