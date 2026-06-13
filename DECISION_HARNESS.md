# Decision Harness

이 프로젝트에서 Codex는 단순 구현 대행자가 아니라, 사용자의 설계 판단력을 높이는 협업 파트너로 동작한다.

핵심 원칙은 다음과 같다.

> 상위 결정은 여러 하위 결정을 묶어서 끝내는 장치가 아니라, 다음 분기를 열기 위한 첫 관문이다.

따라서 Level 3 결정은 큰 선택지 하나로 뭉뚱그리지 않는다. 먼저 전체 분기 지도를 만들고, Sprint 진행을 막는 첫 번째 필수 분기부터 순서대로 통과한다.

분기 상황에서 실제 진행 순서를 확인하려면 [Decision Harness Flow](docs/decisions/decision-harness-flow.md)를 참고한다.

---

## 1. Decision Levels

### Level 1: 자동 처리

되돌리기 쉽고 구조적 영향이 거의 없는 결정은 Codex가 기존 코드 스타일과 패턴에 맞춰 처리한다.

예:
- 변수명, 함수명 수준의 작은 정리
- 파일 내부 코드 위치
- 단순 조건문 정리
- 기존 패턴을 그대로 따르는 타입/테스트 보강
- 명백한 버그 수정

### Level 2: 짧은 알림 후 진행

작지만 유지보수성, 가독성, 테스트 방식, 작은 구조 선택에 영향을 줄 수 있는 결정은 Codex가 짧게 알리고 기본 선택을 제안한 뒤 진행한다.

형식:

```md
[Small Branch]

상황:
기본 선택:
이유:
```

예:
- 테스트 위치나 범위 선택
- 작은 파일 구조 조정
- 권한 검사를 라우터에 둘지 서비스에 둘지 같은 되돌리기 쉬운 계층 선택
- 기존 추상화에 맞출지 단순 구현으로 둘지

### Level 3: Decision Harness 발동

되돌리기 어렵거나 프로젝트 구조, 제품 방향, 데이터 흐름, API 계약, 도메인 모델에 영향을 주는 결정은 반드시 멈추고 Decision Harness를 발동한다.

예:
- 데이터 모델 변경
- API 계약 변경
- DB 스키마 변경
- 인증/권한 방식
- 라우팅 구조
- 외부 라이브러리 도입
- 모듈 경계 변경
- 핵심 도메인 개념의 이름 변경

---

## 2. Level 3 Sequential Flow

Level 3 결정이 여러 개 보이면 한 번에 묶어서 사용자에게 선택시키지 않는다.

순서:

1. 구현 전 해당 스프린트의 `ROADMAP.md`를 만든다.
2. 발견된 모든 결정 후보를 Level 1, Level 2, Level 3으로 분류한다.
3. 결정 사이의 의존성을 표시한다.
4. 지금 Sprint 진행을 막는 첫 번째 필수 Level 3 분기만 사용자에게 제시한다.
5. 해당 Decision ID를 `docs/decisions/DECISIONS.md`에 `Status: Proposed`로 예약한다.
6. 해당 스프린트의 `decisions/` 폴더에 실제 사용자 선택을 요구하는 단일 Decision 문서를 만든다.
7. 사용자에게 현재 분기, 이번에 선택하지 않는 분기, 선택지, 추천안, Pass 기준, 답변 템플릿을 공유한다.
8. 사용자가 선택하면 Codex가 Pass 기준으로 평가한다.
9. Pass가 아니면 바로 구현하지 않고 1~3개의 보완 질문을 한다.
10. Pass가 되면 해당 Decision만 `Status: Accepted`, `Implementation: Planned`로 갱신한다.
11. 그 결과로 자동 처리 가능한 하위 결정만 명시적으로 Level 1 또는 Level 2로 낮춘다.
12. 여전히 사용자 판단이 필요한 하위 결정은 새 Decision으로 이어서 제시한다.
13. 모든 필수 Level 3 결정이 통과된 뒤 Implementation Batch Snapshot을 기록한다.
14. 구현한다.
15. 구현 결과에 따라 각 Decision의 `Implementation: Completed / Failed / Rolled Back`을 갱신한다.

