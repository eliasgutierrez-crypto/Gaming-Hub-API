  # API de Gaming Hub

Una API REST moderna y bien estructurada para gestionar juegos, usuarios y reseñas, desarrollada con **FastAPI** y **SQLModel**.

## Descripción del dominio

Este proyecto representa un servicio para catálogos de videojuegos donde los usuarios pueden registrarse, gestionar su perfil, subir avatares y crear reseñas valorando juegos en una escala de 1 a 10. Además de las operaciones CRUD sobre usuarios, juegos y reseñas, incorpora un sistema de recomendaciones basado en el historial de puntuaciones y estadísticas globales. También permite subir portadas de juegos y avatares de usuarios.

## Características

- 👥 **Gestión de usuarios** – Crear, leer, actualizar y eliminar cuentas con hash de contraseñas
- 🎮 **Catálogo de juegos** – Manejar videojuegos con información detallada
- ⭐ **Sistema de reseñas** – Los usuarios pueden calificar y comentar juegos (escala 1–10)
- 🤖 **Recomendaciones inteligentes** – Sugerencias de juegos basadas en el historial de reseñas
- 🔐 **Seguridad** – Hash de contraseñas con bcrypt y validaciones exhaustivas
- 📚 **Documentación interactiva** – Documentación automática via Swagger UI y ReDoc
- 🗄️ **Base de datos** – SQLite por defecto, preparado para PostgreSQL en producción

## Tech Stack

- **Framework**: FastAPI 0.135+
- **Base de datos**: SQLModel (ORM SQLAlchemy con Pydantic)
- **Autenticación**: bcrypt para hash de contraseñas
- **Servidor**: Uvicorn
- **Validación**: Pydantic v2

## Instalación

### Requisitos previos
- Python 3.10+
- pip

### Configuración del proyecto

1. **Clonar o descargar el repositorio**
   ```bash
   cd Gaming\ Hub\ API
   ```

2. **Crear un entorno virtual (opcional pero recomendado)**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # En Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   - Editar el archivo `.env` (opcional, se proporcionan valores por defecto)
   ```bash
   # Configuración SQLite por defecto
   DATABASE_URL=sqlite:///gaminghub.db
   DEBUG=True
   ```

### Instalación y arranque de Redis

El proyecto utiliza Redis para el cacheo de endpoints. Puedes instalarlo localmente o usar una instancia en la nube.

- **Windows**: descarga el zip de Redis desde https://redis.io/download y ejecuta `redis-server.exe`. También hay scripts `.bat` en el directorio `redis/` que configuran el servicio.
- **Linux/macOS**: usa tu gestor de paquetes, por ejemplo:
  ```bash
  sudo apt install redis-server    # Debian/Ubuntu
  brew install redis              # macOS con Homebrew
  ```

Una vez instalado, inicia el servicio:
```bash
redis-server --daemonize yes        # arranca en segundo plano
# o en Windows simplemente ejecuta redis-server.exe
```
Asegúrate de que Redis escuche en `localhost:6379` o ajusta la configuración si es necesario.

## Ejecución de la aplicación

### Modo de desarrollo

Inicia el servidor con recarga automática:

```bash
python -m uvicorn app.main:app --reload
```

La API estará disponible en: `http://127.0.0.1:8000`

### Modo de producción

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Documentación de la API

Una vez en funcionamiento, accede a la documentación interactiva:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Endpoints de la API

### Usuarios
- `POST /users/` - Crear un nuevo usuario
- `GET /users/` - Obtener todos los usuarios
- `GET /users/{user_id}` - Obtener un usuario específico
- `PUT /users/{user_id}` - Actualizar un usuario
- `DELETE /users/{user_id}` - Eliminar un usuario

### Juegos
- `POST /games/` - Crear un nuevo juego
- `GET /games/` - Obtener todos los juegos
- `GET /games/{game_id}` - Obtener un juego específico
- `PUT /games/{game_id}` - Actualizar un juego
- `DELETE /games/{game_id}` - Eliminar un juego

### Reseñas
- `POST /reviews/` - Crear una nueva reseña
- `GET /reviews/` - Obtener todas las reseñas
- `GET /reviews/{review_id}` - Obtener una reseña específica
- `PUT /reviews/{review_id}` - Actualizar una reseña
- `DELETE /reviews/{review_id}` - Eliminar una reseña

