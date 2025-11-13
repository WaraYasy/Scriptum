"""
SERVICIOS AES
SCRIPTUM - Servicio de cifrado AES (Advanced Encryption Standard)
Autor: Wara

Este módulo proporciona funcionalidades para cifrar y descifrar texto y archivos
utilizando el algoritmo de cifrado AES con soporte para:
- AES-128 (clave de 16 bytes)
- AES-192 (clave de 24 bytes)
- AES-256 (clave de 32 bytes)

Arquitectura del m�dulo:
- Capa 1: Funciones puras de cifrado/descifrado con AES-GCM
- Capa 2: Validaciones y generaci�n de claves
- Capa 3: Utilidades para manejo de datos
"""
import base64
import hashlib
import struct
import logging
from typing import Tuple, Literal, Dict, Any
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# TIPOS Y CONSTANTES
# ============================================================================

TipoAES = Literal["AES-128", "AES-192", "AES-256"]

# Mapeo de tipos de AES a tama�o de clave en bytes
TAMANIOS_CLAVE = {
    "AES-128": 16,  # 128 bits = 16 bytes
    "AES-192": 24,  # 192 bits = 24 bytes
    "AES-256": 32,  # 256 bits = 32 bytes
}

# Tamaño del nonce para AES-GCM (recomendado: 12 bytes)
NONCE_SIZE = 12

# Tamaños para streaming
CHUNK_SIZE = 64 * 1024  # 64 KB por chunk (óptimo para memoria y rendimiento)
SMALL_FILE_THRESHOLD = 10 * 1024 * 1024  # 10 MB - archivos menores se procesan en memoria


# ============================================================================
# CAPA 1: FUNCIONES PURAS DE CIFRADO/DESCIFRADO
# ============================================================================

def cifrar_aes(
    datos: bytes,
    clave: bytes,
    tipo_aes: TipoAES = "AES-256"
) -> Tuple[bytes, bytes, bytes]:
    """
    Cifra datos utilizando AES-GCM (Galois/Counter Mode).

    AES-GCM proporciona:
    - Confidencialidad (cifrado)
    - Autenticidad (detecta manipulaciones)
    - Integridad (verifica que no se alter�)

    Args:
        datos: Datos en bytes a cifrar.
        clave: Clave de cifrado (debe tener el tama�o correcto seg�n tipo_aes).
        tipo_aes: Tipo de AES a usar ("AES-128", "AES-192", "AES-256").

    Returns:
        Tupla (nonce, datos_cifrados, tag):
            - nonce: N�mero usado una sola vez (12 bytes)
            - datos_cifrados: Datos cifrados
            - tag: Tag de autenticaci�n (16 bytes)

    Raises:
        ValueError: Si la clave no tiene el tama�o correcto.

    Example:
        >>> clave = generar_clave_desde_password("mi_password", "AES-256")
        >>> nonce, cifrado, tag = cifrar_aes(b"Hola Mundo", clave, "AES-256")
    """
    logger.debug("Iniciando cifrado AES - Tipo: %s", tipo_aes)

    # Validar tama�o de clave
    tamanio_esperado = TAMANIOS_CLAVE[tipo_aes]
    if len(clave) != tamanio_esperado:
        logger.error("Tamaño de clave inválido - Esperado: %d bytes, Recibido: %d bytes", tamanio_esperado, len(clave))
        raise ValueError(
            f"La clave para {tipo_aes} debe tener {tamanio_esperado} bytes. "
            f"Se proporcionaron {len(clave)} bytes."
        )

    # Generar nonce aleatorio (12 bytes es el tamaño recomendado para GCM)
    nonce = get_random_bytes(NONCE_SIZE)

    # Crear cipher AES-GCM
    cipher = AES.new(clave, AES.MODE_GCM, nonce=nonce)

    # Cifrar y obtener tag de autenticaci�n
    datos_cifrados, tag = cipher.encrypt_and_digest(datos)

    logger.debug("Cifrado completado exitosamente")

    return nonce, datos_cifrados, tag


def descifrar_aes(
    datos_cifrados: bytes,
    clave: bytes,
    nonce: bytes,
    tag: bytes,
    tipo_aes: TipoAES = "AES-256"
) -> bytes:
    """
    Descifra datos cifrados con AES-GCM y verifica autenticidad.

    Args:
        datos_cifrados: Datos cifrados a descifrar.
        clave: Clave de descifrado (debe ser la misma usada para cifrar).
        nonce: Nonce usado en el cifrado (12 bytes).
        tag: Tag de autenticaci�n (16 bytes).
        tipo_aes: Tipo de AES usado ("AES-128", "AES-192", "AES-256").

    Returns:
        Datos descifrados en bytes.

    Raises:
        ValueError: Si la clave es incorrecta, los datos fueron manipulados,
                   o el tag no coincide.

    Example:
        >>> datos_originales = descifrar_aes(cifrado, clave, nonce, tag, "AES-256")
    """
    logger.debug("Iniciando descifrado AES - Tipo: %s", tipo_aes)

    # Validar tama�o de clave
    tamanio_esperado = TAMANIOS_CLAVE[tipo_aes]
    if len(clave) != tamanio_esperado:
        logger.error("Tamaño de clave inválido en descifrado - Esperado: %d bytes, Recibido: %d bytes",
                     tamanio_esperado, len(clave))
        raise ValueError(
            f"La clave para {tipo_aes} debe tener {tamanio_esperado} bytes. "
            f"Se proporcionaron {len(clave)} bytes."
        )

    # Crear cipher AES-GCM con el mismo nonce
    cipher = AES.new(clave, AES.MODE_GCM, nonce=nonce)

    # Descifrar y verificar tag de autenticaci�n
    try:
        datos_descifrados = cipher.decrypt_and_verify(datos_cifrados, tag)
        logger.debug("Descifrado completado exitosamente")
        return datos_descifrados
    except ValueError as e:
        logger.error("Error al descifrar: clave incorrecta o datos manipulados")
        raise ValueError(
            "Error al descifrar: clave incorrecta o datos manipulados. "
            "El tag de autenticaci�n no coincide."
        ) from e


