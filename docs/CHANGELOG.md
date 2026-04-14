# Changelog

이 프로젝트의 모든 중요한 변경 사항을 기록합니다.

## [0.2.0-alpha.1] - 2026-04-15

### Added
- **Dashboard**: Next.js 16 (App Router) + Recharts 기반 모니터링 대시보드
  - 메인 대시보드: KPI 카드 4개 (Total Requests, Tokens, Cost, Active Tools)
  - Daily Token Usage Area Chart (30일 추이)
  - Tool Distribution Donut Chart (도구별 사용 비중)
  - Top Expensive Requests 랭킹 (비용 상위 5건)
  - 사이드바 내비게이션 (Dashboard, History, Projects)
  - 헤더 서버 연결 상태 표시 (30초 간격 폴링)
- **History 페이지**: 로그 목록 테이블
  - 필터: 도구명, 프로젝트 ID, 전문 검색
  - 페이지네이션
  - 로그 상세 모달 (prompt + response 전문)
- **Projects 페이지**: 프로젝트별 사용량 통계 테이블
  - Requests, Tokens, Cost, Avg Latency, Last Used 표시
- **API 유틸리티**: `dashboard/lib/api.ts` — 타입 안전한 FastAPI 서버 연동

### Changed
- Tremor.so에서 Recharts로 차트 라이브러리 변경 (React 19 호환성)

---

## [0.1.0-alpha.1] - 2026-04-14

### Added
- **CLI Wrapper**: `qaiops run <tool> "<prompt>"` 명령어로 Claude, Gemini, GPT CLI 래핑
  - Click 기반 CLI 진입점 (`qaiops`, `qops` alias)
  - 도구별 출력 파서 (JSON 구조화 출력 + plain text 폴백)
  - 메타데이터 자동 추출 (git project ID, cwd, UTC timestamp)
  - 백그라운드 스레드 비동기 로그 전송 (서버 미실행 시 graceful failure)
- **FastAPI Log Server**: 7개 API 엔드포인트
  - `POST /api/v1/logs` — 로그 저장 (서버 사이드 토큰 보정 + 비용 자동 계산)
  - `GET /api/v1/logs` — 페이지네이션 목록 (필터: tool_name, project_id, search)
  - `GET /api/v1/logs/{id}` — 단일 로그 조회
  - `GET /api/v1/stats/daily` — 일별 사용량 통계
  - `GET /api/v1/stats/projects` — 프로젝트별 통계
  - `GET /api/v1/stats/top-costs` — 비용 상위 Top N
  - `GET /health` — 헬스체크
- **Database**: SQLite + SQLModel + Alembic
  - `qaiops_logs` 테이블 (UUID PK, 메타데이터, 토큰, 비용, 태그)
  - `daily_usage_summary` 테이블 (향후 최적화용)
  - 성능 인덱스 4개 (project_id, tool_name, created_at, total_cost)
- **비용 계산**: 6개 모델 단가 테이블
  - Anthropic: claude-opus-4-6, claude-sonnet-4-6
  - Google: gemini-1.5-pro, gemini-2.0-flash
  - OpenAI: gpt-4o, gpt-4o-mini
- **토큰 카운터**: tiktoken 기반 (미지원 모델은 cl100k_base 폴백)
- **테스트**: 40개 전체 통과 (단위 + API 통합)
- **문서**: PRD, Phase 1 구현 계획, 아키텍처 결정사항, 로드맵

### Technical
- Python 3.12, uv 패키지 매니저
- 비동기 전체 스택: FastAPI + aiosqlite + SQLAlchemy async
- PRD의 PostgreSQL 스키마를 SQLite 호환으로 적응 (UUID→TEXT, JSONB→TEXT)
