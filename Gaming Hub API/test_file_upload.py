"""
Test script to demonstrate file upload functionality
"""

import requests
from pathlib import Path
from PIL import Image
import io

BASE_URL = "http://127.0.0.1:8000"


def create_test_image(width: int = 100, height: int = 100, filename: str = "test.png", color: str = "red") -> bytes:
    """Create a test image file."""
    image = Image.new("RGB", (width, height), color=color)
    img_io = io.BytesIO()
    image.save(img_io, format="PNG")
    img_io.seek(0)
    return img_io.getvalue()


def test_upload_workflow():
    """Test complete upload workflow."""
    print("\n" + "=" * 60)
    print("FILE UPLOAD TEST SUITE")
    print("=" * 60 + "\n")
    
    # 1. Crear un usuario de prueba
    print("1️⃣ Creating test user...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    }
    user_response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if user_response.status_code == 200:
        user = user_response.json()
        user_id = user["id"]
        print(f"   ✅ User created: {user['username']} (ID: {user_id})\n")
    else:
        print(f"   ❌ Error: {user_response.json()}\n")
        return
    
    # 2. Crear un juego de prueba
    print("2️⃣ Creating test game...")
    game_data = {
        "title": "Test Game",
        "genre": "Action",
        "release_year": 2024,
        "description": "A test game",
        "developer": "Test Developer"
    }
    game_response = requests.post(f"{BASE_URL}/games/", json=game_data)
    if game_response.status_code == 200:
        game = game_response.json()
        game_id = game["id"]
        print(f"   ✅ Game created: {game['title']} (ID: {game_id})\n")
    else:
        print(f"   ❌ Error: {game_response.json()}\n")
        return
    
    # 3. Subir avatar de usuario
    print("3️⃣ Uploading user avatar...")
    img_content = create_test_image()
    files = {"file": ("avatar.png", img_content, "image/png")}
    avatar_response = requests.post(f"{BASE_URL}/users/{user_id}/avatar", files=files)
    if avatar_response.status_code == 200:
        avatar_data = avatar_response.json()
        print(f"   ✅ Avatar uploaded!")
        print(f"   🖼️  URL: {avatar_data['avatar_url']}")
        print(f"   📦 Size: {avatar_data['file_size']} bytes\n")
    else:
        print(f"   ❌ Error: {avatar_response.json()}\n")
    
    # 4. Obtener avatar de usuario
    print("4️⃣ Retrieving user avatar URL...")
    get_avatar = requests.get(f"{BASE_URL}/users/{user_id}/avatar")
    if get_avatar.status_code == 200:
        print(f"   ✅ Avatar URL: {get_avatar.json()['avatar_url']}\n")
    else:
        print(f"   ❌ Error: {get_avatar.json()}\n")
    
    # 5. Subir portada de juego
    print("5️⃣ Uploading game cover...")
    img_content = create_test_image(width=200, height=300)
    files = {"file": ("cover.png", img_content, "image/png")}
    cover_response = requests.post(f"{BASE_URL}/games/{game_id}/cover", files=files)
    if cover_response.status_code == 200:
        cover_data = cover_response.json()
        print(f"   ✅ Cover uploaded!")
        print(f"   🖼️  URL: {cover_data['cover_url']}")
        print(f"   📦 Size: {cover_data['file_size']} bytes\n")
    else:
        print(f"   ❌ Error: {cover_response.json()}\n")
    
    # 6. Probar errores de validación
    print("6️⃣ Testing validation (invalid file type)...")
    invalid_file = b"This is not an image file"
    files = {"file": ("invalid.txt", invalid_file, "text/plain")}
    invalid_response = requests.post(f"{BASE_URL}/games/{game_id}/cover", files=files)
    if invalid_response.status_code != 200:
        print(f"   ✅ Correctly rejected: {invalid_response.json()['detail']}\n")
    else:
        print(f"   ❌ Should have rejected invalid file\n")
    
    # 7. Probar archivo grande
    print("7️⃣ Testing file size limit...")
    # Create a large file by starting with a large image with random data
    large_image = create_test_image(width=8000, height=8000)
    # If still not large enough, pad it
    large_image_bytes = bytearray(large_image)
    while len(large_image_bytes) < 6 * 1024 * 1024:  # Make it over 6 MB
        large_image_bytes.extend(large_image)
    files = {"file": ("large.png", bytes(large_image_bytes), "image/png")}
    large_response = requests.post(f"{BASE_URL}/users/{user_id}/avatar", files=files)
    if large_response.status_code != 200:
        print(f"   ✅ Correctly rejected: {large_response.json()['detail']}\n")
    else:
        print(f"   ❌ Should have rejected large file\n")
    
    # 8. Replace avatar
    print("8️⃣ Uploading new avatar (replacing old one)...")
    new_img = create_test_image(color="blue")
    files = {"file": ("avatar2.png", new_img, "image/png")}
    replace_response = requests.post(f"{BASE_URL}/users/{user_id}/avatar", files=files)
    if replace_response.status_code == 200:
        print(f"   ✅ Avatar replaced successfully\n")
    else:
        print(f"   ❌ Error: {replace_response.json()}\n")
    
    # 9. Delete avatar
    print("9️⃣ Deleting user avatar...")
    delete_response = requests.delete(f"{BASE_URL}/users/{user_id}/avatar")
    if delete_response.status_code == 200:
        print(f"   ✅ Avatar deleted: {delete_response.json()['message']}\n")
    else:
        print(f"   ❌ Error: {delete_response.json()}\n")
    
    # 10. Verify deletion
    print("🔟 Verifying avatar is deleted...")
    verify_response = requests.get(f"{BASE_URL}/users/{user_id}/avatar")
    if verify_response.status_code != 200:
        print(f"   ✅ Avatar confirmed deleted\n")
    else:
        print(f"   ❌ Avatar still exists\n")
    
    print("=" * 60)
    print("✅ FILE UPLOAD TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_upload_workflow()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API at http://127.0.0.1:8000")
        print("   Make sure the server is running: python -m uvicorn app.main:app --reload\n")
    except ImportError as e:
        print(f"\n❌ Error: Missing required package: {e}")
        print("   Install PIL: pip install Pillow\n")