# ============================================================================
# CAPA 2: GENERACION Y VALIDACION DE CLAVES
# ============================================================================

def generar_clave_desde_password(
    password: str,
    tipo_aes: TipoAES = "AES-256",
    salt: bytes | None = None
) -> Tuple[bytes, bytes]:
    """
    Genera una clave AES derivada de un password usando PBKDF2.

    PBKDF2 (Password-Based Key Derivation Function 2) convierte un password
    legible en una clave criptogr�fica fuerte mediante:
    - Hashing repetido (100,000 iteraciones)
    - Uso de salt aleatorio para prevenir rainbow tables

    Args:
        password: Password en texto plano.
        tipo_aes: Tipo de AES ("AES-128", "AES-192", "AES-256").
        salt: Salt opcional (si no se proporciona, se genera uno aleatorio).

    Returns:
        Tupla (clave, salt):
            - clave: Clave derivada del password
            - salt: Salt usado (necesario para regenerar la misma clave)

    Example:
        >>> clave, salt = generar_clave_desde_password("mi_password_seguro", "AES-256")
        >>> # Para regenerar la misma clave m�s tarde:
        >>> clave2, _ = generar_clave_desde_password("mi_password_seguro", "AES-256", salt)
        >>> assert clave == clave2
    """
    logger.debug("Generando clave desde password - Tipo: %s", tipo_aes)

    # Generar salt si no se proporciona
    if salt is None:
        salt = get_random_bytes(16)  # 16 bytes = 128 bits
        logger.debug("Salt aleatorio generado")
    else:
        logger.debug("Usando salt proporcionado")

    # Obtener tama�o de clave necesario
    tamanio_clave = TAMANIOS_CLAVE[tipo_aes]

    # Derivar clave usando PBKDF2-HMAC-SHA256
    clave = hashlib.pbkdf2_hmac(
        'sha256',           # Funcion hash
        password.encode(),  # Password en bytes
        salt,               # Salt
        100_000,            # Iteraciones (recomendado minimo)
        dklen=tamanio_clave # Longitud de clave deseada
    )

    logger.debug("Clave generada exitosamente desde password")

    return clave, salt


def generar_clave_aleatoria(tipo_aes: TipoAES = "AES-256") -> bytes:
    """
    Genera una clave AES completamente aleatoria.

    �til cuando no se necesita derivar de un password.

    Args:
        tipo_aes: Tipo de AES ("AES-128", "AES-192", "AES-256").

    Returns:
        Clave aleatoria del tama�o apropiado.

    Example:
        >>> clave = generar_clave_aleatoria("AES-256")
        >>> len(clave)
        32
    """
    tamanio_clave = TAMANIOS_CLAVE[tipo_aes]
    return get_random_bytes(tamanio_clave)


def validar_password(password: str) -> None:
    """
    Valida que el password cumpla con requisitos m�nimos de seguridad.

    Requisitos:
    - Longitud m�nima: 8 caracteres
    - Longitud m�xima: 1000 caracteres

    Args:
        password: Password a validar.

    Raises:
        ValueError: Si el password no cumple los requisitos.
    """
    if not password:
        logger.warning("Intento de validación con password vacío")
        raise ValueError("El password no puede estar vac�o.")

    if len(password) < 8:
        logger.warning("Password demasiado corto")
        raise ValueError(
            "El password debe tener al menos 8 caracteres. "
            f"Proporcionado: {len(password)} caracteres."
        )

    if len(password) > 1000:
        logger.warning("Password demasiado largo")
        raise ValueError(
            "El password es demasiado largo (máximo 1000 caracteres)."
        )
    logger.debug("Password validado correctamente")


# ============================================================================
# CAPA 3: UTILIDADES PARA CODIFICACIÓN
# ============================================================================

def empaquetar_datos_cifrados(
    nonce: bytes,
    datos_cifrados: bytes,
    tag: bytes
) -> str:
    """
    Empaqueta nonce, datos cifrados y tag en un solo string base64.

    Formato: base64(nonce + datos_cifrados + tag)

    Args:
        nonce: Nonce (12 bytes).
        datos_cifrados: Datos cifrados.
        tag: Tag de autenticaci�n (16 bytes).

    Returns:
        String en base64 que contiene todo empaquetado.

    Example:
        >>> empaquetado = empaquetar_datos_cifrados(nonce, cifrado, tag)
        >>> # Se puede transmitir/guardar como string
    """
    # Concatenar nonce + datos_cifrados + tag
    paquete = nonce + datos_cifrados + tag

    # Codificar en base64 para facilitar transmisi�n
    return base64.b64encode(paquete).decode('utf-8')


def desempaquetar_datos_cifrados(
    paquete_base64: str
) -> Tuple[bytes, bytes, bytes]:
    """
    Desempaqueta un string base64 en nonce, datos cifrados y tag.

    Args:
        paquete_base64: String en base64 que contiene nonce + datos + tag.

    Returns:
        Tupla (nonce, datos_cifrados, tag).

    Raises:
        ValueError: Si el paquete no tiene el formato correcto.

    Example:
        >>> nonce, cifrado, tag = desempaquetar_datos_cifrados(empaquetado)
    """
    try:
        # Decodificar de base64
        paquete = base64.b64decode(paquete_base64)
        logger.debug("Paquete decodificado de base64")
    except Exception as e:
        logger.exception("Error al decodificar paquete base64")
        raise ValueError("El paquete no es base64 v�lido.") from e

    # Validar tama�o m�nimo (12 bytes nonce + 16 bytes tag = 28 bytes m�nimo)
    if len(paquete) < 28:
        logger.error("Paquete demasiado pequeño - Esperado: >= 28 bytes, Recibido: %d bytes", len(paquete))
        raise ValueError(
            f"El paquete es demasiado peque�o. "
            f"Tama�o m�nimo: 28 bytes, recibido: {len(paquete)} bytes."
        )

    # Extraer componentes
    nonce = paquete[:NONCE_SIZE]                # Primeros 12 bytes
    tag = paquete[-16:]                          # �ltimos 16 bytes
    datos_cifrados = paquete[NONCE_SIZE:-16]     # El resto en el medio

    logger.debug("Datos desempaquetados correctamente")

    return nonce, datos_cifrados, tag


