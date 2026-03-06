from app.models.user import User
from app.models.game import Game
from app.models.review import Review
import inspect

print("User fields:")
for field_name, field_info in User.model_fields.items():
    print(f"  {field_name}: {field_info}")

print("\nUser SQLModel fields:")
for col in User.__table__.columns:
    print(f"  {col.name}: {col.type}")
