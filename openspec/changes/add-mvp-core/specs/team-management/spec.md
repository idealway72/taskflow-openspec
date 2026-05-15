## ADDED Requirements

### Requirement: 초대코드 재발급 UI
칸반 멤버 패널에서 팀 owner는 초대코드를 재발급하고 복사할 수 있어야 한다.

#### Scenario: owner에게 재발급 버튼 표시
- **WHEN** 팀 owner가 칸반의 멤버 패널을 열었을 때
- **THEN** 현재 초대코드와 "재발급" 버튼이 패널 하단에 표시된다

#### Scenario: owner가 재발급 실행
- **WHEN** owner가 "재발급" 버튼을 클릭하고 확인 모달에서 확인
- **THEN** POST /teams/{id}/invite-code 호출 후 새 코드가 패널에 즉시 표시된다
- **AND** 복사 버튼으로 새 코드를 클립보드에 복사할 수 있다

#### Scenario: 일반 멤버에게 버튼 미표시
- **WHEN** 일반 member가 칸반의 멤버 패널을 열었을 때
- **THEN** 초대코드 재발급 버튼이 표시되지 않는다
