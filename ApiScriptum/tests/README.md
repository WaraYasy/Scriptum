# Tests de Scriptum API

Este directorio contiene todos los tests para la API de Scriptum, incluyendo tests de integración, tests unitarios y tests de casos edge.

## Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidas
├── test_api_integration.py  # Tests de integración de endpoints
├── test_edge_cases.py       # Tests de casos límite y validaciones
├── test_empaquetado.py      # Tests de empaquetado de archivos
├── test_streaming.py        # Tests de streaming para archivos grandes
└── README.md               # Este archivo
```

## Instalación de Dependencias

```bash
# Instalar dependencias de testing
pip install pytest pytest-cov httpx

# O desde requirements.txt si está disponible
pip install -r requirements.txt
```

## Ejecutar Tests

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con cobertura

```bash
pytest --cov=app --cov-report=html
```

### Ejecutar tests específicos

```bash
# Solo tests de integración de API
pytest tests/test_api_integration.py

# Solo tests de casos edge
pytest tests/test_edge_cases.py

# Solo tests de empaquetado
pytest tests/test_empaquetado.py

# Ejecutar un test específico
pytest tests/test_api_integration.py::TestAESCifradoTexto::test_cifrar_texto_aes256
```

### Ejecutar tests por marcadores

```bash
# Solo tests rápidos
pytest -m rapido

# Solo tests de seguridad
pytest -m seguridad

# Excluir tests lentos
pytest -m "not lento"
```

### Opciones útiles

```bash
# Mostrar print statements
pytest -s

# Detener en el primer fallo
pytest -x

# Mostrar el top 10 de tests más lentos
pytest --durations=10

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto

# Modo verbose con más detalles
pytest -vv

# Ejecutar solo los tests que fallaron la última vez
pytest --lf
```

## Tipos de Tests

### 1. Tests de Integración (`test_api_integration.py`)

Tests completos de los endpoints de la API:
- **Health Check**: Verifica que la API está funcionando
- **Vigenère**: Cifrado/descifrado de texto y archivos
- **AES**: Cifrado/descifrado con AES-128/192/256
- **Paquetes**: Formato de paquete único con metadata

**Ejemplos:**
- ✅ Cifrado y descifrado exitoso
- ✅ Validación de passwords
- ✅ Manejo de diferentes tipos de archivos
- ❌ Errores de validación
- ❌ Passwords incorrectos

### 2. Tests de Casos Edge (`test_edge_cases.py`)

Tests para casos límite y validaciones especiales:
- **Límites de tamaño**: Archivos muy grandes, archivos vacíos
- **Caracteres especiales**: Unicode, emojis, caracteres invisibles
- **Seguridad**: Detección de manipulación, validación de salts
- **Boundary conditions**: Valores mínimos y máximos

### 3. Tests de Empaquetado (`test_empaquetado.py`)

Tests del sistema de empaquetado de archivos cifrados:
- Creación y extracción de paquetes
- Verificación del formato binario
- Comparación de eficiencia vs JSON
- Ciclo completo de cifrado/descifrado

### 4. Tests de Streaming (`test_streaming.py`)

Tests de procesamiento de archivos grandes:
- Archivos pequeños (<10MB) - método en memoria
- Archivos grandes (≥10MB) - streaming
- Comparación de rendimiento
- Verificación de umbral

## Fixtures Disponibles

En `conftest.py` hay fixtures compartidas:

- `client`: Cliente de pruebas de FastAPI
- `sample_texto`: Texto de ejemplo
- `sample_password`: Password para tests de AES
- `sample_clave_vigenere`: Clave para tests de Vigenère
- `sample_archivo_txt`: Archivo .txt temporal
- `sample_archivo_pdf`: Archivo .pdf temporal
- `sample_archivo_grande`: Archivo >10MB para streaming

## Marcadores (Markers)

Los tests están organizados con marcadores:

- `@pytest.mark.rapido`: Tests rápidos (<1s)
- `@pytest.mark.lento`: Tests que tardan más
- `@pytest.mark.seguridad`: Tests de seguridad
- `@pytest.mark.integracion`: Tests de integración
- `@pytest.mark.unitario`: Tests unitarios

## Estructura de un Test Típico

```python
def test_cifrar_descifrar_ciclo_completo(client, sample_password):
    """
    Test de ciclo completo: cifrar → descifrar

    Verifica que:
    1. El cifrado funciona correctamente
    2. El descifrado recupera el texto original
    3. Los metadatos son correctos
    """
    texto_original = "Mensaje secreto"

    # 1. Cifrar
    response_cifrar = client.post(
        "/aes/cifrar/texto",
        json={
            "texto": texto_original,
            "password": sample_password,
            "tipo_aes": "AES-256"
        }
    )
    assert response_cifrar.status_code == 200
    data = response_cifrar.json()

    # 2. Descifrar
    response_descifrar = client.post(
        "/aes/descifrar/texto",
        json={
            "texto_cifrado": data["texto_cifrado"],
            "password": sample_password,
            "salt": data["salt"],
            "tipo_aes": "AES-256"
        }
    )
    assert response_descifrar.status_code == 200

    # 3. Verificar
    assert response_descifrar.json()["texto_descifrado"] == texto_original
