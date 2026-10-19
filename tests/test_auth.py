import os

# Usa um SQLite temporário: os testes NÃO mexem no banco da AWS.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "chave-de-teste"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)
USER = {"name": "Ana", "email": "ana@email.com", "password": "123456"}


@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


def test_register_ok():
    r = client.post("/auth/register", json=USER)
    assert r.status_code == 201
    assert r.json()["email"] == USER["email"]
    assert "password" not in r.json() and "password_hash" not in r.json()


def test_register_email_duplicado():
    client.post("/auth/register", json=USER)
    assert client.post("/auth/register", json=USER).status_code == 400


def test_login_e_me():
    client.post("/auth/register", json=USER)
    r = client.post("/auth/login", data={"username": USER["email"], "password": USER["password"]})
    assert r.status_code == 200
    token = r.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200 and me.json()["name"] == "Ana"


def test_login_senha_errada():
    client.post("/auth/register", json=USER)
    r = client.post("/auth/login", data={"username": USER["email"], "password": "errada"})
    assert r.status_code == 401


def test_me_sem_token():
    assert client.get("/auth/me").status_code == 401
