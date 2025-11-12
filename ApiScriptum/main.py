"""
SCRIPTUM API - Main Application
API de cifrado y descifrado con múltiples algoritmos
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.routers import health, vigenere, aes
from app.config import settings
from app.logging_config import setup_logging

# Inicializar logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scriptum API",
    description="""
    API de cifrado y descifrado para la aplicación Scriptum.

    **Algoritmos disponibles:**
    - Vigenère: Cifrado clásico polialfabético
    - AES: Cifrado simétrico moderno (AES-128, AES-192, AES-256)

    **Características:**
    - Cifrado/descifrado de texto
    - Cifrado/descifrado de archivos .txt
    - Descarga de archivos procesados
    """,
    version="1.0.0",
    contact={
        "name": "Scriptum Team",
        "email": "scriptum@example.com"
    }
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"=== Incoming Request ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Client: {request.client}")
    logger.info(f"Headers:")
    for name, value in request.headers.items():
        logger.info(f"  {name}: {value}")

    response = await call_next(request)

    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"======================")
    return response

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, tags=["Health"])
app.include_router(vigenere.router)
app.include_router(aes.router)

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Bienvenido a Scriptum API",
        "version": "1.0.0",
        "description": "API de cifrado y descifrado",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "vigenere": "/vigenere",
            "aes": "/aes"
        }
    }

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