```

## Mejores Prácticas

1. **Nombres descriptivos**: Los nombres de tests deben explicar qué se está probando
2. **AAA Pattern**: Arrange (preparar), Act (ejecutar), Assert (verificar)
3. **Un concepto por test**: Cada test debe verificar una sola cosa
4. **Tests independientes**: No deben depender de otros tests
5. **Fixtures para datos**: Usar fixtures para datos de prueba reutilizables
6. **Verificar estados**: Tanto casos de éxito como de error

## Cobertura de Tests

Los tests cubren:

### Endpoints
- ✅ GET /
- ✅ GET /health
- ✅ GET /aes/info
- ✅ POST /aes/cifrar/texto
- ✅ POST /aes/descifrar/texto
- ✅ POST /aes/cifrar/file
- ✅ POST /aes/descifrar/file
- ✅ POST /aes/cifrar/file/paquete
- ✅ POST /aes/descifrar/file/paquete
- ✅ POST /aes/validar-password
- ✅ POST /vigenere/cifrar/texto
- ✅ POST /vigenere/descifrar/texto
- ✅ POST /vigenere/cifrar/file
- ✅ POST /vigenere/descifrar/file
- ✅ POST /vigenere/validar-clave

### Casos de Prueba
- ✅ Casos de éxito
- ✅ Validaciones de entrada
- ✅ Errores de autenticación (password incorrecto)
- ✅ Errores de formato
- ✅ Límites de tamaño
- ✅ Caracteres especiales y Unicode
- ✅ Seguridad y manipulación de datos
- ✅ Boundary conditions

## Continuous Integration

Para CI/CD, ejecuta:

```bash
# Tests rápidos (para builds rápidos)
pytest -m "not lento" --tb=short

# Tests completos con cobertura
pytest --cov=app --cov-report=xml --cov-report=term
```

## Depuración

Para depurar un test que falla:

```bash
# Ejecutar con más información
pytest tests/test_api_integration.py::test_name -vv -s

# Usar pytest debugger
pytest tests/test_api_integration.py::test_name --pdb

# Ver variables locales en el traceback
pytest tests/test_api_integration.py::test_name -l
```

## Contribuir

Al agregar nuevos endpoints o funcionalidades:

1. Agrega tests en `test_api_integration.py` para casos normales
2. Agrega tests en `test_edge_cases.py` para casos especiales
3. Usa las fixtures existentes cuando sea posible
4. Marca los tests apropiadamente (`@pytest.mark.rapido`, etc.)
5. Documenta qué está probando cada test
6. Verifica que todos los tests pasen antes de hacer commit

```bash
# Ejecutar todos los tests antes de commit
pytest -v
```

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
