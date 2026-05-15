## ADDED Requirements

### Requirement: Auth API 테스트
시스템은 회원가입, 로그인, 현재 사용자 조회, 로그아웃 엔드포인트에 대한 pytest 테스트를 포함해야 한다.

#### Scenario: 회원가입 정상/에러 케이스 테스트
- **WHEN** pytest tests/test_auth.py 실행
- **THEN** POST /auth/signup 정상(201), 이메일 중복(409), 유효성 오류(400) 케이스가 모두 pass

#### Scenario: 로그인 정상/에러 케이스 테스트
- **WHEN** pytest tests/test_auth.py 실행
- **THEN** POST /auth/login 정상(200+JWT), 잘못된 자격증명(401) 케이스가 모두 pass

#### Scenario: JWT 인증 필요 엔드포인트 테스트
- **WHEN** pytest tests/test_auth.py 실행
- **THEN** 토큰 없이 GET /auth/me 호출 시 401 반환 케이스가 pass

---

### Requirement: Team API 테스트
시스템은 팀 생성, 합류, 멤버 조회 엔드포인트에 대한 pytest 테스트를 포함해야 한다.

#### Scenario: 팀 생성 테스트
- **WHEN** pytest tests/test_teams.py 실행
- **THEN** POST /teams 정상(201+invite_code), 유효성 오류(400) 케이스가 모두 pass

#### Scenario: 초대코드 합류 테스트
- **WHEN** pytest tests/test_teams.py 실행
- **THEN** POST /teams/join 정상(200), 코드 없음(404), 이미 소속(409) 케이스가 모두 pass

#### Scenario: 비멤버 접근 차단 테스트
- **WHEN** pytest tests/test_teams.py 실행
- **THEN** 다른 팀 사용자가 GET /teams/{id} 호출 시 403 반환 케이스가 pass

---

### Requirement: Task API 테스트
시스템은 태스크 CRUD 및 상태 변경 엔드포인트에 대한 pytest 테스트를 포함해야 한다.

#### Scenario: 태스크 생성/조회/수정/삭제 테스트
- **WHEN** pytest tests/test_tasks.py 실행
- **THEN** POST/GET/PUT/DELETE /tasks 정상 흐름 케이스가 모두 pass

#### Scenario: 상태 변경 테스트
- **WHEN** pytest tests/test_tasks.py 실행
- **THEN** PATCH /tasks/{id}/status 정상(200), 유효하지 않은 status(400) 케이스가 pass

#### Scenario: 삭제 권한 테스트
- **WHEN** pytest tests/test_tasks.py 실행
- **THEN** creator 삭제(204), 권한 없는 삭제(403) 케이스가 모두 pass

---

### Requirement: Message API 테스트
시스템은 메시지 전송, 조회(since=), 삭제 엔드포인트에 대한 pytest 테스트를 포함해야 한다.

#### Scenario: 메시지 전송/조회 테스트
- **WHEN** pytest tests/test_messages.py 실행
- **THEN** POST /teams/{id}/messages 정상(201), 1000자 초과(400) 케이스가 pass
- **AND** GET /teams/{id}/messages?since= 증분 조회 케이스가 pass

#### Scenario: 메시지 삭제 권한 테스트
- **WHEN** pytest tests/test_messages.py 실행
- **THEN** 본인 메시지 삭제(204), 타인 메시지 삭제(403) 케이스가 모두 pass

---

### Requirement: 테스트 격리
모든 pytest 테스트는 SQLite in-memory DB를 사용하여 서로 독립적으로 실행되어야 한다.

#### Scenario: 테스트 DB 격리
- **WHEN** pytest 실행
- **THEN** 각 테스트 함수가 독립된 DB 상태에서 실행되고 테스트 간 데이터 오염이 없다

#### Scenario: 전체 테스트 실행
- **WHEN** pytest tests/ 실행
- **THEN** 모든 테스트가 pass이고 운영 DB에 영향이 없다
