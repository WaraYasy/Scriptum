"""
Configuración de pytest y fixtures compartidos
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """
    Fixture que proporciona un cliente de test para la API
    """
    return TestClient(app)


@pytest.fixture
def sample_text():
    """Texto de ejemplo para tests"""
    return "Hola Mundo"


@pytest.fixture
def sample_key():
    """Clave de ejemplo para tests"""
    return "clave"


@pytest.fixture
def encrypted_text():
    """Texto cifrado conocido para tests"""
    # "Hola Mundo" cifrado con clave "clave" = "JZLVQWYDJ"
    return "JZLVQWYDJ"


@pytest.fixture
def sample_file_content():
    """Contenido de archivo de ejemplo"""
    return "Este es un archivo de prueba\nCon varias líneas\nPara probar el cifrado"


@pytest.fixture
def create_test_file(tmp_path):
    """
    Fixture que crea archivos temporales para tests

    Usage:
        test_file = create_test_file("test.txt", "contenido")
    """
    def _create_file(filename: str, content: str):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path

    return _create_file
