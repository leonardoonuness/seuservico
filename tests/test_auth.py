import pytest


def test_register_and_login(client):
    payload = {
        "name": "João Silva",
        "email": "joao@test.com",
        "password": "senha1234",
        "phone": "99999999999",
        "city": "São Luís",
        "type": "client",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert data["user"]["email"] == "joao@test.com"

    r2 = client.post("/api/v1/auth/login", json={"email": "joao@test.com", "password": "senha1234"})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "name": "Maria", "email": "maria@test.com", "password": "senha1234",
        "phone": "99999999998", "city": "Teresina", "type": "client",
    })
    r = client.post("/api/v1/auth/login", json={"email": "maria@test.com", "password": "errada"})
    assert r.status_code == 401


def test_duplicate_email(client):
    payload = {
        "name": "Pedro", "email": "pedro@test.com", "password": "senha1234",
        "phone": "99999999997", "city": "Fortaleza", "type": "client",
    }
    client.post("/api/v1/auth/register", json=payload)
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


def test_get_me(client):
    client.post("/api/v1/auth/register", json={
        "name": "Ana", "email": "ana@test.com", "password": "senha1234",
        "phone": "99999999996", "city": "Belém", "type": "client",
    })
    login = client.post("/api/v1/auth/login", json={"email": "ana@test.com", "password": "senha1234"})
    token = login.json()["access_token"]
    r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "ana@test.com"


def test_categories_endpoint(client):
    r = client.get("/api/v1/categories")
    assert r.status_code == 200
    data = r.json()
    assert "Manutenção & Reparos" in data
    assert "Eletricista" in data["Manutenção & Reparos"]
