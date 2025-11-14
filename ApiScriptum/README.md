# 🔧 Scriptum API

<div align="center">

**API REST de alto rendimiento para cifrado y descifrado seguro**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)

[Características](#-características) •
[Instalación](#-instalación-rápida) •
[Endpoints](#-endpoints-principales) •
[Documentación](#-documentación-técnica)

</div>

---

## 📖 Descripción

API REST desarrollada con **FastAPI** que proporciona servicios de cifrado y descifrado seguros para el proyecto Scriptum. Soporta múltiples algoritmos criptográficos con procesamiento optimizado para archivos de cualquier tamaño.

---

## ✨ Características

### 🔐 Algoritmos de Cifrado

- **AES (Advanced Encryption Standard)**
  - ✓ AES-128, AES-192, AES-256
  - ✓ Modo GCM (autenticación + cifrado)
  - ✓ Generación de claves con PBKDF2 (100,000 iteraciones)
  - ✓ Verificación de integridad con SHA-256

- **Vigenère**
  - ✓ Cifrado clásico mejorado
  - ✓ Soporte para textos largos
  - ✓ Procesamiento optimizado

### ⚡ Rendimiento

- **Streaming para archivos grandes** (≥ 10 MB)
- **Procesamiento asíncrono** con FastAPI
- **Chunks de 64 KB** para optimizar memoria
- **Empaquetado binario eficiente** (~27-30% menos espacio que JSON)

### 📏 Límites

| Cifrado | Textos | Archivos | Streaming |
|---------|--------|----------|-----------|
| **AES** | 100 MB | 100 MB | ✅ |
| **Vigenère** | 100 MB | 500 MB | ✅ |

**Password:** 8-1,000 caracteres

### 📊 Monitoreo y Logging

- Sistema de **logging robusto** con niveles configurables
- **Rotación automática diaria** de archivos de log (medianoche)
- **Dos niveles de logging**: general (30 días) y debug (7 días)
- Logs detallados de operaciones y tiempos de respuesta

### 🛡️ Seguridad

- ✓ Validación exhaustiva de entradas con Pydantic
- ✓ Manejo seguro de errores sin exponer información sensible
- ✓ CORS configurado para producción
- ✓ Rate limiting recomendado en producción

---

## 🏗️ Estructura del Proyecto

```
ApiScriptum/
├── main.py                 # 🚀 Punto de entrada de la aplicación
├── requirements.txt        # 📦 Dependencias del proyecto
├── Dockerfile             # 🐳 Configuración Docker
├── docker-compose.yml     # 🐳 Orquestación de contenedores
├── railway.json           # 🚂 Configuración para Railway
├── pytest.ini             # 🧪 Configuración de tests
├── pyrightconfig.json     # 🔍 Configuración de type checking
│
└── app/
    ├── __init__.py
    ├── config.py          # ⚙️ Configuración de la aplicación
    ├── logging_config.py  # 📝 Configuración de logging
    │
    ├── routers/           # 🛣️ Endpoints de la API
    │   ├── __init__.py
    │   ├── health.py      # ❤️ Endpoint de salud
    │   ├── aes.py         # 🔒 Endpoints de cifrado AES
    │   └── vigenere.py    # 📝 Endpoints de cifrado Vigenère
    │
    ├── schemas/           # 📋 Validación de datos (Pydantic)
    │   ├── __init__.py
    │   ├── aes.py         # Schemas para AES
    │   └── vigenere.py    # Schemas para Vigenère
    │
    ├── services/          # 💼 Lógica de negocio
    │   ├── __init__.py
    │   ├── aes.py         # Servicio de cifrado AES
    │   └── vigenere.py    # Servicio de cifrado Vigenère
    │
    └── tests/             # 🧪 Suite de pruebas
        ├── test_api_integration.py
        ├── test_edge_cases.py
        ├── test_empaquetado.py
        └── test_streaming.py
```

---

## 🚀 Instalación Rápida

### Requisitos Previos

- 🐍 **Python 3.8+**
- 📦 **pip**
- (Opcional) **Docker** para despliegue en contenedor

### Opción 1: Instalación Local

#### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/WaraYasy/Scriptum.git
cd Scriptum/ApiScriptum
```

#### 2️⃣ Crear entorno virtual

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 4️⃣ (Opcional) Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tu configuración
nano .env
```

#### 5️⃣ Ejecutar el servidor

```bash
# Modo desarrollo (auto-reload)
python main.py

# O usando uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ La API estará disponible en: **http://localhost:8000**

### Opción 2: Docker

```bash
# Construir imagen
docker build -t scriptum-api .

# Ejecutar contenedor
docker run -p 8000:8000 scriptum-api

# O usar docker-compose
docker-compose up
```

### Opción 3: Despliegue en Railway

1. Conectar repositorio con Railway
2. Configurar variables de entorno necesarias
3. Deploy automático desde la rama `main`

Ver [guía de despliegue en Railway →](docs/RAILWAY_DEPLOY.md)

---

## 🌐 Endpoints Principales

### 🏥 Health Check

```http
GET /health
```

Verifica el estado de la API.

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 🔒 Cifrado AES

#### Cifrar Texto

```http
POST /api/aes/cifrar
Content-Type: application/json
```

**Request:**
```json
{
  "texto": "Mensaje secreto",
  "password": "miPassword123",
  "tipo_aes": "AES-256"
}
```

**Response:**
```json
{
  "texto_cifrado": "U2FsdGVkX1...",
  "salt": "cmFuZG9t...",
  "tipo_aes": "AES-256",
  "longitud_original": 15
}
```

#### Descifrar Texto

```http
POST /api/aes/descifrar
Content-Type: application/json
```

**Request:**
```json
{
  "texto_cifrado": "U2FsdGVkX1...",
  "password": "miPassword123",
  "salt": "cmFuZG9t...",
  "tipo_aes": "AES-256"
}
```

**Response:**
```json
{
  "texto_descifrado": "Mensaje secreto",
  "longitud": 15
}
```

#### Cifrar Archivo

```http
POST /api/aes/cifrar-archivo
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Archivo a cifrar
- `password`: Password para cifrar
- `tipo_aes`: "AES-128" | "AES-192" | "AES-256"

**Response:**
```json
{
  "paquete": "U0NSSVBUVU0B...",
  "nombre_original": "documento.pdf",
  "mime_type": "application/pdf",
  "tamanio_original": 1048576,
  "sha256_hash": "a591a6d40bf420404a011733..."
}
```

#### Descifrar Archivo

```http
POST /api/aes/descifrar-archivo
Content-Type: application/json
```

**Request:**
```json
{
  "paquete": "U0NSSVBUVU0B...",
  "password": "miPassword123"
}
```

**Response:** Archivo descifrado (binary download)

### 📝 Cifrado Vigenère

#### Cifrar Texto

```http
POST /api/vigenere/cifrar
Content-Type: application/json
```

**Request:**
```json
{
  "texto": "HOLA MUNDO",
  "clave": "SECRETO"
}
```

**Response:**
```json
{
  "texto_cifrado": "ZINL QYGVI",
  "clave_usada": "SECRETO",
  "longitud": 10
}
```

#### Descifrar Texto

```http
POST /api/vigenere/descifrar
Content-Type: application/json
```

Ver documentación completa de endpoints en: **http://localhost:8000/docs**

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_api_integration.py -v

# Con cobertura
pytest tests/ --cov=app --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html
```

### Tests Disponibles

- ✅ **test_api_integration.py**: Tests de integración de endpoints
- ✅ **test_edge_cases.py**: Casos límite y errores
- ✅ **test_empaquetado.py**: Empaquetado binario de archivos
- ✅ **test_streaming.py**: Procesamiento de archivos grandes

Ver [documentación de tests →](tests/README.md)

---

## 📚 Documentación

### 📖 Para Usuarios

- 🚀 **[Guía Rápida](docs/GUIA_RAPIDA.md)** - Referencia rápida de endpoints y límites
- 📘 **[Guía Completa del Usuario](docs/GUIA_USUARIO.md)** - Tutorial detallado con ejemplos prácticos
- 📦 **[Empaquetado de Archivos](docs/EMPAQUETADO_ARCHIVOS.md)** - Formato binario y casos de uso avanzados

### 🔧 Documentación Técnica

#### Documentación Interactiva

Una vez que la API esté ejecutándose:

- **Swagger UI**: http://localhost:8000/docs
  - Interfaz interactiva para probar endpoints
  - Documentación automática de schemas
  - Ejemplos de requests/responses

- **ReDoc**: http://localhost:8000/redoc
  - Documentación alternativa más visual
  - Mejor para lectura y referencia

#### Documentación de Desarrollo

- 📝 **[Sistema de Logging](docs/LOGGING_SISTEMA.md)** - Configuración y uso de logs
- 🌊 **[Streaming](docs/STREAMING_GUIA.md)** - Manejo de archivos grandes
- 🚂 **[Deploy en Railway](docs/RAILWAY_DEPLOY.md)** - Guía de despliegue

---

## 🛠️ Comandos Útiles

### Desarrollo

```bash
# Ver dependencias instaladas
pip list

# Actualizar dependencia
pip install --upgrade nombre-paquete

# Congelar dependencias
pip freeze > requirements.txt

# Limpiar cache de Python
find . -type d -name __pycache__ -exec rm -rf {} +

# Ver logs en tiempo real
tail -f var/logs/scriptum_api.log
```

### Docker

```bash
# Construir imagen
docker build -t scriptum-api .

# Ejecutar en modo desarrollo
docker run -p 8000:8000 -v $(pwd):/app scriptum-api

# Ver logs del contenedor
docker logs -f <container-id>

# Entrar al contenedor
docker exec -it <container-id> /bin/bash
```

---

## 🛠️ Tecnologías

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno y rápido
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI de alto rendimiento
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Validación de datos con type hints
- **[PyCryptodome](https://www.pycryptodome.org/)** - Biblioteca de criptografía
- **[Pytest](https://pytest.org/)** - Framework de testing
- **Python 3.8+** - Lenguaje de programación

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
# API Configuration
API_TITLE=Scriptum API
API_VERSION=1.0.0
API_PREFIX=/api

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=var/logs/scriptum_api.log

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

---

## 🐛 Solución de Problemas

### La API no arranca

```bash
# Verificar versión de Python
python --version  # Debe ser 3.8+

# Verificar instalación de dependencias
pip list | grep fastapi

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de permisos en logs

```bash
# Crear directorio de logs
mkdir -p var/logs

# Dar permisos
chmod 755 var/logs
```

### Tests fallan

```bash
# Limpiar cache de pytest
pytest --cache-clear

# Reinstalar dependencias de testing
pip install pytest pytest-cov pytest-asyncio
```

### Guía de Estilo

- Seguir **PEP 8** para código Python
- Documentar funciones con **docstrings**
- Añadir **type hints** a todas las funciones
- Escribir **tests** para nuevas funcionalidades
- Mantener **cobertura de tests** > 80%

---

## 👤 Autoras

- 🧙🏻‍♀️ **Arantxa** - [@arantxaMain](https://github.com/arantxaMain)
- 🧙🏽‍♀️ **Wara** - [@WaraYasy](https://github.com/WaraYasy)

---

## 🔗 Enlaces

- 🏠 [Proyecto Principal](../README.md)
- 📱 [ScriptumFX - Aplicación JavaFX](../ScriptumFX/)
- 🚀 [Guía Rápida](docs/GUIA_RAPIDA.md) - Empieza aquí
- 📖 [Guía del Usuario](docs/GUIA_USUARIO.md) - Tutorial completo
- 📦 [Documentación Técnica](docs/)
- 🐛 [Reportar Issues](https://github.com/WaraYasy/Scriptum/issues)

---

<div align="center">
Hecho con ❤️ y ☕

</div>

