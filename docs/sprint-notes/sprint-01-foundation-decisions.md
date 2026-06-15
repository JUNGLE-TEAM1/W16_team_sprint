# Sprint 01 - Foundation 설계 의사결정 가이드

## 0. 이 문서의 목적

이 문서는 AI 지식 공유 게시판의 Sprint 1 기반 설계를 확정하기 위한 가이드입니다.

지금까지의 레포에는 Sprint 1 학습용 `posts` API와 Sprint 2 인증 방식 비교 코드가 섞여 있습니다. 앞으로는 개인 과제 MVP 기준으로 아래 흐름을 만들기 위해 Sprint 1 기반을 정리합니다.

```text
회원가입
-> Session 로그인
-> 로그인한 사용자가 게시글 작성
-> 게시글은 작성자 User와 FK로 연결
-> 이후 Sprint에서 댓글/태그/검색/AI 기능 확장
```

## 1. 확정한 결정

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 서비스 방향 | AI 지식 공유 게시판 | `docs/ai_knowledge_board_sprint_plan.md`의 공통 MVP 기준을 따른다. |
| Backend | FastAPI | 팀 공통 스택이다. |
| Frontend | React + Vite | 팀 공통 스택이다. |
| DB | PostgreSQL | 이후 pgvector 기반 RAG까지 연결하기 위해 필요하다. |
| ORM | SQLAlchemy | 현재 코드가 이미 SQLAlchemy 기반이고, PostgreSQL과 잘 맞는다. |
| 계층 구조 | router / schema / service / repository / model | Sprint 1에서 만든 흐름을 유지하고 Sprint 2 인증에도 확장한다. |
| DB session 주입 | FastAPI dependency `get_db()` | 요청 단위 DB session을 일관되게 관리할 수 있다. |
| Post 작성자 구조 | `posts.author_id -> users.id` FK | Session 인증 후 `current_user.id`로 게시글 작성자를 연결하기 위해 필요하다. |
| `author_name` | 제거 | 문자열 작성자는 인증/인가와 연결되지 않는다. |
| `updated_at` | 추가 | 내일 CRUD Sprint에서 수정 시각을 다루기 위해 필요하다. |
| 응답 작성자 표시 | `author_display_name` 포함 | 프론트에서 게시글 작성자를 바로 표시하기 좋다. |
| Comment/Tag | 내일 Sprint에서 구현 | 오늘 범위를 줄이고 Sprint 1/2 완료에 집중한다. |
| Sprint 2 인증 방식 | Session 인증을 main auth로 선택 | 브라우저 기반 React 앱과 잘 맞고, 서버에서 세션을 삭제해 로그아웃을 명확히 처리할 수 있다. |
| Migration 방식 | 오늘은 DB reset | Alembic은 보류하고 Sprint 1/2 구현에 집중한다. |

## 2. Alembic이 무엇인가?

Alembic은 SQLAlchemy 프로젝트에서 DB schema 변경 이력을 관리하는 migration 도구입니다.

쉽게 말하면, 코드의 Git commit처럼 DB schema 변경에도 버전을 남기는 도구입니다.

예를 들어 Sprint 1에서 `posts` 테이블이 이렇게 시작했다고 가정합니다.

```text
posts
- id
- title
- content
- author_name
- created_at
```

이후 Sprint 2를 위해 아래처럼 바꾸고 싶습니다.

```text
posts
- id
- title
- content
- author_id
- created_at
- updated_at
```

이때 이미 DB에 `posts` 테이블이 있으면 `Base.metadata.create_all()`만으로는 기존 컬럼을 자동 변경하지 않습니다. `create_all()`은 이름 그대로 "없는 테이블을 생성"하는 데 가깝고, 이미 있는 테이블을 안전하게 수정하는 도구는 아닙니다.

Alembic은 이런 변경을 migration 파일로 남깁니다.

```text
revision 001: create users and posts
revision 002: replace posts.author_name with posts.author_id
revision 003: add comments table
```

각 revision 파일에는 DB를 앞으로 변경하는 `upgrade()`와 되돌리는 `downgrade()`가 들어갑니다.

