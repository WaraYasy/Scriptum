"""
Tests para app/routers/vigenere.py
Prueba los endpoints de la API incluyendo:
- Validación de claves (caracteres invisibles)
- Canary check
- Archivos grandes (streaming)
"""
from fastapi.testclient import TestClient
from io import BytesIO
from main import app

client = TestClient(app)


class TestValidacionClave:
    """Tests para el endpoint /vigenere/validar-clave"""

    def test_clave_valida_sin_caracteres_invisibles(self):
        """Prueba clave válida sin caracteres problemáticos"""
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": "clavesecreta"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valida"] is True
        assert data["clave_limpia"] == "CLAVESECRETA"
        assert "sin caracteres invisibles" in data["mensaje"]

    def test_clave_con_zero_width_space(self):
        """Prueba clave con Zero-Width Space (U+200B)"""
        clave_con_invisible = "clave\u200Bsecreta"
        
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisible}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "caracteres invisibles" in data["detail"]["error"]
        assert len(data["detail"]["caracteres_detectados"]) > 0
        assert data["detail"]["caracteres_detectados"][0]["caracter"] == "U+200B"

    def test_clave_con_zero_width_non_joiner(self):
        """Prueba clave con Zero-Width Non-Joiner (U+200C)"""
        clave_con_invisible = "mi\u200Cclave"
        
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisible}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert len(data["detail"]["caracteres_detectados"]) > 0
        assert data["detail"]["caracteres_detectados"][0]["caracter"] == "U+200C"

    def test_clave_con_zero_width_joiner(self):
        """Prueba clave con Zero-Width Joiner (U+200D)"""
        clave_con_invisible = "clave\u200Dtest"
        
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisible}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["caracteres_detectados"][0]["caracter"] == "U+200D"

    def test_clave_con_zero_width_no_break_space(self):
        """Prueba clave con Zero-Width No-Break Space (U+FEFF)"""
        clave_con_invisible = "\uFEFFclave"
        
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisible}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["caracteres_detectados"][0]["caracter"] == "U+FEFF"

    def test_clave_con_non_breaking_space(self):
        """Prueba clave con Non-Breaking Space (U+00A0)"""
        clave_con_invisible = "clave\u00A0test"
        
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisible}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["caracteres_detectados"][0]["caracter"] == "U+00A0"

    def test_clave_con_multiples_caracteres_invisibles(self):
        """Prueba clave con varios caracteres invisibles"""
        clave_con_invisibles = "clave\u200B\u200C\u200Dtest"
        
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisibles}
        )
        
        assert response.status_code == 400
        data = response.json()
        # Debe detectar los 3 caracteres
        assert len(data["detail"]["caracteres_detectados"]) == 3

    def test_posicion_caracter_invisible(self):
        """Prueba que la posición del caracter invisible es correcta"""
        clave_con_invisible = "01234\u200B67890"  # Invisible en posición 5
        
        response = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave_con_invisible}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["caracteres_detectados"][0]["posicion"] == 5


