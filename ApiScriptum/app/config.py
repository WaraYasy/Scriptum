"""
SCRIPTUM API 
Configuración de la aplicación
Autor: Wara - Arantxa
"""
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuración de la aplicación
    """
    APP_NAME: str = "Scriptum API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging
    LOG_DIR: Path = Path(__file__).parent.parent / "var" / "logs"

    # Database
    # DATABASE_URL: str = "sqlite:///./scriptum.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