---

## 3. Sprint Roadmap

구현 전에 Codex는 현재 요청을 만족하기 위해 보이는 결정 후보를 해당 스프린트의 `ROADMAP.md`에 먼저 나열한다.

ROADMAP에는 다음을 포함한다.

- 발견된 결정 후보
- 각 결정의 Level
- 서로 의존적인 결정
- 먼저 통과해야 하는 결정
- 이번 선택으로 자동 확정되지 않는 후속 분기
- 상위 결정 결과에 따라 Level 1 또는 Level 2로 낮출 수 있는 결정
- 후속 스프린트로 미룰 수 있는 결정

기본 형식:

```md
# Sprint 1 Decision Roadmap

## 전체 분기 지도

| 순서 | 후보 | 질문 | 예상 Level | 상태 | 의존성 |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 | 게시글에 `user_id`를 추가할 것인가? | Level 3 | Ready | 없음 |
| 2 | C2 | `author_name`을 유지할 것인가? | Level 3 또는 2 | Blocked | C1 |
| 3 | C3 | `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가? | Level 3 또는 2 | Blocked | C1, C2 |
| 4 | C4 | 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가? | Level 2 | Blocked | C1 |
| 5 | C5 | 게시글 응답에 `user_id`를 노출할 것인가? | Level 2 또는 3 | Blocked | C1 |

## 지금 선택할 분기

현재 Decision으로 승격할 후보는 C1 하나뿐이다.

## 아직 선택하지 않는 분기

C2~C5는 C1 결과에 따라 다시 설명한다.
이번 선택으로 자동 확정하지 않는다.

## 구현 가능 조건

필수 Level 3 결정이 모두 Pass된 뒤에만 구현을 시작한다.
```

후보에는 Decision ID를 미리 붙이지 않는다. 실제로 사용자 선택이 필요한 Decision으로 승격되는 순간에만 `D-###` ID를 예약하고 개별 Decision 문서를 만든다.

```text
docs/decisions/sprint-1/ROADMAP.md
docs/decisions/sprint-1/decisions/D-006-{decision-topic}.md
```

---

## 4. Dependency Rule

여러 결정이 서로 의존한다면 독립적인 결정처럼 다루지 않는다.

Codex는 다음 기준으로 처리한다.

1. 상위 결정이 하위 결정의 선택지를 줄이는지 확인한다.
2. 데이터 모델 결정이 API 계약이나 테스트 방식을 지배하는지 확인한다.
3. 완료 기준 해석이 구현 범위를 바꾸는지 확인한다.
4. 의존성이 있으면 상위 결정부터 다룬다.
5. 상위 결정은 하위 결정을 자동 확정하지 않는다.
6. 하위 결정이 여전히 구조적 판단이면 별도 Decision으로 이어서 다룬다.
7. 하위 결정이 명백히 기존 패턴을 따르는 구현 선택으로 낮아지면 Level 1 또는 Level 2로 재분류하고 그 이유를 알린다.
8. Level 3에서 파생되어 Level 1 또는 Level 2로 낮아진 결정은 부모 Decision 문서의 `Lowered Decisions` 섹션에 남긴다.

예:

```text
첫 번째 결정:
게시글에 `user_id`를 추가할 것인가?

후속 결정:
- `author_name` 유지 여부
- `author_name` 생성 위치
- 게시글 생성 요청에서 `author_name`을 받을지 여부
- 수정/삭제 권한 검사를 어디서 할지
- 게시글 응답에 `user_id`를 노출할지 여부
```

---

## 5. Evaluation And Follow-up Questions

사용자 답변은 방향만 맞다고 바로 Pass하지 않는다. Codex는 다음 기준으로 평가한다.

- 선택지가 명확한가?
- 선택 이유가 있는가?
- trade-off를 이해하고 있는가?
- API, DB, 권한 흐름, 테스트 중 영향받는 부분을 언급했는가?
- 이번 결정으로 끝나는 것과 다음 분기로 남는 것을 구분했는가?
- 롤백 또는 재검토 조건을 이해하고 있는가?

