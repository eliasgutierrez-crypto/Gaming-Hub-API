from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select, func
from typing import List

from app.database import get_session
from app.models.game import Game
from app.models.review import Review
from app.schemas.game_schema import GameCreate, GameRead, GameUpdate, CoverUploadResponse, GameWithRating
from app.utils.file_utils import save_upload_file, delete_file, get_file_url
from app.utils.cache_utils import cached_endpoint, invalidate_cache_pattern
from app.services.recommendation_service import get_game_recommendations

router = APIRouter(prefix="/games", tags=["Games"])


# Endpoints en caché para operaciones pesadas (definidos primero para evitar conflictos de rutas)

@router.get("/top-rated", response_model=List[GameWithRating], tags=["Games"])
@cached_endpoint(ttl=600, key_prefix="games")  # Caché por 10 minutos
def get_top_rated_games(limit: int = 10, session: Session = Depends(get_session)):
    """
    Obtener los juegos mejor calificados según la calificación promedio de reseñas.
    
    En caché por 10 minutos para mejorar el rendimiento.
    
    Args:
        limit: Número máximo de juegos a devolver (por defecto: 10)
        
    Returns:
        Lista de juegos con sus calificaciones promedio y conteos de reseñas
    """
    # Obtener juegos con sus calificaciones promedio y conteos de reseñas
    from sqlalchemy import func, case
    
    # Subconsulta para obtener calificación promedio y conteo por juego
    rating_subquery = session.exec(
        select(
            Review.game_id,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        )
        .group_by(Review.game_id)
        .having(func.count(Review.id) >= 1)  # Solo juegos con al menos 1 reseña
    ).all()
    
    # Convertir a dict para fácil búsqueda
    rating_dict = {r.game_id: {'avg_rating': r.avg_rating, 'review_count': r.review_count} 
                   for r in rating_subquery}
    
    if not rating_dict:
        return []
    
    # Obtener juegos y agregar información de calificación
    game_ids = list(rating_dict.keys())
    games = session.exec(
        select(Game).where(Game.id.in_(game_ids))
    ).all()
    
    # Ordenar por calificación promedio (descendente) y devolver top N
    games_with_ratings = []
    for game in games:
        rating_info = rating_dict[game.id]
        game_dict = game.model_dump()
        game_dict['average_rating'] = round(float(rating_info['avg_rating']), 2)
        game_dict['review_count'] = rating_info['review_count']
        games_with_ratings.append(GameWithRating(**game_dict))
    
    # Ordenar por calificación promedio descendente
    games_with_ratings.sort(key=lambda x: x.average_rating, reverse=True)
    
    return games_with_ratings[:limit]


@router.get("/recommendations/{user_id}", response_model=List[GameRead], tags=["Games"])
@cached_endpoint(ttl=300, key_prefix="recommendations")  # Caché por 5 minutos
def get_user_recommendations(user_id: int, limit: int = 5, session: Session = Depends(get_session)):
    """
    Obtener recomendaciones personalizadas de juegos para un usuario.
    
    En caché por 5 minutos para mejorar el rendimiento.
    
    Args:
        user_id: ID de usuario para obtener recomendaciones
        limit: Número máximo de recomendaciones (por defecto: 5)
        
    Returns:
        Lista de juegos recomendados
    """
    try:
        recommendations = get_game_recommendations(user_id, session, limit)
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats", tags=["Games"])
@cached_endpoint(ttl=300, key_prefix="stats")  # Caché por 5 minutos
def get_games_stats(session: Session = Depends(get_session)):
    """
    Obtener estadísticas completas sobre juegos y reseñas.
    
    En caché por 5 minutos.
    
    Returns:
        Diccionario con varias estadísticas
    """
    from sqlalchemy import func
    
    # Conteos básicos de juegos
    total_games = session.exec(select(func.count(Game.id))).first()
    
    # Estadísticas de reseñas
    total_reviews = session.exec(select(func.count(Review.id))).first()
    avg_rating_all = session.exec(select(func.avg(Review.rating))).first()
    
    # Juegos por género
    genre_stats = session.exec(
        select(Game.genre, func.count(Game.id))
        .group_by(Game.genre)
    ).all()
    
    # Reseñas por distribución de calificaciones
    rating_dist = session.exec(
        select(Review.rating, func.count(Review.id))
        .group_by(Review.rating)
    ).all()
    
    # Juegos mejor calificados (top 5)
    top_rated = session.exec(
        select(
            Game.title,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        )
        .join(Review)
        .group_by(Game.id, Game.title)
        .order_by(func.avg(Review.rating).desc())
        .limit(5)
    ).all()
    
    return {
        "total_games": total_games,
        "total_reviews": total_reviews,
        "average_rating_all_games": round(float(avg_rating_all), 2) if avg_rating_all else 0,
        "games_by_genre": {genre: count for genre, count in genre_stats},
        "rating_distribution": {rating: count for rating, count in rating_dist},
        "top_rated_games": [
            {
                "title": title,
                "average_rating": round(float(avg_rating), 2),
                "review_count": review_count
            }
            for title, avg_rating, review_count in top_rated
        ]
    }


