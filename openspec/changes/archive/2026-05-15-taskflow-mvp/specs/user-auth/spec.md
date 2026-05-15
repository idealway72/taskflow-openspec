## ADDED Requirements

### Requirement: 회원가입
시스템은 이메일 + 비밀번호(8자 이상)로 신규 계정을 생성하고 JWT를 즉시 발급해야 한다.

#### Scenario: 정상 회원가입
- **WHEN** POST /auth/signup { email: "user@example.com", password: "12345678" } 요청
- **THEN** 201 Created + { token: "<JWT>", user: { id, email, team_id: null } } 반환
- **AND** 비밀번호는 bcrypt 해시로 저장되고 평문은 보관하지 않는다

#### Scenario: 이메일 중복
- **WHEN** 이미 가입된 이메일로 POST /auth/signup 요청
- **THEN** 409 Conflict + { error: { code: "EMAIL_TAKEN", message: "이미 가입된 이메일입니다" } } 반환

#### Scenario: 이메일 형식 오류
- **WHEN** 유효하지 않은 이메일 형식으로 POST /auth/signup 요청
- **THEN** 400 Bad Request + { error: { code: "VALIDATION_ERROR", message: "올바른 이메일 형식이 아닙니다" } } 반환

#### Scenario: 비밀번호 8자 미만
- **WHEN** 비밀번호가 7자 이하인 POST /auth/signup 요청
- **THEN** 400 Bad Request + { error: { code: "VALIDATION_ERROR", message: "비밀번호는 8자 이상이어야 합니다" } } 반환

---

### Requirement: 로그인
시스템은 이메일 + 비밀번호 검증 후 JWT(24시간 유효)를 발급해야 한다.

#### Scenario: 정상 로그인
- **WHEN** POST /auth/login { email, password } 요청 (올바른 자격증명)
- **THEN** 200 OK + { token: "<JWT exp 24h>", user: { id, email, team_id } } 반환
- **AND** 클라이언트는 token을 localStorage에 저장하고 team_id가 null이면 팀 선택 화면으로, 값이 있으면 칸반 화면으로 이동한다

#### Scenario: 자격증명 오류
- **WHEN** 존재하지 않는 이메일 또는 틀린 비밀번호로 POST /auth/login 요청
- **THEN** 401 Unauthorized + { error: { code: "INVALID_CREDENTIALS", message: "이메일 또는 비밀번호가 일치하지 않습니다" } } 반환
- **AND** 이메일 존재 여부를 응답에서 구분할 수 없어야 한다

---

### Requirement: 현재 사용자 조회
시스템은 유효한 JWT로 현재 로그인된 사용자 정보를 반환해야 한다.

#### Scenario: 정상 조회
- **WHEN** GET /auth/me 요청 (Authorization: Bearer <valid JWT>)
- **THEN** 200 OK + { id, email, team_id } 반환

#### Scenario: JWT 만료
- **WHEN** GET /auth/me 요청 (만료된 JWT)
- **THEN** 401 Unauthorized + { error: { code: "TOKEN_EXPIRED", message: "인증이 만료되었습니다" } } 반환

---

### Requirement: 로그아웃 (Stateless)
시스템은 로그아웃 요청에 200을 반환하며 서버에 블랙리스트를 유지하지 않는다.

#### Scenario: 로그아웃
- **WHEN** POST /auth/logout 요청 (Authorization: Bearer <JWT>)
- **THEN** 200 OK + {} 반환
- **AND** 클라이언트는 localStorage에서 token을 삭제하고 /login.html로 이동한다

---

### Requirement: JWT 미들웨어
/auth/* 외의 모든 엔드포인트는 유효한 JWT가 필요하다.

#### Scenario: 인증 없이 보호된 엔드포인트 접근
- **WHEN** Authorization 헤더 없이 GET /teams 요청
- **THEN** 401 Unauthorized + { error: { code: "TOKEN_EXPIRED", message: "인증이 만료되었습니다" } } 반환
