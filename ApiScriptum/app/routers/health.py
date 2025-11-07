from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Scriptum API"
    }
