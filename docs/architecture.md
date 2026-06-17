# 조선왕조실록 AI 게시판 아키텍처

이 문서는 현재 코드 기준으로 데이터 구조, 홈페이지 구조, RAG/Agent 구조, 음성 토론 구조를 한 번에 볼 수 있도록 정리한 아키텍처 문서입니다.

## 1. 전체 시스템 구조

```mermaid
flowchart TB
    user["사용자<br/>역사 질문 작성, 검색, 댓글, 음성 토론"]

    subgraph frontend["Frontend - React + Vite"]
        app["App"]
        compose["질문 작성 / 로그인 패널"]
        archive["게시글 검색 / 목록 / 페이지네이션"]
        detail["게시글 상세 / 근거 / 댓글 / AI 토론 / 음성 토론"]
        app --> compose
        app --> archive
        app --> detail
    end

    subgraph backend["Backend - FastAPI"]
        api["REST API"]
        auth["Auth endpoints"]
        posts["Post / Comment endpoints"]
        discussion["AI Discussion SSE"]
        realtime["Realtime endpoints"]
        agent["Post Creation Agent"]
        search["Hybrid Search Service"]
        llm["LLM Service"]
        mcpClient["MCP Client"]
    end

    subgraph mcp["MCP Tool Server"]
        annalsTool["get_annals_article(article_id)"]
    end

    subgraph db["PostgreSQL + pgvector"]
        users["users"]
        postsTable["posts"]
        comments["comments"]
        articles["annals_articles"]
        chunks["annals_chunks<br/>vector(1536)"]
        voiceSessions["voice_sessions"]
        voiceMessages["voice_messages"]
    end

    subgraph openai["OpenAI APIs"]
        chat["Chat Completions<br/>draft, rerank, discussion, routing"]
        embedding["Embeddings<br/>text-embedding-3-small"]
        realtimeApi["Realtime API<br/>WebRTC voice"]
    end

    user --> frontend
    frontend --> api
    api --> auth
    api --> posts
    api --> discussion
    api --> realtime

    posts --> agent
    agent --> search
    agent --> mcpClient
    agent --> llm
    search --> chunks
    search --> articles
    search --> embedding
    mcpClient --> mcp
    annalsTool --> articles
    llm --> chat

    auth --> users
    posts --> postsTable
    posts --> comments
    posts --> articles
    discussion --> postsTable
    discussion --> comments
    discussion --> articles
    discussion --> chat
    realtime --> voiceSessions
    realtime --> voiceMessages
    realtime --> chat
    realtime --> realtimeApi
```

## 2. 배포 / 실행 구조

```mermaid
flowchart LR
    subgraph compose["docker-compose.yml"]
        postgres["postgres<br/>pgvector/pgvector:pg16<br/>5432"]
        backend["backend<br/>FastAPI + Uvicorn<br/>8000"]
        frontend["frontend<br/>Vite dev server<br/>5173"]
        dataVolume["./data:/data:ro"]
    end

    browser["Browser<br/>http://localhost:5173"]
    env[".env / environment<br/>OPENAI_API_KEY<br/>OPENAI_MODEL<br/>OPENAI_EMBEDDING_MODEL<br/>OPENAI_REALTIME_MODEL"]

    browser --> frontend
    frontend -->|"VITE_API_BASE_URL"| backend
    backend --> postgres
    backend --> dataVolume
    env --> backend
```

## 3. 홈페이지 / 프론트엔드 구조

현재 프론트엔드는 `frontend/src/main.jsx`의 단일 React 엔트리에서 `App`과 `PostDetail`을 구성합니다.

