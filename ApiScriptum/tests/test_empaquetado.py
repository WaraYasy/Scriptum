"""
Tests para empaquetado de archivos cifrados con metadatos
"""
import base64
import pytest
from app.services.aes import (
    crear_paquete_archivo_cifrado,
    extraer_paquete_archivo_cifrado,
    cifrar_archivo,
    descifrar_archivo
)


def test_crear_y_extraer_paquete_basico():
    """Test básico: crear paquete y extraerlo"""
    # Datos de prueba
    contenido_original = b"Hola mundo, este es un archivo de prueba"
    password = "password123"
    tipo_aes = "AES-256"

    # Cifrar archivo
    contenido_cifrado, salt = cifrar_archivo(
        contenido_original,
        password,
        tipo_aes
    )

    # Crear paquete
    paquete = crear_paquete_archivo_cifrado(
        contenido_cifrado=contenido_cifrado,
        salt=salt,
        tipo_aes=tipo_aes,
        nombre_archivo="prueba.txt",
        mime_type="text/plain"
    )

    # Verificar que el paquete es un string base64
    assert isinstance(paquete, str)
    assert len(paquete) > 0

    # Extraer paquete
    datos = extraer_paquete_archivo_cifrado(paquete)

    # Verificar que se extraen todos los campos
    assert "contenido_cifrado" in datos
    assert "salt" in datos
    assert "tipo_aes" in datos
    assert "metadata" in datos

    # Verificar metadatos
    assert datos["metadata"]["nombre_original"] == "prueba.txt"
    assert datos["metadata"]["mime_type"] == "text/plain"
    assert datos["tipo_aes"] == "AES-256"
    assert datos["salt"] == salt

    print(f"✅ Test básico OK - Paquete: {len(paquete)} chars")


def test_paquete_ciclo_completo():
    """Test completo: cifrar → empaquetar → extraer → descifrar"""
    # Datos originales
    contenido_original = b"Este es un archivo secreto que sera cifrado y descifrado"
    password = "mi_password_seguro_123"
    tipo_aes = "AES-256"
    nombre = "documento_secreto.pdf"
    mime = "application/pdf"

    # 1. CIFRAR
    contenido_cifrado, salt = cifrar_archivo(
        contenido_original,
        password,
        tipo_aes
    )

    # 2. EMPAQUETAR
    paquete = crear_paquete_archivo_cifrado(
        contenido_cifrado=contenido_cifrado,
        salt=salt,
        tipo_aes=tipo_aes,
        nombre_archivo=nombre,
        mime_type=mime
    )

    print(f"📦 Paquete creado: {len(paquete)} caracteres")

    # 3. EXTRAER
    datos = extraer_paquete_archivo_cifrado(paquete)

    # 4. DESCIFRAR
    contenido_descifrado = descifrar_archivo(
        datos["contenido_cifrado"],
        password,
        datos["salt"],
        datos["tipo_aes"]
    )

    # 5. VERIFICAR
    assert contenido_descifrado == contenido_original
    assert datos["metadata"]["nombre_original"] == nombre
    assert datos["metadata"]["mime_type"] == mime

    print(f"✅ Ciclo completo OK - Contenido recuperado correctamente")


def test_paquete_con_diferentes_tipos_aes():
    """Test con AES-128, AES-192 y AES-256"""
    contenido = b"Contenido de prueba"
    password = "password123"
    nombre = "test.bin"
    mime = "application/octet-stream"

    for tipo_aes in ["AES-128", "AES-192", "AES-256"]:
        # Cifrar
        contenido_cifrado, salt = cifrar_archivo(contenido, password, tipo_aes)

        # Empaquetar
        paquete = crear_paquete_archivo_cifrado(
            contenido_cifrado, salt, tipo_aes, nombre, mime
        )

        # Extraer
        datos = extraer_paquete_archivo_cifrado(paquete)

        # Verificar tipo AES
        assert datos["tipo_aes"] == tipo_aes

        # Descifrar
        descifrado = descifrar_archivo(
            datos["contenido_cifrado"],
            password,
            datos["salt"],
            datos["tipo_aes"]
        )

        assert descifrado == contenido
        print(f"✅ {tipo_aes} OK")


def test_paquete_con_nombres_especiales():
    """Test con nombres de archivo con caracteres especiales"""
    contenido = b"Test"
    password = "pass1234"
    tipo_aes = "AES-256"

    nombres_especiales = [
        "archivo con espacios.txt",
        "archivo_con_ñ_y_tilde_á.pdf",
        "файл.txt",  # Cirílico
        "文件.jpg",   # Chino
        "archivo-con-guiones_y_guion_bajo.docx"
    ]

    for nombre in nombres_especiales:
        contenido_cifrado, salt = cifrar_archivo(contenido, password, tipo_aes)

        paquete = crear_paquete_archivo_cifrado(
            contenido_cifrado, salt, tipo_aes, nombre, "application/octet-stream"
        )

        datos = extraer_paquete_archivo_cifrado(paquete)

        assert datos["metadata"]["nombre_original"] == nombre
        print(f"✅ Nombre especial OK: {nombre}")


