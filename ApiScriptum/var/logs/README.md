# Directorio de Logs - Scriptum API

Este directorio contiene los archivos de logs generados por la aplicación.

## Archivos de Log

### `scriptum.log`
**Archivo principal con logs de operación (INFO, WARNING, ERROR, CRITICAL)**

**⚙️ Rotación automática por día:**
- **Frecuencia**: Cada día a medianoche
- **Histórico**: **30 días** de logs guardados
- **Formato de archivo**: `scriptum.log.2025-11-10`, `scriptum.log.2025-11-09`, etc.
- **Espacio aproximado**: Depende del uso (~1-10 MB por día típicamente)

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

**⚙️ Rotación automática por día:**
- **Frecuencia**: Cada día a medianoche
- **Histórico**: **7 días** de logs guardados
- **Formato de archivo**: `scriptum-debug.log.2025-11-10`, `scriptum-debug.log.2025-11-09`, etc.
- **Espacio aproximado**: Depende del uso (~500 KB - 5 MB por día típicamente)

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

## Rotación de Logs (Ya Configurada ✅)

La rotación está **activa con rotación diaria automática**:

### ¿Cómo funciona?

Cada día a **medianoche (00:00)**:

1. El archivo actual se renombra con la fecha del día anterior
   - `scriptum.log` → `scriptum.log.2025-11-10`
   - `scriptum-debug.log` → `scriptum-debug.log.2025-11-10`
2. Se crean nuevos archivos vacíos para el nuevo día
3. Los archivos más antiguos se eliminan automáticamente:
   - `scriptum.log`: después de 30 días
   - `scriptum-debug.log`: después de 7 días

### Ejemplo de estructura en disco:

```
var/logs/
├── scriptum.log                    # Hoy (11 nov) - Escritura activa
├── scriptum.log.2025-11-10         # Ayer
├── scriptum.log.2025-11-09         # Hace 2 días
├── scriptum.log.2025-11-08         # Hace 3 días
├── ...                             # ... hasta 30 días atrás
├── scriptum.log.2025-10-12         # Hace 30 días ← Se borra mañana
│
├── scriptum-debug.log              # Hoy (11 nov) - Escritura activa
├── scriptum-debug.log.2025-11-10   # Ayer
├── scriptum-debug.log.2025-11-09   # Hace 2 días
├── ...                             # ... hasta 7 días atrás
└── scriptum-debug.log.2025-11-04   # Hace 7 días ← Se borra mañana
```

### Ventajas de rotación por fecha:

✅ **Fácil búsqueda**: "¿Qué pasó el 10 de noviembre?" → Ver `scriptum.log.2025-11-10`  
✅ **Histórico claro**: Cada archivo representa un día completo  
✅ **Depuración simple**: Comparar logs de diferentes días  
✅ **Predecible**: Sabes exactamente qué logs tienes (últimos 30/7 días)  
✅ **Organizado**: No hay archivos .1, .2, .3 confusos  

### Configuración actual:

| Archivo | Rotación | Histórico | Archivos guardados |
|---------|----------|-----------|-------------------|
| **scriptum.log** | Diaria (medianoche) | 30 días | ~31 archivos (hoy + 30 días) |
| **scriptum-debug.log** | Diaria (medianoche) | 7 días | ~8 archivos (hoy + 7 días) |

### Ver logs de una fecha específica:

```bash
# Ver logs del 10 de noviembre
cat var/logs/scriptum.log.2025-11-10

# Ver logs de debug del 9 de noviembre
cat var/logs/scriptum-debug.log.2025-11-09

# Buscar errores en fecha específica
grep "ERROR" var/logs/scriptum.log.2025-11-10

# Ver todos los logs de la última semana
ls -lt var/logs/scriptum.log.* | head -7
```

### Cambiar configuración:

Edita `app/logging_config.py`:

```python
# Para scriptum.log
file_handler = TimedRotatingFileHandler(
    settings.LOG_DIR / "scriptum.log",
    when='midnight',      # 'midnight', 'H' (horas), 'D' (días), 'W0'-'W6' (día semana)
    interval=1,           # Cada cuánto (1 día, 2 días, etc.)
    backupCount=30,       # Cambiar días de histórico aquí (30, 60, 90, etc.)
    encoding='utf-8',
    utc=False
)

# Para scriptum-debug.log
debug_handler = TimedRotatingFileHandler(
    settings.LOG_DIR / "scriptum-debug.log",
    when='midnight',
    interval=1,
    backupCount=7,        # Cambiar días de histórico aquí (7, 14, 30, etc.)
    encoding='utf-8',
    utc=False
)
```

### Otras opciones de rotación:

| `when` | Descripción | Ejemplo |
|--------|-------------|---------|
| `'S'` | Segundos | Cada N segundos |
| `'M'` | Minutos | Cada N minutos |
| `'H'` | Horas | Cada N horas |
| `'D'` | Días | Cada N días |
| `'midnight'` | Medianoche | Cada día a las 00:00 ⭐ |
| `'W0'`-`'W6'` | Día de semana | Lunes (W0) a Domingo (W6) |

## Notas

- Los archivos `.log` están excluidos del control de versiones (`.gitignore`)
- Los logs se escriben en archivo Y consola simultáneamente (excepto DEBUG)
- El encoding usado es UTF-8 para soportar caracteres especiales
- Se usa formato "lazy" (`%s`) en lugar de f-strings para optimizar rendimiento
- El directorio se crea automáticamente si no existe
- DEBUG solo va a archivo, no a consola (para evitar ruido)