```mermaid
flowchart TB
    App["App"]

    subgraph composePane["composePane - 왼쪽 작성 영역"]
        masthead["서비스 헤더<br/>조선왕조실록 AI 게시판"]
        authPanel["authPanel<br/>로그인 / 회원가입 / 로그아웃"]
        questionForm["questionForm<br/>제목 + 역사 질문 작성"]
    end

    subgraph detailPane["detailPane - 오른쪽 탐색/상세 영역"]
        searchPanel["postSearchPanel<br/>질문 아카이브 검색"]
        list["postList<br/>게시글 목록"]
        pagination["paginationControls"]
        emptyDetail["emptyDetail"]
        postDetail["PostDetail"]
    end

    subgraph postDetailSections["PostDetail 세부 섹션"]
        toolbar["태그 / 수정 / 삭제"]
        summary["AI 초벌 요약"]
        interpretation["쉬운 해석"]
        evidence["실록 원문 근거 카드"]
        trace["Agent 실행 흐름"]
        voice["음성 토론 모드"]
        aiDiscussion["AI 토론 도우미"]
        comments["토론 댓글"]
    end

    App --> composePane
    App --> detailPane
    composePane --> masthead
    composePane --> authPanel
    composePane --> questionForm
    detailPane --> searchPanel
    searchPanel --> list
    searchPanel --> pagination
    detailPane --> postDetail
    detailPane --> emptyDetail
    postDetail --> postDetailSections
    postDetailSections --> toolbar
    postDetailSections --> summary
    postDetailSections --> interpretation
    postDetailSections --> evidence
    postDetailSections --> trace
    postDetailSections --> voice
    postDetailSections --> aiDiscussion
    postDetailSections --> comments
```

### 주요 프론트엔드 상태와 API 연결

```mermaid
flowchart LR
    subgraph state["React state"]
        currentUser["currentUser<br/>localStorage: annalsUsername"]
        postsState["posts / postPageInfo"]
        selectedPost["selectedPost"]
        form["form<br/>title, question"]
        discussionState["discussionPrompt / discussionAnswer"]
        voiceState["voiceStatus / voiceEvents / voiceMessages"]
    end

    subgraph endpoints["FastAPI endpoints"]
        authApi["POST /auth/register<br/>POST /auth/login"]
        listApi["GET /posts"]
        detailApi["GET /posts/{id}"]
        createApi["POST /posts"]
        commentApi["POST /posts/{id}/comments"]
        sseApi["POST /posts/{id}/ai-discussion/stream"]
        voiceApi["voice session/message/realtime endpoints"]
    end

    currentUser --> authApi
    postsState --> listApi
    selectedPost --> detailApi
    form --> createApi
    selectedPost --> commentApi
    discussionState --> sseApi
    voiceState --> voiceApi
```

## 4. 백엔드 모듈 구조

```mermaid
flowchart TB
    main["app/main.py<br/>FastAPI routes, auth helper, response assembly"]
    schemas["app/schemas.py<br/>Pydantic request/response DTO"]
    models["app/models.py<br/>SQLAlchemy ORM + pgvector type"]
    database["app/database.py<br/>engine, SessionLocal, create_tables"]
    config["app/config.py<br/>env settings"]

    subgraph services["app/services"]
        agent["agent.py<br/>post creation workflow"]
        search["search.py<br/>hybrid search"]
        llm["llm.py<br/>draft, rerank, discussion stream"]
        realtime["realtime_orchestrator.py<br/>voice turn routing"]
        filters["query_filters.py<br/>king/year/topic extraction"]
        mcpClient["mcp_client.py<br/>stdio MCP calls"]
        tools["tools.py<br/>article lookup payload"]
        chunking["chunking.py<br/>article chunk builder"]
        embeddings["embeddings.py<br/>OpenAI embeddings"]
        xmlParser["xml_parser.py<br/>Annals XML level5 parser"]
    end

    subgraph scripts["backend/scripts"]
        seed["seed_annals.py<br/>XML parse + chunk + embedding seed"]
        importBundle["import_private_bundle.py<br/>JSONL zip import"]
        exportBundle["export_private_bundle.py<br/>team bundle export"]
        privateBundle["private_bundle.py<br/>bundle helpers"]
    end

    main --> schemas
    main --> models
    main --> database
    main --> config
    main --> agent
    main --> search
    main --> llm
    main --> realtime
    main --> tools
    agent --> search
    agent --> llm
    agent --> mcpClient
    search --> filters
    search --> embeddings
    search --> models
    seed --> xmlParser
    seed --> chunking
    seed --> embeddings
    importBundle --> privateBundle
```

## 5. 데이터 모델 ERD

