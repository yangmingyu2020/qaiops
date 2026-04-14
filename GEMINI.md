# QaiOps - Gemini CLI Instructions

> 이 프로젝트는 **문서 기반 개발**을 원칙으로 합니다.
> 세션은 언제든 끊길 수 있으므로, 모든 맥락은 문서에 기록되어야 하며
> 새 세션은 반드시 문서를 읽고 현재 상태를 파악한 뒤 작업을 시작합니다.

## 세션 시작 프로토콜

새 세션에서는 **반드시** 아래 순서로 문서를 읽고 현재 상태를 파악하세요:

```
1. docs/ROADMAP.md          → 현재 어디까지 했고, 다음에 뭘 해야 하는가?
2. docs/phases/PHASEx_PLAN.md → 현재 Phase의 구체적 구현 명세
3. docs/ARCHITECTURE.md      → 기술 설계와 결정 근거
4. docs/QaiOps_PRD.md        → 전체 요구사항 (필요 시)
```

**문서를 읽기 전에 코드를 작성하지 마세요.** ROADMAP.md의 "현재 상태" 테이블만 읽어도 프로젝트 위치를 즉시 파악할 수 있습니다.

## 문서 체계

```
docs/
├── ROADMAP.md          # 진행 현황 + 다음 할 일 (세션 진입점)
├── ARCHITECTURE.md     # 기술 설계, 디렉토리 구조, ADR
├── CHANGELOG.md        # 버전별 변경 이력
├── QaiOps_PRD.md       # 원본 제품 요구사항
└── phases/
    ├── PHASE1_PLAN.md  # Phase 1 상세 계획 (완료)
    ├── PHASE2_PLAN.md  # Phase 2 상세 계획
    └── PHASE3_PLAN.md  # Phase 3 상세 계획
```

| 문서 | 읽는 시점 | 핵심 질문 |
|------|----------|-----------|
| ROADMAP.md | 세션 시작 시 가장 먼저 | 지금 어디이고, 다음은 무엇인가? |
| PHASEx_PLAN.md | 해당 Phase 작업 시 | 구체적으로 뭘 만드는가? |
| ARCHITECTURE.md | 설계 결정 필요 시 | 왜 이렇게 만들었는가? |
| CHANGELOG.md | 커밋/릴리즈 시 | 무엇이 바뀌었는가? |
| QaiOps_PRD.md | 요구사항 확인 시 | 최종 목표는 무엇인가? |

## 작업 후 문서 업데이트 규칙

작업이 끝나면 **반드시** 관련 문서를 업데이트하세요. 다음 세션이 이어받을 수 있도록:

| 이벤트 | 업데이트 대상 | 내용 |
|--------|-------------|------|
| 기능 구현 완료 | ROADMAP.md | 체크리스트 항목 체크 |
| Phase 완료 | ROADMAP.md | "현재 상태" 테이블 업데이트 |
| 커밋/릴리즈 | CHANGELOG.md | 변경사항 추가 |
| 설계 결정 | ARCHITECTURE.md | 결정 내용과 근거 추가 |
| Phase 착수 | 해당 PLAN.md | 상태를 "진행 중"으로 변경 |
| 새 Phase 계획 | docs/phases/ | 새 PLAN.md 생성 |

## 프로젝트 개요

QaiOps는 Gemini, Claude, ChatGPT 등 AI CLI 도구의 사용량/비용/패턴을 통합 모니터링하는 로컬 관제 시스템입니다.

## 기술 스택

- **Backend**: Python 3.12, FastAPI, SQLModel, aiosqlite
- **Database**: SQLite (MVP) → PostgreSQL (확장)
- **Frontend**: Next.js 14, Tremor.so (Phase 2~)
- **CLI**: Click
- **Package Manager**: uv (Python), pnpm or npm (Node.js)

## 개발 명령

```bash
# 환경 설정
uv venv && uv pip install -e ".[dev]"

# 서버 실행
uvicorn qaiops.server.main:app --reload --port 8765

# 테스트
pytest

# 마이그레이션
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 코딩 컨벤션

- 서버 로직은 `async/await` 기본
- 새 API 엔드포인트 추가 시 `qaiops/db/models.py`에 스키마 먼저 정의
- 새 파서 추가 시 `qaiops/wrapper/parsers/`에 모듈 생성 + `__init__.py`의 `get_parser()` 업데이트
- 커밋 메시지: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:` 접두사 사용

## 연관 문서

- [CLAUDE.md](./CLAUDE.md) — Claude Code 에이전트 지침 (이 문서와 동일한 프로토콜)
- [docs/ROADMAP.md](./docs/ROADMAP.md) — 현재 진행 상태
