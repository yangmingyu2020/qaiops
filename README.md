# QaiOps

AI CLI Observability for Developers

Gemini, Claude, ChatGPT 등 파편화된 AI CLI 사용 경험을 하나로 통합하고,
토큰 소모, 비용, 패턴을 실시간으로 시각화하는 로컬 관제 시스템.

## Quick Start

```bash
# 설치
uv venv && uv pip install -e ".[dev]"

# 서버 실행
uvicorn qaiops.server.main:app --reload --port 8765

# CLI 사용
qaiops run claude "리팩토링 방법을 알려줘"
```

## Documentation

| 문서 | 설명 |
|------|------|
| [ROADMAP](docs/ROADMAP.md) | 진행 현황 및 다음 할 일 **(시작점)** |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | 기술 설계 및 결정 사항 |
| [CHANGELOG](docs/CHANGELOG.md) | 버전별 변경 이력 |
| [PRD](docs/QaiOps_PRD.md) | 전체 제품 요구사항 |
| [Phase 1 Plan](docs/phases/PHASE1_PLAN.md) | Phase 1 구현 계획 (완료) |
| [Phase 2 Plan](docs/phases/PHASE2_PLAN.md) | Phase 2 구현 계획 |
| [Phase 3 Plan](docs/phases/PHASE3_PLAN.md) | Phase 3 구현 계획 |

### AI Agent Instructions

- [CLAUDE.md](./CLAUDE.md) — Claude Code 에이전트 지침
- [GEMINI.md](./GEMINI.md) — Gemini CLI 에이전트 지침
