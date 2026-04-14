# Phase 3: Advanced Analysis 구현 계획

> 상태: 완료 (2026-04-15)
> 예상 기간: 2주
> 선행 조건: Phase 2 완료

## 목표

전문 검색, 실시간 스트리밍, 고급 분석 기능을 추가하여 QaiOps의 관제 능력을 강화한다.

## 구현 범위

### 1. 전문 검색 (Full-text Search)

#### 백엔드
- SQLite FTS5 가상 테이블 생성
  ```sql
  CREATE VIRTUAL TABLE qaiops_logs_fts USING fts5(
      prompt_text, response_text, content=qaiops_logs
  );
  ```
- FTS 인덱스 자동 동기화 (트리거 또는 로그 저장 시 갱신)
- `GET /api/v1/logs` 검색 쿼리를 FTS5 MATCH로 전환
- 검색 결과 하이라이팅 지원

#### 프론트엔드
- 히스토리 뷰에 검색바 강화 (자동완성, 검색 결과 하이라이트)
- 검색 결과 페이지네이션

### 2. 실시간 로그 스트리밍

#### 백엔드
- WebSocket 엔드포인트: `WS /ws/live`
- 새 로그 저장 시 연결된 클라이언트에 브로드캐스트
- SSE 대체 엔드포인트: `GET /api/v1/logs/stream` (WebSocket 미지원 환경용)
- 연결 관리: 클라이언트 연결/해제 처리

#### 프론트엔드
- Live Feed 컴포넌트 (실시간 로그 스트림)
- 자동 스크롤 + 일시정지 기능
- 연결 상태 표시 (Connected / Reconnecting)

### 3. 고급 분석 뷰

#### Top 10 Expensive Prompts
- 비용 상위 요청 전용 페이지
- 프롬프트 내용 미리보기
- 기간별 필터 (7일, 30일, 전체)

#### High-Cost Alert
- 단일 요청 10,000+ 토큰 소모 시 대시보드 알림 표시
- 알림 기준값 사용자 설정 가능
- 알림 히스토리

#### 프로젝트 히트맵
- 프로젝트별 AI 의존도 시각화 (시간 x 프로젝트 매트릭스)
- 색상 강도: 토큰 소모량 또는 비용 기준
- Tremor.so 또는 D3.js 활용

## 백엔드 추가 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| WebSocket | `/ws/live` | 실시간 로그 스트리밍 |
| GET | `/api/v1/logs/stream` | SSE 로그 스트리밍 |
| GET | `/api/v1/stats/heatmap` | 프로젝트 히트맵 데이터 |
| GET | `/api/v1/alerts` | 알림 목록 조회 |

## 구현 순서

### Step 1: FTS5 전문 검색
- FTS5 가상 테이블 마이그레이션
- 검색 API 전환
- 프론트엔드 검색 UI 개선

### Step 2: WebSocket 실시간 스트리밍
- FastAPI WebSocket 엔드포인트
- 브로드캐스트 매니저 구현
- Live Feed 프론트엔드 컴포넌트

### Step 3: 고급 분석 뷰
- Top Expensive Prompts 페이지
- High-Cost Alert 시스템
- 프로젝트 히트맵

## 검증 방법

1. FTS5 검색 성능 테스트 (1,000+ 레코드에서 < 100ms)
2. WebSocket 연결 안정성 (연결/해제/재연결)
3. 알림 기준값 초과 시 알림 표시 확인
4. 히트맵 시각화 정상 렌더링
