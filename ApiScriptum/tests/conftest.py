"""
Configuración de pytest con fixtures compartidas para todos los tests
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="session")
def client():
    """
    Cliente de pruebas de FastAPI.
    Scope 'session' para reutilizar el cliente en todos los tests.
    """
    return TestClient(app)


@pytest.fixture
def sample_texto():
    """Texto de ejemplo para tests"""
    return "Hola Mundo, esto es una prueba de cifrado"


@pytest.fixture
def sample_password():
    """Password de ejemplo para tests de AES"""
    return "password_seguro_123"


@pytest.fixture
def sample_clave_vigenere():
    """Clave de ejemplo para tests de Vigenère"""
    return "CLAVE"


@pytest.fixture
def sample_archivo_txt(tmp_path):
    """
    Crea un archivo .txt temporal para tests

    Args:
        tmp_path: Fixture de pytest que proporciona un directorio temporal

    Returns:
        Path del archivo creado
    """
    archivo = tmp_path / "test.txt"
    contenido = "Este es un contenido de prueba para el archivo\ncon multiples lineas\ny caracteres especiales"
    archivo.write_text(contenido, encoding='utf-8')
    return archivo


@pytest.fixture
def sample_archivo_pdf(tmp_path):
    """
    Crea un archivo .pdf temporal para tests
    """
    archivo = tmp_path / "test.pdf"
    # Simular contenido binario de un PDF simple
    contenido = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
    archivo.write_bytes(contenido)
    return archivo


@pytest.fixture
def sample_archivo_grande(tmp_path):
    """
    Crea un archivo grande (>10MB) para tests de streaming
    """
    archivo = tmp_path / "archivo_grande.txt"
    # Crear contenido de ~11 MB
    contenido = "A" * (11 * 1024 * 1024)
    archivo.write_text(contenido, encoding='utf-8')
    return archivo
