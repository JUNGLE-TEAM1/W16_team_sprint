# DB Transaction과 동시성 이해하기

Sprint 1에서 repository 코드를 보면 아래 흐름이 나옵니다.

```python
def create(self, post: Post) -> Post:
    self.db.add(post)
    self.db.flush()
    self.db.refresh(post)
    return post
```

그리고 service에서 최종적으로 commit합니다.

```python
saved_post = self.posts.create(post)
self.db.commit()
return saved_post
```

이 문서는 `add`, `flush`, `refresh`, `commit`의 차이와 PostgreSQL에서 transaction과 동시성을 어떻게 이해해야 하는지 정리합니다.

## add, flush, refresh, commit의 역할

### add

```python
self.db.add(post)
```

`add()`는 SQLAlchemy session에게 이 객체를 저장 대상으로 관리하라고 알려주는 단계입니다.

```text
이 post 객체는 나중에 DB에 INSERT 해야 할 대상이야.
```

이 시점에는 아직 SQL이 DB로 나가지 않았다고 이해하면 됩니다.

### flush

```python
self.db.flush()
```

`flush()`는 session에 쌓인 변경 사항을 실제 DB에 보냅니다.

이때 `INSERT INTO posts ...` 같은 SQL이 DB로 나갑니다.

하지만 아직 최종 확정은 아닙니다.

```text
flush = SQL을 DB에 보냄
commit = transaction을 최종 확정함
```

flush를 하면 DB가 생성하는 값을 받을 수 있습니다.

예를 들어 `id`는 클라이언트가 보내는 값이 아니라 DB가 만들어주는 값입니다.

```python
id: Mapped[int] = mapped_column(primary_key=True, index=True)
```

따라서 flush 이후에는 `post.id` 같은 값을 알 수 있습니다.

### refresh

```python
self.db.refresh(post)
```

`refresh()`는 DB에 저장된 최신 값을 다시 읽어서 Python 객체에 반영합니다.

예를 들어 DB나 ORM model에서 자동으로 채워지는 값이 있습니다.

```python
created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
```

`refresh(post)`는 이런 최신 값을 DB 기준으로 다시 가져옵니다.

```text
DB에 실제로 들어간 최신 상태를 post 객체에 반영해줘.
```

### commit

```python
self.db.commit()
```

`commit()`은 transaction 안에서 일어난 변경을 최종 확정합니다.

현재 구조에서는 repository가 아니라 service에서 commit합니다.

이유는 commit이 DB 작업 하나의 끝이라기보다, 사용자 기능 하나가 성공했다고 확정하는 의미에 가깝기 때문입니다.

## 상태 흐름

게시글 생성 흐름을 단계별로 보면 다음과 같습니다.

```text
post = Post(...)
-> db.add(post)
   SQLAlchemy session이 저장 예정 객체로 기억한다.

-> db.flush()
   INSERT SQL을 DB에 보낸다.
   DB가 id 같은 값을 생성한다.
   아직 commit은 아니다.

-> db.refresh(post)
   DB에 저장된 최신 값을 post 객체에 다시 반영한다.
   그래도 아직 transaction은 commit 전이다.

-> db.commit()
   transaction 안의 변경을 최종 확정한다.
```

## flush와 commit의 차이

헷갈리는 핵심은 아래입니다.

```text
DB에 반영됨과 최종 확정됨은 다르다.
```

`flush()`를 하면 SQL은 DB에 날아갑니다. DB 안에서는 변경이 일어난 상태처럼 보입니다. 같은 transaction 안에서는 그 변경을 다시 읽을 수도 있습니다.

하지만 아직 commit 전이라면 최종 확정은 아닙니다.

```text
flush = DB에게 이 작업을 해보라고 보낸다.
commit = 이제 이 작업을 진짜 확정하라고 말한다.
rollback = 방금 작업을 없던 일로 한다.
```

비유하면 다음과 같습니다.

```text
add = 문서에 쓸 내용을 편집기에 올림
flush = 문서에 임시 저장함
refresh = 임시 저장된 문서를 다시 불러와 화면에 반영함
commit = 최종 제출함
rollback = 제출하지 않고 변경사항 폐기함
```

## 같은 세션과 다른 세션에서 보이는 차이

transaction 안에서 `flush()`된 변경은 같은 session에서는 볼 수 있습니다.

하지만 다른 session에서는 commit 전까지 보통 볼 수 없습니다.

```text
Session A: add(post)
Session A: flush()
Session A: select(post)
-> 보임

Session B: select(post)
-> 보통 안 보임

Session A: commit()

Session B: select(post)
-> 보임
```

PostgreSQL의 기본 isolation level인 `READ COMMITTED`에서는 다른 transaction이 아직 commit하지 않은 변경을 읽지 않습니다.

이런 아직 확정되지 않은 데이터를 읽는 문제를 dirty read라고 합니다.