def empaquetar_salt(salt: bytes) -> str:
    """
    Convierte el salt a base64 para facilitar almacenamiento/transmisi�n.

    Args:
        salt: Salt en bytes.

    Returns:
        Salt en formato base64.
    """
    return base64.b64encode(salt).decode('utf-8')


def desempaquetar_salt(salt_base64: str) -> bytes:
    """
    Convierte un salt de base64 a bytes.

    Args:
        salt_base64: Salt en formato base64.

    Returns:
        Salt en bytes.

    Raises:
        ValueError: Si el salt no es base64 v�lido.
    """
    try:
        return base64.b64decode(salt_base64)
    except Exception as e:
        raise ValueError("El salt no es base64 válido.") from e


# ============================================================================
# FUNCIONES DE ALTO NIVEL (API SIMPLIFICADA)
# ============================================================================

def cifrar_texto(
    texto: str,
    password: str,
    tipo_aes: TipoAES = "AES-256"
) -> Tuple[str, str]:
    """
    Cifra un texto usando un password (funci�n de alto nivel).

    Args:
        texto: Texto a cifrar.
        password: Password para derivar la clave.
        tipo_aes: Tipo de AES a usar.

    Returns:
        Tupla (texto_cifrado_base64, salt_base64):
            - texto_cifrado_base64: Texto cifrado empaquetado en base64
            - salt_base64: Salt generado automáticamente (necesario para descifrar)

    Example:
        >>> cifrado, salt = cifrar_texto("Hola Mundo", "mi_password", "AES-256")
    """
    logger.info("Iniciando cifrado de texto - Tipo: %s", tipo_aes)

    # Validar password
    validar_password(password)

    logger.info("Generando salt automáticamente")

    # Generar clave desde password (salt se genera automáticamente)
    clave, salt = generar_clave_desde_password(password, tipo_aes, None)

    # Cifrar datos
    nonce, datos_cifrados, tag = cifrar_aes(texto.encode('utf-8'), clave, tipo_aes)

    # Empaquetar y retornar
    texto_cifrado = empaquetar_datos_cifrados(nonce, datos_cifrados, tag)
    salt_base64 = empaquetar_salt(salt)

    logger.info("Texto cifrado exitosamente")

    return texto_cifrado, salt_base64


def descifrar_texto(
    texto_cifrado_base64: str,
    password: str,
    salt_base64: str,
    tipo_aes: TipoAES = "AES-256"
) -> str:
    """
    Descifra un texto usando un password (funci�n de alto nivel).

    Args:
        texto_cifrado_base64: Texto cifrado empaquetado en base64.
        password: Password usado para cifrar.
        salt_base64: Salt usado en el cifrado.
        tipo_aes: Tipo de AES usado.

    Returns:
        Texto descifrado.

    Raises:
        ValueError: Si el password es incorrecto o los datos fueron manipulados.

    Example:
        >>> texto_original = descifrar_texto(cifrado, "mi_password", salt, "AES-256")
    """
    logger.info("Iniciando descifrado de texto - Tipo: %s", tipo_aes)

    # Validar password
    validar_password(password)

    # Desempaquetar salt
    salt = desempaquetar_salt(salt_base64)

    # Regenerar clave desde password
    clave, _ = generar_clave_desde_password(password, tipo_aes, salt)

    # Desempaquetar datos cifrados
    nonce, datos_cifrados, tag = desempaquetar_datos_cifrados(texto_cifrado_base64)

    # Descifrar
    datos_descifrados = descifrar_aes(datos_cifrados, clave, nonce, tag, tipo_aes)

    # Decodificar de bytes a string
    texto_descifrado = datos_descifrados.decode('utf-8')

    logger.info("Texto descifrado exitosamente")

    return texto_descifrado


def cifrar_archivo(
    contenido_archivo: bytes,
    password: str,
    tipo_aes: TipoAES = "AES-256"
) -> Tuple[str, str, str]:
    """
    Cifra el contenido de un archivo usando un password.

    Además de cifrar el archivo, calcula el hash SHA256 del contenido original
    para poder verificar su integridad después del descifrado.

    Args:
        contenido_archivo: Contenido del archivo en bytes.
        password: Password para derivar la clave.
        tipo_aes: Tipo de AES a usar.

    Returns:
        Tupla (archivo_cifrado_base64, salt_base64, sha256_hash):
            - archivo_cifrado_base64: Archivo cifrado en base64
            - salt_base64: Salt usado en base64
            - sha256_hash: Hash SHA256 del contenido original (hexadecimal)

    Example:
        >>> with open("documento.pdf", "rb") as f:
        >>>     contenido = f.read()
        >>> cifrado, salt, hash_original = cifrar_archivo(contenido, "mi_password", "AES-256")
        >>> print(f"Hash del archivo: {hash_original}")
    """
    logger.info("Iniciando cifrado de archivo - Tipo: %s", tipo_aes)

    # Validar password
    validar_password(password)

    # Calcular hash SHA256 del contenido ORIGINAL (antes de cifrar)
    logger.debug("Calculando hash SHA256 del contenido original")
    sha256_hash = calcular_hash_sha256(contenido_archivo)
    logger.info("Hash SHA256 calculado: %s...", sha256_hash[:16])

    logger.info("Generando salt automáticamente")

    # Generar clave desde password (salt se genera automáticamente)
    clave, salt = generar_clave_desde_password(password, tipo_aes, None)

    # Cifrar datos
    nonce, datos_cifrados, tag = cifrar_aes(contenido_archivo, clave, tipo_aes)

    # Empaquetar y retornar
    archivo_cifrado = empaquetar_datos_cifrados(nonce, datos_cifrados, tag)
    salt_base64 = empaquetar_salt(salt)

    logger.info("Archivo cifrado exitosamente")

    return archivo_cifrado, salt_base64, sha256_hash


