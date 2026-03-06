"""
Game Recommendation Service

Provides algorithms for recommending games to users based on their review history.
"""

from sqlmodel import Session, select
from app.models.game import Game
from app.models.review import Review
from app.models.user import User


def get_user_reviewed_games(user_id: int, session: Session) -> set[int]:
    """
    Get all game IDs that a user has already reviewed.
    
    Args:
        user_id: The user ID
        session: Database session
        
    Returns:
        Set of game IDs reviewed by the user
    """
    reviews = session.exec(
        select(Review).where(Review.user_id == user_id)
    ).all()
    return {review.game_id for review in reviews}


def get_user_favorite_genres(user_id: int, session: Session, min_rating: int = 7) -> list[str]:
    """
    Get the most common genres from games the user rated highly.
    
    Args:
        user_id: The user ID
        session: Database session
        min_rating: Minimum rating to consider (default: 7/10)
        
    Returns:
        List of favorite genres
    """
    reviews = session.exec(
        select(Review).where(
            (Review.user_id == user_id) & (Review.rating >= min_rating)
        )
    ).all()
    
    if not reviews:
        return []
    
    favorite_genres = {}
    for review in reviews:
        game = session.get(Game, review.game_id)
        if game:
            favorite_genres[game.genre] = favorite_genres.get(game.genre, 0) + 1
    
    # Sort by frequency and return
    return sorted(
        favorite_genres.items(),
        key=lambda x: x[1],
        reverse=True
    )


def get_game_recommendations(
    user_id: int,
    session: Session,
    limit: int = 5,
    min_rating: int = 7
) -> list[Game]:
    """
    Get game recommendations for a user based on their review history.
    
    Algorithm:
    1. Find games the user rated highly (>= min_rating)
    2. Extract genres from those games
    3. Find unreviewed games in those genres
    4. Return top recommendations
    
    Args:
        user_id: The user ID
        session: Database session
        limit: Number of recommendations to return (default: 5)
        min_rating: Minimum rating for preference detection (default: 7)
        
    Returns:
        List of recommended Game objects
    """
    # Verify user exists
    user = session.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    # Get games already reviewed by user
    reviewed_games = get_user_reviewed_games(user_id, session)
    
    # Get user's favorite genres
    favorite_genres = get_user_favorite_genres(user_id, session, min_rating)
    
    if not favorite_genres:
        # If no reviews or all low ratings, recommend popular recent games
        all_games = session.exec(
            select(Game).order_by(Game.created_at.desc())
        ).all()
        return [g for g in all_games if g.id not in reviewed_games][:limit]
    
    # Find games in favorite genres that haven't been reviewed
    recommendations = []
    seen_ids = set()
    
    for genre, _ in favorite_genres:
        games_in_genre = session.exec(
            select(Game).where(Game.genre == genre).order_by(Game.release_year.desc())
        ).all()
        
        for game in games_in_genre:
            if (game.id not in reviewed_games and 
                game.id not in seen_ids):
                recommendations.append(game)
                seen_ids.add(game.id)
                
                if len(recommendations) >= limit:
                    return recommendations[:limit]
    
    # If we need more recommendations, add from other genres
    if len(recommendations) < limit:
        other_games = session.exec(
            select(Game).order_by(Game.release_year.desc())
        ).all()
        
        for game in other_games:
            if (game.id not in reviewed_games and 
                game.id not in seen_ids):
                recommendations.append(game)
                seen_ids.add(game.id)
                
                if len(recommendations) >= limit:
                    break
    
    return recommendations[:limit]


def get_similar_users(
    user_id: int,
    session: Session,
    limit: int = 5
) -> list[int]:
    """
    Find users with similar review patterns (collaborative filtering basis).
    
    Args:
        user_id: The user ID
        session: Database session
        limit: Number of similar users to return
        
    Returns:
        List of user IDs with similar tastes
    """
    user_reviews = session.exec(
        select(Review).where(Review.user_id == user_id)
    ).all()
    
    if not user_reviews:
        return []
    
    user_game_ids = {review.game_id for review in user_reviews}
    similarity_scores = {}
    
    # Find other users who reviewed the same games
    for user_game_id in user_game_ids:
        other_reviews = session.exec(
            select(Review).where(Review.game_id == user_game_id)
        ).all()
        
        for review in other_reviews:
            if review.user_id != user_id:
                similarity_scores[review.user_id] = similarity_scores.get(review.user_id, 0) + 1
    
    # Sort by similarity score
    similar_users = sorted(
        similarity_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [user_id for user_id, _ in similar_users[:limit]]