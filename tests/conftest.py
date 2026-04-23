import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Book
from app.auth import get_password_hash

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def admin_user(db_session):
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def normal_user(db_session):
    user = User(
        username="user",
        email="user@example.com",
        hashed_password=get_password_hash("user1234"),
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_book(db_session):
    book = Book(
        title="Test Book",
        author="Test Author",
        isbn="1234567890123",
        description="A test book",
        total_copies=3,
        available_copies=3,
    )
    db_session.add(book)
    db_session.commit()
    return book

@pytest.fixture
def admin_token(client, admin_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]

@pytest.fixture
def user_token(client, normal_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "user1234"},
    )
    return response.json()["access_token"]
