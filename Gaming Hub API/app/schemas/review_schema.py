from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
from typing import Optional
import re


class ReviewCreate(BaseModel):
    """Esquema para crear una nueva reseña con validación completa."""
    rating: int = Field(
        ge=1,
        le=10,
        description="Calificación de 1 (pobre) a 10 (excelente)"
    )
    comment: str = Field(
        min_length=5,
        max_length=500,
        description="Comentario de reseña: 5-500 caracteres"
    )
    user_id: int = Field(
        gt=0,
        description="ID de usuario debe ser entero positivo"
    )
    game_id: int = Field(
        gt=0,
        description="ID de juego debe ser entero positivo"
    )
    
    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        """Validar calidad del comentario."""
        # Eliminar espacios en blanco extra
        cleaned = " ".join(v.split())
        if not cleaned or len(cleaned) < 5:
            raise ValueError("Comment must contain at least 5 non-whitespace characters")
        # Verificar que tenga contenido significativo (no solo caracteres repetidos)
        if len(set(v.strip())) < 3:
            raise ValueError("Comment must contain varied characters")
        return cleaned
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Validar que la calificación esté en el rango válido."""
        if v < 1 or v > 10:
            raise ValueError("Rating must be between 1 and 10")
        return v
    
    @model_validator(mode="after")
    def validate_ids(self):
        """Validar que los IDs sean válidos."""
        # Validación básica: IDs deben ser positivos
        if self.user_id <= 0 or self.game_id <= 0:
            raise ValueError("User and game IDs must be positive integers")
        return self


class ReviewRead(BaseModel):
    """Esquema para leer datos de reseña."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(gt=0, description="Review ID must be positive")
    rating: int = Field(ge=1, le=10)
    comment: str
    user_id: int = Field(gt=0)
    game_id: int = Field(gt=0)
    created_at: datetime
    updated_at: datetime


class ReviewUpdate(BaseModel):
    """Esquema para actualizar datos de reseña con campos opcionales."""
    rating: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Rating: 1-10 (optional)"
    )
    comment: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Review comment: 5-500 characters (optional)"
    )
    
    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        """Validar calidad del comentario cuando se proporciona."""
        if not v:
            return None
        cleaned = " ".join(v.split())
        if len(cleaned) < 5:
            raise ValueError("Comment must contain at least 5 non-whitespace characters")
        if len(set(v.strip())) < 3:
            raise ValueError("Comment must contain varied characters")
        return cleaned
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: Optional[int]) -> Optional[int]:
        """Validar calificación cuando se proporciona."""
        if v is None:
            return None
        if v < 1 or v > 10:
            raise ValueError("Rating must be between 1 and 10")
        return v
    
    @model_validator(mode="after")
    def check_at_least_one_field(self):
        """Asegurar que al menos un campo sea proporcionado para la actualización."""
        if self.rating is None and self.comment is None:
            raise ValueError("At least one field (rating or comment) must be provided for update")
        return self