class TestCanaryCheck:
    """
    Tests exhaustivos para el canary check en archivos grandes

    El canary check valida los primeros 1KB del archivo antes de procesarlo todo,
    ahorrando tiempo y recursos si la clave es incorrecta.
    """

    def crear_archivo_txt(self, contenido: str) -> BytesIO:
        """Helper para crear un archivo en memoria"""
        return BytesIO(contenido.encode('utf-8'))

    # ========================================================================
    # TESTS BÁSICOS DE CANARY CHECK
    # ========================================================================

    def test_canary_check_clave_correcta(self):
        """✅ Prueba canary check con clave correcta - debe pasar"""
        # Crear texto con magic header (solo letras, compatible con Vigenère)
        texto_original = "SCRIPTUM Este es el contenido del archivo grande con mucho texto"

        # Cifrar el texto para simular un archivo cifrado
        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "CLAVECORRECTA")

        # Crear archivo simulado
        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "CLAVECORRECTA",
                "magic_header": "SCRIPTUM"  # Magic header solo con letras
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"
        assert "SCRIPTUM" in data["texto_descifrado"]
        assert "mensaje" in data
        assert data["mensaje"] == "Archivo descifrado exitosamente"

    def test_canary_check_clave_incorrecta(self):
        """❌ Prueba canary check con clave incorrecta - debe fallar rápidamente"""
        # Crear texto con magic header
        texto_original = "SCRIPTUM Contenido cifrado con clave correcta"

        # Cifrar con una clave
        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "CLAVECORRECTA")

        # Crear archivo simulado
        file = self.crear_archivo_txt(texto_cifrado)

        # Intentar descifrar con clave incorrecta
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "CLAVEINCORRECTA",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "Canary check failed" in data["detail"]["error"]
        assert "esperado" in data["detail"]
        assert "recibido" in data["detail"]
        assert "sugerencia" in data["detail"]
        assert "SCRIPTUM" in data["detail"]["esperado"]

    def test_canary_check_skip(self):
        """⏭️ Prueba omitir canary check con skip_canary=True"""
        texto_cifrado = "TEXTOCIFRADOSINMAGICHEADER"
        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "TESTKEY",
                "skip_canary": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "skipped"
        assert "texto_descifrado" in data

    # ========================================================================
    # TESTS DE MAGIC HEADERS
    # ========================================================================

    def test_canary_check_magic_header_personalizado(self):
        """🎯 Prueba canary check con magic header personalizado"""
        texto_original = "HOGWARTS Contenido del archivo secreto"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "MIKEY")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "MIKEY",
                "magic_header": "HOGWARTS"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"
        assert "HOGWARTS" in data["texto_descifrado"]

    def test_canary_check_magic_header_largo(self):
        """📏 Prueba con magic header muy largo (más de 100 caracteres)"""
        # Magic header de 150 caracteres
        magic_largo = "THISISAVERYLONGMAGICHEADERTOTESTTHECANARYCHECKFUNCTIONALITYWITHEXTREMELYLONGHEADERSTHATSHOULDSTILLWORKPROPERLYANDSECURELY" * 2
        texto_original = magic_largo + " Contenido del archivo"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "LONGKEY")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "LONGKEY",
                "magic_header": magic_largo
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    def test_canary_check_magic_header_una_letra(self):
        """🔤 Prueba con magic header de una sola letra"""
        texto_original = "X Este es el contenido"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "KEY")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "KEY",
                "magic_header": "X"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    def test_canary_check_archivo_sin_magic_header(self):
        """❌ Prueba cuando el archivo no tiene el magic header esperado"""
        texto_original = "Este archivo no tiene magic header"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "KEY")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "KEY",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "Canary check failed" in data["detail"]["error"]

    def test_canary_check_magic_header_con_espacios(self):
        """🔍 Prueba magic header con espacios (se eliminan al procesar)"""
        # Nota: Los espacios se eliminan por formatear_texto()
        texto_original = "MAGIC HEADER Contenido"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "KEY")

        file = self.crear_archivo_txt(texto_cifrado)

        # El magic header sin espacios debe coincidir
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "KEY",
                "magic_header": "MAGICHEADER"  # Sin espacios
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    # ========================================================================
    # TESTS DE CLAVES SIMILARES (Edge Cases)
    # ========================================================================

    def test_canary_check_claves_similares(self):
        """🎭 Prueba con claves completamente diferentes"""
        texto_original = "SCRIPTUM Contenido secreto"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "SECRETKEY")

        file = self.crear_archivo_txt(texto_cifrado)

        # Intentar con clave completamente diferente
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "WRONGKEY",  # Clave totalmente diferente
                "magic_header": "SCRIPTUM"
            }
        )

        # El canary check debe fallar porque la clave es incorrecta
        # y el magic header no coincidirá al descifrar
        assert response.status_code == 400
        data = response.json()
        assert "Canary check failed" in data["detail"]["error"]

    def test_canary_check_clave_con_mayusculas_minusculas(self):
        """🔠 Prueba que mayúsculas/minúsculas se manejan correctamente"""
        texto_original = "SCRIPTUM Contenido"

        from app.services.vigenere import cifrar_vigenere
        # Cifrar con minúsculas
        texto_cifrado = cifrar_vigenere(texto_original, "claveminuscula")

        file = self.crear_archivo_txt(texto_cifrado)

        # Descifrar con mayúsculas (debe funcionar)
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "CLAVEMINUSCULA",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    def test_canary_check_clave_muy_corta(self):
        """🔑 Prueba canary check con clave de 1 letra"""
        texto_original = "SCRIPTUM " + "A" * 2000

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "K")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "K",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    def test_canary_check_clave_muy_larga(self):
        """🔐 Prueba canary check con clave extremadamente larga"""
        clave_larga = "ESTAESUNACLAVEMUYLARGUISIMAQUETIENEMUCHASLETRASPARAPROBARELFUNCIONAMIENTODELCANARYCHECK" * 5
        texto_original = "SCRIPTUM Contenido"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, clave_larga)

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": clave_larga,
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    # ========================================================================
    # TESTS DE TAMAÑOS DE ARCHIVO
    # ========================================================================

    def test_canary_check_archivo_exactamente_1kb(self):
        """📦 Prueba con archivo de exactamente 1KB (tamaño del canary)"""
        # 1KB = 1024 bytes
        texto_original = "SCRIPTUM " + "A" * 1010  # ~1KB después de cifrar

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "KEY1KB")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "KEY1KB",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    def test_canary_check_archivo_menor_1kb(self):
        """📄 Prueba con archivo menor a 1KB"""
        texto_original = "SCRIPTUM ABC"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "TINY")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "TINY",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    def test_canary_check_archivo_100mb(self):
        """💾 Prueba con archivo muy grande (100MB)"""
        # Generar ~100 MB de texto
        bloque = "SCRIPTUMTEST" * 100  # 1200 caracteres
        texto_original = "SCRIPTUM " + bloque * 85000  # ~100 MB

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "BIGKEY100MB")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "BIGKEY100MB",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"
        # Ajuste: permitir margen debido a overhead de formateo
        assert data["tamanio_archivo_mb"] > 95

    # ========================================================================
    # TESTS DE SEGURIDAD Y EDGE CASES
    # ========================================================================

    def test_canary_check_detecta_archivo_corrupto(self):
        """⚠️ Prueba que canary detecta archivo corrupto/modificado"""
        texto_original = "SCRIPTUM Contenido original"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "KEY")

        # Corromper el inicio del archivo cifrado
        texto_corrupto = "CORRUPTED" + texto_cifrado[9:]

        file = self.crear_archivo_txt(texto_corrupto)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "KEY",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 400
        assert "Canary check failed" in response.json()["detail"]["error"]

    def test_canary_check_con_archivo_binario_parcial(self):
        """🚫 Prueba que canary detecta contenido no-texto en el canary"""
        # Crear contenido con bytes no UTF-8 válidos en los primeros 1KB
        contenido_invalido = b'\xFF\xFE\xFD' * 300  # Bytes inválidos

        file = BytesIO(contenido_invalido)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "KEY",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 400
        # Verificar que el error menciona UTF-8
        error_msg = response.json()["detail"]["error"]
        assert "UTF-8" in error_msg or "utf-8" in error_msg.lower()

    def test_canary_check_multiples_archivos_concurrentes(self):
        """🔄 Prueba canary check con múltiples archivos (simula concurrencia)"""
        from app.services.vigenere import cifrar_vigenere

        # Crear 3 archivos diferentes
        archivos = [
            ("SCRIPTUM Archivo uno", "KEY1"),
            ("SCRIPTUM Archivo dos", "KEY2"),
            ("SCRIPTUM Archivo tres", "KEY3")
        ]

        for texto, clave in archivos:
            texto_cifrado = cifrar_vigenere(texto, clave)
            file = self.crear_archivo_txt(texto_cifrado)

            response = client.post(
                "/vigenere/descifrar/file/large",
                files={"file": ("test.txt", file, "text/plain")},
                data={
                    "clave": clave,
                    "magic_header": "SCRIPTUM"
                }
            )

            assert response.status_code == 200
            assert response.json()["canary_check"] == "passed"

    # ========================================================================
    # TESTS DE RESPUESTAS Y METADATOS
    # ========================================================================

    def test_canary_check_metadatos_completos(self):
        """📊 Prueba que la respuesta incluye todos los metadatos esperados"""
        texto_original = "SCRIPTUM " + "TEST" * 500

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "METAKEY")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "METAKEY",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar todos los campos esperados
        assert "texto_descifrado" in data
        assert "clave_usada" in data
        assert "tamanio_archivo_bytes" in data
        assert "tamanio_archivo_mb" in data
        assert "canary_check" in data
        assert "mensaje" in data

        assert data["clave_usada"] == "METAKEY"
        assert data["canary_check"] == "passed"
        assert data["tamanio_archivo_bytes"] > 0
        assert isinstance(data["tamanio_archivo_mb"], (int, float))

    def test_canary_check_mensaje_error_descriptivo(self):
        """💬 Prueba que el mensaje de error del canary es descriptivo"""
        texto_original = "SCRIPTUM Contenido"

        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(texto_original, "CORRECTKEY")

        file = self.crear_archivo_txt(texto_cifrado)

        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": "WRONGKEY",
                "magic_header": "SCRIPTUM"
            }
        )

        assert response.status_code == 400
        data = response.json()["detail"]

        # Verificar que el error es descriptivo
        assert "error" in data
        assert "esperado" in data
        assert "recibido" in data
        assert "sugerencia" in data

        assert "Canary check failed" in data["error"]
        assert "SCRIPTUM" in data["esperado"]
        assert "Verifica que la clave sea correcta" in data["sugerencia"]