```python
def upgrade() -> None:
    op.add_column("posts", sa.Column("author_id", sa.Integer(), nullable=False))
    op.create_foreign_key("fk_posts_author_id_users", "posts", "users", ["author_id"], ["id"])
    op.drop_column("posts", "author_name")


def downgrade() -> None:
    op.add_column("posts", sa.Column("author_name", sa.String(length=40), nullable=False))
    op.drop_constraint("fk_posts_author_id_users", "posts", type_="foreignkey")
    op.drop_column("posts", "author_id")
```

## 3. Alembic을 쓰면 좋은 점

| 장점 | 설명 |
| --- | --- |
| 변경 이력이 남는다 | DB 구조가 언제 왜 바뀌었는지 추적할 수 있다. |
| 팀원이 같은 DB 구조를 맞추기 쉽다 | `alembic upgrade head`로 같은 schema에 도달할 수 있다. |
| 운영 DB를 안전하게 변경할 수 있다 | 데이터를 유지하면서 컬럼 추가/변경/삭제를 관리할 수 있다. |
| 롤백 경로를 남길 수 있다 | 일부 migration은 `downgrade()`로 되돌릴 수 있다. |

## 4. Alembic의 비용

| 비용 | 설명 |
| --- | --- |
| 초기 설정이 필요하다 | `alembic init`, env 설정, metadata 연결이 필요하다. |
| 학습량이 늘어난다 | revision, upgrade, downgrade, autogenerate 개념을 알아야 한다. |
| migration 작성 실수가 가능하다 | 자동 생성 결과를 그대로 믿으면 위험할 수 있다. |
| 오늘 목표를 밀 수 있다 | Sprint 1/2 완료보다 migration 도구 학습에 시간이 쏠릴 수 있다. |

## 5. 오늘의 migration 선택지

### 선택지 A. 오늘 Alembic을 도입한다

```text
장점:
- 실제 서비스 개발 방식에 가깝다.
- 이후 Sprint 3~6에서 DB 변경이 많아질 때 편하다.

단점:
- 오늘 학습/구현 범위가 커진다.
- 인증/게시글 작성자 연결보다 migration 설정에 시간을 쓸 수 있다.
```

### 선택지 B. 오늘은 DB reset으로 간다

```text
장점:
- 빠르게 schema를 바꾸고 Sprint 1/2 구현에 집중할 수 있다.
- 현재는 개인 학습용 로컬 DB라 데이터 손실 부담이 작다.

단점:
- DB 변경 이력은 남지 않는다.
- 나중에 데이터가 중요해지면 Alembic을 다시 도입해야 한다.
```

### 추천

오늘은 **선택지 B: DB reset**을 추천합니다.

이유는 오늘 목표가 migration 도구 학습이 아니라 아래 두 가지이기 때문입니다.

```text
1. Sprint 1 기반 구조를 AI 지식 공유 게시판에 맞게 정리한다.
2. Sprint 2에서 Session 인증을 붙일 수 있는 구조를 만든다.
```

Alembic은 Sprint 3 또는 Sprint 4 시작 전에 도입해도 됩니다. 그 시점에는 댓글, 태그, 검색, RAG를 위해 DB 변경이 계속 생기므로 도입 효과가 더 큽니다.

## 6. DB reset이 의미하는 것

DB reset은 로컬 PostgreSQL의 현재 테이블과 데이터를 지우고, 새 모델 기준으로 다시 테이블을 만드는 방식입니다.

주의할 점:

```text
- 기존 회원/게시글 테스트 데이터는 사라진다.
- 로컬 개발 DB에서만 사용한다.
- 실제 운영 DB에서는 이렇게 하면 안 된다.
```

현재 단계에서는 학습용 데이터만 있으므로 reset 방식으로 진행해도 무리가 작습니다.

## 7. Sprint 1에서 바뀌어야 하는 코드

### 7.1 `backend/app/models/post.py`

현재:

```text
posts.author_name: string
```

변경:

```text
posts.author_id: FK users.id
posts.updated_at: datetime
```

