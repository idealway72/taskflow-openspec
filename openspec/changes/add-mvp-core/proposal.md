## Why

초대코드가 유출되거나 팀 멤버를 교체해야 할 때 기존 코드를 무효화할 방법이 없다. 팀 owner가 언제든지 새 초대코드를 발급할 수 있어야 한다.

## What Changes

- `POST /teams/{id}/invite-code` 엔드포인트 추가 — owner 전용 초대코드 재발급
- 기존 코드는 즉시 무효화되고 새 코드(AAAA-9999 형식)로 교체됨
- 칸반 멤버 패널에 "초대코드 재발급" 버튼 추가 (owner에게만 표시)

## Capabilities

### New Capabilities

- `invite-code-regenerate`: 팀 owner가 초대코드를 재발급하는 기능. 기존 코드 무효화 + 새 코드 발급 + UI 표시

### Modified Capabilities

- `team-management`: `POST /teams/{id}/invite-code` 엔드포인트 추가 (새 요구사항)

## Impact

**Backend**
- `api/routers/teams.py` — `POST /teams/{id}/invite-code` 라우트 추가
- 권한 검증: owner만 재발급 가능, 비owner → 403

**Frontend**
- `frontend/kanban.html` + `frontend/js/kanban.js` — 멤버 패널에 재발급 버튼/복사 기능 추가
