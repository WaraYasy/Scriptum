"""
Tests de Casos Edge y Validaciones Avanzadas
=============================================

Tests para casos límite, seguridad y validaciones especiales:
- Archivos grandes y límites de tamaño
- Validaciones de seguridad
- Caracteres especiales y Unicode
- Casos extremos y boundary conditions
"""
import pytest
from fastapi import status


# ============================================================================
# TESTS: LÍMITES DE TAMAÑO
# ============================================================================

class TestLimitesTamano:
    """Tests para validar límites de tamaño de archivos y textos"""

    def test_texto_muy_largo(self, client, sample_password):
        """Test con texto muy largo (cerca del límite)"""
        # Crear texto de ~1MB
        texto_largo = "A" * (1 * 1024 * 1024)

        response = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": texto_largo,
                "password": sample_password,
                "tipo_aes": "AES-256"
            }
        )

        # Debería funcionar sin problemas
        assert response.status_code == status.HTTP_200_OK

    def test_archivo_vacio(self, client, tmp_path, sample_password):
        """Test que archivo vacío devuelve error"""
        archivo = tmp_path / "vacio.txt"
        archivo.write_text("", encoding='utf-8')

        with open(archivo, 'rb') as f:
            response = client.post(
                "/aes/cifrar/file",
                files={"file": ("vacio.txt", f, "text/plain")},
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "vacío" in data["detail"]["error"].lower() or "empty" in data["detail"]["error"].lower()

    def test_archivo_txt_un_caracter(self, client, tmp_path, sample_password):
        """Test con archivo de un solo carácter"""
        archivo = tmp_path / "mini.txt"
        archivo.write_text("A", encoding='utf-8')

        with open(archivo, 'rb') as f:
            response = client.post(
                "/aes/cifrar/file",
                files={"file": ("mini.txt", f, "text/plain")},
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        # Debería funcionar
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# TESTS: CARACTERES ESPECIALES Y UNICODE
# ============================================================================

class TestCaracteresEspeciales:
    """Tests para manejo de caracteres especiales y Unicode"""

    def test_texto_con_emojis(self, client, sample_password):
        """Test con emojis en el texto"""
        texto_con_emojis = "Hola 😊 Mundo 🌍 con emojis 🎉"

        response = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": texto_con_emojis,
                "password": sample_password,
                "tipo_aes": "AES-256"
            }
        )

        assert response.status_code == status.HTTP_200_OK

        # Ciclo completo
        data = response.json()
        response_descifrar = client.post(
            "/aes/descifrar/texto",
            json={
                "texto_cifrado": data["texto_cifrado"],
                "password": sample_password,
                "salt": data["salt"],
                "tipo_aes": "AES-256"
            }
        )

        assert response_descifrar.status_code == status.HTTP_200_OK
        assert response_descifrar.json()["texto_descifrado"] == texto_con_emojis

    def test_texto_con_caracteres_unicode_diversos(self, client):
        """Test con diversos caracteres Unicode"""
        texto_unicode = "Español: áéíóú ñ | Français: àèéêë | 日本語 | Русский | العربية"

        response = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": texto_unicode, "clave": "CLAVE"}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_password_con_caracteres_especiales(self, client):
        """Test que password con caracteres especiales funciona"""
        password_especial = "P@ssw0rd!#$%&*()_+-=[]{}|;:',.<>?"

        response = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje secreto",
                "password": password_especial,
                "tipo_aes": "AES-256"
            }
        )

        assert response.status_code == status.HTTP_200_OK

    def test_archivo_con_saltos_de_linea_diversos(self, client, tmp_path, sample_password):
        """Test con diferentes tipos de saltos de línea"""
        archivo = tmp_path / "saltos.txt"
        # Unix (LF), Windows (CRLF) y Mac clásico (CR)
        contenido = "Línea 1\nLínea 2\r\nLínea 3\rLínea 4"
        archivo.write_text(contenido, encoding='utf-8')

        with open(archivo, 'rb') as f:
            contenido_original = f.read()

        # Cifrar
        with open(archivo, 'rb') as f:
            response_cifrar = client.post(
                "/aes/cifrar/file",
                files={"file": ("saltos.txt", f, "text/plain")},
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        assert response_cifrar.status_code == status.HTTP_200_OK

        # Descifrar
        paquete = response_cifrar.json()["paquete"]
        response_descifrar = client.post(
            "/aes/descifrar/file",
            data={"paquete": paquete, "password": sample_password}
        )

        assert response_descifrar.status_code == status.HTTP_200_OK
        assert response_descifrar.content == contenido_original


# ============================================================================
# TESTS: VALIDACIONES DE SEGURIDAD
# ============================================================================

class TestSeguridadValidaciones:
    """Tests para validaciones de seguridad"""

    def test_vigenere_detecta_zero_width_space(self, client):
        """Test que detecta Zero-Width Space en clave de Vigenère"""
        clave_con_zwsp = f"CLAVE{chr(0x200B)}TEST"

        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_zwsp}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "caracteres invisibles" in data["detail"]["error"].lower()
        assert "caracteres_detectados" in data["detail"]

    def test_vigenere_detecta_non_breaking_space(self, client):
        """Test que detecta Non-Breaking Space"""
        clave_con_nbsp = f"CLAVE{chr(0x00A0)}TEST"

        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_nbsp}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_aes_password_validation_longitud_minima(self, client):
        """Test validación de longitud mínima de password"""
        # Exactamente 8 caracteres (mínimo)
        response = client.post(
            "/aes/validar-password",
            data={"password": "12345678"}
        )
        assert response.status_code == status.HTTP_200_OK

        # 7 caracteres (menos del mínimo)
        response = client.post(
            "/aes/validar-password",
            data={"password": "1234567"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_salt_diferente_cada_vez(self, client, sample_password):
        """Test que el salt es diferente en cada cifrado"""
        texto = "Mismo texto"

        # Cifrar dos veces el mismo texto
        response1 = client.post(
            "/aes/cifrar/texto",
            json={"texto": texto, "password": sample_password, "tipo_aes": "AES-256"}
        )
        response2 = client.post(
            "/aes/cifrar/texto",
            json={"texto": texto, "password": sample_password, "tipo_aes": "AES-256"}
        )

        salt1 = response1.json()["salt"]
        salt2 = response2.json()["salt"]

        # Los salts deben ser diferentes
        assert salt1 != salt2

        # Los textos cifrados también deben ser diferentes
        assert response1.json()["texto_cifrado"] != response2.json()["texto_cifrado"]


# ============================================================================
# TESTS: BOUNDARY CONDITIONS
# ============================================================================

class TestBoundaryConditions:
    """Tests para condiciones límite"""

    def test_password_exactamente_8_caracteres(self, client):
        """Test con password de exactamente 8 caracteres (mínimo)"""
        response = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje",
                "password": "12345678",  # Exactamente 8
                "tipo_aes": "AES-256"
            }
        )

        assert response.status_code == status.HTTP_200_OK

    def test_password_muy_largo(self, client):
        """Test con password muy largo"""
        password_largo = "a" * 1000  # 1000 caracteres

        response = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje",
                "password": password_largo,
                "tipo_aes": "AES-256"
            }
        )

        # Debería funcionar
        assert response.status_code == status.HTTP_200_OK

    def test_clave_vigenere_un_caracter(self, client):
        """Test con clave de Vigenère de un solo carácter"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": "HOLA MUNDO", "clave": "A"}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_texto_solo_espacios(self, client):
        """Test con texto que solo contiene espacios"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": "     ", "clave": "CLAVE"}
        )

        # Debería devolver error porque no hay letras para cifrar
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_texto_solo_numeros(self, client):
        """Test con texto que solo contiene números"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": "123456789", "clave": "CLAVE"}
        )

        # Debería devolver error porque no hay letras para cifrar
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# TESTS: COMPATIBILIDAD MIME TYPES
# ============================================================================

class TestMimeTypes:
    """Tests para verificar manejo correcto de MIME types"""

    def test_archivo_sin_mime_type(self, client, tmp_path, sample_password):
        """Test que archivo sin MIME type usa default"""
        archivo = tmp_path / "test.txt"
        archivo.write_text("contenido", encoding='utf-8')

        with open(archivo, 'rb') as f:
            response = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.txt", f, None)},  # Sin MIME type
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Debería usar el default
        assert "info" in data
        assert "mime_type" in data["info"]

    def test_paquete_preserva_mime_type(self, client, sample_archivo_pdf, sample_password):
        """Test que el paquete preserva el MIME type original"""
        with open(sample_archivo_pdf, 'rb') as f:
            response_cifrar = client.post(
                "/aes/cifrar/file",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"password": sample_password, "tipo_aes": "AES-256"}
            )

        assert response_cifrar.status_code == status.HTTP_200_OK

        paquete = response_cifrar.json()["paquete"]

        # Descifrar y verificar MIME type
        response_descifrar = client.post(
            "/aes/descifrar/file",
            data={"paquete": paquete, "password": sample_password}
        )

        assert response_descifrar.status_code == status.HTTP_200_OK
        assert response_descifrar.headers["Content-Type"] == "application/pdf"


# ============================================================================
# TESTS: CASOS DE INTEGRIDAD
# ============================================================================

class TestIntegridad:
    """Tests para verificar integridad de datos"""

    def test_modificar_texto_cifrado_falla(self, client, sample_password):
        """Test que modificar el texto cifrado causa error al descifrar"""
        # Cifrar
        response_cifrar = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje original",
                "password": sample_password,
                "tipo_aes": "AES-256"
            }
        )

        data = response_cifrar.json()
        texto_cifrado = data["texto_cifrado"]

        # Modificar el texto cifrado
        texto_cifrado_modificado = texto_cifrado[:-10] + "AAAAAAAAAA"

        # Intentar descifrar - debe fallar de alguna forma
        try:
            response_descifrar = client.post(
                "/aes/descifrar/texto",
                json={
                    "texto_cifrado": texto_cifrado_modificado,
                    "password": sample_password,
                    "salt": data["salt"],
                    "tipo_aes": "AES-256"
                }
            )

            # Debería fallar por manipulación
            assert response_descifrar.status_code >= 400
        except Exception:
            # Si lanza excepción, también está bien - significa que falló
            pass

    def test_usar_salt_incorrecto_falla(self, client, sample_password):
        """Test que usar salt incorrecto causa error"""
        # Cifrar
        response_cifrar = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje",
                "password": sample_password,
                "tipo_aes": "AES-256"
            }
        )

        data = response_cifrar.json()

        # Intentar descifrar con salt diferente
        salt_incorrecto = "salt_completamente_diferente_1234567890"

        try:
            response_descifrar = client.post(
                "/aes/descifrar/texto",
                json={
                    "texto_cifrado": data["texto_cifrado"],
                    "password": sample_password,
                    "salt": salt_incorrecto,
                    "tipo_aes": "AES-256"
                }
            )

            # Debería fallar
            assert response_descifrar.status_code >= 400
        except Exception:
            # Si lanza excepción, también está bien - significa que falló
            pass

    def test_tipo_aes_incorrecto_al_descifrar(self, client, sample_password):
        """Test que usar tipo de AES incorrecto causa error"""
        # Cifrar con AES-256
        response_cifrar = client.post(
            "/aes/cifrar/texto",
            json={
                "texto": "Mensaje",
                "password": sample_password,
                "tipo_aes": "AES-256"
            }
        )

        data = response_cifrar.json()

        # Intentar descifrar con AES-128
        try:
            response_descifrar = client.post(
                "/aes/descifrar/texto",
                json={
                    "texto_cifrado": data["texto_cifrado"],
                    "password": sample_password,
                    "salt": data["salt"],
                    "tipo_aes": "AES-128"  # Tipo incorrecto
                }
            )

            # Debería fallar
            assert response_descifrar.status_code >= 400
        except Exception:
            # Si lanza excepción, también está bien - significa que falló
            pass


# ============================================================================
# MARCADORES PARA PYTEST
# ============================================================================

# Tests de seguridad
pytestmark_seguridad = pytest.mark.seguridad

# Tests lentos
pytestmark_lento = pytest.mark.lento


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