```mermaid
erDiagram
    users {
        int id PK
        string username UK
        string password_hash
        datetime created_at
    }

    posts {
        int id PK
        int user_id FK
        string title
        text question
        text ai_summary
        text ai_interpretation
        jsonb suggested_tags
        jsonb evidence_article_ids
        jsonb agent_trace
        datetime created_at
        datetime updated_at
    }

    comments {
        int id PK
        int post_id FK
        int user_id FK
        text content
        datetime created_at
        datetime updated_at
    }

    annals_articles {
        int id PK
        string article_id UK
        string source_file
        string title
        string king
        string reign_date
        string date
        text content
        string official_url
        jsonb subject_classes
        datetime created_at
    }

    annals_chunks {
        int id PK
        string chunk_id UK
        string article_id FK
        int chunk_index
        text chunk_text
        vector embedding
        string embedding_model
        int token_count_estimate
        datetime created_at
    }

    voice_sessions {
        int id PK
        int post_id FK
        int user_id FK
        datetime created_at
    }

    voice_messages {
        int id PK
        int session_id FK
        int post_id FK
        int user_id FK
        string role
        text content
        string route_action
        text route_reason
        string search_query
        jsonb evidence_article_ids
        datetime created_at
    }

    users ||--o{ posts : writes
    users ||--o{ comments : writes
    users ||--o{ voice_sessions : starts
    users ||--o{ voice_messages : owns
    posts ||--o{ comments : has
    posts ||--o{ voice_sessions : has
    posts ||--o{ voice_messages : has
    voice_sessions ||--o{ voice_messages : records
    annals_articles ||--o{ annals_chunks : indexed_by
```

### 데이터 역할

| 테이블 | 역할 |
| --- | --- |
| `users` | 사용자 계정과 비밀번호 해시 저장 |
| `posts` | 질문 게시글, AI 요약/해석, 추천 태그, 근거 article_id, Agent trace 저장 |
| `comments` | 게시글 토론 댓글 저장 |
| `annals_articles` | 조선왕조실록 원문 기사 원본 저장소 |
| `annals_chunks` | RAG 검색용 chunk와 embedding vector 저장소 |
| `voice_sessions` | 게시글별 음성 토론 세션 저장 |
| `voice_messages` | 사용자/AI 음성 전사, 라우팅 판단, 추가 근거 article_id 저장 |

## 6. 데이터 적재 / 인덱싱 구조

```mermaid
flowchart TB
    subgraph raw["원천 데이터"]
        xml["조선왕조실록 XML<br/>level5 article"]
        bundle["data/annals_private_bundle.zip<br/>manifest.json<br/>annals_articles.jsonl<br/>annals_chunks.jsonl"]
    end

    subgraph xmlPipeline["XML seed pipeline"]
        parser["xml_parser.parse_annals_file"]
        articleRows["AnnalsArticle rows"]
        chunker["chunking.chunk_article<br/>prefix + sentence split"]
        embedder["embeddings.embed_texts<br/>OpenAI embedding"]
        chunkRows["AnnalsChunk rows<br/>vector(1536)"]
    end

    subgraph bundlePipeline["Private bundle pipeline"]
        readManifest["read manifest"]
        importArticles["upsert articles"]
        importChunks["upsert chunks"]
    end

    subgraph database["PostgreSQL + pgvector"]
        articles["annals_articles"]
        chunks["annals_chunks"]
    end

    xml --> parser --> articleRows --> articles
    articleRows --> chunker --> embedder --> chunkRows --> chunks

    bundle --> readManifest
    readManifest --> importArticles --> articles
    readManifest --> importChunks --> chunks
```

## 7. RAG / 게시글 생성 Agent 구조

사용자가 질문 게시글을 작성하면 `/posts` API가 `run_post_creation_agent`를 호출합니다. Agent는 검색, MCP 조회, LLM rerank, 초벌 생성 결과를 `posts` 테이블에 저장합니다.

