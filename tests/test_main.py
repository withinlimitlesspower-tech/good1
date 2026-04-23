import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/auth/register" in schema["paths"]
    assert "/api/auth/login" in schema["paths"]
    assert "/api/books/" in schema["paths"]
    assert "/api/borrow/checkout/{book_id}" in schema["paths"]
