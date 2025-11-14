"""
SCRIPTUM API - Main Application
API de cifrado y descifrado con múltiples algoritmos
"""
import os
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


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

# Headers sensibles que no deben ser registrados
SENSITIVE_HEADERS = {
    'authorization',
    'cookie',
    'x-api-key',
    'x-auth-token',
    'x-csrf-token',
    'proxy-authorization',
    'www-authenticate',
    'set-cookie'
}

def anonymize_ip(client_host: str) -> str:
    """
    Anonimiza la dirección IP del cliente para proteger la privacidad.

    Enmascara los últimos dos octetos de direcciones IPv4 o toda la dirección
    si es IPv6 u otro formato.

    Args:
        client_host: Dirección IP del cliente a anonimizar.

    Returns:
        Dirección IP anonimizada (ej: "192.168.xxx.xxx" o "unknown").
    """
    if not client_host:
        return "unknown"
    # Anonimizar los últimos octetos de IPv4 o segmentos de IPv6
    parts = client_host.split('.')
    if len(parts) == 4:  # IPv4
        return f"{parts[0]}.{parts[1]}.xxx.xxx"
    else:  # IPv6 u otro formato
        return "xxx.xxx.xxx.xxx"

def sanitize_url(url: str) -> str:
    """
    Elimina los parámetros de consulta de una URL para el logging.

    Esto previene que información sensible en los query parameters
    sea registrada en los logs.

    Args:
        url: URL completa con posibles query parameters.

    Returns:
        URL sin query parameters (solo el path base).
    """
    return str(url).split('?')[0]

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Registra las peticiones HTTP entrantes con IP anonimizada y headers filtrados.

    Logs incoming requests with anonymized client IP and filtered headers.

    Args:
        request: Objeto Request de FastAPI con la petición entrante.
        call_next: Función para pasar la petición al siguiente middleware.

    Returns:
        Response: Respuesta HTTP del endpoint procesado.
    """
    logger.info("=== Incoming Request ===")
    logger.info("Method: %s", request.method)
    logger.info("URL: %s", sanitize_url(str(request.url)))

    # Anonimizar IP del cliente
    if request.client:
        anonymized_ip = anonymize_ip(request.client.host)
        logger.info("Client: %s", anonymized_ip)

    # Registrar solo headers no sensibles
    logger.info("Headers (filtered):")
    for name, value in request.headers.items():
        if name.lower() not in SENSITIVE_HEADERS:
            logger.info("  %s: %s", name, value)
        else:
            logger.info("  %s: [FILTERED]", name)

    response = await call_next(request)

    logger.info("Response Status: %s", response.status_code)
    logger.info("======================")
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
    """
    Endpoint raíz con información general de la API.

    Retorna información básica sobre la API de Scriptum,
    incluyendo la versión, descripción y enlaces a los
    principales endpoints disponibles.

    Returns:
        dict: Información de la API con enlaces a endpoints principales.
    """
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
