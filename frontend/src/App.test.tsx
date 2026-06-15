import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the Sprint 4 board shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => ({ items: [], total: 0, page: 1, size: 10, pages: 0 }),
      })),
    );

    render(<App />);

    expect(screen.getByRole("heading", { name: "RAG 유사 글 추천" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "게시글 목록" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "게시글 작성" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "게시글 상세" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "유사 글 찾기" })).toBeInTheDocument();
  });
});
