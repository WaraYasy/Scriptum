# GitHub Actions CI/CD

Este directorio contiene los workflows de GitHub Actions para Integración Continua (CI) y Despliegue Continuo (CD) del proyecto Scriptum API.

## Workflows Disponibles

### 1. CI Principal (`ci.yml`)

**Se ejecuta en:** Push a `main` o `develop`, Pull Requests a `main`

**Jobs incluidos:**
- ✅ **Lint**: Análisis de calidad de código con pylint
- ✅ **Test**: Tests unitarios y de integración (Python 3.11, 3.12, 3.13)
- ✅ **Test-Full**: Suite completa de tests incluyendo los lentos
- ✅ **Security**: Análisis de seguridad con `safety` y `bandit`
- ✅ **Docker**: Build y validación de imagen Docker (opcional)
- ✅ **Summary**: Resumen de resultados

**Características:**
- Matrix testing con múltiples versiones de Python
- Cobertura de código con Codecov
- Cache de dependencias para builds más rápidos
- Artifacts de reportes de cobertura

### 2. Quick Tests (`quick-test.yml`)

**Se ejecuta en:** Push a cualquier rama excepto `main`

**Características:**
- Solo ejecuta tests rápidos (excluye tests marcados como `lento`)
- Feedback inmediato para desarrollo
- Termina en el primer fallo (`-x`)

## Badges para README

Añade estos badges a tu README principal para mostrar el estado del CI:

```markdown
![CI](https://github.com/TU_USUARIO/TU_REPO/workflows/CI%20-%20Scriptum%20API/badge.svg)
![Tests](https://github.com/TU_USUARIO/TU_REPO/workflows/Quick%20Tests/badge.svg)
[![codecov](https://codecov.io/gh/TU_USUARIO/TU_REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/TU_USUARIO/TU_REPO)
```

## Configuración Necesaria

### 1. Codecov (Opcional)

Para reportes de cobertura en Codecov:

1. Ve a [codecov.io](https://codecov.io/)
2. Conecta tu repositorio de GitHub
3. Copia el token de integración
4. Añádelo como secret en GitHub: `Settings > Secrets > CODECOV_TOKEN`

### 2. Requirements.txt

Asegúrate de tener un `requirements.txt` en la carpeta ApiScriptum:

```bash
# Generar requirements.txt
pip freeze > ApiScriptum/requirements.txt
```

### 3. Estructura del Proyecto

El CI espera esta estructura:

```
.
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── quick-test.yml
├── ApiScriptum/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routers/
│   │   ├── services/
│   │   └── schemas/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_api_integration.py
│   │   ├── test_edge_cases.py
│   │   ├── test_empaquetado.py
│   │   └── test_streaming.py
│   ├── requirements.txt
│   ├── pytest.ini
│   └── main.py
└── ScriptumFx/
```

## Ejecutar Localmente

Puedes ejecutar las mismas validaciones localmente:

### Tests rápidos
```bash
cd ApiScriptum
pytest tests/ -v -m "not lento"
```

### Tests completos con cobertura
```bash
cd ApiScriptum
pytest tests/ -v --cov=app --cov-report=html
```

### Linting
```bash
pylint ApiScriptum/app
```

### Seguridad
```bash
# Dependencias
safety check --file ApiScriptum/requirements.txt

# Código
bandit -r ApiScriptum/app/
```

## Solución de Problemas

### El CI falla pero localmente pasa

1. **Verificar versión de Python:**
   ```bash
   python --version
   ```
   Debe coincidir con las versiones en el CI (3.11, 3.12, 3.13)

2. **Limpiar cache:**
   ```bash
   pytest --cache-clear
   ```

3. **Verificar dependencias:**
   ```bash
   pip list
   ```

### Tests lentos en el CI

Si los tests tardan mucho:

1. Usa el workflow `quick-test.yml` en desarrollo
2. Marca tests lentos con `@pytest.mark.lento`
3. Reduce el número de versiones de Python en la matrix

### Problemas con cache

Si hay problemas con el cache de pip:

1. Elimina el cache en GitHub Actions:
   - Ve a `Actions > Caches`
   - Elimina el cache problemático

2. O modifica la key del cache en el workflow

## Personalización

### Añadir más versiones de Python

Edita la matrix en `ci.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13', '3.14']
```

### Cambiar branches monitoreados

Edita los triggers en `ci.yml`:

```yaml
on:
  push:
    branches: [ main, develop, staging ]
  pull_request:
    branches: [ main, develop ]
```

### Añadir notificaciones

Puedes añadir notificaciones a Slack, Discord, etc.:

```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Mejores Prácticas

1. ✅ Ejecuta tests localmente antes de hacer push
2. ✅ Usa branches de feature y pull requests
3. ✅ Mantén los tests rápidos (< 5 minutos)
4. ✅ Revisa los reportes de cobertura
5. ✅ Corrige warnings de seguridad inmediatamente
6. ✅ Actualiza dependencias regularmente

## Próximos Pasos

Workflows adicionales que podrías añadir:

- 🚀 **CD (Continuous Deployment)**: Deploy automático a producción
- 📦 **Release**: Automatizar creación de releases
- 🏷️ **Semantic Versioning**: Versionado automático
- 📊 **Performance**: Tests de rendimiento
- 🔍 **Code Quality**: SonarCloud, CodeClimate
