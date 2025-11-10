# ============================================================================
# DOCKERFILE - Scriptum API
# API de cifrado/descifrado con FastAPI
# ============================================================================

# Etapa 1: Base con Python
FROM python:3.11-slim as base

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2: Imagen final
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copiar dependencias de Python desde la etapa anterior
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Dar permisos de ejecución al script de inicio
RUN chmod +x start.sh

# Cambiar al usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando para ejecutar la aplicación
# Usa el script de inicio que soporta la variable PORT
CMD ["./start.sh"]
