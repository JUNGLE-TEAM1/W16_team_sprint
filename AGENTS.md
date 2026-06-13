# Project Working Rules

이 프로젝트에서 Codex는 구현 중 의미 있는 설계 분기가 생기면 `DECISION_HARNESS.md`를 따른다.

사용자가 단순히 "구현해줘", "스프린트 진행해줘", "Sprint 1 완성해줘"처럼 요청하더라도, Codex는 작업 전에 다음 문서를 확인해야 한다.

- `DECISION_HARNESS.md`
- `docs/decisions/DECISIONS.md`
- `docs/decisions/decision-harness-flow.md`

## Decision Harness Rule

구현 중 선택지가 생기면 임의로 조용히 결정하지 않는다.

결정의 영향도에 따라 `DECISION_HARNESS.md`의 Level 1, Level 2, Level 3 기준을 적용한다.

- Level 1: 되돌리기 쉽고 구조적 영향이 거의 없는 결정은 기존 코드 스타일에 맞춰 자동 처리한다.
- Level 2: 유지보수성, 테스트 범위, 작은 구조 선택에 영향을 주는 결정은 `[Small Branch]` 형식으로 짧게 알리고 진행한다.
- Level 3: 데이터 모델, API 계약, DB 스키마, 인증/권한, 라우팅, 모듈 경계, 외부 라이브러리 도입처럼 되돌리기 비용이 큰 결정은 Decision Harness를 발동한다.

## Level 3 Required Flow

Level 3 분기에서는 바로 구현하지 않는다.

다음 순서를 따른다.

1. 구현 전에 해당 스프린트의 `ROADMAP.md`를 만든다.
2. 발견된 결정 후보를 Level 1, Level 2, Level 3로 분류한다.
3. 결정 후보 사이의 의존성을 확인한다.
4. 서로 의존적인 결정은 처리 순서를 정하되, 상위 결정 하나로 하위 결정을 자동 확정하지 않는다.
5. 다음 Decision ID를 `docs/decisions/DECISIONS.md`에서 확인한다.
6. `docs/decisions/DECISIONS.md`에 `Status: Proposed`로 Decision ID를 먼저 예약한다.
7. 해당 스프린트의 `docs/decisions/sprint-N/decisions/`에 실제 사용자 선택을 요구하는 단일 Decision 문서를 만든다.
8. 사용자에게 현재 분기, 이번에 선택하지 않는 분기, 선택지, 추천안, Pass 기준, 답변 템플릿, Decision 문서 경로를 공유한다.
9. 사용자의 선택을 기다린다.
10. 사용자의 선택을 평가한다.
11. 답변이 부족하면 바로 Pass하지 않고 1~3개의 보완 질문을 한다.
12. Pass 상태가 되면 해당 Decision만 `Status: Accepted`, `Implementation: Planned`로 갱신한다.
13. 여전히 사용자 판단이 필요한 후속 분기가 있으면 다음 Decision으로 이어간다.
14. 필수 Level 3 결정이 모두 Pass되면 구현 전에 `Implementation Batch Snapshot`을 기록한다.
15. 구현한다.
16. 구현 결과에 따라 `Implementation: Completed / Failed / Rolled Back`으로 갱신한다.

## Dependency Rule

구현 전에 여러 결정 후보가 동시에 발견되면 개별 하네스를 즉시 여러 개 발동하지 않는다.

먼저 해당 스프린트의 `ROADMAP.md`를 만들고 다음을 정리한다.

- 발견된 결정 후보
- 각 결정의 Level
- 서로 의존적인 결정
- 먼저 통과해야 하는 상위 결정
- 먼저 선택해야 하는 결정
- 이번 선택으로 자동 확정되지 않는 후속 분기
- 상위 결정 결과에 따라 Level 1 또는 Level 2로 낮출 수 있는 하위 결정
- Sprint 진행을 막는 필수 결정
- 후속 스프린트로 미룰 수 있는 결정

Level 3가 발동되면 전체 후보 지도는 해당 스프린트의 `ROADMAP.md`에 남긴다. 후보에는 Decision ID를 미리 붙이지 않는다. 실제 사용자 선택이 필요한 후보만 Decision으로 승격하고, 그때 `docs/decisions/sprint-N/decisions/`에 개별 Decision 문서를 만든다.

의존성이 있는 경우 상위 결정을 먼저 다룬다. 단, 상위 결정은 하위 결정을 자동 확정하지 않는다.

예를 들어 게시글 작성자 저장 방식이 결정되지 않았으면, 수정/삭제 권한 검사 방식이나 게시글 응답의 작성자 표현을 먼저 확정하지 않는다.

한 번에 사용자에게 선택을 요구하는 Level 3 결정은 1개를 기본값으로 한다. 서로 독립적이고 작게 분리된 경우에도 최대 2개를 넘기지 않는다.

사용자 답변은 방향이 맞다고 바로 Pass하지 않는다. 다음 중 하나라도 부족하면 보완 질문을 한다.

