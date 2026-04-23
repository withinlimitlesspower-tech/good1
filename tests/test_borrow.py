import pytest
from fastapi import status

def test_checkout_book(client, user_token, sample_book):
    response = client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["book_id"] == sample_book.id
    assert data["is_returned"] == False
    assert "due_date" in data

def test_checkout_book_no_copies(client, user_token, sample_book):
    # Set available copies to 0
    sample_book.available_copies = 0
    from app.database import SessionLocal
    db = SessionLocal()
    db.add(sample_book)
    db.commit()
    db.close()
    
    response = client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No available copies"

def test_checkout_book_not_found(client, user_token):
    response = client.post(
        "/api/borrow/checkout/999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_checkout_duplicate(client, user_token, sample_book):
    # First checkout
    response = client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # Second checkout should fail
    response = client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_return_book(client, user_token, sample_book):
    # Checkout first
    checkout_resp = client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    borrow_id = checkout_resp.json()["id"]
    
    # Return the book
    response = client.post(
        f"/api/borrow/return/{borrow_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_returned"] == True
    assert data["return_date"] is not None

def test_return_book_not_found(client, user_token):
    response = client.post(
        "/api/borrow/return/999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_return_already_returned(client, user_token, sample_book):
    # Checkout and return
    checkout_resp = client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    borrow_id = checkout_resp.json()["id"]
    
    client.post(
        f"/api/borrow/return/{borrow_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    # Try to return again
    response = client.post(
        f"/api/borrow/return/{borrow_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_my_borrows(client, user_token, sample_book):
    # Checkout a book
    client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    response = client.get(
        "/api/borrow/my-borrows",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["book_title"] == "Test Book"

def test_get_all_borrows_admin(client, admin_token, user_token, sample_book):
    # User checks out a book
    client.post(
        f"/api/borrow/checkout/{sample_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    
    # Admin views all borrows
    response = client.get(
        "/api/borrow/all",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1

def test_get_all_borrows_non_admin(client, user_token):
    response = client.get(
        "/api/borrow/all",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