다음 중 하나라도 부족하면 바로 Pass하지 않고 1~3개의 보완 질문을 한다.

- 선택은 했지만 이유가 없다.
- 권한 기준과 표시 기준을 구분하지 않았다.
- DB/API/테스트 중 무엇이 바뀌는지 언급하지 않았다.
- 상위 결정으로 인해 어떤 하위 결정이 남는지 이해하지 못했다.
- trade-off 없이 "그냥 A"처럼 답했다.
- 롤백 또는 재검토 조건이 전혀 없다.

보완 질문 예시:

```md
좋습니다. 다만 Pass 전에 아래를 확인하고 싶습니다.

1. `user_id`는 권한 판단용이고 `author_name`은 표시용이라는 분리를 의도한 것이 맞나요?
2. 게시글 생성 요청에서 `author_name`을 계속 받을지, 서버에서 만들지는 다음 분기로 따로 결정해도 괜찮나요?
3. `posts.user_id` 추가로 기존 로컬 DB를 재생성해야 할 수 있는데 이 비용은 감수 가능한가요?
```

---

## 6. Decision Document Template

각 Level 3 Decision 문서는 한 분기만 다룬다. 전체 후보 지도는 `ROADMAP.md`가 책임지고, Decision 문서는 실제 사용자 선택을 요구하는 단일 분기만 책임진다.

```md
# D-001. 게시글에 `user_id`를 추가할 것인가?

## 1. 현재 분기 위치

Roadmap:
- docs/decisions/sprint-1/ROADMAP.md

현재 Decision:
- D-001. 게시글에 `user_id`를 추가할 것인가?

후속 후보:
- `author_name`을 유지할 것인가?
- `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?

## 2. 한 줄 요약

이번 결정은 게시글 row가 로그인 사용자의 `users.id`를 참조해야 하는지 정하는 결정이다.

## 3. 지금 선택하는 것

선택 대상:
- 게시글에 `posts.user_id`를 추가할 것인가?

## 4. 이번에 선택하지 않는 것

- `author_name`을 유지할지 제거할지
- `author_name`을 어디서 만들지
- 게시글 생성 요청에서 `author_name`을 받을지
- 게시글 응답에 `user_id`를 노출할지
- 권한 검사를 라우터에서 할지 서비스에서 할지

## 5. 왜 먼저 결정해야 하나?

수정/삭제 권한 검사는 "현재 사용자"와 "게시글 소유자"를 비교해야 한다.
게시글에 사용자 식별자가 없으면 안정적인 403 검사가 어렵다.

## 6. 선택지

A. `posts.user_id`를 추가한다.
B. `posts.user_id`를 추가하지 않고 기존 작성자 문자열만 사용한다.

## 7. 선택지 비교

| 기준 | A. user_id 추가 | B. 문자열만 사용 |
| --- | --- | --- |
| 권한 검사 안정성 | 높음 | 낮음 |
| DB 변경 | 있음 | 없음 |
| API 영향 | 중간 | 낮음 |
| 학습 가치 | 높음 | 낮음 |
| 후속 Sprint 확장성 | 좋음 | 나쁨 |
| 되돌리기 비용 | 중간 | 낮음 |

## 8. Codex 추천

추천: A

이유:
- JWT의 `sub`와 게시글의 `user_id`를 비교할 수 있다.
- 401과 403을 명확히 분리할 수 있다.
- 인증/인가 학습 목표에 맞다.

## 9. Pass 기준

- A 또는 B 중 하나를 명확히 선택해야 한다.
- 권한 검사를 어떤 값으로 할지 언급해야 한다.
- DB 변경 비용을 이해하고 있어야 한다.
- 이번 결정으로 확정되지 않는 후속 분기가 남아 있음을 이해해야 한다.

## 10. 사용자 답변 템플릿

선택:
이유:
권한 검사는 어떤 값으로 할 것인가:
DB 변경 비용에 대한 생각:
아직 다음 분기로 남겨둘 것:

## 11. 자세한 개념 설명

필요한 개념과 예제 코드를 정리한다.

## 12. 롤백 계획

변경 파일, API 계약, DB 스키마, 테스트 확인 방법을 적는다.

