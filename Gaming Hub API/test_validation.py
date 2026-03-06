"""
Test script to demonstrate Pydantic v2 validation across all schemas
"""

from pydantic import ValidationError
from app.schemas.user_schema import UserCreate, UserUpdate
from app.schemas.game_schema import GameCreate, GameUpdate
from app.schemas.review_schema import ReviewCreate, ReviewUpdate


def test_user_validation():
    """Test user schema validation."""
    print("\n=== USER VALIDATION TESTS ===\n")
    
    # ✅ Valid user
    print("✅ Valid user creation:")
    try:
        user = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="SecurePass123"
        )
        print(f"   Success: {user.username}")
    except ValidationError as e:
        print(f"   ❌ Error: {e}")
    
    # ❌ Invalid username (starts with underscore)
    print("\n❌ Invalid username (starts with underscore):")
    try:
        user = UserCreate(
            username="_john",
            email="john@example.com",
            password="SecurePass123"
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Weak password (no uppercase)
    print("\n❌ Weak password (no uppercase):")
    try:
        user = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="securepass123"
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Weak password (no number)
    print("\n❌ Weak password (no number):")
    try:
        user = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="SecurePass"
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Invalid email
    print("\n❌ Invalid email format:")
    try:
        user = UserCreate(
            username="john_doe",
            email="not-an-email",
            password="SecurePass123"
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Update with no fields
    print("\n❌ User update with no fields provided:")
    try:
        update = UserUpdate()
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")


def test_game_validation():
    """Test game schema validation."""
    print("\n=== GAME VALIDATION TESTS ===\n")
    
    # ✅ Valid game
    print("✅ Valid game creation:")
    try:
        game = GameCreate(
            title="The Legend of Zelda",
            genre="Adventure",
            release_year=2023,
            developer="Nintendo",
            description="An epic adventure game"
        )
        print(f"   Success: {game.title} ({game.genre})")
    except ValidationError as e:
        print(f"   ❌ Error: {e}")
    
    # ❌ Invalid genre
    print("\n❌ Invalid game genre:")
    try:
        game = GameCreate(
            title="Test Game",
            genre="InvalidGenre",
            release_year=2023
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Future release year
    print("\n❌ Future release year (more than 1 year ahead):")
    try:
        game = GameCreate(
            title="Test Game",
            genre="Action",
            release_year=2030
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Title only whitespace
    print("\n❌ Title with only whitespace:")
    try:
        game = GameCreate(
            title="   ",
            genre="Action",
            release_year=2023
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Update with no fields
    print("\n❌ Game update with no fields:")
    try:
        update = GameUpdate()
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")


def test_review_validation():
    """Test review schema validation."""
    print("\n=== REVIEW VALIDATION TESTS ===\n")
    
    # ✅ Valid review
    print("✅ Valid review creation:")
    try:
        review = ReviewCreate(
            rating=9,
            comment="This game is absolutely amazing!",
            user_id=1,
            game_id=1
        )
        print(f"   Success: Rating {review.rating}/10")
    except ValidationError as e:
        print(f"   ❌ Error: {e}")
    
    # ❌ Invalid rating
    print("\n❌ Rating out of range (11):")
    try:
        review = ReviewCreate(
            rating=11,
            comment="This game is absolutely amazing!",
            user_id=1,
            game_id=1
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Comment too short
    print("\n❌ Comment too short (less than 5 chars):")
    try:
        review = ReviewCreate(
            rating=9,
            comment="Good",
            user_id=1,
            game_id=1
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Comment repetitive
    print("\n❌ Comment with repeated characters only:")
    try:
        review = ReviewCreate(
            rating=9,
            comment="aaaaaaaaaa",
            user_id=1,
            game_id=1
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Invalid user ID
    print("\n❌ Invalid user ID (negative):")
    try:
        review = ReviewCreate(
            rating=9,
            comment="Great game!",
            user_id=-1,
            game_id=1
        )
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")
    
    # ❌ Update with no fields
    print("\n❌ Review update with no fields:")
    try:
        update = ReviewUpdate()
    except ValidationError as e:
        print(f"   ✓ Caught: {e.errors()[0]['msg']}")


if __name__ == "__main__":
    print("=" * 60)
    print("PYDANTIC V2 VALIDATION TESTS")
    print("=" * 60)
    
    test_user_validation()
    test_game_validation()
    test_review_validation()
    
    print("\n" + "=" * 60)
    print("✅ VALIDATION TEST SUITE COMPLETE")
    print("=" * 60)
