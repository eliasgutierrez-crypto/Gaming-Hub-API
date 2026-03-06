from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from passlib.context import CryptContext

from app.database import get_session
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate, AvatarUploadResponse
from app.utils.file_utils import save_upload_file, delete_file, get_file_url

# Configurar el hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/users", tags=["Users"])


def hash_password(password: str) -> str:
    """Hashear una contraseña usando bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


# Crear usuario
@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """Crear un nuevo usuario."""
    # Comprobar si el nombre de usuario ya existe
    existing_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Comprobar si el correo electrónico ya existe
    existing_email = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# Obtener todos los usuarios
@router.get("/", response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    """Obtener todos los usuarios."""
    users = session.exec(select(User)).all()
    return users


# Obtener usuario por ID
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Obtener un usuario por ID."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Update user
@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_session)):
    """Actualizar un usuario por ID."""
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user.model_dump(exclude_unset=True)
    
    # Hashear la contraseña si se está actualizando
    if "password" in user_data:
        user_data["password"] = hash_password(user_data["password"])
    
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# Delete user
@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """Eliminar un usuario por ID."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}


# Subir avatar de usuario
@router.post("/{user_id}/avatar", response_model=AvatarUploadResponse, tags=["File Upload"])
async def upload_user_avatar(
    user_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload a user avatar image.
    
    Allowed formats: JPEG, PNG
    Maximum size: 5 MB
    
    Returns the URL where the image is served.
    """
    # Verificar que el usuario existe
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Guardar archivo
    file_path = await save_upload_file(file, upload_type="avatar")
    
    # Eliminar avatar antiguo si existe
    if user.avatar_url:
        old_file = user.avatar_url.replace("/static/", "")
        delete_file(old_file)
    
    # Actualizar usuario con nueva URL de avatar
    user.avatar_url = get_file_url(file_path)
    session.add(user)
    session.commit()
    
    # Obtener tamaño del archivo
    file_content = await file.read()
    file_size = len(file_content)
    
    return AvatarUploadResponse(
        message="Avatar uploaded successfully",
        avatar_url=user.avatar_url,
        file_size=file_size
    )


# Obtener avatar de usuario
@router.get("/{user_id}/avatar", tags=["File Upload"])
def get_user_avatar(user_id: int, session: Session = Depends(get_session)):
    """Obtener URL de avatar de usuario."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.avatar_url:
        raise HTTPException(status_code=404, detail="User has no avatar")
    return {"avatar_url": user.avatar_url}


# Eliminar avatar de usuario
@router.delete("/{user_id}/avatar", tags=["File Upload"])
async def delete_user_avatar(user_id: int, session: Session = Depends(get_session)):
    """Eliminar avatar de usuario."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.avatar_url:
        raise HTTPException(status_code=404, detail="User has no avatar")
    
    # Eliminar archivo
    old_file = user.avatar_url.replace("/static/", "")
    delete_file(old_file)
    
    # Actualizar usuario
    user.avatar_url = None
    session.add(user)
    session.commit()
    
    return {"message": "Avatar deleted successfully"}