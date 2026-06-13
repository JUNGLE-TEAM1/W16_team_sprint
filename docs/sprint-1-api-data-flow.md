# 스프린트 1 API 데이터 흐름

## 학습 목표

팀원들이 기능 하나를 요청부터 응답까지 설명할 수 있어야 합니다.

```text
POST /api/v1/posts
-> 요청 본문 검증
-> 서비스 호출
-> posts 테이블에 행 저장
-> 트랜잭션 커밋
-> 201 응답 반환
```

## 리소스

예제 리소스는 `post`입니다.

```text
post
- id: 기본키
- title: 필수 텍스트
- content: 필수 텍스트
- author_name: 선택 가능한 작성자 표시 이름
- created_at: 서버에서 생성하는 작성 시각
```

## API 계약

### 게시글 생성

```text
POST /api/v1/posts
Status: 201 Created
```

요청:

```json
{
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1"
}
```

응답:

```json
{
  "id": 1,
  "title": "스프린트 1",
  "content": "API와 DB 흐름",
  "author_name": "team1",
  "created_at": "2026-06-13T00:00:00"
}
```

### 게시글 목록 조회

```text
GET /api/v1/posts
Status: 200 OK
```

응답:

```json
[
  {
    "id": 1,
    "title": "스프린트 1",
    "content": "API와 DB 흐름",
    "author_name": "team1",
    "created_at": "2026-06-13T00:00:00"
  }
]
```

### 게시글 단건 조회

```text
GET /api/v1/posts/{post_id}
Status: 200 OK
```

찾을 수 없을 때의 응답:

```json
{
  "error": {
    "code": "POST_NOT_FOUND",
    "message": "게시글을 찾을 수 없습니다.",
    "details": {
      "post_id": 999
    }
  }
}
```

## 파일별 흐름

```text
api/v1/posts.py
  HTTP 요청을 받고 상태 코드를 결정한다.

schemas/post.py
  요청/응답 형태와 검증 규칙을 정의한다.

services/post_service.py
  비즈니스 규칙과 트랜잭션 경계를 담당한다.

repositories/post_repository.py
  SQLAlchemy 쿼리 세부 내용을 감춘다.

models/post.py
  DB 테이블 컬럼과 인덱스를 정의한다.

core/errors.py
  도메인 에러를 공통 에러 응답으로 변환한다.
```

## 스프린트 싱크 질문

이 구현을 보면서 아래 질문에 답할 수 있어야 합니다.

```text
리소스는 무엇인가?
어떤 endpoint가 리소스를 생성하는가?
request body에는 무엇이 들어가는가?
response에는 무엇이 들어가는가?
어떤 validation error가 발생할 수 있는가?
데이터는 어떤 table에 저장되는가?
transaction은 어디에서 commit되는가?
404 error는 어디에서 만들어지는가?
response schema가 바뀌면 어떤 파일을 수정해야 하는가?
DB column이 바뀌면 어떤 파일을 수정해야 하는가?
```
