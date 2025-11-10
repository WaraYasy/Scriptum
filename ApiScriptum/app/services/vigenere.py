"""
SERVICIOS VIGENÈRE
SCRIPTUM - Servicio de cifrado Vigenère
Autoras: Arantxa - Wara

Este módulo proporciona funcionalidades para cifrar y descifrar texto
utilizando el algoritmo de cifrado Vigenère.

Arquitectura del módulo:
- Capa 1: Funciones puras de cifrado/descifrado (sin efectos secundarios)
- Capa 2: Validaciones y sanitización de entradas
- Capa 3: Utilidades para manejo de archivos (opcional)
"""
import os
import re


# ============================================================================
# CAPA 1: FUNCIONES PURAS DE CIFRADO/DESCIFRADO
# ============================================================================

def cifrar_vigenere(texto: str, clave: str) -> str:
    """Cifra un texto utilizando el algoritmo de Vigenère.

    Args:
        texto (str): Texto a cifrar (será limpiado automáticamente).
        clave (str): Clave para el cifrado (solo letras).

    Returns:
        str: Texto cifrado en mayúsculas sin espacios.

    Raises:
        ValueError: Si el texto está vacío o la clave no es válida.

    Example:
        >>> cifrar_vigenere("HELLO WORLD", "KEY")
        'RIJVSUYVJN'
    """
    # Validar y formatear entradas
    texto_limpio = formatear_texto(texto)
    clave_limpia = validar_y_formatear_clave(clave)

    if not texto_limpio:
        raise ValueError("El texto no contiene caracteres válidos para cifrar.")

    # Ajustar la clave al tamaño del texto
    clave_ajustada = ajustar_clave(clave_limpia, len(texto_limpio))

    # Cifrado Vigenère
    texto_cifrado = ""
    for i, letra in enumerate(texto_limpio):
        # Fórmula: C = (P + K) mod 26
        posicion = (ord(letra) - ord('A') + ord(clave_ajustada[i]) - ord('A')) % 26
        letra_cifrada = chr(posicion + ord('A'))
        texto_cifrado += letra_cifrada

    return texto_cifrado


def descifrar_vigenere(texto_cifrado: str, clave: str) -> str:
    """Descifra un texto utilizando el algoritmo de Vigenère.

    FUNCIÓN PURA: No realiza I/O, solo transformaciones.

    Args:
        texto_cifrado (str): Texto cifrado a descifrar (solo mayúsculas sin espacios).
        clave (str): Clave para el descifrado (solo letras).

    Returns:
        str: Texto original descifrado en mayúsculas.

    Raises:
        ValueError: Si el texto está vacío o la clave no es válida.

    Example:
        >>> descifrar_vigenere("RIJVSUYVJN", "KEY")
        'HELLOWORLD'
    """
    # Validar y formatear clave
    clave_limpia = validar_y_formatear_clave(clave)

    # Formatear texto cifrado (por si acaso viene con espacios)
    texto_limpio = formatear_texto(texto_cifrado)

    if not texto_limpio:
        raise ValueError("El texto cifrado no contiene caracteres válidos.")

    # Ajustar la clave al tamaño del texto
    clave_ajustada = ajustar_clave(clave_limpia, len(texto_limpio))

    # Descifrado Vigenère
    texto_original = ""
    for i, letra in enumerate(texto_limpio):
        # Fórmula: P = (C - K + 26) mod 26
        num_letra = ord(letra) - ord('A')
        num_clave = ord(clave_ajustada[i]) - ord('A')
        posicion = (num_letra - num_clave + 26) % 26
        letra_original = chr(posicion + ord('A'))
        texto_original += letra_original

    return texto_original


# ============================================================================
# CAPA 2: VALIDACIONES Y FORMATEO
# ============================================================================

def validar_y_formatear_clave(clave: str) -> str:
    """Valida y formatea la clave para el cifrado Vigenère.

    La clave debe contener solo letras (A-Z, a-z). Se convierte a mayúsculas
    y se eliminan caracteres no alfabéticos.

    Args:
        clave (str): Clave a validar y formatear.

    Returns:
        str: Clave formateada (solo mayúsculas, sin espacios).

    Raises:
        ValueError: Si la clave está vacía o no contiene letras válidas.

    Example:
        >>> validar_y_formatear_clave("Mi Clave 123")
        'MICLAVE'
    """
    if not clave:
        raise ValueError("La clave no puede estar vacía.")

    # Limpiar la clave: solo letras, convertir a mayúsculas
    clave_limpia = ''.join(c.upper() for c in clave if c.isalpha())

    if not clave_limpia:
        raise ValueError("La clave debe contener al menos una letra (A-Z).")

    return clave_limpia