class TestArchivosGrandes:
    """Tests para procesamiento de archivos grandes (streaming)"""

    def crear_archivo_txt(self, contenido: str) -> BytesIO:
        """Helper para crear un archivo en memoria"""
        return BytesIO(contenido.encode('utf-8'))

    def test_archivo_grande_15mb(self):
        """Prueba procesamiento de archivo de ~15 MB"""
        # Generar contenido de 15 MB
        bloque = "TESTCONTENT" * 100  # 1100 caracteres
        contenido_grande = bloque * 14000  # ~15 MB
        
        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(contenido_grande, "BIGKEY")
        
        file = self.crear_archivo_txt(texto_cifrado)
        
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("large.txt", file, "text/plain")},
            data={
                "clave": "BIGKEY",
                "skip_canary": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tamanio_archivo_mb"] > 14
        assert data["texto_descifrado"] == contenido_grande

    def test_archivo_pequeno_menos_10mb(self):
        """Prueba que archivos pequeños también funcionan en /large"""
        contenido = "SCRIPTUM Contenido pequeño de prueba"
        
        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(contenido, "SMALLKEY")
        
        file = self.crear_archivo_txt(texto_cifrado)
        
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("small.txt", file, "text/plain")},
            data={
                "clave": "SMALLKEY",
                "magic_header": "SCRIPTUM"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["canary_check"] == "passed"

    def test_metadatos_archivo_grande(self):
        """Prueba que los metadatos del archivo se retornan correctamente"""
        contenido = "SCRIPTUM " + "A" * 10000  # ~10 KB
        
        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(contenido, "METAKEY")
        
        file = self.crear_archivo_txt(texto_cifrado)
        
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("meta.txt", file, "text/plain")},
            data={
                "clave": "METAKEY",
                "magic_header": "SCRIPTUM"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tamanio_archivo_bytes" in data
        assert "tamanio_archivo_mb" in data
        assert "clave_usada" in data
        assert data["clave_usada"] == "METAKEY"


class TestValidacionClaveEnEndpoints:
    """Tests de validación de caracteres invisibles en endpoints de cifrado/descifrado"""

    def test_cifrar_texto_con_clave_invisible(self):
        """Prueba que cifrar texto rechaza clave con caracteres invisibles"""
        response = client.post(
            "/vigenere/cifrar/texto",
            json={
                "texto": "Hola mundo",
                "clave": "clave\u200Btest"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "caracteres invisibles" in data["detail"]["error"]

    def test_descifrar_texto_con_clave_invisible(self):
        """Prueba que descifrar texto rechaza clave con caracteres invisibles"""
        response = client.post(
            "/vigenere/descifrar/texto",
            json={
                "texto_cifrado": "RIJVS",
                "clave": "key\u200C"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "caracteres invisibles" in data["detail"]["error"]

    def crear_archivo_txt(self, contenido: str) -> BytesIO:
        """Helper para crear un archivo en memoria"""
        return BytesIO(contenido.encode('utf-8'))

    def test_cifrar_archivo_con_clave_invisible(self):
        """Prueba que cifrar archivo rechaza clave con caracteres invisibles"""
        file = self.crear_archivo_txt("Contenido de prueba")
        
        response = client.post(
            "/vigenere/cifrar/file",
            files={"file": ("test.txt", file, "text/plain")},
            data={"clave": "test\u200Dkey"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "caracteres invisibles" in data["detail"]["error"]

    def test_descifrar_archivo_con_clave_invisible(self):
        """Prueba que descifrar archivo rechaza clave con caracteres invisibles"""
        file = self.crear_archivo_txt("TESTCIFRADO")
        
        response = client.post(
            "/vigenere/descifrar/file",
            files={"file": ("test.txt", file, "text/plain")},
            data={"clave": "\uFEFFkey"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "caracteres invisibles" in data["detail"]["error"]

    def test_descifrar_archivo_grande_con_clave_invisible(self):
        """Prueba que descifrar archivo grande rechaza clave con caracteres invisibles"""
        file = self.crear_archivo_txt("TESTCIFRADOGRANDE" * 1000)
        
        response = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={"clave": "key\u00A0test"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "caracteres invisibles" in data["detail"]["error"]


class TestIntegracionCompleta:
    """Tests de integración que combinan varias funcionalidades"""

    def crear_archivo_txt(self, contenido: str) -> BytesIO:
        """Helper para crear un archivo en memoria"""
        return BytesIO(contenido.encode('utf-8'))

    def test_flujo_completo_validacion_cifrado_descifrado(self):
        """Prueba flujo completo: validar clave -> cifrar -> descifrar"""
        clave = "CLAVEPRUEBA"
        texto = "Este es un texto de prueba para el flujo completo"
        
        # 1. Validar clave
        response_val = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave}
        )
        assert response_val.status_code == 200
        assert response_val.json()["valida"] is True
        
        # 2. Cifrar
        response_cifrar = client.post(
            "/vigenere/cifrar/texto",
            json={"texto": texto, "clave": clave}
        )
        assert response_cifrar.status_code == 200
        texto_cifrado = response_cifrar.json()["texto_cifrado"]
        
        # 3. Descifrar
        response_descifrar = client.post(
            "/vigenere/descifrar/texto",
            json={"texto_cifrado": texto_cifrado, "clave": clave}
        )
        assert response_descifrar.status_code == 200
        
        # Verificar que el texto descifrado coincide (sin espacios/símbolos)
        texto_limpio = ''.join(c.upper() for c in texto if c.isalpha())
        assert response_descifrar.json()["texto_descifrado"] == texto_limpio

    def test_archivo_grande_con_canary_y_validacion(self):
        """Prueba archivo grande con canary check y validación de clave"""
        clave = "TESTINTEGRATION"
        contenido = "SCRIPTUM " + "CONTENIDO" * 5000  # ~45 KB
        contenido_esperado = ''.join(c.upper() for c in contenido if c.isalpha())  # Sin espacios
        
        # 1. Validar clave
        response_val = client.post(
            "/vigenere/validar-clave",
            data={"clave": clave}
        )
        assert response_val.status_code == 200
        
        # 2. Cifrar contenido
        from app.services.vigenere import cifrar_vigenere
        texto_cifrado = cifrar_vigenere(contenido, clave)
        
        # 3. Descifrar con canary check
        file = self.crear_archivo_txt(texto_cifrado)
        response_descifrar = client.post(
            "/vigenere/descifrar/file/large",
            files={"file": ("test.txt", file, "text/plain")},
            data={
                "clave": clave,
                "magic_header": "SCRIPTUM"
            }
        )
        
        assert response_descifrar.status_code == 200
        data = response_descifrar.json()
        assert data["canary_check"] == "passed"
        assert data["texto_descifrado"] == contenido_esperado  # Comparar con contenido formateado

    def test_rechazo_clave_invalida_en_todos_endpoints(self):
        """Prueba que todos los endpoints rechazan claves con caracteres invisibles"""
        clave_invalida = "test\u200Bkey"
        
        # Endpoint de validación
        r1 = client.post("/vigenere/validar-clave", data={"clave": clave_invalida})
        assert r1.status_code == 400
        
        # Endpoint de cifrar texto
        r2 = client.post("/vigenere/cifrar/texto", json={"texto": "test", "clave": clave_invalida})
        assert r2.status_code == 400
        
        # Endpoint de descifrar texto
        r3 = client.post("/vigenere/descifrar/texto", json={"texto_cifrado": "TEST", "clave": clave_invalida})
        assert r3.status_code == 400
        
        # Verificar que todos retornan el mismo tipo de error
        assert "caracteres invisibles" in r1.json()["detail"]["error"]
        assert "caracteres invisibles" in r2.json()["detail"]["error"]
        assert "caracteres invisibles" in r3.json()["detail"]["error"]