# Operaciones CRUD

@router.post("/", response_model=GameRead)
def create_game(game: GameCreate, session: Session = Depends(get_session)):
    """Crear un nuevo juego."""
    db_game = Game(**game.model_dump())
    session.add(db_game)
    session.commit()
    session.refresh(db_game)
    return db_game


@router.get("/", response_model=list[GameRead])
def get_games(session: Session = Depends(get_session)):
    """Obtener todos los juegos."""
    games = session.exec(select(Game)).all()
    return games


@router.get("/{game_id}", response_model=GameRead)
def get_game(game_id: int, session: Session = Depends(get_session)):
    """Obtener un juego por ID."""
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.put("/{game_id}", response_model=GameRead)
def update_game(game_id: int, game: GameUpdate, session: Session = Depends(get_session)):
    """Actualizar un juego por ID."""
    db_game = session.get(Game, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_data = game.model_dump(exclude_unset=True)
    db_game.sqlmodel_update(game_data)
    session.add(db_game)
    session.commit()
    session.refresh(db_game)
    return db_game


@router.delete("/{game_id}")
def delete_game(game_id: int, session: Session = Depends(get_session)):
    """Eliminar un juego por ID."""
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    session.delete(game)
    session.commit()
    return {"message": "Game deleted successfully"}


# Subir portada de juego
@router.post("/{game_id}/cover", response_model=CoverUploadResponse, tags=["File Upload"])
async def upload_game_cover(
    game_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Subir una imagen de portada de juego.
    
    Formatos permitidos: JPEG, PNG
    Tamaño máximo: 5 MB
    
    Devuelve la URL donde se sirve la imagen.
    """
    # Verificar que el juego existe
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Guardar archivo
    file_path = await save_upload_file(file, upload_type="cover")
    
    # Eliminar portada antigua si existe
    if game.cover_url:
        old_file = game.cover_url.replace("/static/", "")
        delete_file(old_file)
    
    # Actualizar juego con nueva URL de portada
    game.cover_url = get_file_url(file_path)
    session.add(game)
    session.commit()
    
    # Obtener tamaño del archivo
    file_content = await file.read()
    file_size = len(file_content)
    
    return CoverUploadResponse(
        message="Cover uploaded successfully",
        cover_url=game.cover_url,
        file_size=file_size
    )


# Obtener portada de juego
@router.get("/{game_id}/cover", tags=["File Upload"])
def get_game_cover(game_id: int, session: Session = Depends(get_session)):
    """Obtener URL de portada de juego."""
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not game.cover_url:
        raise HTTPException(status_code=404, detail="Game has no cover")
    return {"cover_url": game.cover_url}


# Eliminar portada de juego
@router.delete("/{game_id}/cover", tags=["File Upload"])
async def delete_game_cover(game_id: int, session: Session = Depends(get_session)):
    """Eliminar portada de juego."""
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not game.cover_url:
        raise HTTPException(status_code=404, detail="Game has no cover")
    
    # Eliminar archivo
    old_file = game.cover_url.replace("/static/", "")
    delete_file(old_file)
    
    # Actualizar juego
    game.cover_url = None
    session.add(game)
    session.commit()
    
    return {"message": "Cover deleted successfully"}