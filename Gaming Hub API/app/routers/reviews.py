from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.database import get_session
from app.models.review import Review
from app.models.user import User
from app.models.game import Game
from app.schemas.review_schema import ReviewCreate, ReviewRead, ReviewUpdate
from app.utils.cache_utils import cached_endpoint

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewRead)
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    """Crear una nueva reseña."""
    # Validar que el usuario exista
    user = session.get(User, review.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validar que el juego exista
    game = session.get(Game, review.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    db_review = Review(**review.model_dump())
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review


@router.get("/", response_model=list[ReviewRead])
def get_reviews(session: Session = Depends(get_session)):
    """Obtener todas las reseñas."""
    reviews = session.exec(select(Review)).all()
    return reviews


# Endpoint en caché (definido antes de rutas parametrizadas)
@router.get("/stats", tags=["Reviews"])
@cached_endpoint(ttl=300, key_prefix="reviews")  # Caché por 5 minutos
def get_reviews_stats(session: Session = Depends(get_session)):
    """
    Obtener estadísticas completas sobre reseñas.
    
    En caché por 5 minutos para mejorar el rendimiento.
    
    Returns:
        Diccionario con estadísticas de reseñas
    """
    # Conteos básicos de reseñas
    total_reviews = session.exec(select(func.count(Review.id))).first()
    
    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_rating": 0,
            "rating_distribution": {},
            "reviews_by_month": {},
            "top_reviewers": [],
            "most_reviewed_games": []
        }
    
    # Calificación promedio
    avg_rating = session.exec(select(func.avg(Review.rating))).first()
    
    # Distribución de calificaciones
    rating_dist = session.exec(
        select(Review.rating, func.count(Review.id))
        .group_by(Review.rating)
    ).all()
    
    # Reseñas por mes (últimos 12 meses)
    from datetime import datetime, timedelta
    one_year_ago = datetime.now() - timedelta(days=365)
    reviews_by_month = session.exec(
        select(
            func.strftime('%Y-%m', Review.created_at).label('month'),
            func.count(Review.id)
        )
        .where(Review.created_at >= one_year_ago)
        .group_by(func.strftime('%Y-%m', Review.created_at))
        .order_by(func.strftime('%Y-%m', Review.created_at))
    ).all()
    
    # Mejores reseñadores (usuarios con más reseñas)
    top_reviewers = session.exec(
        select(
            User.username,
            func.count(Review.id).label('review_count')
        )
        .join(Review)
        .group_by(User.id, User.username)
        .order_by(func.count(Review.id).desc())
        .limit(10)
    ).all()
    
    # Juegos más reseñados
    most_reviewed_games = session.exec(
        select(
            Game.title,
            func.count(Review.id).label('review_count'),
            func.avg(Review.rating).label('avg_rating')
        )
        .join(Review)
        .group_by(Game.id, Game.title)
        .order_by(func.count(Review.id).desc())
        .limit(10)
    ).all()
    
    return {
        "total_reviews": total_reviews,
        "average_rating": round(float(avg_rating), 2),
        "rating_distribution": {rating: count for rating, count in rating_dist},
        "reviews_by_month": {month: count for month, count in reviews_by_month},
        "top_reviewers": [
            {"username": username, "review_count": count}
            for username, count in top_reviewers
        ],
        "most_reviewed_games": [
            {
                "title": title,
                "review_count": review_count,
                "average_rating": round(float(avg_rating), 2)
            }
            for title, review_count, avg_rating in most_reviewed_games
        ]
    }


@router.put("/{review_id}", response_model=ReviewRead)
def update_review(review_id: int, review: ReviewUpdate, session: Session = Depends(get_session)):
    """Actualizar una reseña por ID."""
    db_review = session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review_data = review.model_dump(exclude_unset=True)
    db_review.sqlmodel_update(review_data)
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review


@router.delete("/{review_id}")
def delete_review(review_id: int, session: Session = Depends(get_session)):
    """Eliminar una reseña por ID."""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    session.delete(review)
    session.commit()
    return {"message": "Review deleted successfully"}