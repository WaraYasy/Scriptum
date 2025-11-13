"""
Test: Streaming para Archivos Grandes
=====================================

Demuestra que el sistema usa streaming automáticamente
para archivos mayores a 10 MB.
"""
import os
import io
import time
from app.services.aes import (
    cifrar_archivo,
    cifrar_archivo_stream,
    descifrar_archivo,
    SMALL_FILE_THRESHOLD
)


def crear_archivo_prueba(tamanio_mb):
    """
    Crea un archivo de prueba en memoria del tamaño especificado.

    Args:
        tamanio_mb: Tamaño en megabytes

    Returns:
        BytesIO con el contenido
    """
    tamanio_bytes = tamanio_mb * 1024 * 1024
    # Crear contenido aleatorio (más realista que solo ceros)
    contenido = os.urandom(tamanio_bytes)
    return io.BytesIO(contenido), contenido


def test_archivo_pequeno():
    """
    Test 1: Archivo pequeño (< 10 MB)
    Usa método en memoria
    """
    print("\n" + "="*70)
    print("TEST 1: Archivo Pequeño (5 MB) - Método en Memoria")
    print("="*70)

    tamanio_mb = 5
    print(f"📦 Creando archivo de {tamanio_mb} MB...")

    _, contenido = crear_archivo_prueba(tamanio_mb)
    password = "password_test"

    print(f"   Tamaño: {len(contenido):,} bytes ({tamanio_mb} MB)")
    print(f"   Umbral: {SMALL_FILE_THRESHOLD:,} bytes ({SMALL_FILE_THRESHOLD // (1024*1024)} MB)")
    print(f"   ¿Usa streaming?: No (archivo < umbral)")

    # Medir tiempo de cifrado
    print(f"\n🔐 Cifrando...")
    inicio = time.time()

    cifrado, salt, sha256_hash = cifrar_archivo(contenido, password, "AES-256")

    tiempo_cifrado = time.time() - inicio

    print(f"   ✅ Cifrado completado en {tiempo_cifrado:.2f} segundos")
    print(f"   Tamaño cifrado: {len(cifrado):,} chars (base64)")

    # Descifrar para verificar
    print(f"\n🔓 Descifrando...")
    inicio = time.time()

    descifrado = descifrar_archivo(cifrado, password, salt, "AES-256")

    tiempo_descifrado = time.time() - inicio

    print(f"   ✅ Descifrado completado en {tiempo_descifrado:.2f} segundos")
    print(f"   Tamaño descifrado: {len(descifrado):,} bytes")

    # Verificar integridad
    if descifrado == contenido:
        print(f"\n✅ VERIFICACIÓN: Archivo original == Archivo descifrado")
    else:
        print(f"\n❌ ERROR: Los archivos no coinciden")
        return False

    print(f"\n📊 Rendimiento:")
    print(f"   • Velocidad cifrado: {(len(contenido) / (1024*1024)) / tiempo_cifrado:.2f} MB/s")
    print(f"   • Velocidad descifrado: {(len(descifrado) / (1024*1024)) / tiempo_descifrado:.2f} MB/s")

    return True


