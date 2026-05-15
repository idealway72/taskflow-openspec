## Context

신규 프로젝트. 기존 코드베이스 없음. 두 PDF(프로그램정의 + 스토리보드 v2)에서 도출된 8개 결정사항이 설계 기준이 된다.

**핵심 제약:**
- Day 2 완성 목표 — 복잡도 최소화 우선
- DB 4테이블 고정, API 18개 고정
- 로컬(SQLite) ↔ 운영(Neon) 환경 분리는 DATABASE_URL 하나로 처리
- Vercel Free 티어 한도 내 운영

## Goals / Non-Goals

**Goals:**
- FastAPI 18개 API 구현 + Swagger UI(/docs)
- JWT 인증 미들웨어 (24h, stateless logout)
- SQLAlchemy로 SQLite/PostgreSQL 양쪽 호환
- Vanilla JS MPA 5개 화면 (반응형 768px breakpoint)
- pytest 테스트 (Auth/Team/Task/Chat 정상 흐름 + 주요 에러 케이스)
- Vercel 배포 (FE 정적 + BE Serverless Functions)

**Non-Goals:**
- WebSocket, 파일 첨부, 전문검색, 알림, 다국어
- JWT refresh token, 초대코드 재발급, 팀 전환 UI
- 자동 E2E 테스트, CI/CD 파이프라인, 모니터링

## Decisions

### Decision 1: MPA (Multi-Page Application)
**선택**: HTML 파일 분리 (login.html, signup.html, team.html, kanban.html, chat.html)
**이유**: Vanilla JS + SPA는 클라이언트 라우터 구현 비용이 높음. MPA는 각 페이지가 독립적이어서 디버깅이 단순하고 Vercel 정적 배포와 자연스럽게 호환됨.
**대안**: Hash-based SPA → JWT 체크 로직 중복 없지만 라우팅 복잡도 증가.

### Decision 2: SQLAlchemy + DATABASE_URL 환경변수
**선택**: `DATABASE_URL=sqlite:///./taskflow.db` (로컬) / `DATABASE_URL=postgres://...` (운영)
**이유**: SQLAlchemy가 두 DB를 동일 ORM 코드로 처리. 환경변수 하나로 전환 가능.
**대안**: Tortoise ORM → async 지원 좋지만 SQLite 호환성 제약 있음.

### Decision 3: PATCH /tasks/{id}/status 분리 (결정 #3)
**선택**: 드래그 상태 변경은 `PATCH /tasks/{id}/status`, 제목/assignee 수정은 `PUT /tasks/{id}`
**이유**: 드래그 이벤트는 status만 변경하므로 부분 업데이트가 의미상 정확. PUT으로 매번 전체 필드를 보내면 race condition 위험.

### Decision 4: 1인 1팀 (결정 #1)
**선택**: `users.team_id` FK (nullable). 가입 시 NULL, 팀 생성/합류 시 UPDATE.
**이유**: DB 4테이블 제약 내에서 멤버십을 표현하는 가장 단순한 방법. 중간 테이블(user_teams) 불필요.
**트레이드오프**: 멀티팀 소속 불가 — MVP 범위 내에서는 의도된 제약.

### Decision 5: assignee_id nullable (결정 #4)
**선택**: `tasks.assignee_id` FK → users (nullable). '내 태스크' = `WHERE assignee_id = current_user_id`.
**이유**: creator_id(만든 사람)와 assignee_id(담당자)는 다른 개념. 미할당 카드는 NULL로 표현.

### Decision 6: Vanilla JS fetch wrapper + 401 전역 처리
**선택**: `api.js`에서 모든 fetch 요청을 래핑. 401 응답 시 localStorage 삭제 후 `/login.html` redirect.
**이유**: 각 페이지마다 401 처리를 반복하지 않음. 인터셉터 패턴과 동일.

### Decision 7: Tailwind Play CDN
**선택**: `<script src="https://cdn.tailwindcss.com"></script>` CDN 방식
**이유**: npm 빌드 설정 없이 즉시 사용 가능. Day 2 범위에서 빌드 복잡도 제거.
**트레이드오프**: 프로덕션에서 미사용 CSS purge 불가 → MVP 성능 영향 미미.

### Decision 8: pytest + httpx (TestClient)
**선택**: FastAPI 내장 `TestClient(httpx)` + pytest. SQLite in-memory DB로 격리.
**이유**: 별도 서버 없이 API 테스트 가능. `DATABASE_URL=sqlite:///:memory:` 오버라이드로 테스트 격리.

### Decision 9: Vercel Serverless Functions (FastAPI)
**선택**: `api/index.py`에 FastAPI app 진입점. `vercel.json`의 `routes`로 `/api/*` 매핑.
**이유**: Vercel Python runtime이 ASGI 지원. 별도 서버 설정 없이 배포 가능.

## Risks / Trade-offs

- **SQLite → PostgreSQL 타입 차이**: `AUTOINCREMENT` vs `SERIAL`, boolean 표현 등 → SQLAlchemy가 추상화하므로 위험 낮음. 배포 전 Neon에서 실제 실행 확인 필요.
- **Vercel Cold Start**: Serverless Function 첫 요청 지연 → MVP 범위에서 허용.
- **5초 폴링 부하**: 동시 사용자 50명 × 폴링 2종(칸반/채팅) = 분당 ~1,200 req → Neon Free 티어 내 허용.
- **JWT localStorage 저장**: XSS 취약점 가능성 → MVP 범위에서 허용(httpOnly cookie는 범위 외).
- **pytest 커버리지 한계**: 수동 검증이 필요한 드래그 UI, 모바일 반응형은 자동 테스트 불가.

## Migration Plan

1. `git init` + GitHub 리포 연결
2. 로컬: `pip install -r requirements.txt` → `uvicorn api.main:app --reload`
3. 로컬 테스트: `pytest tests/`
4. Vercel 프로젝트 연결 + Neon DB 프로비저닝
5. `vercel env add DATABASE_URL` (Neon 연결 문자열)
6. `vercel deploy` → `/docs` 접근 확인

## Open Questions

- (없음 — 모든 설계 결정은 스토리보드 v2 기준으로 확정됨)
