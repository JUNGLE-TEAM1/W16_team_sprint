# 풀스택 아키텍처 다이어그램

이 문서는 현재 코드 기준으로 프론트엔드, 백엔드, 데이터베이스, RAG/Agent, MCP, OpenAI 연동을 한 번에 볼 수 있도록 정리한 전체 풀스택 아키텍처 다이어그램입니다.

## 1. 전체 풀스택 구조

```mermaid
flowchart TB
    user["사용자<br/>회원가입, 로그인, 질문 게시글 작성,<br/>댓글 토론, AI 토론, 음성 토론"]

    subgraph browser["Browser"]
        react["React 19 + Vite<br/>frontend/src/main.jsx"]
        state["Client State<br/>currentUser, posts, selectedPost,<br/>discussionAnswer, voiceStatus"]
        localStorage["localStorage<br/>annalsUsername"]
        react <--> state
        react <--> localStorage
    end

    subgraph backend["FastAPI Backend :8000"]
        main["app/main.py<br/>REST API, SSE, WebRTC SDP proxy"]
        auth["Auth API<br/>/auth/register, /auth/login"]
        board["Board API<br/>/posts, /comments, /annals/search"]
        discussion["AI Discussion Stream<br/>/posts/{id}/ai-discussion/stream"]
        realtime["Realtime Voice API<br/>/realtime/session, /turn/route, /turn/retrieve"]

        subgraph services["Backend Services"]
            agent["Post Creation Agent<br/>services/agent.py"]
            search["Hybrid Search<br/>keyword + pgvector"]
            filters["Query Filters<br/>king/source metadata extraction"]
            mcpClient["MCP Client<br/>stdio client"]
            llm["LLM Service<br/>draft, rerank, discussion stream"]
            realtimeOrchestrator["Realtime Orchestrator<br/>voice turn routing"]
            embeddings["Embedding Service<br/>OpenAI embeddings"]
            xmlParser["XML Parser + Chunking<br/>level5 article parse"]
        end

        main --> auth
        main --> board
        main --> discussion
        main --> realtime
        board --> agent
        board --> search
        agent --> filters
        agent --> search
        agent --> mcpClient
        agent --> llm
        search --> filters
        search --> embeddings
        discussion --> llm
        realtime --> realtimeOrchestrator
        realtime --> search
        realtime --> llm
    end

    subgraph mcp["MCP Tool Server"]
        mcpServer["app/mcp_server.py<br/>FastMCP annals-board"]
        tool["get_annals_article(article_id)"]
        mcpServer --> tool
    end

    subgraph db["PostgreSQL + pgvector :5432"]
        users["users<br/>username, password_hash"]
        posts["posts<br/>question, AI summary, tags,<br/>evidence_article_ids, agent_trace"]
        comments["comments"]
        articles["annals_articles<br/>원본 실록 기사"]
        chunks["annals_chunks<br/>chunk_text, vector(1536)"]
        voiceSessions["voice_sessions"]
        voiceMessages["voice_messages"]
    end

    subgraph openai["OpenAI APIs"]
        chat["Chat Completions<br/>OPENAI_MODEL"]
        embedApi["Embeddings<br/>text-embedding-3-small"]
        realtimeApi["Realtime API<br/>gpt-realtime-2, WebRTC"]
    end

    subgraph data["Local Data / Seed Pipeline"]
        xml["조선왕조실록 XML<br/>ANNALS_XML_DIR=/data/xml"]
        bundle["Private Bundle ZIP<br/>/data/annals_private_bundle.zip"]
        seed["backend/scripts/seed_annals.py<br/>parse, chunk, embed, upsert"]
    end

    user --> react
    react -->|"HTTP JSON<br/>VITE_API_BASE_URL"| main
    react -->|"SSE stream"| discussion
    react -->|"WebRTC offer SDP"| realtime

    auth --> users
    board --> users
    board --> posts
    board --> comments
    board --> articles
    discussion --> posts
    discussion --> comments
    discussion --> articles
    realtime --> posts
    realtime --> voiceSessions
    realtime --> voiceMessages

    search --> articles
    search --> chunks
    embeddings --> embedApi
    llm --> chat
    realtimeOrchestrator --> chat
    realtime --> realtimeApi

    mcpClient -->|"stdio MCP"| mcpServer
    tool --> articles

    xml --> seed
    bundle --> seed
    seed --> articles
    seed --> chunks
    seed --> embedApi
```

## 2. 게시글 작성 및 RAG Agent 흐름

