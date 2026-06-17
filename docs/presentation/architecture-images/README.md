# 발표용 아키텍처 이미지 설명

이 폴더는 PPT에 바로 넣을 수 있는 발표용 아키텍처 이미지와 설명 문서를 담고 있습니다.

## 파일 구성

| 이미지 | 대본 문서 | 발표 메시지 |
| --- | --- | --- |
| `01-system-overview.png` | `01-system-overview.md` | 게시판 UI, 백엔드 API, 원문 DB, AI API, MCP 도구가 연결된 근거 기반 AI 게시판 |
| `02-rag-agent-flow.png` | `02-rag-agent-flow.md` | 질문이 원문 근거 기반 AI 답변으로 변환되는 핵심 흐름 |
| `03-data-model-erd.png` | `03-data-model-erd.md` | 원문 데이터, 검색 색인, 게시글, 토론 로그가 분리되어 저장됨 |
| `04-hybrid-search.png` | `04-hybrid-search.md` | embedding 검색과 키워드 검색을 결합해 실록 기사 후보를 찾음 |
| `05-realtime-discussion.png` | `05-realtime-discussion.md` | 게시글 생성 후에도 근거 기반 텍스트/음성 토론이 이어짐 |

## 사용 팁

- PPT에는 PNG를 넣는 것이 가장 안정적입니다.
- SVG는 크기 조절이 더 선명하지만, 발표 환경에 따라 폰트 렌더링 차이가 날 수 있습니다.
- 각 대본 문서의 "발표 대본"은 40-60초 정도로 말할 수 있게 작성했습니다.
- 시간이 부족하면 각 문서의 "짧게 말할 때"만 사용해도 됩니다.
