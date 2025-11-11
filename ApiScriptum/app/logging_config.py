"""
Configuración centralizada de logging para Scriptum API
"""
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from app.config import settings


def setup_logging():
    """
    Configura el sistema de logging de la aplicación.
    
    Crea dos archivos de log con rotación diaria automática:
    - scriptum.log: INFO, WARNING y ERROR (rotación diaria, 30 días de histórico)
    - scriptum-debug.log: DEBUG (rotación diaria, 7 días de histórico)
    
    Rotación: A medianoche cada día se crea un nuevo archivo y el anterior
    se renombra con la fecha (ej: scriptum.log.2025-11-10)
    """
    # Crear directorio de logs si no existe (crea directorios padres si es necesario)
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
      
    # Formato de logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para archivo general con rotación diaria (INFO, WARNING, ERROR, CRITICAL)
    # Rota a medianoche, mantiene 30 días de histórico
    file_handler = TimedRotatingFileHandler(
        settings.LOG_DIR / "scriptum.log",
        when='midnight',          # Rotar a medianoche
        interval=1,               # Cada 1 día
        backupCount=30,           # Mantener 30 días de histórico
        encoding='utf-8',
        utc=False                 # Usar hora local
    )
    # Formato de sufijo para archivos rotados: scriptum.log.2025-11-10
    file_handler.suffix = ".%Y-%m-%d"
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Handler para archivo de debug con rotación diaria (solo DEBUG)
    # Rota a medianoche, mantiene 7 días de histórico
    debug_handler = TimedRotatingFileHandler(
        settings.LOG_DIR / "scriptum-debug.log",
        when='midnight',          # Rotar a medianoche
        interval=1,               # Cada 1 día
        backupCount=7,            # Mantener 7 días de histórico
        encoding='utf-8',
        utc=False                 # Usar hora local
    )
    # Formato de sufijo para archivos rotados: scriptum-debug.log.2025-11-10
    debug_handler.suffix = ".%Y-%m-%d"
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
    logger.info("Rotación diaria: scriptum.log (30 días), scriptum-debug.log (7 días)")


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
