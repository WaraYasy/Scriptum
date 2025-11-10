"""
Tests para app/services/vigenere.py
Prueba las funciones puras de cifrado/descifrado
"""
import pytest
from app.services.vigenere import (
    cifrar_vigenere,
    descifrar_vigenere,
    validar_y_formatear_clave,
    formatear_texto,
    ajustar_clave
)


class TestCifrarVigenere:
    """Tests para la función cifrar_vigenere"""

    def test_cifrar_texto_simple(self):
        """Prueba cifrado básico"""
        resultado = cifrar_vigenere("HELLO", "KEY")
        assert resultado == "RIJVS"

    def test_cifrar_con_espacios(self):
        """Prueba que los espacios se eliminan"""
        resultado = cifrar_vigenere("HELLO WORLD", "KEY")
        assert resultado == "RIJVSUYVJN"

    def test_cifrar_con_minusculas(self):
        """Prueba que convierte a mayúsculas"""
        resultado = cifrar_vigenere("hello world", "key")
        assert resultado == "RIJVSUYVJN"

    def test_cifrar_con_numeros(self):
        """Prueba que ignora números"""
        resultado = cifrar_vigenere("HELLO 123 WORLD", "KEY")
        assert resultado == "RIJVSUYVJN"

    def test_cifrar_con_simbolos(self):
        """Prueba que ignora símbolos"""
        resultado = cifrar_vigenere("HELLO, WORLD!", "KEY")
        assert resultado == "RIJVSUYVJN"

    def test_cifrar_texto_vacio_raise_error(self):
        """Prueba que falla con texto vacío"""
        with pytest.raises(ValueError, match="no contiene caracteres válidos"):
            cifrar_vigenere("", "KEY")

    def test_cifrar_solo_numeros_raise_error(self):
        """Prueba que falla con solo números"""
        with pytest.raises(ValueError, match="no contiene caracteres válidos"):
            cifrar_vigenere("12345", "KEY")

    def test_cifrar_clave_vacia_raise_error(self):
        """Prueba que falla con clave vacía"""
        with pytest.raises(ValueError, match="clave no puede estar vacía"):
            cifrar_vigenere("HELLO", "")

    def test_cifrar_clave_sin_letras_raise_error(self):
        """Prueba que falla con clave sin letras"""
        with pytest.raises(ValueError, match="debe contener al menos una letra"):
            cifrar_vigenere("HELLO", "12345")


class TestDescifrarVigenere:
    """Tests para la función descifrar_vigenere"""

    def test_descifrar_texto_simple(self):
        """Prueba descifrado básico"""
        resultado = descifrar_vigenere("RIJVS", "KEY")
        assert resultado == "HELLO"

    def test_descifrar_texto_largo(self):
        """Prueba descifrado de texto largo"""
        resultado = descifrar_vigenere("RIJVSUYVJN", "KEY")
        assert resultado == "HELLOWORLD"

    def test_descifrar_con_minusculas(self):
        """Prueba que acepta minúsculas"""
        resultado = descifrar_vigenere("rijvs", "key")
        assert resultado == "HELLO"

    def test_cifrar_y_descifrar_ida_y_vuelta(self):
        """Prueba que cifrar y descifrar devuelve el original"""
        original = "HELLO WORLD"
        clave = "SECRET"

        cifrado = cifrar_vigenere(original, clave)
        descifrado = descifrar_vigenere(cifrado, clave)

        # El original limpio debe coincidir
        assert descifrado == "HELLOWORLD"

    def test_descifrar_texto_vacio_raise_error(self):
        """Prueba que falla con texto vacío"""
        with pytest.raises(ValueError, match="no contiene caracteres válidos"):
            descifrar_vigenere("", "KEY")


class TestValidarYFormatearClave:
    """Tests para validar_y_formatear_clave"""

    def test_clave_simple(self):
        """Prueba clave simple"""
        resultado = validar_y_formatear_clave("abc")
        assert resultado == "ABC"

    def test_clave_con_espacios(self):
        """Prueba que elimina espacios"""
        resultado = validar_y_formatear_clave("mi clave")
        assert resultado == "MICLAVE"

    def test_clave_con_numeros(self):
        """Prueba que elimina números"""
        resultado = validar_y_formatear_clave("clave123")
        assert resultado == "CLAVE"

    def test_clave_con_simbolos(self):
        """Prueba que elimina símbolos"""
        resultado = validar_y_formatear_clave("mi-clave!")
        assert resultado == "MICLAVE"

    def test_clave_vacia_raise_error(self):
        """Prueba que falla con clave vacía"""
        with pytest.raises(ValueError, match="clave no puede estar vacía"):
            validar_y_formatear_clave("")

    def test_clave_solo_numeros_raise_error(self):
        """Prueba que falla con solo números"""
        with pytest.raises(ValueError, match="debe contener al menos una letra"):
            validar_y_formatear_clave("12345")


