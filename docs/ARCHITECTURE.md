# QaiOps Architecture & Design

> 최종 업데이트: 2026-04-14

QaiOps의 기술적 설계와 주요 결정 사항을 기록합니다.

## 시스템 구조

```
┌─────────────────────────────────────┐
│         Developer CLI               │
│   (gemini / claude / codex / ...)   │
└──────────────┬──────────────────────┘
               │  qaiops run <tool> "<prompt>"
               ▼
┌─────────────────────────────────────┐
│     CLI Wrapper (qaiops/wrapper/)   │
│  • 명령어 인터셉트 및 subprocess 실행  │
│  • 메타데이터 추출 (git, cwd, time)   │
│  • 도구별 출력 파서 (parsers/)        │
│  • 비동기 로그 전송 (daemon thread)   │
└──────────────┬──────────────────────┘
               │  HTTP POST (비동기, fire-and-forget)
               ▼
┌─────────────────────────────────────┐
│     Log Server (qaiops/server/)     │
│  • FastAPI 비동기 엔드포인트          │
│  • 토큰 보정 (tiktoken)             │
│  • 비용 계산 (모델별 단가 테이블)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Storage (qaiops/db/)            │
│  • SQLite + SQLModel + aiosqlite    │
│  • Alembic 마이그레이션 관리          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Dashboard (dashboard/)          │
│  • Next.js 14 (Phase 2 예정)        │
│  • Tremor.so 차트                   │
└─────────────────────────────────────┘
```

## 디렉토리 구조

PRD의 파편화된 구조 대신, 하나의 Python 패키지(`qaiops`)로 통합하였습니다.

```
qaiops/
├── wrapper/              # CLI 래퍼
│   ├── main.py           # Click CLI 진입점
│   ├── metadata.py       # git root, cwd, timestamp 추출
│   ├── sender.py         # 비동기 로그 전송
│   └── parsers/          # 도구별 출력 파서
│       ├── __init__.py   # ParseResult, get_parser()
│       ├── claude.py
│       ├── gemini.py
│       └── gpt.py
├── server/               # FastAPI 서버
│   ├── main.py           # 앱 생성, CORS, 라이프사이클
│   ├── cost.py           # 모델별 단가 + calculate_cost()
│   ├── token_counter.py  # tiktoken count_tokens()
│   └── routers/
│       ├── logs.py       # POST/GET /api/v1/logs
│       └── stats.py      # GET /api/v1/stats/*
└── db/                   # 데이터베이스
    ├── engine.py         # AsyncEngine, 세션 관리
    ├── models.py         # SQLModel 테이블 + Pydantic 스키마
    └── migrations/       # Alembic
```

## 주요 기술 결정 (ADR)

### ADR-001: Async-first 아키텍처

**결정**: CLI 응답에 지연을 주지 않기 위해 서버 통신과 DB 저장을 모두 비동기로 처리.

- CLI → Server: `threading.Thread(daemon=True)`로 fire-and-forget
- Server → DB: `aiosqlite` + SQLAlchemy async engine
- 서버 미실행 시 stderr 경고만 출력, CLI는 정상 동작

### ADR-002: 단일 Python 패키지 구조

**결정**: `wrapper/`, `server/`, `db/`를 `qaiops/` 패키지로 통합.

- **이유**: `pyproject.toml` entry point와 모듈 간 import가 깔끔해짐
- **결과**: `qaiops`, `qops` 명령어로 CLI 직접 접근 가능

### ADR-003: SQLite 적응 (PostgreSQL → SQLite)

PRD는 PostgreSQL 문법으로 스키마를 정의했으나, MVP에서는 SQLite를 사용.

| PostgreSQL | SQLite 적응 | 이유 |
|-----------|-------------|------|
| `UUID` | `TEXT` (Python uuid4) | SQLite에 UUID 타입 없음 |
| `JSONB` | `TEXT` (JSON 문자열) | SQLite에 JSONB 없음 |
| `TIMESTAMPTZ` | `TEXT` (ISO 8601) | SQLite에 타임존 타입 없음 |
| `gen_random_uuid()` | Python `uuid4()` | 앱 레벨에서 생성 |
| `NUMERIC(10,6)` | `REAL` (float) | SQLModel float 매핑 |

### ADR-004: 서버 사이드 비용 계산

**결정**: 비용 계산은 CLI가 아닌 서버에서 수행.

- **이유**: 단가 테이블을 서버 한 곳에서 관리
- **구현**: `server/cost.py`에 PRICING 딕셔너리, 로그 저장 시 자동 계산
- **미지원 모델**: cost = 0.0 반환, 경고 로그

### ADR-005: 토큰 카운팅 폴백

```
API 응답에 usage 필드 있음?
  ├── YES → API 값 사용 (정확)
  └── NO  → tiktoken 추정 (cl100k_base 폴백)
```

## 모델 단가 테이블

| Provider | Model | Input ($/1M) | Output ($/1M) |
|----------|-------|-------------|--------------|
| Anthropic | claude-opus-4-6 | $15.00 | $75.00 |
| Anthropic | claude-sonnet-4-6 | $3.00 | $15.00 |
| Google | gemini-1.5-pro | $3.50 | $10.50 |
| Google | gemini-2.0-flash | $0.10 | $0.40 |
| OpenAI | gpt-4o | $5.00 | $15.00 |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 |

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/logs` | 로그 저장 (토큰 보정 + 비용 계산) |
| GET | `/api/v1/logs` | 로그 목록 (페이지네이션, 필터) |
| GET | `/api/v1/logs/{id}` | 단일 로그 조회 |
| GET | `/api/v1/stats/daily` | 일별 통계 |
| GET | `/api/v1/stats/projects` | 프로젝트별 통계 |
| GET | `/api/v1/stats/top-costs` | 비용 상위 Top N |
| GET | `/health` | 헬스체크 |
