from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Configuración de la aplicación
    """
    APP_NAME: str = "Scriptum API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database (ejemplo para cuando lo necesites)
    # DATABASE_URL: str = "sqlite:///./scriptum.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
