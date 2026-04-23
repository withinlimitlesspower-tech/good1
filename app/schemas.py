from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, timedelta
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=200)
    isbn: str = Field(..., min_length=10, max_length=13)
    description: Optional[str] = None
    total_copies: int = Field(default=1, ge=1)

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    description: Optional[str] = None
    total_copies: Optional[int] = Field(None, ge=1)

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    description: Optional[str]
    available_copies: int
    total_copies: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BorrowCreate(BaseModel):
    pass

class BorrowResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    fine_amount: float
    is_returned: bool

    class Config:
        from_attributes = True

class BorrowDetailResponse(BorrowResponse):
    book_title: str
    book_author: str
    username: str
