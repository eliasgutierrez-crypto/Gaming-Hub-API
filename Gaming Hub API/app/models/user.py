from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """User model for authentication and profile management."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, min_length=3, max_length=20)
    email: str = Field(unique=True, index=True)
    password: str  # Should be hashed with bcrypt
    avatar_url: Optional[str] = Field(default=None, description="User avatar image URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)