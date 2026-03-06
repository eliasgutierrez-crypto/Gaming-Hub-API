"""
Test script for Redis caching functionality
"""

import requests
import time
import sys
import os

# Corregir codificación para Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

BASE_URL = "http://127.0.0.1:8002"

def create_test_data():
    """Create test users, games, and reviews for testing."""
    print("Creating test data...")

    # Crear usuarios
    users = [
        {"username": "gamer1", "email": "gamer1@test.com", "password": "Pass123!"},
        {"username": "gamer2", "email": "gamer2@test.com", "password": "Pass123!"},
        {"username": "gamer3", "email": "gamer3@test.com", "password": "Pass123!"}
    ]

    user_ids = []
    for user in users:
        response = requests.post(f"{BASE_URL}/users/", json=user)
        if response.status_code == 200:
            user_ids.append(response.json()["id"])
            print(f"[OK] Created user: {user['username']}")
        else:
            print(f"[ERROR] Failed to create user: {response.text}")

    # Crear juegos
    games = [
        {"title": "Cyberpunk 2077", "genre": "RPG", "release_year": 2020, "description": "Futuristic RPG"},
        {"title": "The Witcher 3", "genre": "RPG", "release_year": 2015, "description": "Fantasy RPG"},
        {"title": "FIFA 2024", "genre": "Sports", "release_year": 2024, "description": "Football game"},
        {"title": "Call of Duty", "genre": "Shooter", "release_year": 2023, "description": "First person shooter"},
        {"title": "Minecraft", "genre": "Indie", "release_year": 2011, "description": "Sandbox game"}
    ]

    game_ids = []
    for game in games:
        response = requests.post(f"{BASE_URL}/games/", json=game)
        if response.status_code == 200:
            game_ids.append(response.json()["id"])
            print(f"[OK] Created game: {game['title']}")
        else:
            print(f"[ERROR] Failed to create game: {response.text}")

    # Solo continuar si tenemos al menos algunos juegos
    if len(game_ids) < 3:
        print("[ERROR] Not enough games created for testing. Need at least 3 games.")
        return [], []

    # Crear reseñas (solo para juegos que se crearon correctamente)
    reviews = [
        {"user_id": user_ids[0], "game_id": game_ids[0], "rating": 8, "comment": "Great game with amazing graphics"},
        {"user_id": user_ids[0], "game_id": game_ids[1], "rating": 10, "comment": "Best RPG ever"},
        {"user_id": user_ids[1], "game_id": game_ids[0], "rating": 7, "comment": "Good but has bugs"},
        {"user_id": user_ids[1], "game_id": game_ids[2 % len(game_ids)], "rating": 9, "comment": "Excellent sports game"},
        {"user_id": user_ids[2], "game_id": game_ids[1], "rating": 9, "comment": "Fantastic story"},
        {"user_id": user_ids[2], "game_id": game_ids[2 % len(game_ids)], "rating": 8, "comment": "Fun shooter"},
        {"user_id": user_ids[0], "game_id": game_ids[2 % len(game_ids)], "rating": 10, "comment": "Timeless classic"},
        {"user_id": user_ids[1], "game_id": game_ids[2 % len(game_ids)], "rating": 9, "comment": "Very creative"}
    ]

    for review in reviews:
        response = requests.post(f"{BASE_URL}/reviews/", json=review)
        if response.status_code == 200:
            print(f"✓ Created review: User {review['user_id']} rated game {review['game_id']} with {review['rating']}/10")
        else:
            print(f"✗ Failed to create review: {response.text}")

    return user_ids, game_ids

def test_caching():
    """Test the cached endpoints."""
    print("\n" + "="*60)
    print("TESTING REDIS CACHING FUNCTIONALITY")
    print("="*60)

    # Prueba 1: Juegos mejor calificados
    print("\n1️⃣ Testing /games/top-rated (cached 10 minutes)")
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/games/top-rated")
    first_call = time.time() - start_time

    if response.status_code == 200:
        data = response.json()
        print(f"✓ First call: {first_call:.3f}s - Got {len(data)} games")
        if data:
            print(f"  Top game: {data[0]['title']} (avg rating: {data[0]['average_rating']})")

        # La segunda llamada debe ser más rápida (en caché)
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/games/top-rated")
        second_call = time.time() - start_time

        if response2.status_code == 200:
            print(f"✓ Second call: {second_call:.3f}s - Cached result")
            if abs(first_call - second_call) < 0.1:  # Tiempo similar significa no cacheado
                print("  ⚠️  Warning: Response time similar, caching may not be working")
            else:
                print("  ✅ Caching working - faster response time")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text}")

    # Prueba 2: Recomendaciones de juegos
    print("\n2️⃣ Testing /games/recommendations/{user_id} (cached 5 minutes)")
    user_id = 1  # Asumiendo que el usuario 1 existe
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/games/recommendations/{user_id}")
    first_call = time.time() - start_time

    if response.status_code == 200:
        data = response.json()
        print(f"✓ First call: {first_call:.3f}s - Got {len(data)} recommendations")

        # Second call
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/games/recommendations/{user_id}")
        second_call = time.time() - start_time

        if response2.status_code == 200:
            print(f"✓ Second call: {second_call:.3f}s - Cached result")
            if second_call < first_call * 0.8:  # Al menos 20% más rápido
                print("  ✅ Caching working for recommendations")
            else:
                print("  ⚠️  Warning: Caching may not be working for recommendations")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text}")

    # Prueba 3: Estadísticas de juegos
    print("\n3️⃣ Testing /games/stats (cached 5 minutes)")
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/games/stats")
    first_call = time.time() - start_time

    if response.status_code == 200:
        data = response.json()
        print(f"✓ First call: {first_call:.3f}s - Got stats: {data['total_games']} games, {data['total_reviews']} reviews")

        # Second call
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/games/stats")
        second_call = time.time() - start_time

        if response2.status_code == 200:
            print(f"✓ Second call: {second_call:.3f}s - Cached result")
            if second_call < first_call * 0.8:
                print("  ✅ Caching working for games stats")
            else:
                print("  ⚠️  Warning: Caching may not be working for games stats")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text}")

    # Prueba 4: Estadísticas de reseñas
    print("\n4️⃣ Testing /reviews/stats (cached 5 minutes)")
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/reviews/stats")
    first_call = time.time() - start_time

    if response.status_code == 200:
        data = response.json()
        print(f"✓ First call: {first_call:.3f}s - Got stats: {data['total_reviews']} reviews, avg rating: {data['average_rating']}")

        # Second call
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/reviews/stats")
        second_call = time.time() - start_time

        if response2.status_code == 200:
            print(f"✓ Second call: {second_call:.3f}s - Cached result")
            if second_call < first_call * 0.8:
                print("  ✅ Caching working for reviews stats")
            else:
                print("  ⚠️  Warning: Caching may not be working for reviews stats")
    else:
        print(f"✗ Failed: {response.status_code} - {response.text}")

    print("\n" + "="*60)
    print("✅ CACHING TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    try:
        # Crear datos de prueba
        user_ids, game_ids = create_test_data()

        # Probar caché
        test_caching()

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()