- 선택은 했지만 이유가 없다.
- 권한 기준과 표시 기준을 구분하지 않았다.
- DB/API/테스트 중 무엇이 바뀌는지 언급하지 않았다.
- 이번 결정 이후 어떤 후속 분기가 남는지 이해하지 못했다.
- trade-off 없이 "그냥 A"처럼 답했다.
- 롤백 또는 재검토 조건이 전혀 없다.

Level 2 결정은 별도 결정 로그까지 남기지 않아도 되지만, 작업 완료 응답에 `[Small Branch Summary]`로 요약한다.

Level 3에서 파생되어 Level 1 또는 Level 2로 낮아진 결정은 부모 Decision 문서의 `Lowered Decisions` 섹션에 남긴다.

## Rollback Rule

Decision Harness가 발동된 결정은 구현 전에 롤백 계획을 함께 정리한다.

롤백 계획에는 다음을 포함한다.

- 어떤 파일이나 API 계약이 바뀌는가
- 되돌릴 때 어떤 파일을 다시 수정해야 하는가
- DB 스키마 변경이 있다면 데이터 손실 가능성이 있는가
- 테스트에서 무엇이 원래 상태를 보장하는가
- 어떤 조건이 생기면 이 결정을 되돌릴 것인가

Level 3 결정으로 구현을 시작하기 전에는 현재 git 상태를 확인한다. 이미 사용자 변경이 있는 경우 그 변경은 롤백 대상에 포함하지 않는다.

개별 Decision이 Pass되면 해당 Decision 문서에 선택 시점의 `Pre-Implementation Notes`를 남긴다.

모든 필수 Level 3 결정이 통과되어 실제 구현을 시작하기 직전에는 `Implementation Batch Snapshot`을 남긴다.

포함할 내용:

- 현재 git status
- 수정 예정 파일
- 각 파일에 기존 사용자 변경이 있는지
- Codex가 변경할 범위
- 롤백 시 되돌릴 범위
- 롤백 확인 명령 또는 테스트

잘못된 선택으로 판명되면 무조건 전체 작업을 되돌리지 않는다. 먼저 해당 결정으로 생긴 변경 범위를 식별하고, 사용자 변경과 무관한 부분만 되돌린다.

코드를 수정하다가 새 Level 3 분기를 발견하면 깨진 코드나 반쯤 적용된 API 계약을 남긴 채 멈추지 않는다. 가능한 경우 파일 수정 전에 멈추고, 이미 수정 중이었다면 테스트 가능하거나 설명 가능한 작은 중간 상태로 정리한 뒤 멈춘다.

롤백되었거나 실패한 구현/결정의 상세 기록은 해당 스프린트의 `decisions/`, `troubleshooting/`에 흩어두지 않는다. `docs/decisions/sprint-N/rollbacks/`에 롤백 문서를 만들고, 실패한 분기 설명/Q&A/결론/회수 범위/재진입 조건을 그 문서가 책임지게 한다. `DECISIONS.md`에는 전역 인덱스와 롤백 문서 링크만 간결하게 남긴다.

## Sprint Work

스프린트 구현 요청에서는 `docs/taejung/development-order.md`의 완료 기준을 우선 기준으로 삼는다.

Sprint 1 구현 중 특히 다음은 Level 3 후보로 본다.

- 회원가입 API 계약
- 게시글 작성자 저장 방식
- `Post.author_name` 유지 여부
- `Post.user_id` 추가 여부
- 게시글 수정/삭제 API 계약
- 인증 dependency 적용 범위
- 테스트 DB 전략 변경

이 항목들은 프로젝트 구조, API 계약, 데이터 모델에 영향을 줄 수 있으므로 Decision Harness 기준으로 판단한다.

단, 기존 docker-compose DB 실행, 테스트용 환경변수 설정, 단순 실행 명령 보정은 Level 3가 아니라 Level 1 또는 Level 2로 처리한다. DB 종류 변경, 테스트 격리 전략 변경, PostgreSQL에서 SQLite로 전환처럼 구현 제약이 바뀌는 경우만 Level 3로 본다.

## Documentation

Decision Harness가 발동된 결정은 반드시 `docs/decisions/DECISIONS.md`에 기록한다.

필요한 Decision 문서는 해당 스프린트의 `docs/decisions/sprint-N/decisions/`에 저장한다.

사용자의 질문과 답변이 선택 판단에 영향을 주면 기록한다. 짧은 Q&A는 Decision 문서 하단의 `Q&A` 섹션에 둘 수 있다. 선택을 바꾸거나 길어진 Q&A, 재발 방지 성격의 Q&A, Final Accepted Prompt는 해당 스프린트의 `docs/decisions/sprint-N/troubleshooting/`에 분리 기록한다.

최종 Pass가 되면 troubleshooting 문서에 `Final Accepted Prompt` 섹션을 추가한다. 여기에는 통과된 Decision, 사용자 최종 답변, Codex 평가, Pass 이유, 보완 질문 여부, 아직 남은 후속 분기, 최종 결론을 포함한다.

Decision Harness 기록에는 롤백 계획과 재검토 조건을 포함한다.
