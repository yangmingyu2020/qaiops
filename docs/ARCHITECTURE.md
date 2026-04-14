# QaiOps 아키텍처 결정사항

> 작성일: 2026-04-14
> Phase: 1 (MVP)

## 시스템 구조

```
CLI (qaiops run) → FastAPI Server → SQLite DB
                   ↕ (HTTP POST)
```

## SQLite 적응 (PostgreSQL → SQLite)

PRD는 PostgreSQL 문법으로 스키마를 정의했으나, MVP에서는 SQLite를 사용한다.

| PostgreSQL | SQLite 적응 | 이유 |
|-----------|-------------|------|
| `UUID` | `TEXT` (Python uuid4) | SQLite에 UUID 타입 없음 |
| `JSONB` | `TEXT` (JSON 문자열) | SQLite에 JSONB 없음 |
| `TIMESTAMPTZ` | `TEXT` (ISO 8601) | SQLite에 타임존 타입 없음 |
| `gen_random_uuid()` | Python `uuid4()` | 앱 레벨에서 생성 |
| `NOW()` | Python `datetime.utcnow()` | 앱 레벨에서 생성 |
| `ILIKE` | `contains()` | SQLAlchemy가 자동 처리 |
| `NUMERIC(10,6)` | `REAL` (float) | SQLModel float 매핑 |

## 패키지 구조 변경

PRD의 `wrapper/`, `server/` 최상위 구조를 `qaiops/` Python 패키지로 통합:

```
qaiops/             ← Python 패키지 (import 및 entry point 지원)
├── db/             ← 데이터베이스 레이어
├── server/         ← FastAPI 서버
└── wrapper/        ← CLI 래퍼
```

**이유**: `pyproject.toml` entry point 정의와 모듈 간 import가 깔끔해짐.

## 주요 설계 결정

### 1. 동적 쿼리 vs DB 뷰

PRD의 `project_usage_summary` 뷰와 `daily_usage_summary` 테이블 대신 동적 GROUP BY 쿼리를 사용.

- **이유**: MVP 데이터량에서 성능 문제 없음. 뷰/집계 테이블은 Phase 2에서 도입.

### 2. 비용 계산: 서버 사이드

- **이유**: 단가 테이블을 서버 한 곳에서 관리. CLI 래퍼는 가볍게 유지.
- **구현**: `server/cost.py`에 PRICING 딕셔너리, 서버가 로그 저장 시 자동 계산.

### 3. 토큰 카운팅 폴백

```
API 응답에 usage 필드 있음? → YES → API 값 사용
                           → NO  → tiktoken 추정 (cl100k_base)
```

- **이유**: 모든 CLI가 토큰 정보를 제공하지 않으므로 서버에서 보정.

### 4. CLI 래퍼 투명성

- 래퍼가 도구의 stdout을 그대로 출력
- 로그 전송 실패해도 CLI는 정상 동작
- 도구의 exit code를 그대로 반환

### 5. 비동기 전송 (daemon thread)

- 로그 전송은 `threading.Thread(daemon=True)`로 실행
- CLI 응답 속도에 영향 없음
- 서버 미실행 시 stderr 경고만 출력

## 모델 단가 테이블

| Provider | Model | Input ($/1M) | Output ($/1M) |
|----------|-------|-------------|--------------|
| Anthropic | claude-opus-4-6 | $15.00 | $75.00 |
| Anthropic | claude-sonnet-4-6 | $3.00 | $15.00 |
| Google | gemini-1.5-pro | $3.50 | $10.50 |
| Google | gemini-2.0-flash | $0.10 | $0.40 |
| OpenAI | gpt-4o | $5.00 | $15.00 |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 |

## API 엔드포인트 요약

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/logs` | 로그 저장 |
| GET | `/api/v1/logs` | 로그 목록 (페이지네이션) |
| GET | `/api/v1/logs/{id}` | 단일 로그 조회 |
| GET | `/api/v1/stats/daily` | 일별 통계 |
| GET | `/api/v1/stats/projects` | 프로젝트별 통계 |
| GET | `/api/v1/stats/top-costs` | 비용 상위 Top N |
| GET | `/health` | 헬스체크 |

## 다음 단계 (Phase 2)

- Next.js 14 대시보드 UI
- WebSocket/SSE 실시간 스트리밍
- daily_usage_summary 물리 테이블 전환
- 전문 검색 (FTS5)
