import pytest
from fastapi import status

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newuser123",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_register_duplicate_username(client, normal_user):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user",
            "email": "another@example.com",
            "password": "user1234",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already registered"

def test_register_duplicate_email(client, normal_user):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "anotheruser",
            "email": "user@example.com",
            "password": "user1234",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client, normal_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "user1234"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, normal_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent", "password": "password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, user_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "user"

def test_get_current_user_no_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