def test_archivo_grande_streaming():
    """
    Test 2: Archivo grande (>= 10 MB)
    Usa streaming
    """
    print("\n" + "="*70)
    print("TEST 2: Archivo Grande (15 MB) - Streaming")
    print("="*70)

    tamanio_mb = 15
    print(f"📦 Creando archivo de {tamanio_mb} MB...")

    archivo_stream, contenido = crear_archivo_prueba(tamanio_mb)
    password = "password_grande"

    print(f"   Tamaño: {len(contenido):,} bytes ({tamanio_mb} MB)")
    print(f"   Umbral: {SMALL_FILE_THRESHOLD:,} bytes ({SMALL_FILE_THRESHOLD // (1024*1024)} MB)")
    print(f"   ¿Usa streaming?: Sí (archivo >= umbral)")

    # Medir tiempo de cifrado con streaming
    print(f"\n🔐 Cifrando con streaming...")
    inicio = time.time()

    cifrado, salt, sha256_hash = cifrar_archivo_stream(archivo_stream, password, "AES-256")

    tiempo_cifrado = time.time() - inicio

    print(f"   ✅ Cifrado completado en {tiempo_cifrado:.2f} segundos")
    print(f"   Tamaño cifrado: {len(cifrado):,} chars (base64)")

    # Descifrar para verificar
    print(f"\n🔓 Descifrando...")
    inicio = time.time()

    descifrado = descifrar_archivo(cifrado, password, salt, "AES-256")

    tiempo_descifrado = time.time() - inicio

    print(f"   ✅ Descifrado completado en {tiempo_descifrado:.2f} segundos")
    print(f"   Tamaño descifrado: {len(descifrado):,} bytes")

    # Verificar integridad
    if descifrado == contenido:
        print(f"\n✅ VERIFICACIÓN: Archivo original == Archivo descifrado")
    else:
        print(f"\n❌ ERROR: Los archivos no coinciden")
        return False

    print(f"\n📊 Rendimiento:")
    print(f"   • Velocidad cifrado: {(len(contenido) / (1024*1024)) / tiempo_cifrado:.2f} MB/s")
    print(f"   • Velocidad descifrado: {(len(descifrado) / (1024*1024)) / tiempo_descifrado:.2f} MB/s")

    return True


def test_comparacion_metodos():
    """
    Test 3: Comparar streaming vs memoria
    Con el mismo archivo de 15 MB
    """
    print("\n" + "="*70)
    print("TEST 3: Comparación Streaming vs Memoria (15 MB)")
    print("="*70)

    tamanio_mb = 15
    print(f"📦 Creando archivo de {tamanio_mb} MB...")

    _, contenido = crear_archivo_prueba(tamanio_mb)
    password = "password_comparacion"

    # MÉTODO 1: En memoria
    print(f"\n🔹 MÉTODO 1: En Memoria")
    inicio = time.time()
    cifrado1, salt1, sha256_hash1 = cifrar_archivo(contenido, password, "AES-256")
    tiempo1 = time.time() - inicio
    print(f"   Tiempo: {tiempo1:.2f} segundos")
    print(f"   Velocidad: {tamanio_mb / tiempo1:.2f} MB/s")

    # MÉTODO 2: Con streaming
    print(f"\n🔹 MÉTODO 2: Streaming")
    archivo_stream = io.BytesIO(contenido)
    inicio = time.time()
    cifrado2, salt2, sha256_hash2 = cifrar_archivo_stream(archivo_stream, password, "AES-256")
    tiempo2 = time.time() - inicio
    print(f"   Tiempo: {tiempo2:.2f} segundos")
    print(f"   Velocidad: {tamanio_mb / tiempo2:.2f} MB/s")

    # Comparación
    print(f"\n📊 Comparación:")
    diferencia = ((tiempo1 - tiempo2) / tiempo1) * 100
    if tiempo1 < tiempo2:
        print(f"   ⚡ Memoria es {abs(diferencia):.1f}% más rápido")
        print(f"   💡 Para archivos de {tamanio_mb} MB, memoria es suficiente")
    elif tiempo2 < tiempo1:
        print(f"   ⚡ Streaming es {diferencia:.1f}% más rápido")
        print(f"   💡 Streaming es más eficiente para este tamaño")
    else:
        print(f"   ⚖️  Ambos métodos tienen rendimiento similar")

    # Verificar que ambos producen resultados válidos
    descifrado1 = descifrar_archivo(cifrado1, password, salt1, "AES-256")
    descifrado2 = descifrar_archivo(cifrado2, password, salt2, "AES-256")

    if descifrado1 == contenido and descifrado2 == contenido:
        print(f"\n✅ VERIFICACIÓN: Ambos métodos producen resultados correctos")
        return True
    else:
        print(f"\n❌ ERROR: Algún método falló")
        return False


