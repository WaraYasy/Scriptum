# Sistema de Logging - Scriptum API

## Resumen

El sistema de logging de Scriptum API está diseñado para separar operación normal de debugging:

- **`scriptum.log`**: Operaciones (INFO, WARNING, ERROR, CRITICAL)
- **`scriptum-debug.log`**: Debugging detallado (solo DEBUG)

## Configuración

### Inicialización (main.py)
```python
from app.logging_config import setup_logging

# Inicializar al arrancar la aplicación
setup_logging()
```

### Uso en cualquier módulo
```python
import logging

# Obtener logger para el módulo actual
logger = logging.getLogger(__name__)

# Usar el logger
logger.debug("Detalle técnico interno")        # → scriptum-debug.log
logger.info("Operación completada")            # → scriptum.log
logger.warning("Validación fallida")           # → scriptum.log
logger.error("Error en operación")             # → scriptum.log
```

## Estructura de Archivos

```
logs/
├── scriptum.log          # Operaciones (INFO/WARNING/ERROR/CRITICAL)
├── scriptum-debug.log    # Debugging (solo DEBUG)
└── README.md             # Documentación
```

## Ejemplos de Salida

### scriptum.log
```
2025-11-10 10:30:45 - app.routers.aes - INFO - Iniciando cifrado de texto - Tipo: AES-256, Longitud: 256 caracteres
2025-11-10 10:30:45 - app.services.aes - INFO - Generando clave desde password - Tipo: AES-256
2025-11-10 10:30:45 - app.services.aes - INFO - Iniciando cifrado AES - Tipo: AES-256, Tamaño de datos: 256 bytes
2025-11-10 10:30:45 - app.services.aes - INFO - Cifrado completado exitosamente - Datos cifrados: 256 bytes
2025-11-10 10:30:45 - app.routers.aes - INFO - Texto cifrado exitosamente - Original: 256 bytes, Cifrado: 384 bytes
2025-11-10 10:30:46 - app.routers.aes - WARNING - Extensión no soportada: .exe
2025-11-10 10:30:47 - app.services.aes - ERROR - Tamaño de clave inválido - Esperado: 32 bytes, Recibido: 16 bytes
```

### scriptum-debug.log
```
2025-11-10 10:30:45 - app.services.aes - DEBUG - Salt aleatorio generado - Tamaño: 16 bytes
2025-11-10 10:30:45 - app.services.aes - DEBUG - Usando salt proporcionado - Tamaño: 16 bytes
2025-11-10 10:30:45 - app.services.aes - DEBUG - Paquete decodificado de base64 - Tamaño total: 1052 bytes
2025-11-10 10:30:45 - app.services.aes - DEBUG - Datos desempaquetados - Nonce: 12 bytes, Cifrado: 1024 bytes, Tag: 16 bytes
2025-11-10 10:30:46 - app.routers.aes - DEBUG - Validando archivo: documento.pdf
2025-11-10 10:30:46 - app.routers.aes - DEBUG - Archivo validado correctamente: documento.pdf (2048 bytes)
```

## Ventajas

✅ **Separación clara**: Operaciones vs debugging técnico  
✅ **Producción limpia**: `scriptum.log` sin ruido de debugging  
✅ **Desarrollo facilitado**: `scriptum-debug.log` con detalles internos  
✅ **Rendimiento**: DEBUG solo se escribe en archivo, no en consola  
✅ **Trazabilidad**: Nombre del módulo identifica el origen  
✅ **Centralizado**: Una sola configuración para toda la app  

## Cuándo usar cada nivel

| Nivel | Cuándo usar | Ejemplo |
|-------|-------------|---------|
| **DEBUG** | Detalles técnicos internos | `logger.debug("Salt generado: %d bytes", len(salt))` |
| **INFO** | Operaciones normales importantes | `logger.info("Cifrado completado exitosamente")` |
| **WARNING** | Situaciones inusuales pero manejables | `logger.warning("Extensión no soportada: %s", ext)` |
| **ERROR** | Errores que impiden la operación | `logger.error("Clave inválida", exc_info=True)` |
| **CRITICAL** | Fallos críticos del sistema | `logger.critical("Base de datos no disponible")` |

## Cambiar Configuración

Edita `app/logging_config.py` para:
- Cambiar formato de logs
- Añadir más handlers
- Modificar niveles de log
- Implementar rotación de archivos
- Añadir filtros personalizados

## Monitoreo

### Desarrollo
```bash
# Ver todos los logs en tiempo real
tail -f logs/scriptum.log

# Ver solo debugging
tail -f logs/scriptum-debug.log

# Ver ambos simultáneamente
tail -f logs/scriptum.log logs/scriptum-debug.log
```

### Producción
```bash
# Ver logs principales
tail -f logs/scriptum.log

# Buscar errores
grep "ERROR" logs/scriptum.log

# Ver estadísticas
wc -l logs/scriptum.log
```

## Probar el Sistema

```bash
python test_logging.py
```

Esto generará logs de prueba en todos los niveles y te mostrará el contenido de ambos archivos.