PostgreSQL은 기본적으로 dirty read를 허용하지 않습니다.

## 서로 다른 세션이 같은 데이터를 수정하면?

서로 다른 session이 같은 데이터를 동시에 건드리면 lock, 대기, 덮어쓰기, deadlock 같은 문제가 생길 수 있습니다.

### 같은 row를 동시에 수정하는 경우

예를 들어 게시글 `id=1`을 두 session이 동시에 수정한다고 해봅니다.

```text
Session A: UPDATE posts SET title='A 수정' WHERE id=1;
-> row lock 획득
-> 아직 commit 안 함

Session B: UPDATE posts SET title='B 수정' WHERE id=1;
-> 같은 row를 수정하려고 해서 대기

Session A: commit
-> lock 해제

Session B: 그 다음 UPDATE 진행
```

PostgreSQL은 같은 row를 동시에 마음대로 수정하지 않도록 row lock을 사용합니다.

### 의도치 않은 덮어쓰기

둘 다 같은 데이터를 읽은 뒤 각각 수정하면 나중에 저장한 값이 앞선 변경을 덮어쓸 수 있습니다.

```text
Session A: title = "원래 제목" 읽음
Session B: title = "원래 제목" 읽음

Session A: title = "A가 수정"
Session A: commit

Session B: title = "B가 수정"
Session B: commit
```

최종 결과:

```text
title = "B가 수정"
```

이런 상황을 lost update 문제라고 부릅니다.

PostgreSQL이 모든 서비스 의도를 자동으로 판단해서 막아주지는 않습니다.

### Deadlock

서로 다른 row를 서로 반대 순서로 잡으면 deadlock이 발생할 수 있습니다.

```text
Session A: post 1번 lock
Session B: post 2번 lock

Session A: post 2번도 수정하려고 함
-> B가 잡고 있어서 대기

Session B: post 1번도 수정하려고 함
-> A가 잡고 있어서 대기
```

이렇게 서로가 서로를 기다리면 deadlock입니다.

PostgreSQL은 deadlock을 감지하면 둘 중 하나의 transaction을 실패시킵니다.

## PostgreSQL이 자동으로 해주는 것과 개발자가 정해야 하는 것

PostgreSQL은 기본적인 안전장치를 제공합니다.

- commit 전 변경을 다른 session이 함부로 읽지 못하게 한다.
- 같은 row를 수정할 때 row lock으로 조율한다.
- transaction으로 여러 작업을 성공/실패 단위로 묶을 수 있게 한다.
- deadlock을 감지하고 한쪽 transaction을 실패시킨다.

하지만 PostgreSQL이 서비스 정책까지 자동으로 정해주지는 않습니다.

예를 들어 아래 질문은 개발자가 정해야 합니다.

- 게시글 수정은 마지막 저장이 이기게 할 것인가?
- 동시에 수정되면 사용자에게 경고할 것인가?
- 좋아요 중복 클릭은 어떻게 막을 것인가?
- 같은 AI 요청이 두 번 들어오면 두 번 실행할 것인가?
- deadlock이 발생하면 다시 시도할 것인가?

## 동시성 문제 대응 방법

대표적인 대응 방법은 다음과 같습니다.

| 방법 | 설명 |
| --- | --- |
| row lock | 수정 중인 row를 다른 transaction이 못 건드리게 한다. |
| transaction | 여러 작업을 하나로 묶어 성공/실패를 관리한다. |
| optimistic locking | `version` 같은 값을 두고, 내가 읽은 뒤 누가 수정했는지 확인한다. |
| retry | deadlock이나 일시 충돌이 나면 다시 시도한다. |
| idempotency key | 같은 요청이 중복 실행되어도 한 번만 처리되게 한다. |
| unique constraint | DB 차원에서 중복 데이터를 막는다. |

지금 Sprint 1에서는 이 기법들을 깊게 구현하지 않습니다.

다만 아래 감각은 가져가야 합니다.

```text
PostgreSQL은 기본 안전망을 제공한다.
하지만 우리 서비스가 원하는 정확한 성공/실패 기준은 개발자가 정해야 한다.
```

## Sprint 1에서 기억할 것

```text
add
= 객체를 session에 저장 대상으로 등록한다.

flush
= SQL을 DB에 보내고, transaction 안에서 변경을 반영한다.

refresh
= DB에 저장된 최신 값을 객체에 다시 반영한다.

commit
= transaction을 최종 확정한다.

rollback
= transaction 안의 변경을 취소한다.
```

최종 요약:

```text
flush는 DB에 변경을 보내는 것이다.
commit은 그 변경을 되돌릴 수 없게 확정하는 것이다.
같은 session에서는 flush된 변경을 볼 수 있다.
다른 session에서는 commit 전까지 보통 볼 수 없다.
PostgreSQL은 기본 안전장치를 제공하지만, 서비스 정책은 개발자가 설계해야 한다.
```

