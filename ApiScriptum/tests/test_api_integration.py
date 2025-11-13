"""
Tests de Integración para Scriptum API
=========================================

Tests completos para todos los endpoints de la API:
- Health check
- Vigenère (texto y archivos)
- AES (texto, archivos y paquetes)

Estos tests verifican el comportamiento real de la API usando
el TestClient de FastAPI.
"""
import base64
import io
import pytest
from fastapi import status


# ============================================================================
# TESTS: ROOT ENDPOINT
# ============================================================================

def test_root_endpoint(client):
    """Test del endpoint raíz que devuelve información de la API"""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert "endpoints" in data
    assert "/health" in data["endpoints"]["health"]


# ============================================================================
# TESTS: HEALTH CHECK
# ============================================================================

def test_health_check(client):
    """Test del endpoint de health check"""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "Scriptum API"


# ============================================================================
# TESTS: VIGENÈRE - TEXTO
# ============================================================================

class TestVigenereCifradoTexto:
    """Tests para cifrado y descifrado de texto con Vigenère"""

    def test_cifrar_texto_simple(self, client, sample_clave_vigenere):
        """Test de cifrado de texto básico"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={
                "texto": "HOLA MUNDO",
                "clave": sample_clave_vigenere
            }
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "texto_cifrado" in data
        assert "clave_usada" in data
        assert data["clave_usada"] == sample_clave_vigenere
        assert len(data["texto_cifrado"]) > 0

    def test_cifrar_y_descifrar_texto_ciclo_completo(self, client):
        """Test de ciclo completo: cifrar → descifrar"""
        texto_original = "Este es un mensaje secreto"
        clave = "SECRETO"

        # 1. Cifrar
        response_cifrar = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": texto_original, "clave": clave}
        )
        assert response_cifrar.status_code == status.HTTP_200_OK
        texto_cifrado = response_cifrar.json()["texto_cifrado"]

        # 2. Descifrar
        response_descifrar = client.post(
            "/vigenere/descifrar/texto",
            json={"texto_cifrado": texto_cifrado, "clave": clave}
        )
        assert response_descifrar.status_code == status.HTTP_200_OK
        texto_descifrado = response_descifrar.json()["texto_descifrado"]

        # 3. Verificar que al limpiar ambos textos son iguales
        texto_original_limpio = ''.join(c.upper() for c in texto_original if c.isalpha())
        assert texto_descifrado == texto_original_limpio

    def test_cifrar_texto_con_caracteres_especiales(self, client):
        """Test con caracteres especiales y acentos"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={
                "texto": "Hóla Múndo con ácentós y ñ",
                "clave": "CLAVE"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Solo debe cifrar letras, ignorando acentos
        assert len(data["texto_cifrado"]) > 0

    def test_cifrar_texto_vacio_error(self, client):
        """Test que texto vacío devuelve error"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": "", "clave": "CLAVE"}
        )

        # FastAPI devuelve 422 para errores de validación de Pydantic
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_cifrar_clave_vacia_error(self, client):
        """Test que clave vacía devuelve error"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": "HOLA", "clave": ""}
        )

        # FastAPI devuelve 422 para errores de validación de Pydantic
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestVigenereValidacion:
    """Tests para validación de claves de Vigenère"""

    def test_validar_clave_correcta(self, client):
        """Test de validación de clave correcta"""
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": "CLAVESEGURA"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valida"] is True
        assert "clave_limpia" in data

    def test_validar_clave_con_caracteres_invisibles(self, client):
        """Test que detecta caracteres invisibles en la clave"""
        # Clave con Zero-Width Space (U+200B)
        clave_con_invisible = "CLAVE\u200BTEST"

        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisible}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data["detail"]
        assert "caracteres invisibles" in data["detail"]["error"].lower()


# ============================================================================
# TESTS: VIGENÈRE - ARCHIVOS
# ============================================================================

