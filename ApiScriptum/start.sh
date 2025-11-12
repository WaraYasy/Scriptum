#!/bin/bash
# Script de inicio para Scriptum API
# Soporta variables de entorno PORT para Railway, Render, etc.

# Usar PORT del entorno o 8000 por defecto
PORT=${PORT:-8000}

echo "🚀 Iniciando Scriptum API en puerto $PORT..."

# Ejecutar uvicorn con configuración para archivos grandes
# --timeout-keep-alive: Mantiene la conexión abierta más tiempo (5 min)
# --timeout-graceful-shutdown: Tiempo para cerrar correctamente
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --timeout-keep-alive 300