def descifrar_archivo(
    archivo_cifrado_base64: str,
    password: str,
    salt_base64: str,
    tipo_aes: TipoAES = "AES-256",
    sha256_hash: str | None = None
) -> bytes:
    """
    Descifra un archivo usando un password.

    Opcionalmente verifica la integridad del contenido descifrado comparando
    su hash SHA256 con el hash proporcionado.

    Args:
        archivo_cifrado_base64: Archivo cifrado empaquetado en base64.
        password: Password usado para cifrar.
        salt_base64: Salt usado en el cifrado.
        tipo_aes: Tipo de AES usado.
        sha256_hash: Hash SHA256 esperado del archivo original (opcional).
                     Si se proporciona, se verifica la integridad del archivo descifrado.

    Returns:
        Contenido descifrado del archivo en bytes.

    Raises:
        ValueError: Si el hash SHA256 no coincide con el contenido descifrado.

    Example:
        >>> # Sin verificación de hash
        >>> contenido = descifrar_archivo(cifrado, "mi_password", salt, "AES-256")
        >>>
        >>> # Con verificación de hash
        >>> contenido = descifrar_archivo(cifrado, "mi_password", salt, "AES-256", hash_original)
        >>> with open("documento_descifrado.pdf", "wb") as f:
        >>>     f.write(contenido)
    """
    logger.info("Iniciando descifrado de archivo - Tipo: %s", tipo_aes)

    # Validar password
    validar_password(password)

    # Desempaquetar salt
    salt = desempaquetar_salt(salt_base64)

    # Regenerar clave desde password
    clave, _ = generar_clave_desde_password(password, tipo_aes, salt)

    # Desempaquetar datos cifrados
    nonce, datos_cifrados, tag = desempaquetar_datos_cifrados(archivo_cifrado_base64)

    # Descifrar (el tag GCM ya verifica que no fue manipulado)
    contenido_descifrado = descifrar_aes(datos_cifrados, clave, nonce, tag, tipo_aes)

    logger.info("Archivo descifrado exitosamente")

    # Verificar hash SHA256 si se proporcionó
    if sha256_hash is not None:
        logger.info("Verificando integridad con hash SHA256")
        if not verificar_hash_sha256(contenido_descifrado, sha256_hash):
            logger.error("¡ADVERTENCIA! El hash SHA256 NO coincide")
            raise ValueError(
                "El hash SHA256 del archivo descifrado no coincide con el esperado. "
                "El archivo puede estar corrupto o haber sido modificado antes del cifrado."
            )
        logger.info("✅ Hash SHA256 verificado correctamente - Archivo íntegro")

    return contenido_descifrado


# ============================================================================
# FUNCIONES DE STREAMING (Para archivos grandes)
# ============================================================================

def cifrar_archivo_stream(
    file_stream,
    password: str,
    tipo_aes: TipoAES = "AES-256"
) -> Tuple[str, str, str]:
    """
    Cifra un archivo usando streaming (procesa en chunks).

    Ideal para archivos grandes (> 10 MB) que no caben en memoria.
    Procesa el archivo en chunks de 64 KB para optimizar el uso de memoria.

    Además de cifrar, calcula el hash SHA256 del contenido original para
    verificar integridad después del descifrado.

    NOTA: AES-GCM no soporta cifrado verdaderamente incremental (necesita
    todo el contenido para generar el tag). Esta función lee en chunks
    pero mantiene los datos cifrados en memoria. Aún así, es más eficiente
    que leer todo de una vez.

    Args:
        file_stream: Stream del archivo (UploadFile, file object, etc.)
        password: Password para derivar la clave.
        tipo_aes: Tipo de AES a usar.

    Returns:
        Tupla (datos_cifrados_completos, salt_base64, sha256_hash):
            - datos_cifrados_completos: Contenido cifrado en base64
            - salt_base64: Salt usado en base64
            - sha256_hash: Hash SHA256 del contenido original (hexadecimal)

    Example:
        >>> with open("archivo_grande.pdf", "rb") as f:
        >>>     cifrado, salt, hash_original = cifrar_archivo_stream(f, "password", "AES-256")
    """
    logger.info("Iniciando cifrado con streaming - Tipo: %s", tipo_aes)

    # Validar password
    validar_password(password)

    logger.info("Generando salt automáticamente")

    # Generar clave (salt se genera automáticamente)
    clave, salt = generar_clave_desde_password(password, tipo_aes, None)
    # Leer archivo en chunks
    logger.debug("Leyendo archivo en chunks")
    contenido = bytearray()
    bytes_leidos = 0

    while True:
        chunk = file_stream.read(CHUNK_SIZE)
        if not chunk:
            break
        contenido.extend(chunk)
        bytes_leidos += len(chunk)

        # Log cada 10 MB
        if bytes_leidos % (10 * 1024 * 1024) == 0:
            logger.debug("Progreso de lectura: archivo grande en proceso")

    logger.debug("Archivo leído completamente")

    # Calcular hash SHA256 del contenido ORIGINAL (antes de cifrar)
    contenido_bytes = bytes(contenido)
    logger.debug("Calculando hash SHA256 del contenido original")
    sha256_hash = calcular_hash_sha256(contenido_bytes)
    logger.info("Hash SHA256 calculado: %s...", sha256_hash[:16])

    # Cifrar los datos completos
    nonce, datos_cifrados, tag = cifrar_aes(contenido_bytes, clave, tipo_aes)
    # Empaquetar
    texto_cifrado = empaquetar_datos_cifrados(nonce, datos_cifrados, tag)
    salt_base64_resultado = empaquetar_salt(salt)
    logger.info("Cifrado con streaming completado")
    return texto_cifrado, salt_base64_resultado, sha256_hash