```mermaid
sequenceDiagram
    autonumber
    actor User as 사용자
    participant React as React App
    participant API as FastAPI /posts
    participant Agent as run_post_creation_agent
    participant Filters as query_filters
    participant Search as hybrid search
    participant PG as PostgreSQL + pgvector
    participant Emb as OpenAI Embeddings
    participant MCP as MCP get_annals_article
    participant LLM as OpenAI Chat
    participant DB as posts table

    User->>React: 제목 + 역사 질문 작성
    React->>API: POST /posts
    API->>Agent: question 전달
    Agent->>Filters: keyword, king/year filter, retrieval_query 추출
    Agent->>Search: search_annals_articles(question, limit=8)
    Search->>Emb: 질문 embedding 생성
    Search->>PG: vector distance 검색<br/>annals_chunks <=> query vector
    Search->>PG: keyword ilike 검색<br/>annals_articles title/content
    Search->>Search: vector score + keyword score merge
    Search-->>Agent: article_id 후보
    Agent->>MCP: 후보 article_id별 get_annals_article
    MCP->>PG: annals_articles 조회
    MCP-->>Agent: 원문 기사 payload
    Agent->>LLM: 후보 근거 rerank
    LLM-->>Agent: selected_ids, rejected_ids, reason
    Agent->>LLM: 선택 근거 기반 summary / interpretation / tags 생성
    LLM-->>Agent: grounded draft
    Agent-->>API: summary, interpretation, tags, evidence, trace
    API->>DB: Post 저장<br/>evidence_article_ids, agent_trace 포함
    API-->>React: PostDetail 응답
```

## 8. Hybrid Search 내부 구조

```mermaid
flowchart TB
    query["사용자 질문"]
    filters["extract_search_filters<br/>왕 이름, 재위년, source_file"]
    retrievalQuery["build_retrieval_query<br/>답변 형식 표현 제거 + 주제 확장"]

    subgraph vector["Vector path"]
        hasKey["OPENAI_API_KEY 있음<br/>annals_chunks 존재"]
        embed["OpenAI embedding"]
        pgvector["pgvector distance<br/>MIN(c.embedding <=> query_embedding)"]
        vectorHits["vector_hits<br/>score = 1 - distance"]
    end

    subgraph keyword["Keyword path"]
        tokenize["tokenize_query<br/>조사 제거, stopword 제거"]
        phrase["keyword phrase"]
        ilike["title/content ilike 후보 조회"]
        score["title/content/subject_classes 점수화"]
        keywordHits["keyword_hits"]
    end

    merge["merge_ranked_hits<br/>article_id별 score 합산"]
    result["AnnalsArticle list"]

    query --> filters --> retrievalQuery
    retrievalQuery --> hasKey --> embed --> pgvector --> vectorHits --> merge
    retrievalQuery --> tokenize --> ilike --> score --> keywordHits --> merge
    retrievalQuery --> phrase --> ilike
    merge --> result
```

## 9. MCP 도구 구조

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Agent
    participant Client as mcp_client.py
    participant Stdio as stdio transport
    participant Server as app/mcp_server.py
    participant Tool as get_annals_article
    participant DB as annals_articles

    Agent->>Client: get_annals_articles_via_mcp(article_ids)
    Client->>Stdio: Python MCP server process 실행
    Stdio->>Server: session.initialize
    loop article_id마다
        Client->>Server: call_tool("get_annals_article")
        Server->>Tool: article_id 전달
        Tool->>DB: SELECT by article_id
        DB-->>Tool: AnnalsArticle
        Tool-->>Server: JSON payload
        Server-->>Client: TextContent JSON
    end
    Client-->>Agent: evidence list
```

## 10. AI 토론 도우미 구조

게시글 상세 화면의 텍스트 기반 AI 토론 도우미는 SSE로 답변 조각을 스트리밍합니다.

```mermaid
sequenceDiagram
    autonumber
    actor User as 사용자
    participant Detail as PostDetail
    participant API as /posts/{id}/ai-discussion/stream
    participant DB as PostgreSQL
    participant LLM as stream_discussion_reply

    User->>Detail: 후속 질문 입력
    Detail->>API: POST message
    API->>DB: post 조회
    API->>DB: evidence_article_ids로 원문 조회
    API->>DB: comments 조회
    API->>LLM: 게시글 + 근거 + 댓글 + 후속 질문
    loop token chunk
        LLM-->>API: delta
        API-->>Detail: SSE event: token
        Detail->>Detail: discussionAnswer 누적
    end
    API-->>Detail: SSE event: done