def formatear_texto(texto: str) -> str:
    """Formatea el texto eliminando caracteres no alfabéticos y convirtiendo a mayúsculas.

    Prepara el texto para el proceso de cifrado eliminando todos los
    caracteres que no sean letras (A-Z) y convirtiendo a mayúsculas.

    Args:
        texto (str): Texto a formatear.

    Returns:
        str: Texto formateado (solo mayúsculas A-Z, sin espacios ni símbolos).

    Example:
        >>> formatear_texto("Hello, World! 123")
        'HELLOWORLD'
    """
    if not texto:
        return ""

    # Método optimizado: usar lista y join es más eficiente que concatenación
    caracteres_validos = [c.upper() for c in texto if c.isalpha()]
    return "".join(caracteres_validos)


def ajustar_clave(clave: str, longitud: int) -> str:
    """Ajusta la clave repitiendo sus caracteres para alcanzar la longitud deseada.

    Repite la clave de forma cíclica hasta que coincida con la longitud
    del texto a procesar.

    Args:
        clave (str): La clave a repetir (ya debe estar formateada).
        longitud (int): Longitud objetivo para la clave.

    Returns:
        str: Clave repetida cíclicamente con la longitud especificada.

    Raises:
        ValueError: Si la clave está vacía.

    Example:
        >>> ajustar_clave("KEY", 10)
        'KEYKEYKEYK'
    """
    if not clave:
        raise ValueError("La clave no puede estar vacía.")

    if longitud <= 0:
        return ""

    # Método optimizado: repetir la clave completa y cortar
    repeticiones = (longitud // len(clave)) + 1
    clave_extendida = clave * repeticiones
    return clave_extendida[:longitud]


# ============================================================================
# CAPA 3: UTILIDADES PARA ARCHIVOS
# ============================================================================

# NOTA: Las funciones cifrar_vigenere_file y descifrar_vigenere_file han sido
# eliminadas para reducir duplicación. Ahora se manejan directamente en el router
# usando las funciones puras cifrar_vigenere() y descifrar_vigenere().
#
# Esto simplifica el código y evita tener lógica de archivos en los servicios,
# que deben ser funciones puras sin efectos secundarios.


def grabar_fichero(nombre_fichero: str, contenido: str) -> str:
    """Guarda contenido en un archivo de texto en la carpeta data/.

    Crea o sobrescribe un archivo en el directorio 'data/' del proyecto.
    Incluye protección contra path traversal.

    Args:
        nombre_fichero (str): Nombre del archivo (solo nombre, sin path).
        contenido (str): Contenido a escribir en el archivo.

    Returns:
        str: Ruta completa del archivo guardado.

    Raises:
        ValueError: Si el nombre del archivo contiene caracteres peligrosos.

    Security:
        - Protege contra path traversal (../, ..\\, etc.)
        - Solo permite nombres de archivo seguros

    """
    # SEGURIDAD: Validar nombre de archivo para prevenir path traversal
    nombre_seguro = sanitizar_nombre_archivo(nombre_fichero)

    # Obtener directorio del proyecto
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_proyecto = os.path.dirname(directorio_actual)

    # Construir ruta al directorio data
    directorio_data = os.path.join(directorio_proyecto, 'data')
    ruta_archivo = os.path.join(directorio_data, nombre_seguro)

    # Verificación adicional: asegurar que la ruta está dentro de data/
    ruta_absoluta = os.path.abspath(ruta_archivo)
    directorio_data_absoluto = os.path.abspath(directorio_data)

    if not ruta_absoluta.startswith(directorio_data_absoluto):
        raise ValueError("Intento de path traversal detectado.")

    # Crear el directorio data si no existe
    os.makedirs(directorio_data, exist_ok=True)

    # Escribir el contenido en el archivo
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)

    return ruta_archivo


def sanitizar_nombre_archivo(nombre: str) -> str:
    """Sanitiza el nombre de archivo para prevenir ataques de path traversal.

    Elimina caracteres peligrosos y secuencias de path traversal.

    Args:
        nombre (str): Nombre del archivo a sanitizar.

    Returns:
        str: Nombre de archivo seguro.

    Raises:
        ValueError: Si el nombre es inválido o contiene patrones peligrosos.

    Security:
        - Bloquea ../ y ..\\ (path traversal)
        - Solo permite caracteres alfanuméricos, guiones, puntos y guiones bajos
    """
    if not nombre:
        raise ValueError("El nombre del archivo no puede estar vacío.")

    # Detectar path traversal
    if '..' in nombre or '/' in nombre or '\\' in nombre:
        raise ValueError("El nombre del archivo contiene caracteres no permitidos (../, /, \\).")

    # Solo permitir caracteres seguros: letras, números, puntos, guiones, guiones bajos
    patron_seguro = re.compile(r'^[a-zA-Z0-9._-]+$')

    if not patron_seguro.match(nombre):
        raise ValueError(
            "El nombre del archivo solo puede contener letras, números, "
            "puntos, guiones y guiones bajos."
        )

    return nombre