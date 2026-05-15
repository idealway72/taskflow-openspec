## ADDED Requirements

### Requirement: 팀 생성
시스템은 인증된 사용자가 팀을 생성하면 초대코드(AAAA-9999 형식)를 자동 발급하고 생성자를 owner로 지정해야 한다.

#### Scenario: 정상 팀 생성
- **WHEN** POST /teams { name: "Frontiers" } 요청 (인증된 사용자, team_id = null)
- **THEN** 201 Created + { id, name, invite_code: "FRNT-2026", owner_id, created_at } 반환
- **AND** users.team_id가 해당 팀 id로 UPDATE된다

#### Scenario: 팀 이름 유효성 오류
- **WHEN** POST /teams { name: "" } 또는 31자 이상의 이름으로 요청
- **THEN** 400 Bad Request + { error: { code: "VALIDATION_ERROR", message: "팀 이름은 1-30자이어야 합니다" } } 반환

---

### Requirement: 초대코드로 팀 합류
시스템은 유효한 초대코드로 사용자를 팀에 합류시키고 users.team_id를 업데이트해야 한다.

#### Scenario: 정상 합류
- **WHEN** POST /teams/join { invite_code: "FRNT-2026" } 요청 (team_id = null인 사용자)
- **THEN** 200 OK + { team: { id, name, member_count }, redirect: "/teams/<id>" } 반환
- **AND** users.team_id가 해당 팀 id로 UPDATE된다

#### Scenario: 잘못된 초대코드 형식
- **WHEN** POST /teams/join { invite_code: "abcd1234" } 요청 (소문자 또는 하이픈 없음)
- **THEN** 400 Bad Request + { error: { code: "VALIDATION_ERROR", message: "초대코드 형식이 올바르지 않습니다" } } 반환

#### Scenario: 존재하지 않는 초대코드
- **WHEN** POST /teams/join { invite_code: "XXXX-9999" } 요청 (DB에 없는 코드)
- **THEN** 404 Not Found + { error: { code: "NOT_FOUND", message: "해당 초대코드를 찾을 수 없습니다" } } 반환

#### Scenario: 이미 팀 소속인 사용자
- **WHEN** POST /teams/join 요청 (team_id != null인 사용자)
- **THEN** 409 Conflict + { error: { code: "ALREADY_IN_TEAM", message: "이미 다른 팀에 소속되어 있습니다" } } 반환

---

### Requirement: 팀 정보 조회
시스템은 팀 멤버에게 팀 정보를 반환해야 한다.

#### Scenario: 정상 조회
- **WHEN** GET /teams/{id} 요청 (해당 팀 멤버)
- **THEN** 200 OK + { id, name, invite_code, owner_id, member_count, created_at } 반환

#### Scenario: 비멤버 접근
- **WHEN** GET /teams/{id} 요청 (다른 팀 소속 또는 미가입 사용자)
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN", message: "이 팀의 멤버가 아닙니다" } } 반환

---

### Requirement: 팀 멤버 목록
시스템은 팀 멤버에게 모든 멤버 목록(owner 표시 포함)을 반환해야 한다.

#### Scenario: 멤버 목록 조회
- **WHEN** GET /teams/{id}/members 요청 (해당 팀 멤버)
- **THEN** 200 OK + [{ id, email, is_owner: bool, joined_at }] 반환

---

### Requirement: 팀 떠나기 (API)
시스템은 팀 멤버가 자신의 팀을 떠날 수 있도록 users.team_id를 NULL로 설정해야 한다. (UI 플로우는 범위 외)

#### Scenario: 정상 탈퇴
- **WHEN** DELETE /teams/{id}/leave 요청 (해당 팀 멤버, owner가 아닌 경우)
- **THEN** 200 OK + {} 반환
- **AND** users.team_id가 NULL로 UPDATE된다

#### Scenario: Owner의 팀 떠나기 시도
- **WHEN** DELETE /teams/{id}/leave 요청 (팀 owner)
- **THEN** 400 Bad Request + { error: { code: "OWNER_CANNOT_LEAVE", message: "팀 owner는 팀을 떠날 수 없습니다" } } 반환
