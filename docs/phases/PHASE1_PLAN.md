# Phase 1 (MVP) 구현 계획서

> 작성일: 2026-04-14
> 상태: 구현 완료

## 개요

QaiOps Phase 1은 AI CLI 도구(Claude, Gemini, GPT)의 사용 로그를 수집하고 저장하는 핵심 인프라 구축에 집중한다.

## 구현 범위

### 1. CLI Wrapper (`qaiops/wrapper/`)
- `qaiops run <tool> "<prompt>"` 명령으로 AI CLI 래핑
- 메타데이터 자동 추출 (git project, cwd, timestamp)
- 도구별 출력 파서 (Claude, Gemini, GPT)
- 백그라운드 스레드를 통한 비동기 로그 전송
- 서버 미실행 시에도 CLI 정상 동작 (graceful failure)

### 2. FastAPI Log Server (`qaiops/server/`)
- `POST /api/v1/logs` — 로그 저장 (토큰 보정 + 비용 자동 계산)
- `GET /api/v1/logs` — 페이지네이션 목록 (필터: tool, project, search)
- `GET /api/v1/logs/{id}` — 단일 로그 조회
- `GET /api/v1/stats/daily` — 일별 사용량 통계
- `GET /api/v1/stats/projects` — 프로젝트별 통계
- `GET /api/v1/stats/top-costs` — 비용 상위 요청
- `GET /health` — 헬스체크

### 3. SQLite Database (`qaiops/db/`)
- `qaiops_logs` 테이블 (UUID PK, 메타데이터, 토큰, 비용, 태그)
- `daily_usage_summary` 테이블 (향후 최적화용)
- 성능 인덱스 4개 (project_id, tool_name, created_at, total_cost)
- Alembic 마이그레이션 관리

## 기술 스택

| 영역 | 선택 |
|------|------|
| Runtime | Python 3.12 |
| Package Manager | uv |
| Web Framework | FastAPI |
| ORM | SQLModel |
| Database | SQLite (aiosqlite) |
| Tokenizer | tiktoken |
| HTTP Client | httpx |
| CLI Framework | click |
| Migration | Alembic |

## 테스트 결과

- 총 40개 테스트 전체 통과
- 단위 테스트: cost, token_counter, parsers, metadata, sender
- 통합 테스트: logs API, stats API, health check
