from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# Käyttäjän rekisteröinti
def test_register_user():
    response = client.post(
        "/register",
        json={
            "fname": "Testi01",
            "lname": "Käyttäjä01",
            "email": "test01@example.com",
            "password": "string",
        },
    )
    assert response.status_code == 200
    assert "email" in response.json()


def test_register_user_with_existing_email():
    client.post(
        "/register",
        json={  # ensimmäinen rekisteröinti
            "fname": "Testi02",
            "lname": "Käyttäjä02",
            "email": "test02@example.com",
            "password": "string",
        },
    )
    response = client.post(
        "/register",
        json={  # toinen rekisteröinti samalla sähköpostilla
            "fname": "Testi02",
            "lname": "Käyttäjä02",
            "email": "test02@example.com",
            "password": "string",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


# Käyttäjän kirjautuminen
def test_login_with_valid_credentials():
    client.post(
        "/register",
        json={  # rekisteröi käyttäjä ennen kirjautumista
            "fname": "Testi3",
            "lname": "Käyttäjä3",
            "email": "test3@example.com",
            "password": "string",
        },
    )
    response = client.post(
        "/token",
        data={"username": "test3@example.com", "password": "string"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_with_invalid_credentials():
    response = client.post(
        "/token",
        data={"username": "wrong@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


# Tiketin luonti
def test_submit_ticket():
    response = client.post(
        "/ticket",
        json={
            "issue_description": "Test ticket",
            "email": "test@example.com",
        },
    )
    assert response.status_code == 200
    assert "Thank you!" in response.json()["response"]


# Chatbotin vastaus
def test_chatbot_response():
    response = client.post(
        "/chat",
        json={
            "message": "hello",
        },
    )
    assert response.status_code == 200
    assert "response" in response.json()

# Chatbot ei osaa vastata
def test_chatbot_unknown_input():
    response = client.post(
        "/chat",
        json={
            "message": "blablagibberish",
        },
    )
    assert response.status_code == 200
    assert "contact request" in response.json()["response"]
