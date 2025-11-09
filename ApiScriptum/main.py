"""
SCRIPTUM API - Main Application
API de cifrado y descifrado con múltiples algoritmos
"""
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routers import health, vigenere
from app.config import settings

app = FastAPI(
    title="Scriptum API",
    description="""
    API de cifrado y descifrado para la aplicación Scriptum.

    **Algoritmos disponibles:**
    - Vigenère: Cifrado clásico polialfabético
    - AES: Cifrado simétrico moderno (próximamente)

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
            "vigenere": "/vigenere"
        }
    }


# ============================================================================
# ENDPOINTS STUB PARA AES (Próximamente)
# ============================================================================

@app.post("/aes/cifrar/texto")
async def aes_cifrar(text: str, key: str, longitud: int):  # pylint: disable=unused-argument
    """Endpoint stub para cifrado AES de texto (próximamente)"""
    return {
        "message": "Cifrado AES (próximamente)",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/aes/decifrar/texto")
async def aes_decifrar():
    """Endpoint stub para descifrado AES de texto (próximamente)"""
    return {
        "message": "Descifrado AES (próximamente)",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/aes/cifrar/file")
async def aes_cifrar_file(file: UploadFile, key: str, longitud: int):  # pylint: disable=unused-argument
    """Endpoint stub para cifrado AES de archivos (próximamente)"""
    return {
        "message": "Cifrado AES de archivo (próximamente)",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/aes/decifrar/file")
async def aes_decifrar_file():
    """Endpoint stub para descifrado AES de archivos (próximamente)"""
    return {
        "message": "Decifrado AES de archivo (próximamente)",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
