# 🏗️ ARQUITECTURA DEL MÓDULO VIGENÈRE

**Documentación completa del flujo de datos y capas de la implementación**

---

## 📋 ÍNDICE

1. [Visión General](#visión-general)
2. [Arquitectura en Capas](#arquitectura-en-capas)
3. [Flujo de una Request Completa](#flujo-de-una-request-completa)
4. [Capa 1: Main (Aplicación FastAPI)](#capa-1-main-aplicación-fastapi)
5. [Capa 2: Router (Endpoints HTTP)](#capa-2-router-endpoints-http)
6. [Capa 3: Schemas (Validación)](#capa-3-schemas-validación)
7. [Capa 4: Services (Lógica de Negocio)](#capa-4-services-lógica-de-negocio)
8. [Manejo de Errores](#manejo-de-errores)
9. [Seguridad y Validaciones](#seguridad-y-validaciones)
10. [Lo que Falta por Añadir](#lo-que-falta-por-añadir)

---

## 🎯 VISIÓN GENERAL

La implementación de Vigenère sigue una **arquitectura en capas** (Layered Architecture) que separa responsabilidades:

```
┌─────────────────────────────────────────────────────┐
│  CLIENTE (Frontend, curl, Postman, etc.)           │
└────────────────┬────────────────────────────────────┘
                 │ HTTP Request
                 ▼
┌─────────────────────────────────────────────────────┐
│  CAPA 1: MAIN.PY (FastAPI App + Middleware)        │
│  - CORS                                             │
│  - Configuración global                             │
│  - Registro de routers                              │
└────────────────┬────────────────────────────────────┘
                 │ Route to /vigenere/*
                 ▼
┌─────────────────────────────────────────────────────┐
│  CAPA 2: ROUTER (app/routers/vigenere.py)          │
│  - Endpoints HTTP                                   │
│  - Funciones auxiliares (validaciones)              │
│  - Manejo de archivos                               │
│  - Orquestación                                     │
└────────────────┬────────────────────────────────────┘
                 │ Usa
                 ▼
┌─────────────────────────────────────────────────────┐
│  CAPA 3: SCHEMAS (app/schemas/vigenere.py)         │
│  - Modelos Pydantic                                 │
│  - Validaciones automáticas                         │
│  - Documentación OpenAPI                            │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  CAPA 4: SERVICES (app/services/vigenere.py)       │
│  - Funciones puras                                  │
│  - Algoritmo Vigenère                               │
│  - Utilidades (formateo, validación)                │
└────────────────┬────────────────────────────────────┘
                 │ Return
                 ▼
┌─────────────────────────────────────────────────────┐
│  CLIENTE (Recibe Response JSON)                     │
└─────────────────────────────────────────────────────┘
```

---

## 🏛️ ARQUITECTURA EN CAPAS

### **Principios de Diseño**

1. **Separación de Responsabilidades**: Cada capa tiene una función específica
2. **Unidireccional**: Las capas superiores dependen de las inferiores, no al revés
3. **Funciones Puras en Services**: Sin efectos secundarios, fácil de testear
4. **Validación en Múltiples Niveles**: Pydantic + Funciones auxiliares
5. **Centralización**: Manejo de errores y validaciones reutilizables

---

## 🔄 FLUJO DE UNA REQUEST COMPLETA

### **Ejemplo: Cifrar texto "Hola Mundo" con clave "secreto"**

```bash
curl -X POST "http://localhost:8000/vigenere/cifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{"texto": "Hola Mundo", "clave": "secreto"}'
```

#### **Paso a Paso:**

```
1. REQUEST LLEGA
   ↓
   Cliente envía: {"texto": "Hola Mundo", "clave": "secreto"}

2. MAIN.PY (Capa 1)
   ↓
   - Middleware CORS verifica origen
   - FastAPI enruta a /vigenere/cifrar/texto
   - Busca el router correspondiente

3. ROUTER (Capa 2) - Función cifrar_texto()
   ↓
   a) Pydantic valida el JSON contra CifrarTextoRequest:
      - ✅ texto: "Hola Mundo" (1-1,000,000 chars)
      - ✅ clave: "secreto" (1-1000 chars)

   b) Función auxiliar validar_clave_sin_caracteres_invisibles():
      - Busca caracteres invisibles en "secreto"
      - ✅ No hay caracteres invisibles

   c) Llama al servicio:
      texto_cifrado = cifrar_vigenere("Hola Mundo", "secreto")

4. SERVICES (Capa 4) - Función cifrar_vigenere()
   ↓
   a) formatear_texto("Hola Mundo")
      → "HOLAMUNDO"

   b) validar_y_formatear_clave("secreto")
      → "SECRETO"

   c) ajustar_clave("SECRETO", len("HOLAMUNDO"))
      → "SECRETOSEC" (9 caracteres)

   d) Cifrado letra por letra:
      H + S = Z
      O + E = S
      L + C = N
      A + R = R
      M + E = Q
      U + T = N
      N + O = B
      D + S = V
      O + E = S
      → "ZSNRQNBVS"

5. ROUTER (Capa 2) - Continúa
   ↓
   - Crea CifradoResponse con:
     * texto_cifrado: "ZSNRQNBVS"
     * clave_usada: "SECRETO"
     * texto_original_length: 10

6. MAIN.PY (Capa 1)
   ↓
   - FastAPI serializa la respuesta a JSON
   - Añade headers HTTP

7. RESPONSE ENVIADA
   ↓
   {
     "texto_cifrado": "ZSNRQNBVS",
     "clave_usada": "SECRETO",
     "texto_original_length": 10
   }
```

---

## 📄 CAPA 1: MAIN (Aplicación FastAPI)

**Archivo:** [`main.py`](../main.py)

### **Responsabilidades:**

- ✅ Crear la aplicación FastAPI
- ✅ Configurar middleware (CORS)
- ✅ Registrar routers
- ✅ Configurar documentación OpenAPI

### **Código Clave:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, vigenere
from app.config import settings

# Crear aplicación
app = FastAPI(
    title="Scriptum API",
    description="API de cifrado y descifrado",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTRAR ROUTER VIGENÈRE
app.include_router(health.router, tags=["Health"])
app.include_router(vigenere.router)  # ← Aquí se añade Vigenère

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a Scriptum API",
        "endpoints": {
            "docs": "/docs",
            "vigenere": "/vigenere"
        }
    }
```

### **¿Qué hace el router include?**

```python
app.include_router(vigenere.router)
```

Esto registra **todos los endpoints** definidos en `app/routers/vigenere.py`:
- `POST /vigenere/cifrar/texto`
- `POST /vigenere/descifrar/texto`
- `POST /vigenere/cifrar/file`
- `POST /vigenere/descifrar/file`
- `POST /vigenere/validar-clave`
- `POST /vigenere/descifrar/file/large`

---

## 🛣️ CAPA 2: ROUTER (Endpoints HTTP)

**Archivo:** [`app/routers/vigenere.py`](../app/routers/vigenere.py)

### **Responsabilidades:**

- ✅ Definir endpoints HTTP
- ✅ Validar requests con Pydantic
- ✅ Orquestar llamadas a servicios
- ✅ Manejar errores
- ✅ Formatear responses

### **Estructura del Router:**

```python
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
import logging

from app.schemas.vigenere import (
    CifrarTextoRequest,
    DescifrarTextoRequest,
    CifradoResponse,
    DescifradoResponse,
    ErrorResponse
)
from app.services.vigenere import (
    cifrar_vigenere,
    descifrar_vigenere
)

logger = logging.getLogger(__name__)

# ✅ CREAR ROUTER con prefijo /vigenere
router = APIRouter(prefix="/vigenere", tags=["Vigenère"])

# Constantes
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
SMALL_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
CANARY_SIZE = 1024  # 1 KB
```

### **Funciones Auxiliares (Reutilizables):**

```python
def detectar_caracteres_invisibles(texto: str) -> list:
    """Detecta caracteres invisibles en texto"""
    warnings = []
    for i, char in enumerate(texto):
        if char in CARACTERES_INVISIBLES:
            warnings.append({
                'posicion': i,
                'caracter': f'U+{ord(char):04X}',
                'nombre': CARACTERES_INVISIBLES[char]
            })
    return warnings

async def leer_archivo_seguro(file: UploadFile, max_size: int) -> bytes:
    """Lee archivo con validaciones de seguridad"""
    # 1. Validar extensión
    if not file.filename.endswith('.txt'):
        raise HTTPException(400, detail={"error": "Solo .txt"})

    # 2. Validar tamaño
    contenido = await file.read()
    if len(contenido) > max_size:
        raise HTTPException(413, detail={"error": "Archivo muy grande"})

    # 3. Validar UTF-8
    try:
        contenido.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(400, detail={"error": "No es UTF-8"})

    return contenido

def validar_clave_sin_caracteres_invisibles(clave: str) -> None:
    """Valida que no haya caracteres invisibles"""
    warnings = detectar_caracteres_invisibles(clave)
    if warnings:
        raise HTTPException(400, detail={
            "error": "Clave con caracteres invisibles",
            "caracteres_detectados": warnings
        })

def manejar_error(e: Exception, operacion: str) -> HTTPException:
    """Centraliza manejo de errores"""
    if isinstance(e, HTTPException):
        return e

    if isinstance(e, ValueError):
        logger.warning(f"Error validación: {str(e)}")
        return HTTPException(400, detail={"error": str(e)})

    # Error inesperado - NO exponer detalles
    logger.error(f"Error interno: {str(e)}", exc_info=True)
    return HTTPException(500, detail={"error": "Error interno"})
```

### **Endpoint de Ejemplo:**

```python
@router.post(
    "/cifrar/texto",
    response_model=CifradoResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Cifrar texto con Vigenère"
)
async def cifrar_texto(request: CifrarTextoRequest):
    """
    Cifra un texto con Vigenère

    Args:
        request: Objeto validado con texto y clave

    Returns:
        CifradoResponse con texto cifrado
    """
    try:
        # 1. Validar clave (no caracteres invisibles)
        validar_clave_sin_caracteres_invisibles(request.clave)

        # 2. Cifrar (llamada a services)
        texto_cifrado = cifrar_vigenere(request.texto, request.clave)

        # 3. Crear respuesta
        return CifradoResponse(
            texto_cifrado=texto_cifrado,
            clave_usada=''.join(c.upper() for c in request.clave if c.isalpha()),
            texto_original_length=len(request.texto)
        )
    except Exception as e:
        raise manejar_error(e, "cifrar texto")
```

### **Flujo dentro del endpoint:**

```
1. FastAPI recibe request
   ↓
2. Pydantic valida contra CifrarTextoRequest
   ↓
3. validar_clave_sin_caracteres_invisibles()
   ↓
4. cifrar_vigenere() ← Llamada a services
   ↓
5. Crear CifradoResponse
   ↓
6. FastAPI serializa a JSON
```

---

## 📋 CAPA 3: SCHEMAS (Validación)

**Archivo:** [`app/schemas/vigenere.py`](../app/schemas/vigenere.py)

### **Responsabilidades:**

- ✅ Definir estructura de requests/responses
- ✅ Validaciones automáticas con Pydantic
- ✅ Documentación OpenAPI (Swagger)
- ✅ Type hints para el código

### **Schemas Definidos:**

```python
from pydantic import BaseModel, Field

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CifrarTextoRequest(BaseModel):
    """Request para cifrar texto"""
    texto: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,  # 1 MB máx
        description="Texto a cifrar (máximo 1 MB)"
    )
    clave: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Clave para cifrado (max 1000 chars)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "texto": "Hola Mundo",
                "clave": "clave"
            }]
        }
    }

class DescifrarTextoRequest(BaseModel):
    """Request para descifrar texto"""
    texto_cifrado: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,
        description="Texto cifrado (máximo 1 MB)"
    )
    clave: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Clave para descifrado"
    )

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class CifradoResponse(BaseModel):
    """Response de cifrado exitoso"""
    texto_cifrado: str = Field(..., description="Texto cifrado")
    clave_usada: str = Field(..., description="Clave formateada")
    texto_original_length: int = Field(..., description="Longitud original")

class DescifradoResponse(BaseModel):
    """Response de descifrado exitoso"""
    texto_descifrado: str = Field(..., description="Texto descifrado")
    clave_usada: str = Field(..., description="Clave formateada")

class ErrorResponse(BaseModel):
    """Response de error"""
    error: str = Field(..., description="Mensaje de error")
    detalle: str = Field(None, description="Detalles adicionales")
```

### **¿Qué hace Pydantic?**

```python
# Request del cliente:
{
    "texto": "Hola",
    "clave": "abc"
}

# Pydantic automáticamente:
1. ✅ Verifica que "texto" existe
2. ✅ Verifica que es string
3. ✅ Verifica min_length=1 (✓)
4. ✅ Verifica max_length=1_000_000 (✓)
5. ✅ Repite para "clave"
6. ✅ Crea objeto CifrarTextoRequest
7. ✅ Lo pasa al endpoint

# Si falla alguna validación:
HTTP 422 Unprocessable Entity
{
    "detail": [
        {
            "loc": ["body", "texto"],
            "msg": "ensure this value has at least 1 characters",
            "type": "value_error.any_str.min_length"
        }
    ]
}
```

---

## ⚙️ CAPA 4: SERVICES (Lógica de Negocio)

**Archivo:** [`app/services/vigenere.py`](../app/services/vigenere.py)

### **Responsabilidades:**

- ✅ Implementar algoritmo Vigenère
- ✅ Funciones puras (sin efectos secundarios)
- ✅ Utilidades de formateo y validación
- ✅ Fácil de testear

### **Estructura en 3 Capas:**

```python
# ============================================================================
# CAPA 1: FUNCIONES PURAS DE CIFRADO/DESCIFRADO
# ============================================================================

def cifrar_vigenere(texto: str, clave: str) -> str:
    """
    Cifra texto con Vigenère

    FUNCIÓN PURA: Sin I/O, solo transformaciones

    Example:
        >>> cifrar_vigenere("HELLO WORLD", "KEY")
        'RIJVSUYVJN'
    """
    # 1. Formatear texto y clave
    texto_limpio = formatear_texto(texto)
    clave_limpia = validar_y_formatear_clave(clave)

    if not texto_limpio:
        raise ValueError("Texto vacío")

    # 2. Ajustar clave al tamaño del texto
    clave_ajustada = ajustar_clave(clave_limpia, len(texto_limpio))

    # 3. Cifrado letra por letra
    texto_cifrado = ""
    for i, letra in enumerate(texto_limpio):
        # Fórmula: C = (P + K) mod 26
        posicion = (ord(letra) - ord('A') + ord(clave_ajustada[i]) - ord('A')) % 26
        letra_cifrada = chr(posicion + ord('A'))
        texto_cifrado += letra_cifrada

    return texto_cifrado

def descifrar_vigenere(texto_cifrado: str, clave: str) -> str:
    """
    Descifra texto con Vigenère

    FUNCIÓN PURA: Sin I/O, solo transformaciones

    Example:
        >>> descifrar_vigenere("RIJVSUYVJN", "KEY")
        'HELLOWORLD'
    """
    clave_limpia = validar_y_formatear_clave(clave)
    texto_limpio = formatear_texto(texto_cifrado)

    if not texto_limpio:
        raise ValueError("Texto vacío")

    clave_ajustada = ajustar_clave(clave_limpia, len(texto_limpio))

    # Descifrado letra por letra
    texto_original = ""
    for i, letra in enumerate(texto_limpio):
        # Fórmula: P = (C - K + 26) mod 26
        num_letra = ord(letra) - ord('A')
        num_clave = ord(clave_ajustada[i]) - ord('A')
        posicion = (num_letra - num_clave + 26) % 26
        letra_original = chr(posicion + ord('A'))
        texto_original += letra_original

    return texto_original

# ============================================================================
# CAPA 2: VALIDACIONES Y FORMATEO
# ============================================================================

def validar_y_formatear_clave(clave: str) -> str:
    """
    Valida y formatea clave

    Example:
        >>> validar_y_formatear_clave("Mi Clave 123")
        'MICLAVE'
    """
    if not clave:
        raise ValueError("Clave vacía")

    # Solo letras, mayúsculas
    clave_limpia = ''.join(c.upper() for c in clave if c.isalpha())

    if not clave_limpia:
        raise ValueError("Clave debe tener al menos una letra")

    return clave_limpia

def formatear_texto(texto: str) -> str:
    """
    Formatea texto: solo letras mayúsculas

    Example:
        >>> formatear_texto("Hello, World! 123")
        'HELLOWORLD'
    """
    if not texto:
        return ""

    caracteres_validos = [c.upper() for c in texto if c.isalpha()]
    return "".join(caracteres_validos)

def ajustar_clave(clave: str, longitud: int) -> str:
    """
    Repite clave para alcanzar longitud

    Example:
        >>> ajustar_clave("KEY", 10)
        'KEYKEYKEYK'
    """
    if not clave:
        raise ValueError("Clave vacía")

    if longitud <= 0:
        return ""

    # Repetir cíclicamente
    repeticiones = (longitud // len(clave)) + 1
    clave_extendida = clave * repeticiones
    return clave_extendida[:longitud]

# ============================================================================
# CAPA 3: UTILIDADES PARA ARCHIVOS
# ============================================================================

# NOTA: Las funciones de archivos se eliminaron para reducir duplicación.
# Ahora se manejan directamente en el router usando las funciones puras.
```

### **¿Por qué funciones puras?**

```python
# ✅ FUNCIÓN PURA (Recomendado)
def cifrar_vigenere(texto: str, clave: str) -> str:
    texto_limpio = formatear_texto(texto)
    # ... solo transformaciones ...
    return texto_cifrado

# ❌ FUNCIÓN IMPURA (Evitar en services)
async def cifrar_vigenere_file(file: UploadFile, clave: str) -> str:
    contenido = await file.read()  # ← I/O (efecto secundario)
    return cifrar_vigenere(contenido, clave)
```

**Ventajas de funciones puras:**
- ✅ Fácil de testear (no requiere mocks)
- ✅ Predecibles (mismo input = mismo output)
- ✅ Reutilizables en diferentes contextos
- ✅ Sin efectos secundarios

---

## ❌ MANEJO DE ERRORES

### **Niveles de Manejo:**

```
1. PYDANTIC (Automático)
   ↓ Valida tipos, min/max length
   └─→ HTTP 422 si falla

2. FUNCIONES AUXILIARES (Router)
   ↓ Validaciones custom
   └─→ HTTPException 400/413

3. SERVICIOS (Lógica)
   ↓ ValueError si datos inválidos
   └─→ Capturado en router

4. CENTRALIZADO (manejar_error)
   ↓ Procesa todas las excepciones
   └─→ HTTP 400/500 + logging
```

### **Función Centralizada:**

```python
def manejar_error(e: Exception, operacion: str) -> HTTPException:
    """Centraliza manejo de errores"""

    # 1. Si ya es HTTPException, re-lanzar
    if isinstance(e, HTTPException):
        return e

    # 2. ValueError = error de validación (400)
    if isinstance(e, ValueError):
        logger.warning(f"Validación falló al {operacion}: {str(e)}")
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )

    # 3. Otros errores = interno (500)
    # ⚠️ NO exponer detalles al usuario
    logger.error(f"Error interno al {operacion}: {str(e)}", exc_info=True)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"error": f"Error interno al {operacion}"}
    )
```

### **Ejemplo de Error:**

```python
# Usuario envía clave con caracteres invisibles
{
    "texto": "Hola",
    "clave": "cla​ve"  # ← Zero-Width Space en posición 3
}

# Respuesta:
HTTP 400 Bad Request
{
    "detail": {
        "error": "La clave contiene caracteres invisibles",
        "caracteres_detectados": [
            {
                "posicion": 3,
                "caracter": "U+200B",
                "nombre": "Zero-Width Space"
            }
        ],
        "sugerencia": "Elimina los caracteres invisibles"
    }
}
```

---

## 🔒 SEGURIDAD Y VALIDACIONES

### **Múltiples Niveles de Validación:**

```
NIVEL 1: PYDANTIC (Automático)
├─ min_length / max_length
├─ Tipos de datos
└─ Campos requeridos

NIVEL 2: FUNCIONES AUXILIARES
├─ Caracteres invisibles
├─ Extensión de archivo
├─ Tamaño de archivo
└─ Encoding UTF-8

NIVEL 3: SERVICIOS
├─ Clave con al menos una letra
├─ Texto no vacío
└─ Valores numéricos válidos

NIVEL 4: CANARY CHECK (Archivos grandes)
└─ Verificación de clave correcta
```

### **Protecciones Implementadas:**

| Amenaza | Protección | Ubicación |
|---------|-----------|-----------|
| **DoS (texto gigante)** | `max_length=1_000_000` | Schemas |
| **DoS (archivo gigante)** | `MAX_FILE_SIZE=500MB` | Router |
| **Path Traversal** | Validación extensión `.txt` | Router |
| **Encoding inválido** | Validación UTF-8 | Router |
| **Caracteres invisibles** | Detección 5 tipos Unicode | Router |
| **Clave incorrecta** | Canary Check (1KB) | Router |
| **Información sensible** | Logging interno, no exponer | Router |

---

## 🚀 CÓMO AÑADIR VIGENÈRE A MAIN

### **Pasos Completos:**

#### **1. Estructura de Archivos:**

```
ApiScriptum/
├── main.py                          ← Aplicación principal
├── app/
│   ├── __init__.py
│   ├── config.py                    ← Configuración
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── vigenere.py              ← Router Vigenère ✅
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── vigenere.py              ← Schemas ✅
│   └── services/
│       ├── __init__.py
│       └── vigenere.py              ← Services ✅
```

#### **2. En `main.py`:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, vigenere  # ← Importar router
from app.config import settings

app = FastAPI(
    title="Scriptum API",
    description="API de cifrado y descifrado",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTRAR ROUTERS
app.include_router(health.router, tags=["Health"])
app.include_router(vigenere.router)  # ← Añadir Vigenère

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a Scriptum API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "vigenere": "/vigenere"  # ← Documentar
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

#### **3. Verificar Importaciones:**

En `app/routers/__init__.py`:
```python
# Permite importar como: from app.routers import vigenere
from . import health
from . import vigenere

__all__ = ["health", "vigenere"]
```

#### **4. Iniciar Servidor:**

```bash
# Método 1: Con uvicorn directamente
uvicorn main:app --reload --port 8000

# Método 2: Con python
python main.py

# Método 3: Con venv activado
source venv/bin/activate
python main.py
```

#### **5. Verificar Endpoints:**

```bash
# Health check
curl http://localhost:8000/health

# Documentación interactiva
open http://localhost:8000/docs

# Probar cifrado
curl -X POST "http://localhost:8000/vigenere/cifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{"texto": "Hola Mundo", "clave": "clave"}'
```

---

## 📝 LO QUE FALTA POR AÑADIR

### **🔴 CRÍTICO (Implementar Pronto)**

#### **1. Rate Limiting**
**Problema:** Sin protección contra abuso/DoS

**Solución:**
```python
# 1. Añadir a requirements.txt
slowapi==0.1.9

# 2. En main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. En cada endpoint del router
@limiter.limit("10/minute")
@router.post("/cifrar/texto")
async def cifrar_texto(request: Request, data: CifrarTextoRequest):
    # ...
```

#### **2. Logging Estructurado**
**Problema:** Logs no están configurados adecuadamente

**Solución:**
```python
# En main.py o config.py
import logging
from logging.handlers import RotatingFileHandler

# Crear directorio de logs
import os
os.makedirs("logs", exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/api.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
```

#### **3. Variables de Entorno para Configuración**
**Problema:** Constantes hardcoded en router

**Solución:**
```python
# En app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Límites de archivos
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500 MB
    SMALL_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    CANARY_SIZE: int = 1024  # 1 KB

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    class Config:
        env_file = ".env"

settings = Settings()

# En router, usar:
from app.config import settings
MAX_FILE_SIZE = settings.MAX_FILE_SIZE
```

#### **4. Endpoint de Cifrar Archivo Grande**
**Problema:** Solo existe `/descifrar/file/large`, falta el de cifrado

**Solución:**
```python
# En app/routers/vigenere.py
@router.post("/cifrar/file/large")
async def cifrar_archivo_grande(
    file: UploadFile = File(...),
    clave: str = Form(...),
    add_magic_header: bool = Form(default=True)
):
    """Cifra archivos grandes (10-500 MB)"""
    try:
        validar_clave_sin_caracteres_invisibles(clave)

        contenido_bytes = await leer_archivo_seguro(file, MAX_FILE_SIZE)
        contenido = contenido_bytes.decode('utf-8')

        # Añadir magic header si se solicita
        if add_magic_header:
            contenido = "MAGICv1\n" + contenido

        texto_cifrado = cifrar_vigenere(contenido, clave)

        return CifradoResponse(
            texto_cifrado=texto_cifrado,
            clave_usada=''.join(c.upper() for c in clave if c.isalpha()),
            texto_original_length=len(contenido)
        )
    except Exception as e:
        raise manejar_error(e, "cifrar archivo grande")
```

---

### **🟡 IMPORTANTE (Siguiente Sprint)**

#### **5. Tests Automatizados**
```bash
# Crear tests/test_vigenere.py
pytest tests/

# Cobertura:
pytest --cov=app tests/
```

**Ejemplo de test:**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_cifrar_texto():
    response = client.post(
        "/vigenere/cifrar/texto",
        json={"texto": "Hola", "clave": "clave"}
    )
    assert response.status_code == 200
    assert "texto_cifrado" in response.json()

def test_clave_con_caracteres_invisibles():
    response = client.post(
        "/vigenere/cifrar/texto",
        json={"texto": "Hola", "clave": "cla\u200Bve"}
    )
    assert response.status_code == 400
    assert "caracteres invisibles" in response.json()["detail"]["error"]
```

#### **6. Validación de Content-Type Real (Magic Bytes)**
```python
# Añadir a requirements.txt
python-magic==0.4.27

# En router
import magic

async def leer_archivo_seguro(file: UploadFile, max_size: int) -> bytes:
    contenido = await file.read()

    # Validar magic bytes
    file_type = magic.from_buffer(contenido, mime=True)
    if file_type not in ['text/plain', 'application/octet-stream']:
        raise HTTPException(400, detail={"error": "Solo archivos de texto"})

    # ... resto de validaciones ...
```

#### **7. CORS Más Restrictivo**
```python
# En main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Solo orígenes específicos
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Solo métodos necesarios
    allow_headers=["Content-Type", "Authorization"],  # Headers específicos
)
```

#### **8. HTTPS Redirect Middleware**
```python
# En main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

### **🟢 MEJORAS OPCIONALES (Backlog)**

#### **9. Streaming Real para Archivos Muy Grandes**
Solo implementar si realmente necesitas procesar archivos >500 MB

#### **10. Autenticación (JWT/OAuth2)**
Si la API se expone públicamente

#### **11. Base de Datos**
Si necesitas persistir resultados o claves

#### **12. Métricas y Monitoreo**
```python
# Prometheus + Grafana
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🎯 CHECKLIST DE INTEGRACIÓN

```
✅ Archivos creados:
   ✅ app/routers/vigenere.py
   ✅ app/schemas/vigenere.py
   ✅ app/services/vigenere.py

✅ Main.py configurado:
   ✅ Router importado
   ✅ Router registrado con include_router()
   ✅ Endpoint raíz documenta /vigenere

✅ Validaciones implementadas:
   ✅ Pydantic schemas con max_length
   ✅ Detección caracteres invisibles
   ✅ Validación extensión .txt
   ✅ Validación UTF-8
   ✅ Límites de tamaño

✅ Endpoints funcionando:
   ✅ POST /vigenere/cifrar/texto
   ✅ POST /vigenere/descifrar/texto
   ✅ POST /vigenere/cifrar/file
   ✅ POST /vigenere/descifrar/file
   ✅ POST /vigenere/validar-clave
   ✅ POST /vigenere/descifrar/file/large

🔴 PENDIENTE:
   ❌ Rate limiting (slowapi)
   ❌ Logging configurado
   ❌ POST /vigenere/cifrar/file/large
   ❌ Tests automatizados
   ❌ Variables de entorno para constantes
```

---

## 📚 RECURSOS ADICIONALES

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Pydantic Docs:** https://docs.pydantic.dev/
- **Vigenère Algorithm:** https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/

---

**Generado:** 2025-11-09
**Versión API:** 1.0.0
**Autor:** Claude Code + Wara