async def cifrar_archivo_stream_async(
    file_upload,
    password: str,
    tipo_aes: TipoAES = "AES-256"
) -> Tuple[str, str, str]:
    """
    Cifra un archivo usando streaming asíncrono (para FastAPI UploadFile).

    Versión asíncrona de cifrar_archivo_stream para usar con FastAPI.
    Además de cifrar, calcula el hash SHA256 del contenido original.

    Args:
        file_upload: UploadFile de FastAPI
        password: Password para derivar la clave
        tipo_aes: Tipo de AES

    Returns:
        Tupla (texto_cifrado_base64, salt_base64, sha256_hash):
            - texto_cifrado_base64: Contenido cifrado en base64
            - salt_base64: Salt usado en base64
            - sha256_hash: Hash SHA256 del contenido original (hexadecimal)

    Example:
        >>> # En un endpoint FastAPI
        >>> file: UploadFile = File(...)
        >>> cifrado, salt, hash_original = await cifrar_archivo_stream_async(file, "password", "AES-256")
    """
    logger.info("Iniciando cifrado asíncrono con streaming - Tipo: %s", tipo_aes)

    # Validar password
    validar_password(password)

    logger.info("Generando salt automáticamente")

    # Generar clave (salt se genera automáticamente)
    clave, salt = generar_clave_desde_password(password, tipo_aes, None)
    # Leer archivo en chunks de manera asíncrona
    logger.debug("Leyendo archivo en chunks de manera asíncrona")
    contenido = bytearray()
    bytes_leidos = 0

    while True:
        chunk = await file_upload.read(CHUNK_SIZE)
        if not chunk:
            break
        contenido.extend(chunk)
        bytes_leidos += len(chunk)

        # Log cada 10 MB
        if bytes_leidos % (10 * 1024 * 1024) == 0:
            logger.debug("Progreso de lectura: archivo grande en proceso")

    logger.debug("Archivo leído completamente")

    # Calcular hash SHA256 del contenido ORIGINAL (antes de cifrar)
    contenido_bytes = bytes(contenido)
    logger.debug("Calculando hash SHA256 del contenido original")
    sha256_hash = calcular_hash_sha256(contenido_bytes)
    logger.info("Hash SHA256 calculado: %s...", sha256_hash[:16])

    # Cifrar los datos completos
    nonce, datos_cifrados, tag = cifrar_aes(contenido_bytes, clave, tipo_aes)
    # Empaquetar
    texto_cifrado = empaquetar_datos_cifrados(nonce, datos_cifrados, tag)
    salt_base64_resultado = empaquetar_salt(salt)
    logger.info("Cifrado asíncrono con streaming completado")

    return texto_cifrado, salt_base64_resultado, sha256_hash


# ============================================================================
# FUNCIONES DE INTEGRIDAD CON SHA256
# ============================================================================

def calcular_hash_sha256(contenido: bytes) -> str:
    """
    Calcula el hash SHA256 del contenido.

    Este hash sirve como "fingerprint" único del archivo original.
    Puede usarse para:
    - Verificar integridad después del descifrado
    - Publicar como referencia sin revelar el contenido
    - Auditoría y trazabilidad

    El hash SHA256 es complementario al tag de AES-GCM:
    - Tag GCM: Verifica integridad del contenido CIFRADO
    - SHA256: Verifica integridad del contenido ORIGINAL

    Args:
        contenido: Contenido en bytes del archivo original

    Returns:
        Hash SHA256 en formato hexadecimal (64 caracteres)

    Example:
        >>> contenido = b"Hola Mundo"
        >>> hash_original = calcular_hash_sha256(contenido)
        >>> print(hash_original)
        'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e'
    """
    logger.debug("Calculando hash SHA256 del contenido")
    hash_hex = hashlib.sha256(contenido).hexdigest()
    logger.debug("Hash SHA256 calculado: %s...", hash_hex[:16])
    return hash_hex


def verificar_hash_sha256(contenido: bytes, hash_esperado: str) -> bool:
    """
    Verifica que el hash del contenido coincida con el esperado.

    Utiliza hmac.compare_digest() para prevenir timing attacks,
    aunque para hashes públicos no es crítico.

    Args:
        contenido: Contenido a verificar
        hash_esperado: Hash SHA256 esperado (hexadecimal, 64 caracteres)

    Returns:
        True si el hash coincide, False si no coincide

    Raises:
        ValueError: Si el hash esperado no tiene el formato correcto

    Example:
        >>> contenido = b"Hola Mundo"
        >>> hash_guardado = "a591a6d40bf420404a011733cfb7b190..."
        >>> es_valido = verificar_hash_sha256(contenido, hash_guardado)
        >>> if es_valido:
        >>>     print("✅ Archivo íntegro")
        >>> else:
        >>>     print("❌ Archivo corrupto o modificado")
    """
    logger.debug("Verificando hash SHA256")

    # Validar formato del hash esperado
    if not isinstance(hash_esperado, str) or len(hash_esperado) != 64:
        logger.error("Hash esperado inválido - debe ser string hexadecimal de 64 caracteres")
        raise ValueError(
            f"Hash SHA256 debe ser un string hexadecimal de 64 caracteres. "
            f"Recibido: {len(hash_esperado) if isinstance(hash_esperado, str) else 'tipo inválido'}"
        )

    # Validar que sea hexadecimal válido
    try:
        int(hash_esperado, 16)
    except ValueError as e:
        logger.error("Hash esperado no es hexadecimal válido")
        raise ValueError("Hash SHA256 debe contener solo caracteres hexadecimales (0-9, a-f)") from e

    # Calcular hash del contenido
    hash_calculado = calcular_hash_sha256(contenido)

    # Comparación segura (previene timing attacks)
    import hmac
    coincide = hmac.compare_digest(hash_calculado.lower(), hash_esperado.lower())

    if coincide:
        logger.info("✅ Hash SHA256 verificado correctamente")
    else:
        logger.warning("❌ Hash SHA256 NO coincide - archivo puede estar corrupto o modificado")

    return coincide


