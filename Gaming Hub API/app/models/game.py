from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Game(SQLModel, table=True):
    """Game model for the gaming catalog."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, min_length=2, max_length=100)
    genre: str = Field(min_length=2, max_length=50)
    release_year: int = Field(ge=1970, le=2100)
    description: Optional[str] = Field(None, max_length=500)
    developer: Optional[str] = Field(None, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    cover_url: Optional[str] = Field(default=None, description="Game cover image URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)