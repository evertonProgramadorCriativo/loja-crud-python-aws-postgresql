import os

# Usa um SQLite temporário: os testes NÃO mexem no banco da AWS.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "chave-de-teste-com-32-caracteres-ok"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Cart, CartItem, User  # noqa: E402

client = TestClient(app)


# O SQLite não confere chaves estrangeiras por padrão (o PostgreSQL confere).
# Ligamos aqui para o teste se comportar como o banco de verdade.
@event.listens_for(engine, "connect")
def _ligar_chaves_estrangeiras(dbapi_conn, _record):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")


USER = {"name": "Ana", "email": "ana@email.com", "password": "123456"}
MOUSE = {"name": "Mouse Gamer", "description": "RGB", "price": "49.90", "stock": 10}


@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def auth():
    client.post("/auth/register", json=USER)
    r = client.post("/auth/login", data={"username": USER["email"], "password": USER["password"]})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_criar_produto_exige_login():
    assert client.post("/products", json=MOUSE).status_code == 401


def test_criar_e_buscar_produto(auth):
    r = client.post("/products", json=MOUSE, headers=auth)
    assert r.status_code == 201
    pid = r.json()["id"]
    r = client.get(f"/products/{pid}")  # leitura é pública
    assert r.status_code == 200
    assert r.json()["name"] == "Mouse Gamer"
    assert float(r.json()["price"]) == 49.90


def test_listar_com_busca_e_paginacao(auth):
    for nome in ["Mouse", "Teclado", "Monitor"]:
        client.post("/products", json={**MOUSE, "name": nome}, headers=auth)
    assert len(client.get("/products").json()) == 3
    assert [p["name"] for p in client.get("/products?q=tecl").json()] == ["Teclado"]
    assert len(client.get("/products?limit=2").json()) == 2
    assert len(client.get("/products?skip=2").json()) == 1


def test_atualizar_parcialmente(auth):
    pid = client.post("/products", json=MOUSE, headers=auth).json()["id"]
    r = client.patch(f"/products/{pid}", json={"stock": 3}, headers=auth)
    assert r.status_code == 200
    assert r.json()["stock"] == 3
    assert r.json()["name"] == "Mouse Gamer"  # o resto não mudou


def test_apagar_produto(auth):
    pid = client.post("/products", json=MOUSE, headers=auth).json()["id"]
    assert client.delete(f"/products/{pid}", headers=auth).status_code == 204
    assert client.get(f"/products/{pid}").status_code == 404


def test_produto_inexistente_404(auth):
    assert client.get("/products/999").status_code == 404
    assert client.patch("/products/999", json={"stock": 1}, headers=auth).status_code == 404
    assert client.delete("/products/999", headers=auth).status_code == 404


@pytest.mark.parametrize(
    "dados", [{"price": "0"}, {"price": "-5"}, {"stock": -1}, {"name": "x"}, {"price": "1.999"}]
)
def test_validacoes(auth, dados):
    r = client.post("/products", json={**MOUSE, **dados}, headers=auth)
    assert r.status_code == 422


def test_nao_apaga_produto_que_esta_em_carrinho(auth):
    pid = client.post("/products", json=MOUSE, headers=auth).json()["id"]
    with SessionLocal() as db:
        cart = db.query(User).first().cart
        db.add(CartItem(cart_id=cart.id, product_id=pid, quantity=1))
        db.commit()
    assert client.delete(f"/products/{pid}", headers=auth).status_code == 409
    assert client.get(f"/products/{pid}").status_code == 200
