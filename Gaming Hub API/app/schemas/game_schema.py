from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime, date
from typing import Optional

# Géneros de juegos válidos
VALID_GENRES = {
    "Action", "Adventure", "RPG", "Strategy", "Simulation",
    "Sports", "Racing", "Puzzle", "Indie", "Horror",
    "Shooter", "Fighting", "Platform", "Stealth", "Survival"
}


class GameCreate(BaseModel):
    """Esquema para crear un nuevo juego con validación completa."""
    title: str = Field(
        min_length=2,
        max_length=100,
        description="Título del juego: 2-100 caracteres"
    )
    genre: str = Field(
        min_length=2,
        max_length=50,
        description="Género del juego - debe ser un género válido"
    )
    release_year: int = Field(
        ge=1970,
        le=2100,
        description="Año de lanzamiento: 1970-2100"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción opcional del juego: máximo 500 caracteres"
    )
    developer: Optional[str] = Field(
        None,
        max_length=100,
        description="Nombre de desarrollador opcional"
    )
    publisher: Optional[str] = Field(
        None,
        max_length=100,
        description="Nombre de editor opcional"
    )
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validar que el título no esté vacío ni solo contenga espacios."""
        if not v.strip():
            raise ValueError("Title cannot be empty or only whitespace")
        return v.strip()
    
    @field_validator("genre")
    @classmethod
    def validate_genre(cls, v: str) -> str:
        """Validar que el género esté en la lista permitida."""
        genre_normalized = v.strip().upper()
        if genre_normalized not in {g.upper() for g in VALID_GENRES}:
            genres_list = ", ".join(sorted(VALID_GENRES))
            raise ValueError(f"Genre must be one of: {genres_list}")
        # Devolver la versión correctamente capitalizada de VALID_GENRES
        for valid_genre in VALID_GENRES:
            if valid_genre.upper() == genre_normalized:
                return valid_genre
        return v.strip()  # fallback
    
    @field_validator("release_year")
    @classmethod
    def validate_release_year(cls, v: int) -> int:
        """Validar que el año de lanzamiento no esté en el futuro."""
        current_year = date.today().year
        if v > current_year + 1:  # Permitir un año en el futuro para juegos próximos
            raise ValueError(f"Release year cannot be more than 1 year in the future (max: {current_year + 1})")
        return v
    
    @field_validator("description", "developer", "publisher")
    @classmethod
    def validate_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        """Validar que las cadenas opcionales no sean solo espacios."""
        if v and not v.strip():
            raise ValueError("Field cannot be only whitespace")
        return v.strip() if v else None


class GameRead(BaseModel):
    """Esquema para leer datos de juego."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(gt=0, description="ID del juego debe ser positivo")
    title: str
    genre: str
    release_year: int = Field(ge=1970, le=2100)
    description: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    cover_url: Optional[str] = Field(None, description="URL de la imagen de portada del juego")
    created_at: datetime
    updated_at: datetime


class GameUpdate(BaseModel):
    """Esquema para actualizar datos de juego con campos opcionales."""
    title: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Título del juego: 2-100 caracteres"
    )
    genre: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Género de juego válido"
    )
    release_year: Optional[int] = Field(
        None,
        ge=1970,
        le=2100,
        description="Año de lanzamiento: 1970-2100"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción del juego: máximo 500 caracteres"
    )
    developer: Optional[str] = Field(
        None,
        max_length=100,
        description="Nombre del desarrollador"
    )
    publisher: Optional[str] = Field(
        None,
        max_length=100,
        description="Nombre del editor"
    )
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validar título cuando se proporciona."""
        if v and not v.strip():
            raise ValueError("Title cannot be empty or only whitespace")
        return v.strip() if v else None
    
    @field_validator("genre")
    @classmethod
    def validate_genre(cls, v: Optional[str]) -> Optional[str]:
        """Validar género cuando se proporciona."""
        if not v:
            return None
        genre_stripped = v.strip().capitalize()
        if genre_stripped not in VALID_GENRES:
            genres_list = ", ".join(sorted(VALID_GENRES))
            raise ValueError(f"Genre must be one of: {genres_list}")
        return genre_stripped
    
    @field_validator("release_year")
    @classmethod
    def validate_release_year(cls, v: Optional[int]) -> Optional[int]:
        """Validar año de lanzamiento cuando se proporciona."""
        if not v:
            return None
        current_year = date.today().year
        if v > current_year + 1:
            raise ValueError(f"Release year cannot be more than 1 year in the future (max: {current_year + 1})")
        return v
    
    @field_validator("description", "developer", "publisher")
    @classmethod
    def validate_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        """Validar que las cadenas opcionales no sean solo espacios."""
        if v and not v.strip():
            raise ValueError("Field cannot be only whitespace")
        return v.strip() if v else None
    
    @model_validator(mode="after")
    def check_at_least_one_field(self):
        """Asegurar que al menos un campo se proporcione para actualización."""
        if not any([self.title, self.genre, self.release_year, 
                   self.description, self.developer, self.publisher]):
            raise ValueError("At least one field must be provided for update")
        return self


class CoverUploadResponse(BaseModel):
    """Respuesta luego de subir portada de juego."""
    message: str
    cover_url: str = Field(description="URL de la portada subida")
    file_size: int = Field(description="Tamaño del archivo subido en bytes")


class GameWithRating(BaseModel):
    """Esquema para juegos con información de calificación promedio."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(gt=0, description="Game ID must be positive")
    title: str
    genre: str
    release_year: int = Field(ge=1970, le=2100)
    description: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    cover_url: Optional[str] = Field(None, description="URL de la imagen de portada del juego")
    created_at: datetime
    updated_at: datetime
    average_rating: float = Field(description="Calificación promedio de reseñas (1-10)")
    review_count: int = Field(description="Número de reseñas")