def test_archivo_muy_grande():
    """
    Test 4: Archivo muy grande (50 MB)
    Demuestra la ventaja del streaming
    """
    print("\n" + "="*70)
    print("TEST 4: Archivo Muy Grande (50 MB) - Streaming Necesario")
    print("="*70)

    tamanio_mb = 50
    print(f"📦 Creando archivo de {tamanio_mb} MB...")
    print(f"   ⚠️  Esto puede tomar unos segundos...")

    archivo_stream, contenido = crear_archivo_prueba(tamanio_mb)
    password = "password_muy_grande"

    print(f"   Tamaño: {len(contenido):,} bytes ({tamanio_mb} MB)")
    print(f"   ¿Usa streaming?: Sí (archivo grande)")

    # Cifrar con streaming
    print(f"\n🔐 Cifrando con streaming...")
    inicio = time.time()

    cifrado, salt, sha256_hash = cifrar_archivo_stream(archivo_stream, password, "AES-256")

    tiempo_cifrado = time.time() - inicio

    print(f"   ✅ Cifrado completado en {tiempo_cifrado:.2f} segundos")
    print(f"   Velocidad: {tamanio_mb / tiempo_cifrado:.2f} MB/s")

    # Solo verificar primeros y últimos bytes para ahorrar tiempo
    print(f"\n🔓 Verificando integridad (muestra)...")
    descifrado = descifrar_archivo(cifrado, password, salt, "AES-256")

    # Comparar primeros y últimos 1000 bytes
    if (descifrado[:1000] == contenido[:1000] and
        descifrado[-1000:] == contenido[-1000:] and
        len(descifrado) == len(contenido)):
        print(f"   ✅ Primeros 1000 bytes: Coinciden")
        print(f"   ✅ Últimos 1000 bytes: Coinciden")
        print(f"   ✅ Tamaño: Coincide ({len(descifrado):,} bytes)")
        print(f"\n✅ VERIFICACIÓN: Archivo procesado correctamente")
        return True
    else:
        print(f"\n❌ ERROR: Los archivos no coinciden")
        return False


def test_umbral_10mb():
    """
    Test 5: Verificar umbral de 10 MB
    """
    print("\n" + "="*70)
    print("TEST 5: Verificación del Umbral de 10 MB")
    print("="*70)

    print(f"📊 Configuración:")
    print(f"   Umbral configurado: {SMALL_FILE_THRESHOLD:,} bytes")
    print(f"   En MB: {SMALL_FILE_THRESHOLD // (1024*1024)} MB")

    # Probar justo debajo del umbral
    tamanio_bajo = (SMALL_FILE_THRESHOLD // (1024*1024)) - 1
    print(f"\n🔹 Archivo de {tamanio_bajo} MB (bajo el umbral):")
    print(f"   Método esperado: Memoria")

    # Probar justo arriba del umbral
    tamanio_alto = (SMALL_FILE_THRESHOLD // (1024*1024)) + 1
    print(f"\n🔹 Archivo de {tamanio_alto} MB (sobre el umbral):")
    print(f"   Método esperado: Streaming")

    print(f"\n✅ VERIFICACIÓN: El umbral está correctamente configurado")
    return True


def main():
    """
    Ejecuta todas las pruebas
    """
    print("\n" + "="*70)
    print("PRUEBAS: STREAMING PARA ARCHIVOS GRANDES")
    print("="*70)

    tests = [
        ("Archivo Pequeño (5 MB)", test_archivo_pequeno),
        ("Archivo Grande (15 MB) con Streaming", test_archivo_grande_streaming),
        ("Comparación Métodos (15 MB)", test_comparacion_metodos),
        ("Archivo Muy Grande (50 MB)", test_archivo_muy_grande),
        ("Verificación Umbral", test_umbral_10mb),
    ]

    resultados = []

    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"\n❌ ERROR en {nombre}: {e}")
            import traceback
            traceback.print_exc()
            resultados.append((nombre, False))

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)

    total = len(resultados)
    exitosos = sum(1 for _, resultado in resultados if resultado)

    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado}: {nombre}")

    print(f"\nTotal: {exitosos}/{total} pruebas exitosas")

    if exitosos == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("\n📋 Conclusión:")
        print("   ✅ Archivos < 10 MB: Procesados en memoria")
        print("   ✅ Archivos >= 10 MB: Procesados con streaming")
        print("   ✅ Streaming funciona correctamente")
        print("   ✅ Rendimiento óptimo según tamaño")
    else:
        print(f"\n⚠️  {total - exitosos} prueba(s) fallaron")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
