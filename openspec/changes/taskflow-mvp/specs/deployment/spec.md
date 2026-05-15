## ADDED Requirements

### Requirement: 환경 분리 (로컬/운영)
시스템은 DATABASE_URL 환경변수 하나로 로컬 SQLite와 운영 Neon PostgreSQL을 전환해야 한다.

#### Scenario: 로컬 개발 환경
- **WHEN** DATABASE_URL=sqlite:///./taskflow.db 설정 후 uvicorn 실행
- **THEN** 로컬 SQLite 파일에 연결되어 모든 API가 정상 동작한다

#### Scenario: 운영 환경
- **WHEN** DATABASE_URL=postgresql://...neon.tech/... 설정 후 배포
- **THEN** Neon PostgreSQL에 연결되어 모든 API가 정상 동작한다

---

### Requirement: Swagger UI
시스템은 FastAPI의 자동 생성 Swagger UI를 /docs 경로에 제공해야 한다.

#### Scenario: Swagger UI 접근
- **WHEN** GET /docs 요청
- **THEN** 200 OK + Swagger UI HTML 반환 (18개 엔드포인트 문서화)

#### Scenario: OpenAPI JSON
- **WHEN** GET /openapi.json 요청
- **THEN** 200 OK + OpenAPI 3.0 스펙 JSON 반환

---

### Requirement: Vercel 배포
시스템은 GitHub main 브랜치 push 시 Vercel이 FE(정적) + BE(Serverless Functions)를 자동 배포해야 한다.

#### Scenario: 배포 후 API 접근
- **WHEN** git push origin main 후 Vercel 빌드 완료
- **THEN** https://<project>.vercel.app/api/auth/me 가 정상 응답한다

#### Scenario: 배포 후 프론트엔드 접근
- **WHEN** https://<project>.vercel.app/login.html 접근
- **THEN** 로그인 화면이 정상 렌더링된다

---

### Requirement: CORS 설정
시스템은 Vercel 배포 도메인과 로컬 개발(localhost)에서의 CORS 요청을 허용해야 한다.

#### Scenario: 허용된 오리진에서 요청
- **WHEN** https://<project>.vercel.app에서 /api/* 요청
- **THEN** CORS 헤더가 포함된 정상 응답 반환

#### Scenario: 허용되지 않은 오리진
- **WHEN** 허용되지 않은 도메인에서 /api/* 요청
- **THEN** 403 또는 CORS 오류 반환
