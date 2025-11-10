"""
SCRIPTUM API - Main Application
API de cifrado y descifrado con múltiples algoritmos
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routers import health, vigenere, aes
from app.config import settings
from app.logging_config import setup_logging

# Inicializar logging
setup_logging()

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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
