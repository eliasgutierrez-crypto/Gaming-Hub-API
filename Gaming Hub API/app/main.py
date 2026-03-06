from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from app.database import create_db_and_tables

# Importa los modelos para que SQLModel cree las tablas
from app.models.user import User
from app.models.game import Game
from app.models.review import Review

# Importar utilidades de caché
from app.utils.cache_utils import cache

# Enrutadores
from app.routers.users import router as users_router
from app.routers.games import router as games_router
from app.routers.reviews import router as reviews_router

# Configurar registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Eventos de ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Inicio
    logger.info("Starting up Gaming Hub API...")
    create_db_and_tables()
    logger.info("Database tables created")
    
    # Inicializar caché de Redis
    if cache.is_connected():
        logger.info("Redis cache connected successfully")
    else:
        logger.warning("Redis cache not available - endpoints will work without caching")
    
    yield
    # Apagado
    logger.info("Shutting down Gaming Hub API...")


app = FastAPI(
    title="Gaming Hub API",
    description="A modern REST API for managing games, users, and reviews",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir enrutadores
app.include_router(users_router)
app.include_router(games_router)
app.include_router(reviews_router)

# Montar archivos estáticos para servir imágenes
app.mount("/static", StaticFiles(directory="static"), name="static")


# Punto de entrada raíz
@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint - API status check."""
    return {
        "message": "Gaming Hub API running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}