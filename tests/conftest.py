import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import Base, get_db
from api.main import app

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def pytest_html_results_table_row(report, cells):
    """테스트 행에 한글 설명(docstring) 추가"""
    if hasattr(report, 'description') and report.description:
        cells.insert(1, f'<td class="col-description">{report.description}</td>')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """테스트 결과에 docstring을 description으로 저장"""
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__ or '').strip().split('\n')[0]


def pytest_html_results_table_header(cells):
    """리포트 테이블 헤더에 '설명' 컬럼 추가"""
    cells.insert(1, '<th class="sortable" data-column-type="description">설명</th>')


@pytest.fixture(autouse=True)
def reset_db():
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    yield
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    res = client.post("/api/auth/signup", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['token']}"}


@pytest.fixture
def team_with_auth(client, registered_user, auth_headers):
    res = client.post("/api/teams", json={"name": "Test Team"}, headers=auth_headers)
    assert res.status_code == 201
    return {"team": res.json(), "user": registered_user, "headers": auth_headers}
