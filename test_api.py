import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from redis_client import get_redis

# 1. In-Memory Isolated SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tables create karein
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Redis Mock (In-Memory Dummy Dictionary taaki test ke waqt Redis call na fate)
class DummyRedis:
    def __init__(self):
        self.store = {}
    def get(self, key):
        return self.store.get(key)
    def setex(self, key, time, value):
        self.store[key] = value
    def keys(self, pattern):
        return list(self.store.keys())
    def delete(self, *keys):
        for k in keys:
            self.store.pop(k, None)

dummy_redis = DummyRedis()
def override_get_redis():
    return dummy_redis

# Dependency Overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis] = override_get_redis

# Disable rate limiter for testing
app.state.limiter.enabled = False

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Candidate Management API"}

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_and_login():
    test_email = "new_unit_test_user@example.com"
    test_password = "password123"

    # Register
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": test_email, "password": test_password}
    )
    assert reg_res.status_code == 201, f"Register failed: {reg_res.text}"

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": test_email, "password": test_password}
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    assert "access_token" in login_res.json()

def test_full_candidate_workflow():
    test_email = "workflow_isolated@example.com"
    test_password = "password123"

    # Register & Login
    reg = client.post("/api/v1/auth/register", json={"email": test_email, "password": test_password})
    assert reg.status_code == 201, f"Workflow register failed: {reg.text}"

    login = client.post("/api/v1/auth/login", data={"username": test_email, "password": test_password})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Candidate
    post_res = client.post(
        "/api/v1/candidates",
        json={"name": "Aman", "skill": "FastAPI", "experience": 2},
        headers=headers
    )
    assert post_res.status_code == 201
    candidate_id = post_res.json()["id"]

    # 2. Get Candidates
    get_res = client.get("/api/v1/candidates?search=FastAPI")
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1

    # 3. Delete Candidate
    del_res = client.delete(f"/api/v1/candidates/{candidate_id}", headers=headers)
    assert del_res.status_code == 200