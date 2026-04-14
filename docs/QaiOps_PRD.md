# ⚡ QaiOps — AI CLI Observability for Developers

> **Gemini · Claude · ChatGPT 등 파편화된 AI CLI 사용 경험을 하나로 통합하고,  
> 토큰 소모 · 비용 · 패턴을 실시간으로 시각화하는 로컬 관제 시스템**

```
 ██████╗  █████╗ ██╗ ██████╗ ██████╗ ███████╗
██╔═══██╗██╔══██╗██║██╔═══██╗██╔══██╗██╔════╝
██║   ██║███████║██║██║   ██║██████╔╝███████╗
██║▄▄ ██║██╔══██║██║██║   ██║██╔═══╝ ╚════██║
╚██████╔╝██║  ██║██║╚██████╔╝██║     ███████║
 ╚══▀▀═╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚══════╝
```

---

## 📌 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [핵심 가치 및 해결 문제](#2-핵심-가치-및-해결-문제)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [핵심 기능 명세](#4-핵심-기능-명세)
5. [데이터 모델 설계](#5-데이터-모델-설계)
6. [API 명세](#6-api-명세)
7. [기술 스택](#7-기술-스택)
8. [구현 로드맵](#8-구현-로드맵)
9. [디렉토리 구조](#9-디렉토리-구조)
10. [핵심 리스크 및 대응](#10-핵심-리스크-및-대응)
11. [기여 가이드](#11-기여-가이드)

---

## 1. 프로젝트 개요

현대적인 개발 환경에서 **Gemini CLI, Claude Code, OpenAI Codex** 등 다양한 AI CLI 도구를 동시에 활용하는 사례가 급증하고 있습니다.  
그러나 각 도구는 독립적인 실행 환경에서 동작하며, 다음과 같은 구조적 문제를 야기합니다.

| 문제 | 설명 |
|------|------|
| **사용량 분산** | 도구별 사용 현황을 한눈에 파악할 수 없음 |
| **비용 불투명** | 토큰 소모 기반 비용을 실시간으로 추산하기 어려움 |
| **히스토리 유실** | 대화 내역이 각 CLI 세션에만 존재하고, 영구 보존되지 않음 |
| **인사이트 부재** | 어떤 프로젝트에서 AI를 얼마나, 어떻게 쓰는지 파악 불가 |

**QaiOps**는 이 모든 문제를 하나의 로컬 관제 시스템으로 해결합니다.

---

## 2. 핵심 가치 및 해결 문제

```
┌─────────────────────────────────────────────────────────────────┐
│                          QaiOps                                 │
│                                                                 │
│  Visibility   →  분산된 AI 호출을 단일 대시보드에서 모니터링    │
│  Cost Control →  토큰 소모 기반 실시간 비용 추적 및 경보        │
│  Insight      →  프로젝트·질문 패턴 기반 사용 효율 분석         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 시스템 아키텍처

QaiOps는 **4개의 레이어**로 구성된 경량 로컬 시스템입니다.

```
┌──────────────────────────────────────────────────────────┐
│                     Developer CLI                        │
│          (gemini / claude / codex / ...)                 │
└────────────────────┬─────────────────────────────────────┘
                     │ qaiops run <tool> "<prompt>"
                     ▼
┌──────────────────────────────────────────────────────────┐
│              CLI Wrapper (Layer 1)                       │
│  • 명령어 인터셉트 및 실행                                 │
│  • 메타데이터 추출 (project, dir, timestamp)              │
│  • 출력 표준 JSON 스키마 변환                              │
│  • 로그 비동기 전송 (Background Process)                  │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP POST (비동기)
                     ▼
┌──────────────────────────────────────────────────────────┐
│              Log Server (Layer 2)                        │
│  • FastAPI 기반 비동기 수집 엔드포인트                     │
│  • 토큰 계산 보정 (tiktoken / Anthropic SDK)              │
│  • 비용 계산 및 DB 트랜잭션 처리                           │
│  • WebSocket / SSE 실시간 스트리밍                        │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              Storage (Layer 3)                           │
│  • SQLite (MVP) / PostgreSQL (확장)                      │
│  • 영구 기록 보관 및 통계 쿼리 처리                        │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              Frontend Dashboard (Layer 4)                │
│  • Next.js 14 (App Router)                               │
│  • 실시간 스트리밍 뷰 (WebSocket/SSE)                     │
│  • 사용량 통계 차트 / 히스토리 검색                        │
└──────────────────────────────────────────────────────────┘
```

---

## 4. 핵심 기능 명세

### 4.1 CLI 인터셉터 (Universal Wrapper)

단순 실행을 넘어 **실행 전후의 전체 컨텍스트를 캡처**합니다.

#### 사용 방법

```bash
# 명시적 래핑
qaiops run claude "리팩토링 방법을 알려줘"
qaiops run gemini "이 코드의 버그를 찾아줘"

# 줄인 명령어
qops run claude "리팩토링 방법을 알려줘"

# Alias를 통한 투명한 래핑 (.bashrc / .zshrc)
alias claude="qaiops run claude"
alias gemini="qaiops run gemini"
```

#### 추출 메타데이터

| 필드 | 추출 방법 | 예시 |
|------|-----------|------|
| `project_id` | `git rev-parse --show-toplevel` | `my-saas-app` |
| `directory` | `os.getcwd()` | `/home/user/projects/...` |
| `timestamp` | UTC ISO 8601 | `2025-07-18T09:23:00Z` |
| `tool_name` | CLI 인자 파싱 | `claude`, `gemini`, `gpt` |

#### 표준 출력 스키마

```json
{
  "tool": "claude",
  "model": "claude-opus-4-6",
  "project_id": "my-saas-app",
  "prompt": "리팩토링 방법을 알려줘",
  "response": "...",
  "usage": {
    "input_tokens": 120,
    "output_tokens": 850
  },
  "latency_ms": 3200,
  "status": "success",
  "tags": []
}
```

---

### 4.2 토큰 및 비용 분석 (Cost Analytics)

#### 토큰 계산 전략

```
API 응답의 usage 필드 존재 여부 확인
        │
        ├─ YES → API 응답값 사용 (정확)
        │
        └─ NO  → tiktoken 로컬 추정 (실시간 추정치)
```

#### 모델별 단가 테이블 (2025년 기준 예시)

| Provider | Model | Input ($/1M) | Output ($/1M) |
|----------|-------|--------------|---------------|
| Anthropic | claude-opus-4-6 | $15.00 | $75.00 |
| Anthropic | claude-sonnet-4-6 | $3.00 | $15.00 |
| Google | gemini-1.5-pro | $3.50 | $10.50 |
| OpenAI | gpt-4o | $5.00 | $15.00 |

> ⚠️ 실제 단가는 각 Provider 공식 문서를 기준으로 주기적으로 업데이트합니다.

#### High-Cost Alert

단일 요청이 **10,000 토큰 이상**을 소모할 경우, 대시보드에 강조 표시 및 알림을 제공합니다.

---

### 4.3 실시간 대시보드 (Dashboard Views)

| 뷰 | 차트 유형 | 설명 |
|----|-----------|------|
| 일일 사용량 | Area Chart | 시간대별 토큰 소모 추이 |
| 도구별 비중 | Donut Chart | Claude vs Gemini vs GPT 비율 |
| 프로젝트 히트맵 | Heatmap | 프로젝트별 AI 의존도 시각화 |
| 비용 상위 요청 | Ranked List | Top 10 Expensive Prompts |
| 실시간 로그 | Live Stream | WebSocket/SSE 기반 실시간 스트리밍 |

---

### 4.4 프로젝트별 인사이트 (Project-centric Analysis)

- **Prompt Efficiency**: 반복 질문 패턴 감지 및 비효율 알림
- **도구 추천**: 프로젝트 특성에 따른 최적 AI 도구 제안
- **태그 분석**: `refactoring`, `debug`, `unit-test` 등 태그 기반 용도 분류

---

### 4.5 히스토리 검색 (Full-text Search)

```sql
-- 예시: "리팩토링" 관련 대화 검색
SELECT * FROM qaiops_logs
WHERE prompt_text ILIKE '%리팩토링%'
   OR response_text ILIKE '%리팩토링%'
ORDER BY created_at DESC;
```

SQLite FTS5 확장 또는 PostgreSQL `tsvector`를 활용하여 빠른 전문 검색을 지원합니다.

---

## 5. 데이터 모델 설계

### 핵심 로그 테이블

```sql
CREATE TABLE qaiops_logs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_name     VARCHAR(50)    NOT NULL,      -- gemini, claude, gpt
    model_name    VARCHAR(50),                  -- claude-opus-4-6, gemini-1.5-pro
    project_id    VARCHAR(100),                 -- git repo 명 또는 디렉토리명
    directory     TEXT,                         -- 실행 경로 (절대 경로)
    prompt_text   TEXT           NOT NULL,
    response_text TEXT,
    input_tokens  INT            DEFAULT 0,
    output_tokens INT            DEFAULT 0,
    total_cost    NUMERIC(10, 6),               -- USD 기준 소모 비용
    latency_ms    INT,                          -- 응답 소요 시간 (ms)
    status_code   SMALLINT       DEFAULT 0,     -- 0: 성공, 1: 실패, 2: 타임아웃
    error_message TEXT,                         -- 실패 시 오류 메시지
    tags          JSONB,                        -- ['refactoring', 'debug', ...]
    raw_response  JSONB,                        -- 원본 API 응답 메타데이터
    created_at    TIMESTAMPTZ    DEFAULT NOW()
);

-- 성능 인덱스
CREATE INDEX idx_qaiops_project  ON qaiops_logs (project_id);
CREATE INDEX idx_qaiops_tool     ON qaiops_logs (tool_name);
CREATE INDEX idx_qaiops_created  ON qaiops_logs (created_at DESC);
CREATE INDEX idx_qaiops_cost     ON qaiops_logs (total_cost DESC);
```

### 프로젝트별 통계 뷰

```sql
CREATE VIEW project_usage_summary AS
SELECT
    project_id,
    tool_name,
    COUNT(*)                              AS request_count,
    SUM(input_tokens + output_tokens)     AS total_tokens,
    SUM(total_cost)                       AS total_cost_usd,
    AVG(latency_ms)                       AS avg_latency_ms,
    MAX(created_at)                       AS last_used_at
FROM qaiops_logs
WHERE status_code = 0
GROUP BY project_id, tool_name;
```

### 일별 집계 테이블 (성능 최적화용)

```sql
CREATE TABLE daily_usage_summary (
    date           DATE           NOT NULL,
    tool_name      VARCHAR(50)    NOT NULL,
    model_name     VARCHAR(50),
    total_requests INT            DEFAULT 0,
    total_tokens   BIGINT         DEFAULT 0,
    total_cost     NUMERIC(12, 6) DEFAULT 0,
    PRIMARY KEY (date, tool_name, model_name)
);
```

---

## 6. API 명세

### Log Server (FastAPI)

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/api/v1/logs` | 새 AI 상호작용 로그 저장 |
| `GET` | `/api/v1/logs` | 로그 목록 조회 (페이지네이션) |
| `GET` | `/api/v1/logs/{id}` | 단일 로그 상세 조회 |
| `GET` | `/api/v1/stats/daily` | 일별 사용량 통계 |
| `GET` | `/api/v1/stats/projects` | 프로젝트별 사용량 통계 |
| `GET` | `/api/v1/stats/top-costs` | 비용 상위 요청 Top N |
| `WebSocket` | `/ws/live` | 실시간 로그 스트리밍 |

#### POST `/api/v1/logs` 요청 예시

```json
{
  "tool_name": "claude",
  "model_name": "claude-sonnet-4-6",
  "project_id": "my-saas-app",
  "prompt_text": "이 함수를 리팩토링해줘",
  "response_text": "...",
  "input_tokens": 120,
  "output_tokens": 850,
  "latency_ms": 3200,
  "status_code": 0,
  "tags": ["refactoring"]
}
```

---

## 7. 기술 스택

| 영역 | 1순위 (권장) | 대체안 |
|------|-------------|--------|
| **Frontend** | Next.js 14 (App Router) | React + Vite |
| **Charts** | Tremor.so | Recharts, Chart.js |
| **Backend** | FastAPI (Python) | Next.js API Routes |
| **Database** | SQLite (MVP) | PostgreSQL / Supabase Local |
| **ORM** | SQLModel (Python) | Prisma (Node.js) |
| **Tokenizer** | tiktoken (OpenAI) | Anthropic SDK token counter |
| **Runtime** | Python 3.11+ | — |
| **Package Manager** | uv / pip | poetry |

### 선택 이유

- **SQLite**: 로컬 실행 환경에 최적화, 설치 불필요, 단일 파일로 백업 용이
- **FastAPI**: 비동기 처리 지원, 자동 API 문서 생성, Python 생태계 활용
- **Next.js + Tremor**: 대시보드 UI에 최적화된 차트 컴포넌트, 빠른 프로토타이핑

---

## 8. 구현 로드맵

### Phase 1: Logging Foundation (MVP) — 2주

```
[ ] Python 기반 유니버설 CLI Wrapper 개발
    ├─ [ ] 명령어 파싱 및 실행 모듈
    ├─ [ ] 메타데이터 추출 (git root, cwd, timestamp)
    ├─ [ ] 도구별 출력 파서 (Claude / Gemini / GPT)
    └─ [ ] 비동기 로그 전송 (Background Thread)

[ ] FastAPI 기반 로컬 로그 수집 서버 구축
    ├─ [ ] POST /api/v1/logs 엔드포인트
    ├─ [ ] 토큰 계산 보정 로직 (tiktoken 연동)
    └─ [ ] 비용 계산 모듈

[ ] SQLite DB 연동
    ├─ [ ] 스키마 마이그레이션 (Alembic)
    └─ [ ] 기본 CRUD 검증
```

### Phase 2: Monitoring Dashboard — 2주

```
[ ] Next.js 기반 대시보드 UI 구축
    ├─ [ ] 일일 토큰 사용량 · 비용 Area Chart
    ├─ [ ] 도구별 사용 비중 Donut Chart
    ├─ [ ] 프로젝트별 사용량 테이블
    └─ [ ] 기본 히스토리 목록 뷰
```

### Phase 3: Advanced Analysis — 2주

```
[ ] 전문 검색 (Full-text Search) 기능
[ ] Top 10 Expensive Prompts 섹션
[ ] 실시간 CLI 로그 스트리밍 (WebSocket/SSE)
[ ] 프로젝트 히트맵 시각화
[ ] High-Cost Alert 알림 시스템
```

### Phase 4: Hardening & Extension — 지속

```
[ ] 단가 테이블 자동 업데이트
[ ] 사용 패턴 기반 도구 추천 기능
[ ] 데이터 내보내기 (CSV / JSON)
[ ] PostgreSQL 마이그레이션 지원
```

---

## 9. 디렉토리 구조

```
qaiops/
├── wrapper/                    # CLI Wrapper (Python)
│   ├── main.py                 # 진입점: qaiops run <tool> "<prompt>"
│   ├── parsers/
│   │   ├── claude.py           # Claude 출력 파서
│   │   ├── gemini.py           # Gemini 출력 파서
│   │   └── gpt.py              # GPT 출력 파서
│   ├── metadata.py             # git root / cwd / timestamp 추출
│   └── sender.py               # 비동기 로그 전송
│
├── server/                     # Log Server (FastAPI)
│   ├── main.py
│   ├── routers/
│   │   ├── logs.py
│   │   └── stats.py
│   ├── models.py               # SQLModel 데이터 모델
│   ├── cost.py                 # 비용 계산 모듈
│   └── token_counter.py        # tiktoken 연동
│
├── dashboard/                  # Frontend (Next.js)
│   ├── app/
│   │   ├── page.tsx            # 메인 대시보드
│   │   ├── history/page.tsx    # 히스토리 검색
│   │   └── projects/page.tsx   # 프로젝트별 뷰
│   └── components/
│       ├── charts/
│       └── live-feed/
│
├── db/
│   ├── migrations/             # Alembic 마이그레이션
│   └── qaiops.db               # SQLite 데이터 파일
│
├── docs/
│   └── QaiOps_PRD.md
│
├── pyproject.toml
├── package.json
└── README.md
```

---

## 10. 핵심 리스크 및 대응

| 리스크 | 영향도 | 대응 전략 |
|--------|--------|-----------|
| **CLI 응답 속도 저하** | 높음 | Wrapper에서 로그 전송을 Background Thread / Async로 분리하여 사용자 경험 유지 |
| **출력 포맷 파편화** | 높음 | 도구별 전용 Parser Module 작성, 표준 JSON 스키마로 정규화 |
| **민감 정보 포함** | 높음 | 모든 데이터 로컬(Local-only) 저장, 외부 클라우드 전송 전면 금지 |
| **DB 용량 증가** | 중간 | 90일 이상 오래된 로그 자동 아카이빙 및 압축 옵션 제공 |
| **모델 단가 변경** | 낮음 | 단가 테이블을 별도 설정 파일로 분리, 쉽게 수동 업데이트 가능하도록 설계 |
| **다중 API 버전** | 중간 | Parser 모듈 버전 관리 및 출력 스키마 유효성 검사 (Pydantic) |

---

## 11. 기여 가이드

### 로컬 환경 설정

```bash
# 1. 레포지토리 클론
git clone https://github.com/your-org/qaiops.git && cd qaiops

# 2. Python 환경 설정
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 3. 서버 실행
cd server && uvicorn main:app --reload --port 8765

# 4. 대시보드 실행
cd dashboard && npm install && npm run dev

# 5. Wrapper 테스트
python wrapper/main.py run claude "Hello, QaiOps!"
```

### 커밋 컨벤션

```
feat:     새로운 기능 추가
fix:      버그 수정
docs:     문서 수정
refactor: 코드 리팩토링
test:     테스트 추가
chore:    빌드 설정, 의존성 변경
```

---

## 📎 결론

QaiOps는 단순히 로그를 쌓는 도구가 아닙니다.  
**개발자의 AI 협업 패턴을 데이터화**하여 지출 최적화와 워크플로우 개선을 이끄는 것이 궁극적 목표입니다.

Phase 1의 **CLI Wrapper 구현을 통해 데이터 흐름을 먼저 확보**하는 것이 성공의 핵심입니다.  
데이터가 쌓이면, 그 위에서 어떤 인사이트도 만들어낼 수 있습니다.

---

*Last updated: 2025-07*  
*Version: 0.1.0-draft*  
*Author: Q*
