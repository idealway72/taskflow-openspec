## Context

현재 `teams.invite_code`는 팀 생성 시 한 번만 발급되며 변경 수단이 없다. MVP 스펙에서 "재발급은 Day 2 범위 외"로 명시됐으나, 코드 유출 시 팀 보안을 유지할 방법이 필요하다.

## Goals / Non-Goals

**Goals:**
- owner가 새 초대코드를 발급하고 기존 코드를 무효화
- 새 코드를 즉시 UI에서 복사 가능하게 표시
- 비owner의 재발급 시도는 403으로 차단

**Non-Goals:**
- 코드 만료 시간(TTL) 설정 — 단순성 유지
- 재발급 이력 기록 — MVP 범위 외
- 기존 멤버 강제 퇴장 — 재발급은 새 합류만 차단

## Decisions

### Decision 1: PATCH vs POST
**선택**: `POST /teams/{id}/invite-code`
**이유**: 새 리소스(코드)를 생성하는 행위이므로 POST가 의미상 정확. PATCH는 부분 수정을 의미하므로 부적합.

### Decision 2: 재발급 시 기존 멤버 영향 없음
**선택**: 기존 team_id가 있는 멤버는 그대로 유지. 코드만 변경.
**이유**: 재발급 목적은 새 합류 차단이지 기존 멤버 퇴장이 아님.

### Decision 3: UI — 멤버 패널에 통합
**선택**: 칸반의 멤버 사이드패널 하단에 owner에게만 "초대코드 재발급" 버튼 표시
**이유**: 별도 페이지 불필요. 멤버 관리 컨텍스트와 자연스럽게 연결됨.

## Risks / Trade-offs

- [재발급 직후 공유 중이던 코드 무효화] → 재발급 전 확인 모달로 완화
- [동시 재발급 경쟁 조건] → 단일 UPDATE 트랜잭션으로 처리, 영향 없음

## Migration Plan

1. `api/routers/teams.py`에 엔드포인트 추가
2. `frontend/js/kanban.js` 멤버 패널에 버튼 추가
3. 배포 후 `/docs`에서 새 엔드포인트 확인

## Open Questions

(없음)
