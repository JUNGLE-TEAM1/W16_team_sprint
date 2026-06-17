# 01. Product Planning

This is the baseline product planning document for the existing 조선왕조실록 AI 게시판 codebase.

## Product Summary

조선왕조실록 AI 게시판은 사용자가 역사 질문 게시글을 작성하면 관련 실록 원문을 검색하고, AI가 원문 근거 기반 초벌 요약과 쉬운 해석을 생성해 토론을 돕는 웹 애플리케이션이다.

## Target Users

- 한국사 학습자
- 역사 콘텐츠 작성자
- 조선왕조실록 원문 근거를 확인하며 토론하려는 사용자

## User Problems

- 조선왕조실록 원문은 양이 많아 필요한 기사를 찾기 어렵다.
- 원문이 한문 중심이라 검색 결과의 맥락을 바로 이해하기 어렵다.
- 일반 LLM 답변은 원문 근거를 확인하기 어렵다.
- 역사 토론에서 신뢰할 수 있는 근거 자료를 함께 보기 어렵다.

## Core Value

사용자가 질문 글을 작성하는 순간 관련 실록 원문을 함께 찾고, AI가 해당 원문만 근거로 초벌 요약과 쉬운 해석을 제공한다.

Core flow:

```text
사용자 질문 게시글 작성
→ 관련 조선왕조실록 원문 검색
→ MCP tool로 원문 기사 조회
→ LLM이 원문 기반 초벌 요약/해석 생성
→ 추천 태그와 근거 기사 저장
→ 게시글 상세 화면에서 근거 기반 토론
```

## Current Product Scope

- 회원가입과 로그인
- 게시글 작성, 목록, 상세, 수정, 삭제
- 댓글 작성과 조회
- 게시글 검색, 페이징, 태그 필터
- 실록 XML 파싱과 기사 저장
- chunk 생성, embedding, hybrid search
- metadata filter, query rewrite, reranking
- 원문 근거 기반 AI 요약/해석과 추천 태그
- MCP tool 기반 기사 조회
- AI 토론 도우미 스트리밍
- Realtime 음성 토론 모드

## Current Non-Goals / Unknowns

- 운영 배포와 CD 정책은 아직 정의되지 않았다.
- CI/PR 정책은 아직 정의되지 않았다.
- 관리자 기능, 권한 세분화, 운영 모니터링은 baseline 범위에서 확인되지 않았다.
- 검색 품질 평가 기준과 AI 답변 품질 기준은 별도 acceptance 문서가 필요하다.

## Success Criteria Baseline

- 사용자가 질문 글을 작성하고 관련 실록 근거와 AI 초벌 답변을 볼 수 있다.
- 사용자가 근거 기사와 댓글을 바탕으로 토론할 수 있다.
- AI 답변은 저장된 원문 근거와 연결된다.
- 기본 로컬 개발 명령과 테스트 명령이 문서화되어 있다.

## Source

This baseline is summarized from `README.md` and `docs/02-architecture.md`.
