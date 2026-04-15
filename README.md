# QaiOps

AI CLI Observability for Developers

Gemini, Claude, ChatGPT 등 파편화된 AI CLI 사용 경험을 하나로 통합하고,
토큰 소모, 비용, 패턴을 실시간으로 시각화하는 로컬 관제 시스템.

## Prerequisites

- Python 3.11+ (uv로 자동 설치 가능)
- Node.js 18+ (대시보드용)
- [uv](https://docs.astral.sh/uv/) (Python 패키지 매니저)

## Installation

### 1. uv 설치 (처음 한 번)

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Python 설치 (uv로 관리)

```bash
uv python install 3.12
```

### 3. 백엔드 설치

```bash
cd QaiOps
uv venv
uv pip install -e ".[dev]"
```

### 4. 대시보드 설치

```bash
cd dashboard
npm install
```

## 실행 방법

### 가상환경 활성화 (매 터미널마다 필요)

서버나 CLI를 실행하기 전에 반드시 가상환경을 먼저 활성화해야 합니다:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

> 활성화되면 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다.

### 백엔드 서버 실행

```bash
# 가상환경 활성화 후 실행
uvicorn qaiops.server.main:app --reload --port 8765

# 또는 CLI 명령으로 실행
qaiops server
qaiops server --port 9000  # 포트 변경
```

서버가 실행되면 아래 URL로 접속할 수 있습니다:
- API 문서 (Swagger): http://localhost:8765/docs
- 헬스체크: http://localhost:8765/health

### 대시보드 실행

```bash
cd dashboard
npm run dev
```

대시보드 접속: http://localhost:3000

> 대시보드는 백엔드 서버(port 8765)가 실행 중이어야 데이터를 표시합니다.

### CLI Wrapper 사용

AI CLI 도구를 래핑하여 사용량을 자동으로 로깅합니다:

```bash
# 기본 사용법
qaiops run claude "리팩토링 방법을 알려줘"
qaiops run gemini "이 코드의 버그를 찾아줘"
qaiops run gpt "유닛 테스트를 작성해줘"

# 줄인 명령어 (alias)
qops run claude "설명해줘"
```

> 서버가 실행되지 않아도 CLI는 정상 동작합니다. 로그 전송만 실패하며 경고 메시지가 표시됩니다.

## 대시보드 페이지

| 페이지 | URL | 설명 |
|--------|-----|------|
| Dashboard | `/` | KPI 카드, 일일 토큰 추이 차트, 도구별 비중, 비용 랭킹 |
| Live Feed | `/live` | WebSocket 기반 실시간 로그 스트림 |
| History | `/history` | 로그 검색/필터/페이지네이션, 상세 모달 |
| Projects | `/projects` | 프로젝트별 사용량 통계 |
| Alerts | `/alerts` | 고비용 요청 알림 (토큰 기준값 설정 가능) |

## API Endpoints

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/logs` | 로그 저장 (토큰 보정 + 비용 자동 계산) |
| GET | `/api/v1/logs` | 로그 목록 (FTS5 검색, 페이지네이션) |
| GET | `/api/v1/logs/{id}` | 단일 로그 조회 |
| GET | `/api/v1/stats/daily` | 일별 통계 |
| GET | `/api/v1/stats/projects` | 프로젝트별 통계 |
| GET | `/api/v1/stats/top-costs` | 비용 상위 Top N |
| GET | `/api/v1/stats/heatmap` | 프로젝트 히트맵 데이터 |
| GET | `/api/v1/stats/alerts` | 고비용 알림 목록 |
| WebSocket | `/ws/live` | 실시간 로그 스트리밍 |
| GET | `/health` | 헬스체크 |

## 테스트

```bash
pytest           # 전체 테스트 실행
pytest -v        # 상세 출력
pytest --cov     # 커버리지 포함
```

## DB 마이그레이션

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 프로젝트 구조

```
QaiOps/
├── qaiops/
│   ├── wrapper/          # CLI Wrapper (qaiops run <tool>)
│   ├── server/           # FastAPI Log Server
│   └── db/               # SQLite + SQLModel + Alembic
├── dashboard/            # Next.js 대시보드 UI
├── tests/                # pytest 테스트
├── docs/                 # 프로젝트 문서
│   ├── ROADMAP.md        # 진행 현황 (시작점)
│   ├── ARCHITECTURE.md   # 기술 설계
│   ├── CHANGELOG.md      # 변경 이력
│   └── phases/           # Phase별 구현 계획
└── pyproject.toml        # Python 패키지 설정
```

## Documentation

| 문서 | 설명 |
|------|------|
| [ROADMAP](docs/ROADMAP.md) | 진행 현황 및 다음 할 일 **(시작점)** |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | 기술 설계 및 결정 사항 |
| [CHANGELOG](docs/CHANGELOG.md) | 버전별 변경 이력 |
| [PRD](docs/QaiOps_PRD.md) | 전체 제품 요구사항 |

### AI Agent Instructions

- [CLAUDE.md](./CLAUDE.md) -- Claude Code 에이전트 지침
- [GEMINI.md](./GEMINI.md) -- Gemini CLI 에이전트 지침
