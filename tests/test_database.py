import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from server import app

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def _signup(email="user@example.com", password="testpass123", name="Test User"):
    return client.post("/auth/signup", json={"name": name, "email": email, "password": password})


def _get_token(email="user@example.com", password="testpass123", name="Test User"):
    resp = _signup(email=email, password=password, name=name)
    return resp.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_signup_success():
    resp = _signup()
    assert resp.status_code == 201
    assert "access_token" in resp.json()


def test_signup_duplicate_email():
    _signup()
    resp = _signup()
    assert resp.status_code == 400


def test_login_success():
    _signup()
    resp = client.post("/auth/login", json={"email": "user@example.com", "password": "testpass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password():
    _signup()
    resp = client.post("/auth/login", json={"email": "user@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_get_me_authenticated():
    token = _get_token()
    resp = client.get("/auth/me", headers=_auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@example.com"


def test_get_me_unauthenticated():
    resp = client.get("/auth/me")
    assert resp.status_code == 403


def test_create_bike():
    token = _get_token()
    resp = client.post(
        "/bikes",
        json={"name": "My Bike", "brand": "Trek", "model": "Slash", "year": 2023},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Bike"
    assert data["brand"] == "Trek"


def test_list_bikes():
    token = _get_token()
    headers = _auth_headers(token)
    client.post("/bikes", json={"name": "Bike One"}, headers=headers)
    client.post("/bikes", json={"name": "Bike Two"}, headers=headers)
    resp = client.get("/bikes", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_bike():
    token = _get_token()
    headers = _auth_headers(token)
    create_resp = client.post("/bikes", json={"name": "Old Name"}, headers=headers)
    bike_id = create_resp.json()["id"]
    resp = client.put(f"/bikes/{bike_id}", json={"name": "New Name"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_delete_bike():
    token = _get_token()
    headers = _auth_headers(token)
    create_resp = client.post("/bikes", json={"name": "To Delete"}, headers=headers)
    bike_id = create_resp.json()["id"]
    del_resp = client.delete(f"/bikes/{bike_id}", headers=headers)
    assert del_resp.status_code == 204
    list_resp = client.get("/bikes", headers=headers)
    assert list_resp.json() == []


def test_cannot_access_other_users_bike():
    token1 = _get_token(email="user1@example.com", name="User One")
    token2 = _get_token(email="user2@example.com", name="User Two")
    create_resp = client.post("/bikes", json={"name": "User1 Bike"}, headers=_auth_headers(token1))
    bike_id = create_resp.json()["id"]
    resp = client.get(f"/bikes/{bike_id}", headers=_auth_headers(token2))
    assert resp.status_code in (403, 404)


def test_create_trail():
    token = _get_token()
    resp = client.post(
        "/trails",
        json={"name": "Epic Trail", "location": "Mountains", "rating": 4.5},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Epic Trail"
    assert data["location"] == "Mountains"


def test_list_trails():
    token = _get_token()
    headers = _auth_headers(token)
    client.post("/trails", json={"name": "Trail A"}, headers=headers)
    client.post("/trails", json={"name": "Trail B"}, headers=headers)
    client.post("/trails", json={"name": "Trail C"}, headers=headers)
    resp = client.get("/trails", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_save_conversation():
    token = _get_token()
    messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]
    resp = client.post(
        "/conversations",
        json={"messages": messages},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["messages"] == messages


def test_list_conversations():
    token = _get_token()
    headers = _auth_headers(token)
    client.post("/conversations", json={"messages": [{"role": "user", "content": "msg1"}]}, headers=headers)
    client.post("/conversations", json={"messages": [{"role": "user", "content": "msg2"}]}, headers=headers)
    resp = client.get("/conversations", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