# ============================================================================
# FUNCIONES DE ALTO NIVEL (Cifrado + Empaquetado en una sola operación)
# ============================================================================

def cifrar_y_empaquetar_archivo(
    contenido_archivo: bytes,
    password: str,
    nombre_archivo: str,
    mime_type: str,
    tipo_aes: TipoAES = "AES-256"
) -> str:
    """
    Cifra un archivo y devuelve directamente el paquete completo.

    Esta función combina cifrado + empaquetado en una sola operación.
    Es la forma recomendada de cifrar archivos en Scriptum.

    Args:
        contenido_archivo: Contenido del archivo en bytes
        password: Password para cifrar
        nombre_archivo: Nombre original del archivo
        mime_type: MIME type del archivo
        tipo_aes: Tipo de AES a usar

    Returns:
        Paquete completo en base64 (listo para guardar/enviar)

    Example:
        >>> contenido = open("foto.jpg", "rb").read()
        >>> paquete = cifrar_y_empaquetar_archivo(
        ...     contenido, "password123", "foto.jpg", "image/jpeg", "AES-256"
        ... )
        >>> # Usuario solo guarda 'paquete'
    """
    logger.info("Cifrando y empaquetando archivo: %s", nombre_archivo)

    # Cifrar (devuelve cifrado, salt, hash)
    archivo_cifrado, salt, sha256_hash = cifrar_archivo(contenido_archivo, password, tipo_aes)

    # Empaquetar todo
    paquete = crear_paquete_archivo_cifrado(
        contenido_cifrado=archivo_cifrado,
        salt=salt,
        tipo_aes=tipo_aes,
        nombre_archivo=nombre_archivo,
        mime_type=mime_type,
        sha256_hash=sha256_hash
    )

    logger.info("Paquete creado exitosamente")
    return paquete


async def cifrar_y_empaquetar_archivo_stream(
    file_upload,
    password: str,
    nombre_archivo: str,
    mime_type: str,
    tipo_aes: TipoAES = "AES-256"
) -> str:
    """
    Cifra un archivo grande usando streaming y devuelve el paquete completo.

    Versión asíncrona para FastAPI UploadFile. Ideal para archivos > 10 MB.

    Args:
        file_upload: UploadFile de FastAPI
        password: Password para cifrar
        nombre_archivo: Nombre original del archivo
        mime_type: MIME type del archivo
        tipo_aes: Tipo de AES a usar

    Returns:
        Paquete completo en base64

    Example:
        >>> # En endpoint FastAPI
        >>> file: UploadFile = File(...)
        >>> paquete = await cifrar_y_empaquetar_archivo_stream(
        ...     file, "password123", file.filename, file.content_type, "AES-256"
        ... )
    """
    logger.info("Cifrando y empaquetando archivo con streaming: %s", nombre_archivo)

    # Cifrar con streaming
    archivo_cifrado, salt, sha256_hash = await cifrar_archivo_stream_async(
        file_upload, password, tipo_aes
    )

    # Empaquetar todo
    paquete = crear_paquete_archivo_cifrado(
        contenido_cifrado=archivo_cifrado,
        salt=salt,
        tipo_aes=tipo_aes,
        nombre_archivo=nombre_archivo,
        mime_type=mime_type,
        sha256_hash=sha256_hash
    )

    logger.info("Paquete con streaming creado exitosamente")
    return paquete


