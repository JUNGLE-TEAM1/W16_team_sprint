import { useState } from "react";

import type {
  ApiResult,
  ExternalReferencesJsonRpcResponse,
  ExternalReferencesState,
  PostFormState,
  RequestOptions,
} from "../types";
import { buildExternalReferencesPayload } from "../utils/postFormatting";

const EXTERNAL_REFERENCES_MIN_QUERY_LENGTH = 20;

type RequestFunction = <T>(endpoint: string, options?: RequestOptions) => Promise<ApiResult<T>>;

interface UseExternalReferencesOptions {
  request: RequestFunction;
}

function emptyExternalReferencesState(): ExternalReferencesState {
  return {
    items: [],
    isLoading: false,
    errorText: "",
  };
}

function buildJsonRpcBody(form: PostFormState) {
  return JSON.stringify({
    jsonrpc: "2.0",
    id: `external-reference-${Date.now()}`,
    method: "tools/call",
    params: {
      name: "search_external_references",
      arguments: buildExternalReferencesPayload(form),
    },
  });
}

export function useExternalReferences({ request }: UseExternalReferencesOptions) {
  const [composeExternalReferences, setComposeExternalReferences] =
    useState<ExternalReferencesState>(emptyExternalReferencesState);

  function resetComposeExternalReferences() {
    setComposeExternalReferences(emptyExternalReferencesState());
  }

  async function findComposeExternalReferences(form: PostFormState) {
    const queryText = `${form.title.trim()} ${form.content.trim()}`.trim();
    if (queryText.length < EXTERNAL_REFERENCES_MIN_QUERY_LENGTH) {
      setComposeExternalReferences({
        items: [],
        isLoading: false,
        errorText: `제목과 본문을 합쳐 ${EXTERNAL_REFERENCES_MIN_QUERY_LENGTH}자 이상 입력하면 참고자료를 찾을 수 있습니다.`,
      });
      return;
    }

    setComposeExternalReferences({
      items: [],
      isLoading: true,
      errorText: "",
    });

    try {
      const result = await request<ExternalReferencesJsonRpcResponse>("/api/v1/mcp", {
        method: "POST",
        body: buildJsonRpcBody(form),
        quiet: true,
      });

      if (!result.ok) {
        throw new Error("request failed");
      }

      if (result.data.error) {
        setComposeExternalReferences({
          items: [],
          isLoading: false,
          errorText: result.data.error.message || "외부 참고자료를 불러오지 못했습니다.",
        });
        return;
      }

      const items = result.data.result?.structuredContent?.items ?? [];
      setComposeExternalReferences({
        items,
        isLoading: false,
        errorText: items.length > 0 ? "" : "관련 외부 참고자료를 찾지 못했습니다.",
      });
    } catch {
      setComposeExternalReferences({
        items: [],
        isLoading: false,
        errorText: "외부 참고자료를 불러오지 못했습니다.",
      });
    }
  }

  return {
    composeExternalReferences,
    findComposeExternalReferences,
    resetComposeExternalReferences,
  };
}
