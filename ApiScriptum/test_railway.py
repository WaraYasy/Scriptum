#!/usr/bin/env python3
"""
Script para probar el endpoint de Railway con el archivo grande
"""
import sys
import time
import requests
from pathlib import Path

def test_railway_descifrado(railway_url: str, archivo_path: str = "archivo_grande_10mb.txt"):
    """
    Prueba el descifrado en Railway

    Args:
        railway_url: URL de tu deployment en Railway (ej: https://tu-app.railway.app)
        archivo_path: Ruta al archivo a descifrar
    """

    # Verificar que el archivo existe
    archivo = Path(archivo_path)
    if not archivo.exists():
        print(f"❌ Error: No se encuentra el archivo {archivo_path}")
        return

    tamanio_mb = archivo.stat().st_size / (1024 * 1024)
    print(f"📁 Archivo: {archivo_path} ({tamanio_mb:.2f} MB)")

    # URL del endpoint
    url = f"{railway_url.rstrip('/')}/vigenere/descifrar/file/large"
    print(f"🌐 URL: {url}")

    # Preparar el request
    clave = "BIGFILE"
    print(f"🔑 Clave: {clave}")

    # Hacer el request con timeout largo
    print(f"\n⏳ Enviando request... (esto puede tardar)")

    inicio = time.time()

    try:
        with open(archivo_path, 'rb') as f:
            files = {'file': (archivo.name, f, 'text/plain')}
            data = {'clave': clave}

            # Timeout de 5 minutos (300 segundos)
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=300
            )

        duracion = time.time() - inicio
        print(f"\n✅ Request completado en {duracion:.2f} segundos")

        # Verificar status code
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            resultado = response.json()
            print(f"\n🎉 ¡Descifrado exitoso!")
            print(f"   - Tamaño procesado: {resultado.get('tamanio_archivo_mb')} MB")
            print(f"   - Bloques: {resultado.get('bloques_procesados')}")
            print(f"   - Canary check: {resultado.get('canary_check')}")
            print(f"   - Mensaje: {resultado.get('mensaje')}")

            # Mostrar primeros caracteres del texto descifrado
            texto = resultado.get('texto_descifrado', '')
            if texto:
                print(f"\n📝 Primeros 100 caracteres:")
                print(f"   {texto[:100]}")
        else:
            print(f"\n❌ Error en el servidor:")
            print(f"   Status: {response.status_code}")
            try:
                error = response.json()
                print(f"   Detalle: {error}")
            except:
                print(f"   Respuesta: {response.text[:500]}")

    except requests.exceptions.Timeout:
        duracion = time.time() - inicio
        print(f"\n⏱️ TIMEOUT después de {duracion:.2f} segundos")
        print(f"   El servidor Railway no respondió a tiempo.")
        print(f"   Esto puede ser debido a:")
        print(f"   1. Límite de timeout del proxy de Railway (~100s)")
        print(f"   2. Archivo muy grande para procesar en tiempo límite")
        print(f"   3. Conexión lenta al subir el archivo")

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Error de conexión: {e}")
        print(f"   Verifica que la URL de Railway sea correcta")

    except Exception as e:
        duracion = time.time() - inicio
        print(f"\n❌ Error inesperado después de {duracion:.2f} segundos:")
        print(f"   {type(e).__name__}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso: python test_railway.py <RAILWAY_URL> [archivo]")
        print()
        print("Ejemplos:")
        print("  python test_railway.py https://tu-app.railway.app")
        print("  python test_railway.py https://tu-app.railway.app archivo_grande_10mb.txt")
        sys.exit(1)

    railway_url = sys.argv[1]
    archivo = sys.argv[2] if len(sys.argv) > 2 else "archivo_grande_10mb.txt"

    print("="*60)
    print("🚂 TEST RAILWAY - Descifrado Vigenère")
    print("="*60)

    test_railway_descifrado(railway_url, archivo)