예상 모델:

```text
Post
- id
- title
- content
- author_id
- created_at
- updated_at
```

### 7.2 `backend/app/schemas/post.py`

현재 `PostCreate`는 `author_name`을 받습니다.

변경 후 `PostCreate`는 작성자 정보를 받지 않습니다. 작성자는 Sprint 2에서 Session 인증으로 확인한 `current_user`에서 결정합니다.

```text
PostCreate
- title
- content

PostRead
- id
- title
- content
- author_id
- author_display_name
- created_at
- updated_at
```

### 7.3 `backend/app/services/post_service.py`

현재는 payload만으로 Post를 생성합니다.

```python
def create(self, payload: PostCreate) -> Post:
    post = Post(**payload.model_dump())
```

Sprint 2에서는 아래처럼 현재 사용자 id를 받아 저장하는 구조가 됩니다.

```python
def create(self, payload: PostCreate, author_id: int) -> Post:
    post = Post(**payload.model_dump(), author_id=author_id)
```

Sprint 1에서 이 시그니처를 먼저 바꿀지, Sprint 2에서 인증과 함께 바꿀지는 구현 순서에 따라 결정합니다. 추천은 Sprint 1에서 모델/schema를 먼저 바꾸고, Sprint 2에서 `current_user` 연결과 함께 service 시그니처를 확정하는 것입니다.

### 7.4 `backend/app/api/v1/posts.py`

Sprint 1에서는 인증 없이 게시글 생성 흐름을 유지할 수 있습니다.

Sprint 2에서는 아래처럼 바뀝니다.

```python
@router.post("", response_model=PostRead, status_code=201)
def create_post(
    payload: PostCreate,
    current_user: User = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create(payload, author_id=current_user.id)
```

### 7.5 테스트

기존 테스트는 `author_name`을 request body에 넣습니다.

변경 후에는 테스트가 아래 흐름을 가져야 합니다.

```text
1. 테스트용 user 생성
2. user.id를 author_id로 사용하거나
3. Sprint 2에서는 session login 후 cookie로 게시글 생성
```

## 8. Sprint 1에서 하지 않을 것

오늘 Sprint 1에서는 아래를 하지 않습니다.

```text
- Comment 구현
- Tag 구현
- Post 수정/삭제 권한 구현
- OAuth/OIDC 구현
- pgvector 구현
- Alembic 도입
```

다만 Comment/Tag/pgvector는 이후 Sprint에서 붙일 수 있도록 모델 관계를 염두에 둡니다.

## 9. Sprint 1 완료 기준

이번 기준으로 Sprint 1이 완료되려면 아래를 만족해야 합니다.

```text
1. PostgreSQL 연결이 된다.
2. FastAPI 앱이 실행된다.
3. React + Vite 앱이 실행된다.
4. User 모델이 있다.
5. Post 모델이 User와 FK로 연결된다.
6. Post에는 updated_at이 있다.
7. Post 응답에는 author_display_name이 포함된다.
8. 게시글 생성 또는 조회 API가 동작한다.
9. 요청이 router -> schema -> service -> repository -> DB -> response로 흐르는 것을 설명할 수 있다.
10. DB schema 변경은 오늘 DB reset으로 처리한다고 문서화했다.
```

## 10. 오늘 구현 전 최종 확인

현재까지 확정:

```text
- Post.author_id FK 사용
- Post.updated_at 추가
- PostRead에 author_display_name 포함
- Comment/Tag는 내일 구현
- Session 인증을 Sprint 2 main auth로 사용
- DB schema 변경은 오늘 DB reset으로 처리
```

Alembic은 Sprint 3 또는 Sprint 4 시작 전에 도입 여부를 다시 결정합니다.

## 11. 발표에 사용할 한 문장

```text
Sprint 1에서는 이후 Session 인증과 작성자 권한 처리를 붙일 수 있도록,
게시글을 문자열 작성자가 아니라 User FK 기반으로 모델링하고,
FastAPI의 router/service/repository 구조와 PostgreSQL 연결 흐름을 정리했습니다.
```
