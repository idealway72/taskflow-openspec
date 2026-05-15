## Why

소규모 팀(3-5인)이 태스크 진행 상황과 의사결정을 한 화면에서 추적할 수 없어 도구 분산과 컨텍스트 손실이 발생한다. TaskFlow MVP는 칸반 + 실시간 채팅을 단일 화면에 통합하여 이 문제를 해결한다.

## What Changes

- 이메일/비밀번호 기반 회원가입·로그인, JWT 인증(24h) 신규 구현
- 초대코드(XXXX-9999) 기반 팀 생성·합류 시스템 신규 구현
- TODO/DOING/DONE 3컬럼 칸반 보드(드래그 앤 드롭, assignee) 신규 구현
- 팀 단위 채팅(5초 폴링, since= 증분 조회) 신규 구현
- FastAPI 백엔드(Vercel Serverless) + Vanilla JS 프론트(MPA) 신규 구현
- Vercel + Neon(PostgreSQL) 자동 배포 파이프라인 신규 구현
- FastAPI Swagger UI(/docs) 활성화
- pytest 기반 API 테스트 코드 신규 구현

## Capabilities

### New Capabilities

- `user-auth`: 회원가입, 로그인, JWT 발급·검증, bcrypt 비밀번호 해시, 로그아웃(stateless)
- `team-management`: 팀 생성(초대코드 자동 발급), 초대코드 합류, 멤버 목록, 팀 떠나기(API만)
- `kanban-board`: TODO/DOING/DONE 3컬럼, 카드 생성·수정·삭제, 드래그 상태 변경, assignee 필터
- `team-chat`: 팀 단위 메시지 송수신, 5초 폴링(since= 증분), 1000자 제한, 본인 메시지 삭제
- `deployment`: 로컬 SQLite ↔ 운영 Neon 환경 분리, Vercel 배포, Swagger UI
- `api-tests`: Auth·Team·Task·Chat 엔드포인트 pytest 테스트

### Modified Capabilities

(없음 — 신규 프로젝트)

## Impact

**Backend (FastAPI)**
- `api/` — Auth 4 + Team 5 + Task 6 + Chat 3 = 18 엔드포인트
- `api/models.py` — users, teams, tasks, messages 4테이블 (SQLAlchemy)
- `api/auth.py` — JWT 미들웨어, bcrypt
- `api/database.py` — DATABASE_URL 환경변수로 SQLite/Neon 전환

**Frontend (Vanilla JS + Tailwind CDN)**
- `frontend/` — login.html, signup.html, team.html, kanban.html, chat.html (MPA)
- `frontend/js/` — api.js(fetch wrapper + 401 intercept), auth.js, kanban.js, chat.js

**Database**
- users(id, email, password_hash, team_id, created_at)
- teams(id, name, invite_code, owner_id, created_at)
- tasks(id, team_id, title, status, creator_id, assignee_id, created_at)
- messages(id, team_id, user_id, content, created_at)

**Out of Scope**
- WebSocket(폴링으로 대체), 파일 첨부, 전문검색, 다국어, 알림, 초대코드 재발급, 팀 전환 UI
