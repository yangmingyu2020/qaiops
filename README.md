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

- [PRD](docs/QaiOps_PRD.md)
- [Phase 1 구현 계획](docs/PHASE1_PLAN.md)
- [아키텍처 결정사항](docs/ARCHITECTURE.md)
