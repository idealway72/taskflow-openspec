## ADDED Requirements

### Requirement: 메시지 목록 조회 (폴링)
시스템은 팀 멤버에게 메시지 목록을 반환하며 since= 파라미터로 증분 조회를 지원해야 한다.

#### Scenario: 초기 조회 (전체)
- **WHEN** GET /teams/{id}/messages 요청 (since 파라미터 없음)
- **THEN** 200 OK + 최근 50개 메시지 [{ id, user_id, user_email, content, created_at }] 반환 (created_at asc)

#### Scenario: 증분 조회 (since=)
- **WHEN** GET /teams/{id}/messages?since=2026-05-13T14:27:00Z 요청
- **THEN** 200 OK + created_at > since인 메시지만 반환 (빈 배열 가능)

#### Scenario: 메시지 없음
- **WHEN** GET /teams/{id}/messages 요청 (메시지 0건 팀)
- **THEN** 200 OK + [] 반환

---

### Requirement: 메시지 전송
시스템은 팀 멤버가 1-1000자 텍스트 메시지를 전송할 수 있어야 한다.

#### Scenario: 정상 전송
- **WHEN** POST /teams/{id}/messages { content: "안녕하세요" } 요청 (해당 팀 멤버)
- **THEN** 201 Created + { id, user_id, user_email, content, created_at } 반환

#### Scenario: 1000자 초과
- **WHEN** POST /teams/{id}/messages { content: "<1001자 문자열>" } 요청
- **THEN** 400 Bad Request + { error: { code: "TOO_LONG", message: "메시지는 1000자 이내로 입력하세요", limit: 1000, actual: 1001 } } 반환

#### Scenario: 빈 메시지
- **WHEN** POST /teams/{id}/messages { content: "" } 요청
- **THEN** 400 Bad Request + { error: { code: "VALIDATION_ERROR", message: "메시지를 입력해주세요" } } 반환

---

### Requirement: 메시지 삭제
시스템은 메시지 작성자 본인만 자신의 메시지를 삭제할 수 있어야 한다. Owner도 타인 메시지를 삭제할 수 없다.

#### Scenario: 본인 메시지 삭제
- **WHEN** DELETE /messages/{id} 요청 (user_id = current_user_id)
- **THEN** 204 No Content 반환

#### Scenario: 타인 메시지 삭제 시도
- **WHEN** DELETE /messages/{id} 요청 (user_id != current_user_id, owner 포함)
- **THEN** 403 Forbidden + { error: { code: "NOT_OWNER", message: "본인의 메시지만 삭제할 수 있습니다" } } 반환

#### Scenario: 존재하지 않는 메시지 삭제
- **WHEN** DELETE /messages/{id} 요청 (존재하지 않는 id)
- **THEN** 404 Not Found + { error: { code: "NOT_FOUND", message: "해당 항목을 찾을 수 없습니다" } } 반환

---

### Requirement: 채팅 폴링 클라이언트
클라이언트는 5초마다 새 메시지를 폴링하고 마지막 메시지의 created_at을 since= 파라미터로 전달해야 한다.

#### Scenario: 폴링 사이클
- **WHEN** 채팅 화면 진입
- **THEN** 즉시 GET /teams/{id}/messages 호출 후 5초 간격 setInterval로 반복 호출
- **AND** 이전 응답의 마지막 메시지 created_at을 since= 파라미터로 전달

#### Scenario: 폴링 중 네트워크 오류
- **WHEN** GET /teams/{id}/messages 요청 실패 (네트워크 오류)
- **THEN** "연결 끊김" 상태 표시 후 다음 인터벌에 재시도
- **AND** 재연결 시 since= 파라미터로 누락 메시지 일괄 수신
