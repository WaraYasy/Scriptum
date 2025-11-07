# Scriptum API

API REST desarrollada con FastAPI para el proyecto Scriptum.

## Estructura del Proyecto

```
ApiScriptum/
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── .env.example           # Ejemplo de variables de entorno
├── .gitignore             # Archivos ignorados por Git
└── app/
    ├── __init__.py
    ├── config.py          # Configuración de la aplicación
    ├── routers/           # Endpoints de la API
    │   ├── __init__.py
    │   └── health.py      # Endpoint de salud
    ├── models/            # Modelos de base de datos
    │   └── __init__.py
    ├── schemas/           # Schemas de Pydantic
    │   └── __init__.py
    └── services/          # Lógica de negocio
        └── __init__.py
```

## Guía para Colaboradores

Si ya tienes el proyecto en tu ordenador y quieres desplegarlo localmente para probarlo o colaborar, sigue estos pasos:

### 1. Verificar requisitos previos

Asegúrate de tener instalado:
- Python 3.8 o superior: `python3 --version` o `python --version`
- pip: `pip --version`

### 2. Configurar el entorno de desarrollo

**Paso 1: Navegar a la carpeta del proyecto**
```bash
cd ruta/al/proyecto/ApiScriptum
```

**Paso 2: Crear entorno virtual**
```bash
python3 -m venv venv
```
o en Windows:
```bash
python -m venv venv
```

**Paso 3: Activar el entorno virtual**

- **macOS/Linux:**
```bash
source venv/bin/activate
```

- **Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

- **Windows (CMD):**
```bash
venv\Scripts\activate.bat
```

Cuando esté activado, verás `(venv)` al inicio de tu terminal.

**Paso 4: Instalar dependencias**
```bash
pip install -r requirements.txt
```

**Paso 5: Configurar variables de entorno (opcional)**
```bash
cp .env.example .env
```
Edita el archivo `.env` si necesitas cambiar alguna configuración.

### 3. Ejecutar el proyecto

**Iniciar el servidor de desarrollo:**
```bash
python main.py
```

El servidor arrancará en `http://localhost:8000` con auto-reload activado (los cambios se reflejarán automáticamente).

### 4. Probar la API

Una vez que el servidor esté corriendo:

1. **Abrir la documentación interactiva:** http://localhost:8000/docs
2. **Probar endpoints:** Usa Swagger UI para probar los endpoints directamente desde el navegador
3. **Ver documentación alternativa:** http://localhost:8000/redoc
4. **Health check:** http://localhost:8000/health

### 5. Detener el servidor

Presiona `CTRL+C` en la terminal donde está corriendo el servidor.

### 6. Desactivar el entorno virtual

Cuando termines de trabajar:
```bash
deactivate
```

### Comandos útiles para colaboradores

```bash
# Ver todas las dependencias instaladas
pip list

# Actualizar una dependencia específica
pip install --upgrade nombre-paquete

# Congelar dependencias después de instalar nuevas
pip freeze > requirements.txt

# Limpiar archivos cache de Python
find . -type d -name __pycache__ -exec rm -rf {} +
```

## Instalación (alternativa sin colaboración)

Si simplemente quieres instalar y probar el proyecto:

1. Crear un entorno virtual:
```bash
python -m venv venv
```

2. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- macOS/Linux:
```bash
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
```

## Ejecución

### Modo desarrollo (con auto-reload):
```bash
python main.py
```

O usando uvicorn directamente:
```bash
uvicorn main:app --reload
```

### Modo producción:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Documentación de la API

Una vez que la aplicación esté corriendo, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Endpoint raíz**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

## Próximos pasos

1. Agregar más endpoints en `app/routers/`
2. Definir modelos de base de datos en `app/models/`
3. Crear schemas de validación en `app/schemas/`
4. Implementar lógica de negocio en `app/services/`
5. Configurar base de datos (SQLAlchemy, MongoDB, etc.)
6. Agregar autenticación y autorización
7. Implementar tests

## Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Pydantic**: Validación de datos
- **Python 3.8+**