```

## 11. Realtime 음성 토론 구조

음성 토론은 WebRTC로 OpenAI Realtime API에 연결하고, 각 사용자 발화 전사마다 백엔드가 추가 검색 필요 여부를 판단합니다.

```mermaid
sequenceDiagram
    autonumber
    actor User as 사용자
    participant Detail as PostDetail
    participant API as FastAPI realtime endpoints
    participant OpenAI as OpenAI Realtime API
    participant Router as realtime_orchestrator
    participant Search as hybrid search
    participant LLM as rerank_evidence
    participant DB as voice tables / annals tables

    User->>Detail: 음성 토론 시작
    Detail->>API: POST /voice-sessions
    API->>DB: voice_sessions 생성
    Detail->>Detail: getUserMedia + RTCPeerConnection + DataChannel 생성
    Detail->>API: POST /realtime/session<br/>offer SDP
    API->>OpenAI: /v1/realtime/calls<br/>session config + SDP
    OpenAI-->>API: answer SDP
    API-->>Detail: application/sdp
    Detail->>OpenAI: WebRTC 연결

    User->>OpenAI: 음성 발화
    OpenAI-->>Detail: transcription completed
    Detail->>API: save user voice message
    Detail->>API: POST /realtime/turn/route
    API->>Router: current_context / retrieve / out_of_scope / clarify 판단
    Router-->>API: route plan

    alt 추가 검색 필요
        Detail->>API: POST /realtime/turn/retrieve
        API->>Search: search_annals_articles
        Search->>DB: annals_chunks + annals_articles 검색
        API->>LLM: 후보 근거 rerank
        LLM-->>API: selected evidence
        API-->>Detail: retrieval events + evidence_article_ids
    else 현재 근거로 답변 가능
        API-->>Detail: current_context events
    end

    Detail->>OpenAI: response.create events
    OpenAI-->>Detail: AI 음성 + transcript
    Detail->>API: save assistant voice message<br/>route metadata 포함
    API->>DB: voice_messages 저장
```

## 12. API 표면

| 영역 | Method / Path | 역할 |
| --- | --- | --- |
| Health | `GET /health` | API 상태 확인 |
| Auth | `POST /auth/register` | 회원가입 |
| Auth | `POST /auth/login` | 로그인 |
| Annals | `GET /annals/search` | 실록 원문 직접 검색 |
| Posts | `POST /posts` | 질문 작성 + RAG Agent 실행 + AI 초벌 저장 |
| Posts | `GET /posts` | 게시글 목록, 검색, 태그 필터, 페이징 |
| Posts | `GET /posts/{post_id}` | 게시글 상세, 댓글, 근거 기사 포함 |
| Posts | `PUT /posts/{post_id}` | 게시글 제목 수정 |
| Posts | `DELETE /posts/{post_id}` | 게시글 삭제 |
| Comments | `POST /posts/{post_id}/comments` | 댓글 작성 |
| AI Discussion | `POST /posts/{post_id}/ai-discussion/stream` | SSE 기반 후속 토론 답변 |
| Voice | `POST /posts/{post_id}/voice-sessions` | 음성 토론 로그 세션 생성 |
| Voice | `GET /posts/{post_id}/voice-messages` | 음성 대화 기록 조회 |
| Voice | `POST /posts/{post_id}/voice-sessions/{session_id}/messages` | 음성 전사/AI 답변 저장 |
| Realtime | `POST /posts/{post_id}/realtime/session` | OpenAI Realtime WebRTC SDP 교환 |
| Realtime | `POST /posts/{post_id}/realtime/turn/route` | 사용자 음성 발화 라우팅 |
| Realtime | `POST /posts/{post_id}/realtime/turn/retrieve` | 추가 RAG 검색 및 근거 이벤트 생성 |

## 13. 핵심 설계 포인트

- `annals_articles`는 원문 보존 테이블이고, `annals_chunks`는 검색 색인 테이블입니다.
- 게시글 생성 시에는 검색 결과 원문 전체를 바로 LLM에 넘기지 않고, MCP tool 조회와 LLM reranking을 거친 근거만 초벌 생성에 사용합니다.
- `posts.evidence_article_ids`와 `posts.agent_trace`를 저장해서, 게시글 상세에서 어떤 근거와 어떤 단계로 AI 결과가 만들어졌는지 확인할 수 있습니다.
- 검색은 embedding 기반 pgvector 검색과 keyword 검색을 합치는 hybrid 방식입니다. API 키나 chunk가 없으면 keyword 검색 중심으로 fallback됩니다.
- 텍스트 토론은 SSE 스트리밍, 음성 토론은 WebRTC + Realtime API로 분리되어 있습니다.
- 음성 토론은 모든 발화마다 무조건 RAG 검색하지 않고, `realtime_orchestrator`가 현재 근거로 답할지 추가 검색할지 먼저 라우팅합니다.
