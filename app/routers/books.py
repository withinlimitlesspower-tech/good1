from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Book, User
from app.schemas import BookCreate, BookUpdate, BookResponse
from app.auth import get_current_active_user, get_admin_user
from app.redis_client import redis_client
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

router = APIRouter(prefix="/api/books", tags=["Books"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/", response_model=List[BookResponse])
@limiter.limit("30/minute")
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    cache_key = f"books:list:{skip}:{limit}:{search}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    query = db.query(Book)
    if search:
        query = query.filter(
            Book.title.ilike(f"%{search}%") | Book.author.ilike(f"%{search}%")
        )
    books = query.offset(skip).limit(limit).all()
    
    await redis_client.set(cache_key, [book.__dict__ for book in books])
    return books

@router.get("/{book_id}", response_model=BookResponse)
@limiter.limit("30/minute")
async def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    cache_key = f"book:{book_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await redis_client.set(cache_key, book.__dict__)
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    existing = db.query(Book).filter(Book.isbn == book_data.isbn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
    db_book = Book(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
        description=book_data.description,
        total_copies=book_data.total_copies,
        available_copies=book_data.total_copies,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    await redis_client.delete(f"books:list:*")
    return db_book

@router.put("/{book_id}", response_model=BookResponse)
@limiter.limit("10/minute")
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    if "total_copies" in update_data:
        db_book.available_copies = update_data["total_copies"] - (db_book.total_copies - db_book.available_copies)
    
    db.commit()
    db.refresh(db_book)
    
    await redis_client.delete(f"book:{book_id}")
    await redis_client.delete(f"books:list:*")
    return db_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    
    await redis_client.delete(f"book:{book_id}")
    await redis_client.delete(f"books:list:*")