def test_paquete_con_imagen():
    """Test simulando una imagen JPG"""
    # Simular bytes de una imagen (datos binarios)
    imagen_bytes = bytes([0xFF, 0xD8, 0xFF, 0xE0]) + b"fake jpeg data" * 100
    password = "foto_password_123"
    tipo_aes = "AES-256"

    # Cifrar
    cifrado, salt = cifrar_archivo(imagen_bytes, password, tipo_aes)

    # Empaquetar
    paquete = crear_paquete_archivo_cifrado(
        contenido_cifrado=cifrado,
        salt=salt,
        tipo_aes=tipo_aes,
        nombre_archivo="foto_vacaciones.jpg",
        mime_type="image/jpeg"
    )

    # Extraer
    datos = extraer_paquete_archivo_cifrado(paquete)

    # Descifrar
    descifrado = descifrar_archivo(
        datos["contenido_cifrado"],
        password,
        datos["salt"],
        datos["tipo_aes"]
    )

    # Verificar
    assert descifrado == imagen_bytes
    assert datos["metadata"]["mime_type"] == "image/jpeg"
    assert datos["metadata"]["nombre_original"] == "foto_vacaciones.jpg"

    print(f"✅ Imagen OK - {len(imagen_bytes)} bytes recuperados")


def test_paquete_formato_binario():
    """Test para verificar el formato binario del paquete"""
    contenido = b"Test"
    password = "pass1234"
    tipo_aes = "AES-256"

    cifrado, salt = cifrar_archivo(contenido, password, tipo_aes)

    paquete = crear_paquete_archivo_cifrado(
        cifrado, salt, tipo_aes, "test.txt", "text/plain"
    )

    # Decodificar base64 para ver el contenido binario
    paquete_bytes = base64.b64decode(paquete)

    # Verificar magic bytes "SCRIPTUM"
    assert paquete_bytes[0:8] == b"SCRIPTUM"

    # Verificar versión = 1
    assert paquete_bytes[8] == 1

    # Verificar tipo AES (3 = AES-256)
    assert paquete_bytes[9] == 3

    # Verificar que tiene salt (16 bytes en posición 10-25)
    salt_en_paquete = paquete_bytes[10:26]
    assert len(salt_en_paquete) == 16

    print(f"✅ Formato binario correcto - Magic: {paquete_bytes[0:8]}")


def test_paquete_invalido():
    """Test para verificar manejo de paquetes inválidos"""

    # Paquete con magic bytes incorrecto
    paquete_malo = base64.b64encode(b"WRONGMAG" + b"\x00" * 100).decode()

    with pytest.raises(ValueError, match="Magic bytes inválido"):
        extraer_paquete_archivo_cifrado(paquete_malo)

    print("✅ Validación de paquete inválido OK")


def test_comparacion_tamaño_vs_json():
    """Comparar tamaño del paquete binario vs JSON equivalente"""
    import json

    contenido = b"A" * 1000  # 1 KB
    password = "pass1234"
    tipo_aes = "AES-256"

    cifrado, salt = cifrar_archivo(contenido, password, tipo_aes)

    # Paquete binario
    paquete_binario = crear_paquete_archivo_cifrado(
        cifrado, salt, tipo_aes, "archivo.bin", "application/octet-stream"
    )

    # Equivalente JSON (aproximado)
    paquete_json = {
        "v": 1,
        "aes": tipo_aes,
        "salt": salt,
        "meta": {
            "nombre": "archivo.bin",
            "mime": "application/octet-stream"
        },
        "data": cifrado
    }
    json_str = json.dumps(paquete_json, separators=(',', ':'))
    json_base64 = base64.b64encode(json_str.encode()).decode()

    # Comparar tamaños
    tamaño_binario = len(paquete_binario)
    tamaño_json = len(json_base64)
    ahorro = ((tamaño_json - tamaño_binario) / tamaño_json) * 100

    print(f"📊 Binario: {tamaño_binario} chars")
    print(f"📊 JSON: {tamaño_json} chars")
    print(f"💾 Ahorro: {ahorro:.1f}%")

    # El formato binario debe ser más compacto
    assert tamaño_binario < tamaño_json


if __name__ == "__main__":
    print("="*60)
    print("TESTS DE EMPAQUETADO DE ARCHIVOS CIFRADOS")
    print("="*60)

    test_crear_y_extraer_paquete_basico()
    test_paquete_ciclo_completo()
    test_paquete_con_diferentes_tipos_aes()
    test_paquete_con_nombres_especiales()
    test_paquete_con_imagen()
    test_paquete_formato_binario()
    test_paquete_invalido()
    test_comparacion_tamaño_vs_json()

    print("\n" + "="*60)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*60)
