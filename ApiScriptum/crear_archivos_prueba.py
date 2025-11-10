#!/usr/bin/env python3
"""
Script para crear archivos de prueba para las validaciones de Vigenère
"""
import sys
import os

# Añadir directorio padre al path para importar servicios
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.vigenere import cifrar_vigenere


def crear_archivo_con_magic_header():
    """Crea un archivo cifrado con Magic Header para Canary Check"""
    
    # Contenido original con Magic Header
    contenido = """MAGICv1
Este es un mensaje secreto cifrado con Vigenère.
El profesor quiere que demostremos que podemos:
1. Procesar archivos grandes con streaming
2. Hacer canary check (validar clave antes de descifrar todo)
3. Detectar caracteres invisibles en la clave

Este archivo se usa para probar el endpoint /descifrar/file/large
"""
    
    clave = "HOGWARTS"
    
    print(f"  Creando archivo de prueba...")
    print(f"   Contenido original: {len(contenido)} caracteres")
    print(f"   Clave: {clave}")
    
    # Cifrar
    texto_cifrado = cifrar_vigenere(contenido, clave)
    
    # Guardar
    nombre_archivo = "archivo_prueba_magic.txt"
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(texto_cifrado)
    
    print(f"✅ Archivo creado: {nombre_archivo}")
    print(f"   Tamaño: {len(texto_cifrado)} caracteres")
    print(f"\n🧪 Para probar:")
    print(f"   curl -X POST 'http://localhost:8000/vigenere/descifrar/file/large' \\")
    print(f"     -F 'file=@{nombre_archivo}' \\")
    print(f"     -F 'clave={clave}' \\")
    print(f"     -F 'magic_header=MAGICv1\\n'")
    print()


def crear_archivo_grande():
    """Crea un archivo grande para probar límites"""
    
    # Crear archivo de 10 MB (para pruebas rápidas)
    tamanio_mb = 10
    contenido_base = "MAGICv1\n" + "A" * 1000  # 1KB de 'A'
    
    # Repetir para llegar al tamaño deseado
    repeticiones = (tamanio_mb * 1024 * 1024) // len(contenido_base)
    contenido = contenido_base * repeticiones
    
    clave = "BIGFILE"
    
    print(f"📝 Creando archivo grande de prueba...")
    print(f"   Tamaño objetivo: {tamanio_mb} MB")
    print(f"   Clave: {clave}")
    print(f"   ⏳ Esto puede tardar un poco...")
    
    # Cifrar
    texto_cifrado = cifrar_vigenere(contenido, clave)
    
    # Guardar
    nombre_archivo = f"archivo_grande_{tamanio_mb}mb.txt"
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(texto_cifrado)
    
    tamanio_real_mb = len(texto_cifrado) / (1024 * 1024)
    print(f"✅ Archivo grande creado: {nombre_archivo}")
    print(f"   Tamaño real: {tamanio_real_mb:.2f} MB")
    print()


def crear_clave_con_invisible():
    """Crea un archivo con clave que contiene caracter invisible"""
    
    # Clave con Zero-Width Space
    clave_con_invisible = "CLAVE\u200BSECRETA"  # U+200B después de CLAVE
    
    nombre_archivo = "clave_con_invisible.txt"
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(clave_con_invisible)
    
    print(f"📝 Archivo con clave invisible creado: {nombre_archivo}")
    print(f"   Clave: '{clave_con_invisible}'")
    print(f"   Longitud: {len(clave_con_invisible)} caracteres")
    print(f"   Caracter invisible U+200B en posición 5")
    print(f"\n🧪 Para probar:")
    print(f"   curl -X POST 'http://localhost:8000/vigenere/validar-clave' \\")
    print(f"     -F 'clave@{nombre_archivo}'")
    print()


def mostrar_menu():
    """Muestra menú de opciones"""
    print("\n" + "="*60)
    print("🧙 Generador de archivos de prueba - Vigenère")
    print("="*60)
    print("\nOpciones:")
    print("  1. Crear archivo con Magic Header (para Canary Check)")
    print("  2. Crear archivo grande (10 MB)")
    print("  3. Crear clave con caracter invisible")
    print("  4. Crear todos los archivos")
    print("  0. Salir")
    print()


def main():
    """Función principal"""
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "1":
            crear_archivo_con_magic_header()
        elif opcion == "2":
            crear_archivo_grande()
        elif opcion == "3":
            crear_clave_con_invisible()
        elif opcion == "4":
            crear_archivo_con_magic_header()
            crear_archivo_grande()
            crear_clave_con_invisible()
            print("\n✅ Todos los archivos de prueba creados!")
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.")
        
        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
