"""
Utilidades de carga de archivos para manejar imágenes y validaciones.
"""

import os
import mimetypes
from pathlib import Path
from fastapi import UploadFile, HTTPException
from datetime import datetime
import uuid


# Configuración
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
UPLOAD_DIRS = {
    "avatar": "static/avatars",
    "cover": "static/covers"
}


def get_file_extension(filename: str) -> str:
    """Get file extension without the dot."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """
    Validate image file.
    
    Args:
        file: Uploaded file from FastAPI
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Comprobar extensión de archivo
        extension = get_file_extension(file.filename)
        if extension not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Intentar obtener tipo MIME
        mime_type, _ = mimetypes.guess_type(file.filename)
        
        # Verificación adicional de tipo MIME
        if mime_type and mime_type not in ALLOWED_MIME_TYPES:
            return False, f"Invalid file type. Allowed: JPEG, PNG"
        
        return True, ""
    except Exception as e:
        return False, f"Error validating file: {str(e)}"


async def save_upload_file(
    file: UploadFile,
    upload_type: str = "avatar"
) -> str:
    """
    Save uploaded file to disk with validations.
    
    Args:
        file: Uploaded file from FastAPI
        upload_type: Type of upload ("avatar" or "cover")
        
    Returns:
        Filename saved (relative path for serving)
        
    Raises:
        HTTPException: If validation fails or save fails
    """
    # Validar tipo de subida
    if upload_type not in UPLOAD_DIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid upload type. Allowed: {list(UPLOAD_DIRS.keys())}"
        )
    
    # Validar archivo
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Leer contenido para comprobar tamaño
    try:
        file_content = await file.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
            )
        
        # Restablecer posición del archivo
        await file.seek(0)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    try:
        # Crear nombre de archivo seguro con UUID para evitar colisiones
        extension = get_file_extension(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"{timestamp}_{unique_id}.{extension}"
        
        # Obtener directorio de subida
        upload_dir = Path(UPLOAD_DIRS[upload_type])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo
        file_path = upload_dir / new_filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Devolver ruta relativa para servir
        relative_path = f"{upload_type}/{new_filename}"
        return relative_path
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )


async def delete_file(file_path: str) -> bool:
    """
    Delete a file from the static directory.
    
    Args:
        file_path: Relative path from static folder (e.g., "avatars/filename.jpg")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        full_path = Path("static") / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")
        return False


def get_file_url(file_path: str) -> str:
    """
    Get the serving URL for a file.
    
    Args:
        file_path: Relative path (e.g., "avatars/filename.jpg")
        
    Returns:
        URL path for serving
    """
    return f"/static/{file_path}"