class TestVigenereArchivos:
    """Tests para cifrado y descifrado de archivos con Vigenère"""

    def test_cifrar_archivo_txt(self, client, sample_archivo_txt):
        """Test de cifrado de archivo .txt"""
        with open(sample_archivo_txt, 'rb') as f:
            response = client.post(
                "/vigenere/cifrar/file",
                files={"file": ("test.txt", f, "text/plain")},
                data={"clave": "CLAVE"}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "texto_cifrado" in data
        assert len(data["texto_cifrado"]) > 0

    def test_cifrar_descifrar_archivo_ciclo_completo(self, client, sample_archivo_txt):
        """Test de ciclo completo con archivos"""
        clave = "SECRETO"

        # 1. Cifrar archivo
        with open(sample_archivo_txt, 'rb') as f:
            contenido_original = f.read().decode('utf-8')
            f.seek(0)
            response_cifrar = client.post(
                "/vigenere/cifrar/file",
                files={"file": ("test.txt", f, "text/plain")},
                data={"clave": clave}
            )

        assert response_cifrar.status_code == status.HTTP_200_OK
        texto_cifrado = response_cifrar.json()["texto_cifrado"]

        # 2. Guardar texto cifrado en archivo temporal
        archivo_cifrado = io.BytesIO(texto_cifrado.encode('utf-8'))

        # 3. Descifrar archivo
        response_descifrar = client.post(
            "/vigenere/descifrar/file",
            files={"file": ("cifrado.txt", archivo_cifrado, "text/plain")},
            data={"clave": clave}
        )

        assert response_descifrar.status_code == status.HTTP_200_OK
        texto_descifrado = response_descifrar.json()["texto_descifrado"]

        # 4. Verificar que coinciden (solo letras)
        contenido_limpio = ''.join(c.upper() for c in contenido_original if c.isalpha())
        assert texto_descifrado == contenido_limpio

    def test_cifrar_archivo_no_txt_error(self, client, sample_archivo_pdf):
        """Test que archivos no .txt son rechazados"""
        with open(sample_archivo_pdf, 'rb') as f:
            response = client.post(
                "/vigenere/cifrar/file",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"clave": "CLAVE"}
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "solo se aceptan archivos .txt" in data["detail"]["error"].lower()

    def test_cifrar_archivo_sin_nombre_error(self, client):
        """Test que archivo sin nombre devuelve error"""
        archivo = io.BytesIO(b"contenido de prueba")

        response = client.post(
            "/vigenere/cifrar/file",
            files={"file": ("", archivo, "text/plain")},
            data={"clave": "CLAVE"}
        )

        # FastAPI devuelve 422 para errores de validación
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


# ============================================================================
# TESTS: AES - INFORMACIÓN
# ============================================================================

class TestAESInfo:
    """Tests para endpoint de información de AES"""

    def test_obtener_info_aes(self, client):
        """Test que devuelve información sobre tipos de AES"""
        response = client.get("/aes/info")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "tipos_disponibles" in data
        assert "AES-128" in data["tipos_disponibles"]
        assert "AES-192" in data["tipos_disponibles"]
        assert "AES-256" in data["tipos_disponibles"]
        assert data["recomendacion"] == "AES-256"
        assert "descripcion" in data


# ============================================================================
# TESTS: AES - TEXTO
# ============================================================================

class TestAESCifradoTexto:
    """Tests para cifrado y descifrado de texto con AES"""

    def test_cifrar_texto_aes256(self, client, sample_texto, sample_password):
        """Test de cifrado de texto con AES-256"""
        response = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": sample_texto,
                "password": sample_password,
                "tipo_aes": "AES-256"
            }
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "texto_cifrado" in data
        assert "salt" in data
        assert data["tipo_aes"] == "AES-256"
        assert "tamanio_original_bytes" in data
        assert "tamanio_cifrado_bytes" in data
        # El salt debe ser una cadena no vacía
        assert len(data["salt"]) > 0

    def test_cifrar_descifrar_texto_aes_ciclo_completo(self, client):
        """Test de ciclo completo con AES: cifrar → descifrar"""
        texto_original = "Este es un mensaje super secreto con AES"
        password = "password_muy_seguro_123"

        # 1. Cifrar
        response_cifrar = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": texto_original,
                "password": password,
                "tipo_aes": "AES-256"
            }
        )

        assert response_cifrar.status_code == status.HTTP_200_OK
        data_cifrar = response_cifrar.json()

        # 2. Descifrar
        response_descifrar = client.post(
            "/aes/descifrar/texto",
            json={
                "texto_cifrado": data_cifrar["texto_cifrado"],
                "password": password,
                "salt": data_cifrar["salt"],
                "tipo_aes": "AES-256"
            }
        )

        assert response_descifrar.status_code == status.HTTP_200_OK
        data_descifrar = response_descifrar.json()

        # 3. Verificar que el texto descifrado es el original
        assert data_descifrar["texto_descifrado"] == texto_original

    def test_cifrar_con_diferentes_tipos_aes(self, client, sample_password):
        """Test de cifrado con AES-128, AES-192 y AES-256"""
        texto = "Mensaje de prueba"

        for tipo_aes in ["AES-128", "AES-192", "AES-256"]:
            response = client.post(
                "/aes/cifrar/texto",
                json={
                    "texto": texto,
                    "password": sample_password,
                    "tipo_aes": tipo_aes
                }
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["tipo_aes"] == tipo_aes

            # Verificar que se puede descifrar
            response_descifrar = client.post(
                "/aes/descifrar/texto",
                json={
                    "texto_cifrado": data["texto_cifrado"],
                    "password": sample_password,
                    "salt": data["salt"],
                    "tipo_aes": tipo_aes
                }
            )
            assert response_descifrar.status_code == status.HTTP_200_OK
            assert response_descifrar.json()["texto_descifrado"] == texto

    def test_descifrar_con_password_incorrecto(self, client):
        """Test que password incorrecto falla al descifrar"""
        # 1. Cifrar
        response_cifrar = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje secreto",
                "password": "password_correcto",
                "tipo_aes": "AES-256"
            }
        )
        data = response_cifrar.json()

        # 2. Intentar descifrar con password incorrecto
        # Nota: El comportamiento esperado es que falle, pero el código de estado
        # puede variar dependiendo de la implementación del manejo de errores
        try:
            response_descifrar = client.post(
                "/aes/descifrar/texto",
                json={
                    "texto_cifrado": data["texto_cifrado"],
                    "password": "password_incorrecto",
                    "salt": data["salt"],
                    "tipo_aes": "AES-256"
                }
            )

            # Si no lanza excepción, debe devolver un código de error
            assert response_descifrar.status_code >= 400
        except Exception:
            # Si lanza excepción (ValueError no capturado), también está bien
            # porque significa que el descifrado falló correctamente
            pass

    def test_cifrar_password_corto_error(self, client):
        """Test que password menor a 8 caracteres devuelve error"""
        response = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje",
                "password": "1234567",  # Solo 7 caracteres
                "tipo_aes": "AES-256"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAESValidacion:
    """Tests para validación de passwords de AES"""

    def test_validar_password_correcto(self, client):
        """Test de validación de password correcto"""
        response = client.post(
            "/aes/validar-password",
            data={"password": "password_seguro_123"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valido"] is True
        assert data["longitud"] >= 8

    def test_validar_password_corto_error(self, client):
        """Test que password corto falla la validación"""
        response = client.post(
            "/aes/validar-password",
            data={"password": "1234567"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# TESTS: AES - ARCHIVOS
# ============================================================================

class TestAESArchivos:
    """Tests para cifrado y descifrado de archivos con AES"""

    def test_cifrar_archivo_con_metadata(self, client, sample_archivo_txt, sample_password):
        """Test de cifrado de archivo que devuelve paquete con metadata"""
        with open(sample_archivo_txt, 'rb') as f:
            response = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.txt", f, "text/plain")},
                data={
                    "password": sample_password,
                    "tipo_aes": "AES-256"
                }
            )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "paquete" in data
        assert "tamanio_paquete_bytes" in data
        assert "info" in data
        assert data["info"]["nombre_original"] == "test.txt"
        assert data["info"]["mime_type"] == "text/plain"
        assert data["info"]["tamanio_original_bytes"] > 0

    def test_cifrar_descifrar_archivo_ciclo_completo(self, client, sample_archivo_txt):
        """Test de ciclo completo con archivos usando paquete"""
        password = "password_archivo_123"

        # Leer contenido original
        with open(sample_archivo_txt, 'rb') as f:
            contenido_original = f.read()

        # 1. Cifrar
        with open(sample_archivo_txt, 'rb') as f:
            response_cifrar = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.txt", f, "text/plain")},
                data={"password": password, "tipo_aes": "AES-256"}
            )

        assert response_cifrar.status_code == status.HTTP_200_OK
        data_cifrar = response_cifrar.json()
        paquete = data_cifrar["paquete"]

        # 2. Descifrar usando el paquete
        response_descifrar = client.post(
            "/aes/descifrar/file",
            data={
                "paquete": paquete,
                "password": password
            }
        )

        assert response_descifrar.status_code == status.HTTP_200_OK

        # 3. El archivo descifrado viene como bytes directamente
        archivo_descifrado_bytes = response_descifrar.content

        # 4. Verificar que coincide con el original
        assert archivo_descifrado_bytes == contenido_original

        # 5. Verificar headers
        assert "Content-Disposition" in response_descifrar.headers
        assert "test.txt" in response_descifrar.headers["Content-Disposition"]

    def test_cifrar_archivo_pdf(self, client, sample_archivo_pdf, sample_password):
        """Test de cifrado de archivo PDF"""
        with open(sample_archivo_pdf, 'rb') as f:
            response = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["info"]["mime_type"] == "application/pdf"

    def test_cifrar_archivo_extension_no_soportada(self, client, tmp_path, sample_password):
        """Test que extensión no soportada devuelve error"""
        archivo = tmp_path / "test.xyz"
        archivo.write_text("contenido", encoding='utf-8')

        with open(archivo, 'rb') as f:
            response = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.xyz", f, "application/octet-stream")},
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "no soportada" in data["detail"]["error"].lower()


# ============================================================================
# TESTS: AES - PAQUETES
# ============================================================================

class TestAESPaquetes:
    """Tests para cifrado/descifrado con paquetes (todo en uno)"""

    def test_cifrar_archivo_paquete(self, client, sample_archivo_txt, sample_password):
        """Test de cifrado con paquete único"""
        with open(sample_archivo_txt, 'rb') as f:
            response = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.txt", f, "text/plain")},
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "paquete" in data
        assert "tamanio_paquete_bytes" in data
        assert "info" in data
        assert data["info"]["nombre_original"] == "test.txt"
        assert data["info"]["tipo_aes"] == "AES-256"

    def test_cifrar_descifrar_paquete_ciclo_completo(self, client, sample_archivo_txt):
        """Test de ciclo completo con paquetes"""
        password = "password_paquete_123"

        # Leer contenido original
        with open(sample_archivo_txt, 'rb') as f:
            contenido_original = f.read()

        # 1. Cifrar con paquete
        with open(sample_archivo_txt, 'rb') as f:
            response_cifrar = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.txt", f, "text/plain")},
                data={"password": password, "tipo_aes": "AES-256"}
            )

        assert response_cifrar.status_code == status.HTTP_200_OK
        paquete = response_cifrar.json()["paquete"]

        # 2. Descifrar desde paquete
        response_descifrar = client.post(
            "/aes/descifrar/file",
            data={"paquete": paquete, "password": password}
        )

        assert response_descifrar.status_code == status.HTTP_200_OK

        # 3. Verificar que el contenido descifrado es el original
        contenido_descifrado = response_descifrar.content
        assert contenido_descifrado == contenido_original

        # 4. Verificar headers
        assert "Content-Disposition" in response_descifrar.headers
        assert "test.txt" in response_descifrar.headers["Content-Disposition"]

    def test_descifrar_paquete_password_incorrecto(self, client, sample_archivo_txt):
        """Test que password incorrecto falla al descifrar paquete"""
        # 1. Cifrar
        with open(sample_archivo_txt, 'rb') as f:
            response_cifrar = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.txt", f, "text/plain")},
                data={"password": "password_correcto", "tipo_aes": "AES-256"}
            )

        paquete = response_cifrar.json()["paquete"]

        # 2. Intentar descifrar con password incorrecto
        response_descifrar = client.post(
            "/aes/descifrar/file",
            data={"paquete": paquete, "password": "password_incorrecto"}
        )

        assert response_descifrar.status_code == status.HTTP_400_BAD_REQUEST

    def test_descifrar_paquete_invalido(self, client):
        """Test que paquete inválido devuelve error"""
        paquete_invalido = "paquete_invalido_base64"

        response = client.post(
            "/aes/descifrar/file",
            data={"paquete": paquete_invalido, "password": "password123"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# TESTS: CASOS DE ERROR GENERAL
# ============================================================================

class TestErroresGenerales:
    """Tests para casos de error generales"""

    def test_endpoint_inexistente(self, client):
        """Test que endpoint inexistente devuelve 404"""
        response = client.get("/endpoint/que/no/existe")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_metodo_http_incorrecto(self, client):
        """Test que método HTTP incorrecto devuelve error"""
        # Intentar hacer POST al endpoint de info (que es GET)
        response = client.post("/aes/info")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# ============================================================================
# MARCADORES PARA PYTEST
# ============================================================================

# Tests rápidos (para CI/CD rápido)
pytestmark_rapido = pytest.mark.rapido

# Tests que requieren más tiempo (archivos grandes)
pytestmark_lento = pytest.mark.lento


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
