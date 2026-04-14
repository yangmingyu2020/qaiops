# QaiOps Roadmap

> 최종 업데이트: 2026-04-15

## 현재 상태

| 항목 | 값 |
|------|-----|
| **현재 Phase** | Phase 2 완료, Phase 3 대기 |
| **버전** | 0.2.0-alpha.1 |
| **다음 작업** | Phase 3 — 전문 검색, 실시간 스트리밍, 알림 |
| **상세 계획** | [Phase 3 구현 계획](phases/PHASE3_PLAN.md) |

---

## Milestones

- [x] **v0.1.0 (MVP)**: CLI Wrapper + Log Server + SQLite 저장
- [x] **v0.2.0**: Next.js 기반 대시보드 UI
- [ ] **v0.3.0**: 실시간 스트리밍, 전문 검색, 알림

---

## Phase 1: Logging Foundation — 완료

> 상세: [Phase 1 구현 계획](phases/PHASE1_PLAN.md)

### CLI Wrapper (`qaiops/wrapper/`)
- [x] Click 기반 CLI 진입점 (`qaiops run <tool> "<prompt>"`)
- [x] 도구별 출력 파서 (Claude, Gemini, GPT)
- [x] 메타데이터 추출 (git root, cwd, timestamp)
- [x] 백그라운드 스레드 비동기 로그 전송
- [x] 서버 미실행 시 graceful failure

### FastAPI Log Server (`qaiops/server/`)
- [x] POST /api/v1/logs — 로그 저장 (토큰 보정 + 비용 계산)
- [x] GET /api/v1/logs — 페이지네이션 목록 (필터: tool, project, search)
- [x] GET /api/v1/logs/{id} — 단일 로그 조회
- [x] GET /api/v1/stats/daily — 일별 통계
- [x] GET /api/v1/stats/projects — 프로젝트별 통계
- [x] GET /api/v1/stats/top-costs — 비용 상위 Top N
- [x] GET /health — 헬스체크

### Database (`qaiops/db/`)
- [x] SQLModel 기반 qaiops_logs 테이블
- [x] Alembic 마이그레이션 환경
- [x] 성능 인덱스 4개

### 품질
- [x] 40개 테스트 전체 통과 (단위 + 통합)
- [x] 6개 모델 단가 테이블 (Anthropic, Google, OpenAI)

---

## Phase 2: Monitoring Dashboard — 완료

> 상세: [Phase 2 구현 계획](phases/PHASE2_PLAN.md)

### 환경 구성
- [x] Next.js 16 (App Router) 프로젝트 초기화
- [x] Recharts 차트 라이브러리 연동 (Tremor.so는 React 19 미호환으로 대체)
- [x] FastAPI 서버와 API 연동 설정 (lib/api.ts)

### 대시보드 뷰
- [x] 메인 대시보드 (KPI 카드 4개 + 일일 토큰 Area Chart)
- [x] 도구별 사용 비중 Donut Chart
- [x] 프로젝트별 사용량 테이블 (/projects)
- [x] 히스토리 목록 뷰 (/history — 필터, 검색, 페이지네이션, 상세 모달)
- [x] 비용 상위 요청 Top 5 랭킹

---

## Phase 3: Advanced Analysis — 예정

> 상세: [Phase 3 구현 계획](phases/PHASE3_PLAN.md)

### 검색 및 스트리밍
- [ ] 전문 검색 (SQLite FTS5)
- [ ] 실시간 로그 스트리밍 (WebSocket/SSE)

### 분석 및 알림
- [ ] Top 10 Expensive Prompts 섹션
- [ ] High-Cost Alert 알림 시스템 (10,000+ 토큰)
- [ ] 프로젝트 히트맵 시각화

---

## Phase 4: Hardening & Extension — 장기

- [ ] 모델 단가 테이블 자동 업데이트
- [ ] 사용 패턴 기반 도구 추천
- [ ] 데이터 내보내기 (CSV / JSON)
- [ ] PostgreSQL 마이그레이션 지원

---

## 문서 기반 개발 프로토콜

> 세션은 언제든 끊길 수 있습니다. 모든 맥락은 문서에 기록되어야 하며,
> 새 세션은 반드시 문서를 읽고 현재 상태를 파악한 뒤 작업을 시작합니다.

### 세션 시작 시 읽기 순서

```
1. 이 문서 (ROADMAP.md)       → 현재 상태와 다음 할 일
2. docs/phases/PHASEx_PLAN.md → 현재 Phase의 구체적 구현 명세
3. docs/ARCHITECTURE.md       → 기술 설계 결정사항
4. docs/QaiOps_PRD.md         → 전체 요구사항 (필요 시)
```

### 작업 후 문서 업데이트 규칙

| 이벤트 | 업데이트 대상 | 내용 |
|--------|-------------|------|
| 기능 구현 완료 | 이 문서 (ROADMAP.md) | 체크리스트 항목 체크 |
| Phase 완료 | 이 문서 (ROADMAP.md) | "현재 상태" 테이블 업데이트 |
| 커밋/릴리즈 | CHANGELOG.md | 변경사항 추가 |
| 설계 결정 | ARCHITECTURE.md | ADR 추가 |
| Phase 착수 | 해당 PLAN.md | 상태를 "진행 중"으로 변경 |

### 에이전트 지침 파일

- [CLAUDE.md](../CLAUDE.md) — Claude Code 세션용
- [GEMINI.md](../GEMINI.md) — Gemini CLI 세션용

두 파일은 동일한 프로토콜을 공유합니다. 어느 에이전트든 같은 문서를 읽고 같은 방식으로 작업합니다.
