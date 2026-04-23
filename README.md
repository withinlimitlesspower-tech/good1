# Library Management System

A production-ready FastAPI application for managing library books, users, and borrowing operations.

## Features

- User registration and JWT-based authentication
- Book CRUD operations with Redis caching
- Borrowing system with due dates and fines
- PostgreSQL database with SQLAlchemy ORM
- Redis caching for frequently accessed books
- Rate limiting on API endpoints
- Docker and Docker Compose setup
- API documentation with Swagger UI
- Comprehensive unit tests with pytest
- Environment configuration with .env
- Structured logging and error handling

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose up --build`
4. Access API docs at http://localhost:8000/docs

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/books/` - List books (cached)
- `POST /api/books/` - Create book (admin)
- `GET /api/books/{id}` - Get book details
- `PUT /api/books/{id}` - Update book (admin)
- `DELETE /api/books/{id}` - Delete book (admin)
- `POST /api/borrow/checkout/{book_id}` - Check out book
- `POST /api/borrow/return/{borrow_id}` - Return book
- `GET /api/borrow/my-borrows` - Get user's borrows

## Testing

```bash
pytest --cov=app tests/
```