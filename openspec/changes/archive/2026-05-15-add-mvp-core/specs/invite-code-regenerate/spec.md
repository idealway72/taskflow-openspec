## ADDED Requirements

### Requirement: 초대코드 재발급
팀 owner는 기존 초대코드를 무효화하고 새 초대코드(AAAA-9999 형식)를 발급받을 수 있어야 한다.

#### Scenario: owner가 재발급 성공
- **WHEN** POST /teams/{id}/invite-code 요청 (팀 owner)
- **THEN** 200 OK + { invite_code: "XXXX-9999" } 반환
- **AND** teams.invite_code가 새 코드로 UPDATE된다
- **AND** 기존 코드로는 더 이상 팀에 합류할 수 없다

#### Scenario: 비owner가 재발급 시도
- **WHEN** POST /teams/{id}/invite-code 요청 (일반 member)
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN", message: "팀 owner만 초대코드를 재발급할 수 있습니다" } } 반환

#### Scenario: 비멤버가 재발급 시도
- **WHEN** POST /teams/{id}/invite-code 요청 (다른 팀 소속 또는 미가입)
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN", message: "이 팀의 멤버가 아닙니다" } } 반환

#### Scenario: 재발급 후 기존 멤버 유지
- **WHEN** 초대코드 재발급 성공
- **THEN** 기존 team_id를 가진 멤버들은 팀에 그대로 소속된 상태를 유지한다
