"""
Configuración centralizada de logging para Scriptum API
"""
import logging
import sys
from app.config import settings


def setup_logging():
    """
    Configura el sistema de logging de la aplicación.
    
    Crea dos archivos de log:
    - scriptum.log: INFO, WARNING y ERROR
    - scriptum-debug.log: DEBUG (información detallada para desarrollo)
    """
    # Crear directorio de logs si no existe
    settings.LOG_DIR.mkdir(exist_ok=True)
      
    # Formato de logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para archivo general (INFO, WARNING, ERROR, CRITICAL)
    file_handler = logging.FileHandler(
        settings.LOG_DIR / "scriptum.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Handler para archivo de debug (solo DEBUG)
    debug_handler = logging.FileHandler(
        settings.LOG_DIR / "scriptum-debug.log",
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(log_format, date_format))
    # Filtro para que solo capture DEBUG (no INFO ni superiores)
    debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG)
    
    # Handler para consola (INFO y superior)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        '%H:%M:%S'
    ))
    
    # Añadir handlers al logger raíz
    root_logger.addHandler(file_handler)
    root_logger.addHandler(debug_handler)
    root_logger.addHandler(console_handler)
    
    # Logger inicial
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging inicializado correctamente")
    logger.info("Logs guardados en: %s", settings.LOG_DIR)


# Función helper para obtener logger
def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado.
    
    Args:
        name: Nombre del módulo (generalmente __name__)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
