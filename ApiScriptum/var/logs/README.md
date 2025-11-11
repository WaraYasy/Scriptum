# Directorio de Logs - Scriptum API

Este directorio contiene los archivos de logs generados por la aplicación.

## Archivos de Log

### `scriptum.log`
**Archivo principal con logs de operación (INFO, WARNING, ERROR, CRITICAL)**

Registra:
- ✅ Todas las peticiones HTTP a los endpoints
- ✅ Operaciones de cifrado/descifrado (AES, Vigenère)
- ✅ Generación de claves y validaciones
- ✅ Validaciones de archivos (extensiones, tamaños)
- ✅ Operaciones exitosas y flujo normal de la aplicación
- ⚠️ Warnings de validaciones fallidas
- ❌ Errores en operaciones

**Úsalo para:** Monitoreo general, análisis de uso, seguimiento de operaciones, detección de errores

### `scriptum-debug.log`
**Archivo de debugging con información detallada (solo DEBUG)**

Registra únicamente:
- 🔍 Información detallada de validaciones
- 🔍 Tamaños de componentes internos (nonce, tag, salt)
- 🔍 Flujo interno de funciones
- 🔍 Detalles de procesamiento de archivos
- � Información técnica para desarrollo

**Úsalo para:** Debugging, desarrollo, análisis profundo de problemas, optimización

## Niveles de Log

| Nivel | Descripción | Dónde se registra |
|-------|-------------|-------------------|
| **DEBUG** | Información técnica detallada para debugging | `scriptum-debug.log` solamente |
| **INFO** | Operaciones normales y flujo de ejecución | `scriptum.log` + consola |
| **WARNING** | Validaciones fallidas, situaciones inusuales | `scriptum.log` + consola |
| **ERROR** | Errores en operaciones | `scriptum.log` + consola |
| **CRITICAL** | Errores críticos del sistema | `scriptum.log` + consola |

## Formato de Log

### Archivos
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Ejemplo en scriptum.log:**
```
2025-11-10 10:30:45 - app.services.aes - INFO - Iniciando cifrado AES - Tipo: AES-256, Tamaño de datos: 1024 bytes
2025-11-10 10:30:45 - app.services.aes - INFO - Cifrado completado exitosamente - Datos cifrados: 1024 bytes
2025-11-10 10:30:46 - app.routers.aes - WARNING - Extensión no soportada: .exe para archivo: malware.exe
2025-11-10 10:30:47 - app.services.aes - ERROR - Tamaño de clave inválido - Esperado: 32 bytes, Recibido: 16 bytes
```

**Ejemplo en scriptum-debug.log:**
```
2025-11-10 10:30:45 - app.services.aes - DEBUG - Salt aleatorio generado - Tamaño: 16 bytes
2025-11-10 10:30:45 - app.services.aes - DEBUG - Datos desempaquetados - Nonce: 12 bytes, Cifrado: 1024 bytes, Tag: 16 bytes
2025-11-10 10:30:46 - app.routers.aes - DEBUG - Validando archivo: documento.pdf
2025-11-10 10:30:46 - app.routers.aes - DEBUG - Archivo validado correctamente: documento.pdf (2048 bytes)
```

### Consola (más compacta)
```
%(asctime)s - %(levelname)s - %(message)s
```

Ejemplo:
```
10:30:45 - INFO - Iniciando cifrado AES - Tipo: AES-256, Tamaño de datos: 1024 bytes
10:30:46 - ERROR - Tamaño de clave inválido
```

## Configuración

El sistema de logging está centralizado en:
- **Configuración**: `app/logging_config.py` (configuración centralizada)
- **Inicialización**: `main.py` (llama a `setup_logging()`)
- **Uso**: Todos los módulos usan `logging.getLogger(__name__)`

## Ventajas del Sistema de Dos Niveles

✅ **Separación clara**: Operación normal vs debugging  
✅ **Producción limpia**: `scriptum.log` sin ruido de debugging  
✅ **Desarrollo facilitado**: `scriptum-debug.log` con detalles técnicos  
✅ **Rendimiento**: DEBUG solo se escribe en archivo, no en consola  
✅ **Logging por módulo**: El nombre del módulo (`%(name)s`) te dice el origen  
✅ **Fácil activación**: Cambiar nivel de log en un solo lugar  

## Uso en Desarrollo vs Producción

### Desarrollo
- `scriptum.log`: Monitorear operaciones y errores
- `scriptum-debug.log`: Ver todos los detalles internos
- Consola: Ver flujo en tiempo real

### Producción
- `scriptum.log`: Único archivo a monitorear
- `scriptum-debug.log`: Revisar solo cuando hay problemas complejos
- Consola: Normalmente redirigida a archivo de sistema

## Comandos Útiles

```bash
# Ver todos los logs en tiempo real
tail -f logs/scriptum.log

# Ver solo debugging en tiempo real
tail -f logs/scriptum-debug.log

# Ver ambos simultáneamente
tail -f logs/scriptum.log logs/scriptum-debug.log

# Buscar errores
grep "ERROR" logs/scriptum.log

# Buscar operaciones específicas
grep "AES-256" logs/scriptum.log

# Ver estadísticas de logs
wc -l logs/scriptum.log
wc -l logs/scriptum-debug.log

# Limpiar logs antiguos (cuidado!)
> logs/scriptum.log
> logs/scriptum-debug.log
```

## Rotación de Logs (Recomendación para Producción)

Para evitar que los archivos crezcan demasiado:

```python
from logging.handlers import RotatingFileHandler

# En logging_config.py, reemplazar FileHandler por:
handler = RotatingFileHandler(
    'scriptum.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,           # Mantener 5 archivos antiguos
    encoding='utf-8'
)
```

Esto creará:
- `scriptum.log` (actual)
- `scriptum.log.1` (anterior)
- `scriptum.log.2` (más antiguo)
- ... hasta `scriptum.log.5`

## Notas

- Los archivos `.log` están excluidos del control de versiones (`.gitignore`)
- Los logs se escriben en archivo Y consola simultáneamente (excepto DEBUG)
- El encoding usado es UTF-8 para soportar caracteres especiales
- Se usa formato "lazy" (`%s`) en lugar de f-strings para optimizar rendimiento
- El directorio se crea automáticamente si no existe
- DEBUG solo va a archivo, no a consola (para evitar ruido)