def desempaquetar_y_descifrar_archivo(
    paquete: str,
    password: str
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Desempaqueta y descifra un archivo en una sola operación.

    Extrae automáticamente todos los metadatos del paquete,
    descifra el archivo y verifica su integridad con SHA256.

    Args:
        paquete: Paquete completo en base64 (obtenido al cifrar)
        password: Password usado para cifrar

    Returns:
        Tupla (contenido_descifrado, metadata):
            - contenido_descifrado: Contenido del archivo en bytes
            - metadata: Dict con nombre_original, mime_type, tipo_aes

    Raises:
        ValueError: Si el password es incorrecto o el archivo está corrupto

    Example:
        >>> contenido, metadata = desempaquetar_y_descifrar_archivo(paquete, "password123")
        >>> print(f"Archivo: {metadata['nombre_original']}")
        >>> with open(metadata['nombre_original'], "wb") as f:
        ...     f.write(contenido)
    """
    logger.info("Desempaquetando y descifrando archivo")

    # Extraer datos del paquete
    datos = extraer_paquete_archivo_cifrado(paquete)

    contenido_cifrado = datos["contenido_cifrado"]
    salt = datos["salt"]
    tipo_aes = datos["tipo_aes"]
    sha256_hash = datos["sha256_hash"]
    metadata = datos["metadata"]

    logger.info("Paquete extraído: %s, tipo=%s", metadata["nombre_original"], tipo_aes)

    # Descifrar con verificación de hash
    contenido_descifrado = descifrar_archivo(
        contenido_cifrado,
        password,
        salt,
        tipo_aes,
        sha256_hash  # Verifica automáticamente integridad
    )

    # Agregar tipo_aes al metadata para el usuario
    metadata["tipo_aes"] = tipo_aes

    logger.info("Archivo desempaquetado y descifrado exitosamente")
    return contenido_descifrado, metadata


# ============================================================================
# EMPAQUETADO DE ARCHIVOS CON METADATOS (Formato Binario)
# ============================================================================

# Constantes para el formato de paquete
MAGIC_BYTES = b"SCRIPTUM"  # 8 bytes
VERSION_BYTE = 1            # Versión del formato
SALT_SIZE = 16              # Tamaño del salt en bytes
SHA256_SIZE = 32            # Tamaño del hash SHA256 en bytes

# Mapeo de tipos AES a valores numéricos
AES_TYPE_MAP = {
    "AES-128": 1,
    "AES-192": 2,
    "AES-256": 3
}
AES_TYPE_REVERSE_MAP = {v: k for k, v in AES_TYPE_MAP.items()}


def crear_paquete_archivo_cifrado(
    contenido_cifrado: str,
    salt: str,
    tipo_aes: TipoAES,
    nombre_archivo: str,
    mime_type: str,
    sha256_hash: str
) -> str:
    """
    Crea un paquete binario que contiene el archivo cifrado + metadatos.

    Formato del paquete (binario):

    ┌─────────────────────────────────────────────────────────────┐
    │  HEADER (sin cifrar)                                        │
    ├─────────────────────────────────────────────────────────────┤
    │  Magic:         "SCRIPTUM" (8 bytes)                        │
    │  Version:       1 (1 byte)                                  │
    │  Tipo AES:      1/2/3 (1 byte) → 128/192/256               │
    │  Salt:          [16 bytes]                                  │
    │  SHA256:        [32 bytes] → Hash del archivo original      │
    │  Nombre len:    N (2 bytes, unsigned short, big-endian)    │
    │  Nombre:        [N bytes UTF-8]                             │
    │  MIME len:      M (2 bytes, unsigned short, big-endian)    │
    │  MIME:          [M bytes UTF-8]                             │
    ├─────────────────────────────────────────────────────────────┤
    │  BODY (cifrado en base64)                                   │
    ├─────────────────────────────────────────────────────────────┤
    │  Contenido cifrado [bytes restantes]                        │
    └─────────────────────────────────────────────────────────────┘

    Todo el paquete → base64 → UN SOLO STRING

    Ventajas:
    - Usuario guarda UN SOLO campo
    - Más compacto que JSON (~30% menos espacio)
    - No puede perder el salt o metadatos
    - Formato binario eficiente
    - Extensible (versión permite cambios futuros)

    Args:
        contenido_cifrado: Contenido cifrado en base64
        salt: Salt en base64
        tipo_aes: Tipo de AES usado ("AES-128", "AES-192", "AES-256")
        nombre_archivo: Nombre original del archivo
        mime_type: MIME type del archivo
        sha256_hash: Hash SHA256 del archivo original (hexadecimal, 64 caracteres)

    Returns:
        Paquete completo en base64

    Raises:
        ValueError: Si el tipo de AES no es válido o los datos son inválidos

    Example:
        >>> paquete = crear_paquete_archivo_cifrado(
        ...     "U2FsdGVkX1...",
        ...     "cmFuZG9t...",
        ...     "AES-256",
        ...     "foto.jpg",
        ...     "image/jpeg",
        ...     "a591a6d40bf420404a011733cfb7b190..."
        ... )
        >>> # Usuario solo guarda 'paquete' (un string base64)
    """
    logger.debug("Creando paquete binario con tipo AES: %s", tipo_aes)

    # Validar tipo de AES
    if tipo_aes not in AES_TYPE_MAP:
        raise ValueError(f"Tipo de AES inválido: {tipo_aes}")

    # Decodificar salt de base64
    try:
        salt_bytes = base64.b64decode(salt)
        if len(salt_bytes) != SALT_SIZE:
            raise ValueError(f"Salt debe tener {SALT_SIZE} bytes, tiene {len(salt_bytes)}")
    except Exception as e:
        logger.exception("Error al decodificar salt en crear_paquete_archivo_cifrado")
        raise ValueError(f"Salt inválido: {e}") from e

    # Validar y convertir hash SHA256
    if not isinstance(sha256_hash, str) or len(sha256_hash) != 64:
        logger.error("Hash SHA256 inválido - debe ser string hexadecimal de 64 caracteres")
        raise ValueError(
            f"Hash SHA256 debe ser un string hexadecimal de 64 caracteres. "
            f"Recibido: {len(sha256_hash) if isinstance(sha256_hash, str) else 'tipo inválido'}"
        )
    try:
        # Convertir de hex a bytes
        sha256_bytes = bytes.fromhex(sha256_hash)
        if len(sha256_bytes) != SHA256_SIZE:
            raise ValueError(f"Hash SHA256 debe tener {SHA256_SIZE} bytes")
    except Exception as e:
        logger.exception("Error al procesar hash SHA256 en crear_paquete_archivo_cifrado")
        raise ValueError(f"Hash SHA256 inválido: {e}") from e

    # Decodificar contenido cifrado de base64
    try:
        contenido_bytes = base64.b64decode(contenido_cifrado)
    except Exception as e:
        logger.exception("Error al decodificar contenido cifrado en crear_paquete_archivo_cifrado")
        raise ValueError(f"Contenido cifrado inválido: {e}") from e

    # Convertir strings a bytes
    nombre_bytes = nombre_archivo.encode('utf-8')
    mime_bytes = mime_type.encode('utf-8')

    # Validar longitudes (máximo 65535 bytes por campo, límite de unsigned short)
    if len(nombre_bytes) > 65535:
        raise ValueError("Nombre de archivo demasiado largo")
    if len(mime_bytes) > 65535:
        raise ValueError("MIME type demasiado largo")

    # Construir el paquete binario
    paquete = bytearray()

    # HEADER
    paquete.extend(MAGIC_BYTES)                                    # 8 bytes
    paquete.append(VERSION_BYTE)                                   # 1 byte
    paquete.append(AES_TYPE_MAP[tipo_aes])                        # 1 byte
    paquete.extend(salt_bytes)                                     # 16 bytes
    paquete.extend(sha256_bytes)                                   # 32 bytes

    # Nombre del archivo (longitud + contenido)
    paquete.extend(struct.pack('>H', len(nombre_bytes)))          # 2 bytes
    paquete.extend(nombre_bytes)                                   # N bytes

    # MIME type (longitud + contenido)
    paquete.extend(struct.pack('>H', len(mime_bytes)))            # 2 bytes
    paquete.extend(mime_bytes)                                    

    # BODY (contenido cifrado)
    paquete.extend(contenido_bytes)                               

    # Convertir todo a base64
    paquete_base64 = base64.b64encode(bytes(paquete)).decode('ascii')

    logger.info("Paquete creado exitosamente")

    return paquete_base64


def extraer_paquete_archivo_cifrado(paquete_base64: str) -> Dict[str, Any]:
    """
    Extrae el contenido de un paquete binario cifrado.

    Lee el header para obtener metadatos y extrae el contenido cifrado.

    Args:
        paquete_base64: Paquete en base64 (creado con crear_paquete_archivo_cifrado)

    Returns:
        Diccionario con:
        - contenido_cifrado: Contenido cifrado en base64
        - salt: Salt en base64
        - tipo_aes: Tipo de AES ("AES-128", "AES-192", "AES-256")
        - sha256_hash: Hash SHA256 del archivo original (hexadecimal)
        - metadata: Dict con:
          - nombre_original: Nombre del archivo
          - mime_type: MIME type del archivo

    Raises:
        ValueError: Si el paquete está corrupto o tiene formato inválido

    Example:
        >>> datos = extraer_paquete_archivo_cifrado(paquete)
        >>> print(datos['metadata']['nombre_original'])  # "foto.jpg"
        >>> print(datos['salt'])                         # "cmFuZG9t..."
        >>> print(datos['tipo_aes'])                     # "AES-256"
        >>> print(datos['sha256_hash'])                  # "a591a6d40bf420404a011733..."
    """
    logger.debug("Extrayendo paquete binario cifrado")

    try:
        # Decodificar de base64
        paquete_bytes = base64.b64decode(paquete_base64)
    except Exception as e:
        logger.exception("Error al decodificar paquete base64 en extraer_paquete_archivo_cifrado")
        raise ValueError(f"Paquete base64 inválido: {e}") from e

    # Verificar tamaño mínimo (header sin nombre ni mime)
    # Magic(8) + Version(1) + AES(1) + Salt(16) + SHA256(32) + NombreLen(2) + MIMELen(2) = 62 bytes
    if len(paquete_bytes) < 62:
        raise ValueError(f"Paquete demasiado pequeño: {len(paquete_bytes)} bytes (mínimo 62)")

    offset = 0

    # Leer HEADER

    # Magic bytes
    magic = paquete_bytes[offset:offset+8]
    offset += 8
    if magic != MAGIC_BYTES:
        raise ValueError(f"Magic bytes inválido: esperado {MAGIC_BYTES}, obtenido {magic}")

    # Versión
    version = paquete_bytes[offset]
    offset += 1
    if version != VERSION_BYTE:
        raise ValueError(f"Versión no soportada: {version} (esperado {VERSION_BYTE})")

    # Tipo AES
    aes_type_byte = paquete_bytes[offset]
    offset += 1
    if aes_type_byte not in AES_TYPE_REVERSE_MAP:
        raise ValueError(f"Tipo de AES inválido: {aes_type_byte}")
    tipo_aes = AES_TYPE_REVERSE_MAP[aes_type_byte]

    # Salt
    salt_bytes = paquete_bytes[offset:offset+SALT_SIZE]
    offset += SALT_SIZE
    if len(salt_bytes) != SALT_SIZE:
        raise ValueError(f"Salt incompleto: {len(salt_bytes)} bytes (esperado {SALT_SIZE})")
    salt_base64 = base64.b64encode(salt_bytes).decode('ascii')

    # Hash SHA256
    sha256_bytes = paquete_bytes[offset:offset+SHA256_SIZE]
    offset += SHA256_SIZE
    if len(sha256_bytes) != SHA256_SIZE:
        raise ValueError(f"Hash SHA256 incompleto: {len(sha256_bytes)} bytes (esperado {SHA256_SIZE})")
    sha256_hash = sha256_bytes.hex()

    # Longitud del nombre
    if offset + 2 > len(paquete_bytes):
        raise ValueError("Paquete truncado: falta longitud de nombre")
    nombre_len = struct.unpack('>H', paquete_bytes[offset:offset+2])[0]
    offset += 2

    # Nombre del archivo
    if offset + nombre_len > len(paquete_bytes):
        raise ValueError(f"Paquete truncado: falta nombre ({nombre_len} bytes)")
    nombre_bytes = paquete_bytes[offset:offset+nombre_len]
    offset += nombre_len
    try:
        nombre_original = nombre_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        logger.exception("Error al decodificar nombre de archivo en extraer_paquete")
        raise ValueError(f"Nombre de archivo no es UTF-8 válido: {e}") from e

    # Longitud del MIME
    if offset + 2 > len(paquete_bytes):
        raise ValueError("Paquete truncado: falta longitud de MIME")
    mime_len = struct.unpack('>H', paquete_bytes[offset:offset+2])[0]
    offset += 2

    # MIME type
    if offset + mime_len > len(paquete_bytes):
        raise ValueError(f"Paquete truncado: falta MIME ({mime_len} bytes)")
    mime_bytes = paquete_bytes[offset:offset+mime_len]
    offset += mime_len
    try:
        mime_type = mime_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        logger.exception("Error al decodificar MIME type en extraer_paquete")
        raise ValueError(f"MIME type no es UTF-8 válido: {e}") from e

    # BODY (contenido cifrado)
    contenido_bytes = paquete_bytes[offset:]
    if len(contenido_bytes) == 0:
        raise ValueError("Paquete no contiene datos cifrados")
    contenido_cifrado_base64 = base64.b64encode(contenido_bytes).decode('ascii')

    logger.info("Paquete extraído exitosamente con tipo AES: %s", tipo_aes)

    return {
        "contenido_cifrado": contenido_cifrado_base64,
        "salt": salt_base64,
        "tipo_aes": tipo_aes,
        "sha256_hash": sha256_hash,
        "metadata": {
            "nombre_original": nombre_original,
            "mime_type": mime_type
        }
    }