## Ejemplos de uso

### Crear un usuario
```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
  }'
```

### Crear un juego
```bash
curl -X POST http://127.0.0.1:8000/games/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Legend of Zelda: Breath of the Wild",
    "genre": "Action-Adventure",
    "release_year": 2017,
    "developer": "Nintendo EPD",
    "publisher": "Nintendo",
    "description": "An epic action-adventure game"
  }'
```

### Crear una reseña
```bash
curl -X POST http://127.0.0.1:8000/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 9,
    "comment": "Amazing game! The open world is incredible.",
    "user_id": 1,
    "game_id": 1
  }'
```

## Estructura del proyecto

```
Gaming Hub API/
├── app/
│   ├── main.py              # Configuración de la aplicación FastAPI
│   ├── database.py          # Configuración de base de datos
│   ├── models/              # Modelos de datos SQLModel
│   │   ├── user.py
│   │   ├── game.py
│   │   └── review.py
│   ├── schemas/             # Esquemas Pydantic para peticiones/respuestas
│   │   ├── user_schema.py
│   │   ├── game_schema.py
│   │   └── review_schema.py
│   ├── routers/             # Endpoints de la API
│   │   ├── users.py
│   │   ├── games.py
│   │   └── reviews.py
│   └── services/            # Lógica de negocio
│       └── recommendation_service.py
├── requirements.txt         # Dependencias de Python
├── .env                     # Variables de entorno
└── README.md               # Este archivo
```

## Base de datos

### SQLite (desarrollo)
- Base de datos por defecto: `gaminghub.db`
- Creada automáticamente en la primera ejecución
- Ideal para desarrollo y pruebas

### PostgreSQL (producción)
Actualiza el archivo `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/gaminghub
```

## Características de seguridad

- ✅ Hash de contraseñas con bcrypt
- ✅ Validación de entrada con Pydantic
- ✅ Configuración CORS lista
- ✅ Prevención de usuarios/correos duplicados
- ✅ Validación de claves foráneas para reseñas
- ✅ Protección contra inyección SQL (mediante SQLAlchemy)

## Manejo de errores

La API devuelve códigos HTTP y mensajes claros:

- `200` - Éxito
- `201` - Creado
- `400` - Petición incorrecta (error de validación)
- `404` - No encontrado
- `500` - Error del servidor

Ejemplo de respuesta en caso de error:
```json
{
  "detail": "User not found"
}
```

## Sistema de recomendaciones

El archivo `recommendation_service.py` proporciona recomendaciones inteligentes de juegos:

```python
from app.services.recommendation_service import get_game_recommendations

# Obtener 5 recomendaciones para el usuario 1
recommendations = get_game_recommendations(
    user_id=1,
    session=session,
    limit=5
)
```

### Algoritmo
1. Encuentra juegos que el usuario calificó alto (≥7 por defecto)
2. Extrae géneros favoritos de esos juegos
3. Recomienda juegos no reseñados de esos géneros
4. Si no hay preferencias, vuelve a juegos recientes populares

## Desarrollo

### Ejecutar pruebas
Para añadir soporte de testing, instala pytest:
```bash
pip install pytest pytest-asyncio
```

### Calidad de código
El código cumple con:
- Guías de estilo PEP 8
- Anotaciones de tipo en todo el código
- Docstrings completos
- Manejo adecuado de errores

## Problemas comunes

### Puerto ya en uso
```bash
# Cambiar el puerto
python -m uvicorn app.main:app --reload --port 8001
```

### Base de datos bloqueada (SQLite)
- Reiniciar la aplicación
- Verificar procesos uvicorn múltiples

### Errores de importación
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## Mejoras futuras

- [ ] Autenticación y autorización JWT
- [ ] Sistema de seguidores entre usuarios
- [ ] Listas de deseos de juegos
- [ ] Filtrado y búsqueda avanzados
- [ ] Mejoras de paginación
- [ ] Verificación de correo electrónico
- [ ] Limitación de tasa (rate limiting)
- [ ] Caching con Redis

## Contribución

1. Crea una rama de característica
2. Realiza tus cambios
3. Prueba a fondo
4. Envía un pull request

## Licencia

Este proyecto es de código abierto bajo la licencia MIT.

## Soporte

Para problemas o preguntas, abre un issue en el repositorio.

---

**Construido con ❤️ usando FastAPI**
