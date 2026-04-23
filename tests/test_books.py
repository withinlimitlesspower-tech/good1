import pytest
from fastapi import status

def test_list_books_empty(client, user_token):
    response = client.get(
        "/api/books/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_books_with_data(client, user_token, sample_book):
    response = client.get(
        "/api/books/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Book"

def test_get_book(client, user_token, sample_book):
    response = client.get(
        f"/api/books/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"

def test_get_book_not_found(client, user_token):
    response = client.get(
        "/api/books/999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_book_admin(client, admin_token):
    response = client.post(
        "/api/books/",
        json={
            "title": "New Book",
            "author": "New Author",
            "isbn": "9876543210123",
            "description": "A new book",
            "total_copies": 5,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Book"
    assert data["available_copies"] == 5

def test_create_book_non_admin(client, user_token):
    response = client.post(
        "/api/books/",
        json={
            "title": "New Book",
            "author": "New Author",
            "isbn": "9876543210123",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_book_duplicate_isbn(client, admin_token, sample_book):
    response = client.post(
        "/api/books/",
        json={
            "title": "Another Book",
            "author": "Another Author",
            "isbn": "1234567890123",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_update_book_admin(client, admin_token, sample_book):
    response = client.put(
        f"/api/books/{sample_book.id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"

def test_delete_book_admin(client, admin_token, sample_book):
    response = client.delete(
        f"/api/books/{sample_book.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_book_non_admin(client, user_token, sample_book):
    response = client.delete(
        f"/api/books/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
