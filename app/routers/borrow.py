from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models import Borrow, Book, User
from app.schemas import BorrowResponse, BorrowDetailResponse
from app.auth import get_current_active_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/borrow", tags=["Borrowing"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/checkout/{book_id}", response_model=BorrowResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def checkout_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No available copies")
    
    # Check if user already has an active borrow for this book
    existing_borrow = db.query(Borrow).filter(
        Borrow.user_id == current_user.id,
        Borrow.book_id == book_id,
        Borrow.is_returned == False
    ).first()
    if existing_borrow:
        raise HTTPException(status_code=400, detail="You already have an active borrow for this book")
    
    # Create borrow
    due_date = datetime.now(timezone.utc) + timedelta(days=14)
    db_borrow = Borrow(
        user_id=current_user.id,
        book_id=book_id,
        due_date=due_date,
    )
    
    book.available_copies -= 1
    
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    
    return db_borrow

@router.post("/return/{borrow_id}", response_model=BorrowResponse)
@limiter.limit("5/minute")
async def return_book(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    borrow = db.query(Borrow).filter(Borrow.id == borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="Borrow not found")
    
    if borrow.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to return this borrow")
    
    if borrow.is_returned:
        raise HTTPException(status_code=400, detail="Book already returned")
    
    # Calculate fine if overdue
    now = datetime.now(timezone.utc)
    if now > borrow.due_date:
        days_overdue = (now - borrow.due_date).days
        borrow.fine_amount = days_overdue * 1.0  # $1 per day fine
    
    borrow.return_date = now
    borrow.is_returned = True
    
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    book.available_copies += 1
    
    db.commit()
    db.refresh(borrow)
    
    return borrow

@router.get("/my-borrows", response_model=List[BorrowDetailResponse])
@limiter.limit("10/minute")
async def get_my_borrows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    borrows = db.query(Borrow).filter(Borrow.user_id == current_user.id).all()
    
    result = []
    for borrow in borrows:
        book = db.query(Book).filter(Book.id == borrow.book_id).first()
        result.append(BorrowDetailResponse(
            id=borrow.id,
            user_id=borrow.user_id,
            book_id=borrow.book_id,
            borrow_date=borrow.borrow_date,
            due_date=borrow.due_date,
            return_date=borrow.return_date,
            fine_amount=borrow.fine_amount,
            is_returned=borrow.is_returned,
            book_title=book.title,
            book_author=book.author,
            username=current_user.username,
        ))
    
    return result

@router.get("/all", response_model=List[BorrowDetailResponse])
@limiter.limit("10/minute")
async def get_all_borrows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    borrows = db.query(Borrow).all()
    
    result = []
    for borrow in borrows:
        book = db.query(Book).filter(Book.id == borrow.book_id).first()
        user = db.query(User).filter(User.id == borrow.user_id).first()
        result.append(BorrowDetailResponse(
            id=borrow.id,
            user_id=borrow.user_id,
            book_id=borrow.book_id,
            borrow_date=borrow.borrow_date,
            due_date=borrow.due_date,
            return_date=borrow.return_date,
            fine_amount=borrow.fine_amount,
            is_returned=borrow.is_returned,
            book_title=book.title,
            book_author=book.author,
            username=user.username,
        ))
    
    return result
