# Phase 2: Monitoring Dashboard 구현 계획

> 상태: 완료 (2026-04-15)
> 예상 기간: 2주
> 선행 조건: Phase 1 완료 (완료됨)

## 목표

FastAPI 백엔드의 데이터를 시각화하는 Next.js 14 기반 대시보드를 구축한다.

## 기술 스택

| 영역 | 선택 | 이유 |
|------|------|------|
| Framework | Next.js 14 (App Router) | SSR + 서버 컴포넌트, 빠른 초기 로딩 |
| Charts | Tremor.so | 대시보드 특화 차트 컴포넌트, Tailwind 기반 |
| Styling | Tailwind CSS | Tremor 의존성, 유틸리티 퍼스트 |
| HTTP Client | fetch (서버 컴포넌트) | Next.js 내장, 캐싱 지원 |
| Package Manager | pnpm 또는 npm | Next.js 표준 |

## 디렉토리 구조

```
dashboard/
├── app/
│   ├── layout.tsx          # 루트 레이아웃 (사이드바, 헤더)
│   ├── page.tsx            # 메인 대시보드 (일일 통계)
│   ├── history/
│   │   └── page.tsx        # 히스토리 검색/목록
│   └── projects/
│       └── page.tsx        # 프로젝트별 분석
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx     # 사이드바 내비게이션
│   │   └── Header.tsx      # 상단 헤더
│   ├── charts/
│   │   ├── DailyUsageChart.tsx    # 일일 토큰/비용 Area Chart
│   │   ├── ToolDistribution.tsx   # 도구별 비중 Donut Chart
│   │   └── CostRanking.tsx        # 비용 상위 요청 리스트
│   └── common/
│       ├── StatsCard.tsx   # KPI 카드 (총 요청, 총 비용 등)
│       └── LogTable.tsx    # 로그 테이블 (페이지네이션)
├── lib/
│   └── api.ts              # FastAPI 서버 API 호출 유틸리티
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.ts
```

## 구현 순서

### Step 1: 프로젝트 초기화
- Next.js 14 프로젝트 생성 (`create-next-app`)
- Tremor.so, Tailwind CSS 설치 및 설정
- API 호출 유틸리티 (`lib/api.ts`) 작성
- FastAPI CORS 설정 확인

### Step 2: 레이아웃 구성
- 사이드바 내비게이션 (Dashboard, History, Projects)
- 상단 헤더 (프로젝트명, 서버 상태 표시)
- 반응형 레이아웃

### Step 3: 메인 대시보드 (`/`)
- KPI 카드 4개: 총 요청 수, 총 토큰, 총 비용, 평균 응답 시간
- 일일 토큰/비용 추이 Area Chart (`GET /api/v1/stats/daily`)
- 도구별 사용 비중 Donut Chart
- 비용 상위 요청 Top 5 리스트 (`GET /api/v1/stats/top-costs`)

### Step 4: 히스토리 뷰 (`/history`)
- 로그 목록 테이블 (페이지네이션)
- 필터: 도구명, 프로젝트, 검색어
- 로그 상세 모달/페이지 (prompt + response 전문)
- 데이터 소스: `GET /api/v1/logs`

### Step 5: 프로젝트별 뷰 (`/projects`)
- 프로젝트별 사용량 요약 테이블
- 프로젝트 선택 시 상세 통계
- 데이터 소스: `GET /api/v1/stats/projects`

## API 연동 매핑

| 대시보드 컴포넌트 | API 엔드포인트 | 비고 |
|-------------------|---------------|------|
| KPI 카드 | `/api/v1/stats/daily` + 집계 | 클라이언트에서 합산 |
| 일일 추이 차트 | `/api/v1/stats/daily?days=30` | |
| 도구별 비중 | `/api/v1/stats/daily` | tool_name 기준 그룹핑 |
| 비용 상위 | `/api/v1/stats/top-costs?limit=5` | |
| 히스토리 테이블 | `/api/v1/logs?page=N&size=20` | 필터 파라미터 포함 |
| 프로젝트 통계 | `/api/v1/stats/projects` | |

## 검증 방법

1. `npm run dev` → http://localhost:3000 접속
2. FastAPI 서버 실행 상태에서 대시보드 데이터 표시 확인
3. 빈 데이터 상태에서도 빈 상태 UI 정상 표시
4. 각 필터/페이지네이션 동작 확인
5. 모바일 반응형 레이아웃 확인