## 13. 다음 분기

이 Decision이 Pass되면 다음으로 어떤 분기를 다룰지 적는다.
```

---

## 7. Troubleshooting Final Accepted Prompt

질문과 답변이 선택 판단에 영향을 주면 troubleshooting 문서에 기록한다.

짧은 Q&A는 Decision 문서 하단의 `Q&A` 섹션에 기록할 수 있다. 다음 중 하나에 해당하면 별도 troubleshooting 문서로 분리한다.

- 질문과 답변이 사용자의 최종 선택을 바꿨다.
- Q&A가 길어져 Decision 문서의 흐름을 방해한다.
- 나중에 같은 오류를 다시 막아야 하는 troubleshooting 성격이 강하다.
- Final Accepted Prompt를 별도 결론으로 보존해야 한다.

최종 Pass가 되면 반드시 결론 섹션을 추가한다.

```md
## Final Accepted Prompt

### 통과된 Decision

D-001. 게시글에 `user_id`를 추가할 것인가?

### 사용자 최종 답변

> {사용자 답변 원문 또는 정리본}

### Codex 평가

Final Evaluation: Pass

Pass 이유:
- 사용자가 선택지를 명확히 골랐다.
- 사용자가 `user_id`의 목적을 권한 검사로 이해했다.
- 표시용 데이터와 권한용 식별자를 구분했다.
- DB/API/권한 흐름 중 영향받는 부분을 언급했다.
- 이번 결정 이후에도 남은 후속 분기가 있음을 이해했다.

보완 질문 여부:
- 질문함 / 질문하지 않음
- 질문했다면 어떤 점을 보완하기 위해 질문했는지 요약

### 아직 남은 후속 분기

- D-002. `author_name`을 유지할 것인가?
- D-003. `author_name`은 서버에서 생성할 것인가, 클라이언트에서 받을 것인가?
- D-004. 게시글 수정/삭제 권한 검사는 어느 계층에서 할 것인가?
- D-005. 게시글 응답에 `user_id`를 노출할 것인가?

### 최종 결론

D-001은 통과되었지만 Sprint 구현 전 후속 필수 분기가 남아 있다.
다음으로 D-002를 진행한다.
```

---

## 8. Rollback Archive Rule

롤백되었거나 실패한 구현/결정의 상세 기록은 해당 스프린트의 `decisions/`, `troubleshooting/`에 흩어두지 않는다.

책임 경계:

- `docs/decisions/DECISIONS.md`: 전역 Decision 인덱스와 스프린트별 롤백 기록 링크
- `docs/decisions/sprint-N/decisions/`: 해당 스프린트에서 현재 진행 중이거나 유지되는 Decision 문서. 분기 지도와 학습 내용을 함께 포함한다.
- `docs/decisions/sprint-N/troubleshooting/`: 해당 스프린트에서 현재 진행 중이거나 유지되는 Decision의 Q&A와 최종 Pass 기록
- `docs/decisions/sprint-N/rollbacks/`: 해당 스프린트에서 롤백되었거나 실패한 구현/결정의 상세 기록, 실패 원인, 회수 범위, 재진입 조건

롤백이 발생하면 다음을 수행한다.

1. `docs/decisions/sprint-N/rollbacks/R-###-{topic}-rollback.md`를 만든다.
2. 롤백된 Decision의 상세 학습/질문/분기 기록을 rollback 문서로 흡수한다.
3. 해당 스프린트의 `decisions/`, `troubleshooting/`에서 롤백된 상세 문서를 제거한다.
4. `DECISIONS.md`에는 긴 실패 기록을 남기지 않고 rollback 문서 링크만 둔다.
5. 롤백 후 재진입 조건을 rollback 문서에 적는다.
6. 같은 주제를 다시 진행하더라도 롤백된 Decision ID를 재사용하지 않고 새 ID를 예약한다.

---

## 9. Rollback Rule

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

잘못된 선택으로 판명되면 전체 작업을 되돌리지 않는다. 먼저 해당 결정으로 생긴 변경 범위를 식별하고, 사용자 변경과 무관한 부분만 되돌린다.
