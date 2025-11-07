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

## Instalación

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