```mermaid
sequenceDiagram
    autonumber
    actor U as 사용자
    participant FE as React Frontend
    participant API as FastAPI /posts
    participant Agent as Post Creation Agent
    participant Search as Hybrid Search
    participant DB as PostgreSQL + pgvector
    participant MCP as MCP get_annals_article
    participant LLM as OpenAI Chat Completions

    U->>FE: 제목 + 역사 질문 작성
    FE->>API: POST /posts {title, question, username}
    API->>DB: 사용자 조회
    API->>Agent: run_post_creation_agent(question)
    Agent->>Agent: 키워드/왕/메타데이터 분석
    Agent->>Search: 검색 질의 생성 후 후보 검색
    Search->>DB: annals_chunks vector search
    Search->>DB: annals_articles keyword search
    Search-->>Agent: 후보 article_id 목록
    Agent->>MCP: get_annals_article(article_id)
    MCP->>DB: annals_articles 원문 조회
    MCP-->>Agent: 원문 기사 payload
    Agent->>LLM: 근거 reranking
    LLM-->>Agent: selected_evidence
    Agent->>LLM: 원문 기반 초벌 요약/해석/태그 생성
    LLM-->>Agent: summary, interpretation, tags
    Agent-->>API: evidence, trace 포함 결과
    API->>DB: posts 저장
    API-->>FE: PostDetail 반환
    FE-->>U: AI 요약, 쉬운 해석, 근거 기사 표시
```

## 3. 토론 및 음성 기능 흐름

```mermaid
flowchart LR
    post["게시글 상세 화면<br/>PostDetail"]

    subgraph textDiscussion["텍스트 AI 토론"]
        prompt["사용자 후속 질문"]
        sse["POST /posts/{id}/ai-discussion/stream<br/>SSE token stream"]
        context["게시글 + 근거 기사 + 최근 댓글"]
        answer["AI 답변 조각 표시"]
    end

    subgraph voiceDiscussion["Realtime 음성 토론"]
        mic["브라우저 마이크<br/>WebRTC offer SDP"]
        session["POST /posts/{id}/realtime/session"]
        route["POST /realtime/turn/route<br/>추가 검색 필요 여부 판단"]
        retrieve["POST /realtime/turn/retrieve<br/>추가 실록 근거 검색"]
        voiceStore["voice_sessions / voice_messages 저장"]
    end

    subgraph shared["공유 컨텍스트"]
        dbPost["posts"]
        dbComments["comments"]
        dbArticles["annals_articles"]
        dbChunks["annals_chunks"]
        openaiChat["OpenAI Chat Completions"]
        openaiRealtime["OpenAI Realtime API"]
    end

    post --> prompt --> sse
    sse --> context
    context --> dbPost
    context --> dbComments
    context --> dbArticles
    context --> openaiChat
    sse --> answer

    post --> mic --> session
    session --> openaiRealtime
    post --> route --> openaiChat
    route --> retrieve
    retrieve --> dbChunks
    retrieve --> dbArticles
    retrieve --> openaiChat
    session --> voiceStore
    route --> voiceStore
    retrieve --> voiceStore
```

## 4. 배포 / 실행 컨테이너 구조

```mermaid
flowchart LR
    subgraph compose["docker-compose.yml"]
        postgres["postgres<br/>pgvector/pgvector:pg16<br/>5432"]
        backend["backend<br/>FastAPI + Uvicorn<br/>8000"]
        frontend["frontend<br/>Vite dev server<br/>5173"]
        volume["./data:/data:ro"]
    end

    env["환경 변수<br/>OPENAI_API_KEY<br/>OPENAI_MODEL<br/>OPENAI_EMBEDDING_MODEL<br/>OPENAI_REALTIME_MODEL"]
    browser["Browser<br/>http://localhost:5173"]

    browser --> frontend
    frontend -->|"VITE_API_BASE_URL=http://localhost:8000"| backend
    backend -->|"DATABASE_URL"| postgres
    backend --> volume
    env --> backend
```

## 5. 저장 데이터 관점

```mermaid
erDiagram
    users ||--o{ posts : writes
    users ||--o{ comments : writes
    users ||--o{ voice_sessions : starts
    users ||--o{ voice_messages : speaks
    posts ||--o{ comments : has
    posts ||--o{ voice_sessions : has
    posts ||--o{ voice_messages : has
    voice_sessions ||--o{ voice_messages : contains
    annals_articles ||--o{ annals_chunks : split_into

    users {
        int id
        string username
        string password_hash
        datetime created_at
    }

    posts {
        int id
        int user_id
        string title
        text question
        text ai_summary
        text ai_interpretation
        jsonb suggested_tags
        jsonb evidence_article_ids
        jsonb agent_trace
    }

    annals_articles {
        int id
        string article_id
        string source_file
        string title
        string king
        string reign_date
        string date
        text content
        string official_url
        jsonb subject_classes
    }

    annals_chunks {
        int id
        string chunk_id
        string article_id
        text chunk_text
        vector embedding
        string embedding_model
    }
```
