from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Review(SQLModel, table=True):
    """Review model for user game reviews and ratings."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    rating: int = Field(ge=1, le=10, description="Rating from 1 to 10")
    comment: str = Field(min_length=5, max_length=500)
    user_id: int = Field(foreign_key="user.id")
    game_id: int = Field(foreign_key="game.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)