class TestFormatearTexto:
    """Tests para formatear_texto"""

    def test_texto_simple(self):
        """Prueba formateo simple"""
        resultado = formatear_texto("hello")
        assert resultado == "HELLO"

    def test_texto_con_espacios(self):
        """Prueba que elimina espacios"""
        resultado = formatear_texto("hello world")
        assert resultado == "HELLOWORLD"

    def test_texto_con_numeros(self):
        """Prueba que elimina números"""
        resultado = formatear_texto("hello123world")
        assert resultado == "HELLOWORLD"

    def test_texto_con_simbolos(self):
        """Prueba que elimina símbolos"""
        resultado = formatear_texto("hello, world!")
        assert resultado == "HELLOWORLD"

    def test_texto_vacio(self):
        """Prueba con texto vacío"""
        resultado = formatear_texto("")
        assert resultado == ""

    def test_texto_solo_numeros(self):
        """Prueba con solo números"""
        resultado = formatear_texto("12345")
        assert resultado == ""


class TestAjustarClave:
    """Tests para ajustar_clave"""

    def test_ajustar_clave_simple(self):
        """Prueba ajuste simple"""
        resultado = ajustar_clave("KEY", 10)
        assert resultado == "KEYKEYKEYK"

    def test_ajustar_clave_exacta(self):
        """Prueba cuando la longitud es múltiplo de la clave"""
        resultado = ajustar_clave("KEY", 6)
        assert resultado == "KEYKEY"

    def test_ajustar_clave_menor(self):
        """Prueba cuando la longitud es menor que la clave"""
        resultado = ajustar_clave("KEYLARGE", 3)
        assert resultado == "KEY"

    def test_ajustar_clave_longitud_cero(self):
        """Prueba con longitud cero"""
        resultado = ajustar_clave("KEY", 0)
        assert resultado == ""

    def test_ajustar_clave_vacia_raise_error(self):
        """Prueba que falla con clave vacía"""
        with pytest.raises(ValueError, match="clave no puede estar vacía"):
            ajustar_clave("", 10)


class TestCasosReales:
    """Tests con casos de uso reales"""

    def test_caso_ejemplo_documentacion(self):
        """Prueba el ejemplo de la documentación"""
        texto = "Hola Mundo"
        clave = "clave"

        cifrado = cifrar_vigenere(texto, clave)
        descifrado = descifrar_vigenere(cifrado, clave)

        assert descifrado == "HOLAMUNDO"

    def test_texto_largo(self):
        """Prueba con texto largo"""
        texto = "Este es un texto muy largo para probar el cifrado Vigenere con muchas palabras"
        clave = "secreto"

        cifrado = cifrar_vigenere(texto, clave)
        descifrado = descifrar_vigenere(cifrado, clave)

        # Comparar sin espacios
        texto_limpio = ''.join(c.upper() for c in texto if c.isalpha())
        assert descifrado == texto_limpio

    def test_clave_mas_larga_que_texto(self):
        """Prueba con clave más larga que el texto"""
        texto = "HOLA"
        clave = "CLAVEMUYLARGUISIMA"

        cifrado = cifrar_vigenere(texto, clave)
        descifrado = descifrar_vigenere(cifrado, clave)

        assert descifrado == "HOLA"

    def test_caracteres_especiales_espaniol(self):
        """Prueba con caracteres especiales del español"""
        texto = "Niño español con ñ y acentos"
        clave = "clave"

        cifrado = cifrar_vigenere(texto, clave)
        # Los caracteres especiales se eliminan, solo quedan las letras ASCII
        assert len(cifrado) > 0


