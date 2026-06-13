# W16 팀 스프린트

팀 프로젝트 준비를 위한 스프린트별 학습 예제 저장소입니다.

## 스프린트 1: API + 데이터 흐름

현재 저장소에는 작은 `posts` API 예제가 구현되어 있습니다. 이 예제의 목적은 아래 흐름을 코드로 확인하는 것입니다.

```text
클라이언트 요청 -> API 라우터 -> 검증/스키마 -> 서비스 -> 레포지토리 -> DB -> 응답/에러
```

## 실행 방법

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

API 문서는 아래 주소에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

## 요청 예시

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"스프린트 1","content":"API와 DB 흐름","author_name":"team1"}'
```

```bash
curl http://127.0.0.1:8000/api/v1/posts
```

```bash
curl http://127.0.0.1:8000/api/v1/posts/1
```

## 문서

* [스프린트 1 파일 구조](docs/sprint-1-file-structure.md)
* [스프린트 1 API 데이터 흐름](docs/sprint-1-api-data-flow.md)
