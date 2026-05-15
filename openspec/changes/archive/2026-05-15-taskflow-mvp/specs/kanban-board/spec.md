## ADDED Requirements

### Requirement: 태스크 목록 조회
시스템은 팀 멤버에게 태스크 목록을 반환하며 필터(전체/내 태스크/미할당)와 정렬(생성순 desc)을 지원해야 한다.

#### Scenario: 전체 목록 조회
- **WHEN** GET /teams/{id}/tasks 요청 (해당 팀 멤버)
- **THEN** 200 OK + [{ id, title, status, creator_id, assignee_id, created_at }] 반환 (created_at desc 정렬)

#### Scenario: 내 태스크 필터
- **WHEN** GET /teams/{id}/tasks?filter=me 요청
- **THEN** assignee_id = current_user_id인 태스크만 반환

#### Scenario: 미할당 필터
- **WHEN** GET /teams/{id}/tasks?filter=unassigned 요청
- **THEN** assignee_id IS NULL인 태스크만 반환

---

### Requirement: 태스크 생성
시스템은 팀 멤버가 TODO 상태의 태스크를 생성할 수 있어야 한다.

#### Scenario: 정상 생성
- **WHEN** POST /teams/{id}/tasks { title: "DB 마이그레이션", assignee_id: null } 요청
- **THEN** 201 Created + { id, title, status: "TODO", creator_id, assignee_id, created_at } 반환

#### Scenario: 제목 유효성 오류
- **WHEN** POST /teams/{id}/tasks { title: "" } 또는 101자 이상 제목으로 요청
- **THEN** 400 Bad Request + { error: { code: "VALIDATION_ERROR", message: "제목은 1-100자이어야 합니다" } } 반환

---

### Requirement: 태스크 단일 조회
시스템은 팀 멤버에게 특정 태스크의 상세 정보를 반환해야 한다.

#### Scenario: 정상 조회
- **WHEN** GET /tasks/{id} 요청 (해당 팀 멤버)
- **THEN** 200 OK + { id, title, status, creator_id, assignee_id, team_id, created_at } 반환

#### Scenario: 존재하지 않는 태스크
- **WHEN** GET /tasks/{id} 요청 (존재하지 않는 id)
- **THEN** 404 Not Found + { error: { code: "NOT_FOUND", message: "해당 항목을 찾을 수 없습니다" } } 반환

---

### Requirement: 태스크 제목·assignee 수정
시스템은 팀 멤버가 태스크의 제목과 담당자를 수정할 수 있어야 한다.

#### Scenario: 제목 수정
- **WHEN** PUT /tasks/{id} { title: "새 제목" } 요청 (해당 팀 멤버)
- **THEN** 200 OK + 업데이트된 태스크 반환

#### Scenario: Assignee 변경
- **WHEN** PUT /tasks/{id} { assignee_id: 42 } 요청 (해당 팀 멤버)
- **THEN** 200 OK + 업데이트된 태스크 반환

#### Scenario: Assignee NULL 설정 (미할당)
- **WHEN** PUT /tasks/{id} { assignee_id: null } 요청
- **THEN** 200 OK + assignee_id: null 반환

---

### Requirement: 태스크 상태 변경 (드래그)
시스템은 팀 멤버가 태스크 상태를 TODO/DOING/DONE 중 하나로 변경할 수 있어야 한다.

#### Scenario: 정상 상태 변경
- **WHEN** PATCH /tasks/{id}/status { status: "DOING" } 요청 (해당 팀 멤버)
- **THEN** 200 OK + 업데이트된 태스크 반환

#### Scenario: 유효하지 않은 상태값
- **WHEN** PATCH /tasks/{id}/status { status: "IN_PROGRESS" } 요청
- **THEN** 400 Bad Request + { error: { code: "VALIDATION_ERROR", message: "status는 TODO, DOING, DONE 중 하나이어야 합니다" } } 반환

---

### Requirement: 태스크 삭제
시스템은 태스크의 creator 또는 팀 owner만 태스크를 삭제할 수 있어야 한다.

#### Scenario: Creator가 삭제
- **WHEN** DELETE /tasks/{id} 요청 (creator_id = current_user_id)
- **THEN** 204 No Content 반환

#### Scenario: Team owner가 타인 태스크 삭제
- **WHEN** DELETE /tasks/{id} 요청 (team owner, 다른 사람이 만든 태스크)
- **THEN** 204 No Content 반환

#### Scenario: 권한 없는 삭제 시도
- **WHEN** DELETE /tasks/{id} 요청 (creator도 owner도 아닌 멤버)
- **THEN** 403 Forbidden + { error: { code: "FORBIDDEN", message: "권한이 없습니다" } } 반환