class TestArchivosGrandes:
    """Tests para archivos grandes (1MB, 5MB, 10MB)"""

    def test_archivo_1mb(self):
        """Prueba cifrado/descifrado de ~1MB de texto"""
        # Generar aproximadamente 1MB de texto (1MB ≈ 1,000,000 caracteres)
        bloque = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 40  # 1040 caracteres
        texto = bloque * 1000  # ~1MB
        clave = "CLAVEPRUEBA"

        # Cifrar
        cifrado = cifrar_vigenere(texto, clave)
        
        # Verificar que el cifrado tiene la misma longitud
        assert len(cifrado) == len(texto)
        
        # Descifrar
        descifrado = descifrar_vigenere(cifrado, clave)
        
        # Verificar que recuperamos el original
        assert descifrado == texto
        
    def test_archivo_5mb(self):
        """Prueba cifrado/descifrado de ~5MB de texto"""
        # Generar aproximadamente 5MB de texto
        bloque = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG" * 30  # 1050 caracteres
        texto = bloque * 5000  # ~5MB
        clave = "LARGEKEY"

        # Cifrar
        cifrado = cifrar_vigenere(texto, clave)
        
        # Verificar longitud
        assert len(cifrado) == len(texto)
        assert len(cifrado) > 5_000_000
        
        # Descifrar
        descifrado = descifrar_vigenere(cifrado, clave)
        
        # Verificar correctitud
        assert descifrado == texto

    def test_archivo_10mb(self):
        """Prueba cifrado/descifrado de ~10MB de texto"""
        # Generar aproximadamente 10MB de texto
        bloque = "LOREMIPSUMDOLORSITAMETCONSECTETUR" * 30  # 1020 caracteres
        texto = bloque * 10000  # ~10MB

        clave = "BIGFILE"

        # Cifrar
        cifrado = cifrar_vigenere(texto, clave)
        
        # Verificar longitud
        assert len(cifrado) == len(texto)
        assert len(cifrado) > 9_000_000  # Más de 9MB
        
        # Descifrar
        descifrado = descifrar_vigenere(cifrado, clave)
        
        # Verificar correctitud
        assert descifrado == texto

    def test_archivo_grande_con_texto_variado(self):
        """Prueba con archivo grande con contenido variado"""
        # Simular contenido más realista (párrafos repetidos)
        parrafo = (
            "En un lugar de la Mancha de cuyo nombre no quiero acordarme "
            "no ha mucho tiempo que vivia un hidalgo de los de lanza en astillero "
            "adarga antigua rocin flaco y galgo corredor "
        )
        texto = parrafo * 10000  # ~2.5MB
        clave = "CERVANTES"

        # Cifrar
        cifrado = cifrar_vigenere(texto, clave)
        
        # Verificar que el cifrado es diferente al original
        texto_formateado = formatear_texto(texto)
        assert cifrado != texto_formateado
        assert len(cifrado) == len(texto_formateado)
        
        # Descifrar
        descifrado = descifrar_vigenere(cifrado, clave)
        
        # Verificar que recuperamos el texto formateado
        assert descifrado == texto_formateado

    def test_rendimiento_archivo_grande(self):
        """Prueba que archivos grandes se procesan en tiempo razonable"""
        import time
        
        # Generar 5MB de texto
        bloque = "PERFORMANCETEST" * 70  # 1050 caracteres
        texto = bloque * 5000  # ~5MB
        clave = "SPEED"

        # Medir tiempo de cifrado
        inicio_cifrado = time.time()
        cifrado = cifrar_vigenere(texto, clave)
        tiempo_cifrado = time.time() - inicio_cifrado

        # Medir tiempo de descifrado
        inicio_descifrado = time.time()
        descifrado = descifrar_vigenere(cifrado, clave)
        tiempo_descifrado = time.time() - inicio_descifrado

        # Verificar correctitud
        assert descifrado == texto
        
        # Verificar que se procesa en menos de 5 segundos cada operación
        assert tiempo_cifrado < 5.0, f"Cifrado tardó {tiempo_cifrado:.2f}s (demasiado lento)"
        assert tiempo_descifrado < 5.0, f"Descifrado tardó {tiempo_descifrado:.2f}s (demasiado lento)"

    def test_archivo_grande_clave_corta(self):
        """Prueba archivo grande con clave muy corta"""
        # Texto de 1MB
        texto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 40000  # ~1MB
        clave = "A"  # Clave de un solo carácter

        cifrado = cifrar_vigenere(texto, clave)
        descifrado = descifrar_vigenere(cifrado, clave)

        assert descifrado == texto

    def test_archivo_grande_clave_larga(self):
        """Prueba archivo grande con clave muy larga"""
        # Texto de 1MB
        texto = "TESTTEXT" * 125000  # ~1MB
        clave = "ESTAESUNACLAVEMUYLARGUISIMAQUETIENEMUCHASLETRAS" * 10  # Clave muy larga

        cifrado = cifrar_vigenere(texto, clave)
        descifrado = descifrar_vigenere(cifrado, clave)

        assert descifrado == texto
