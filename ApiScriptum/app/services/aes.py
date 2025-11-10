"""
SERVICIOS AES
SCRIPTUM - Servicio de cifrado AES (Advanced Encryption Standard)
Autoras: Arantxa - Wara

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
import logging
from typing import Tuple, Literal
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
    logger.info("Iniciando cifrado AES - Tipo: %s, Tamaño de datos: %d bytes", tipo_aes, len(datos))
    
    # Validar tama�o de clave
    tamanio_esperado = TAMANIOS_CLAVE[tipo_aes]
    if len(clave) != tamanio_esperado:
        logger.error("Tamaño de clave inválido - Esperado: %d bytes, Recibido: %d bytes", tamanio_esperado, len(clave))
        raise ValueError(
            f"La clave para {tipo_aes} debe tener {tamanio_esperado} bytes. "
            f"Se proporcionaron {len(clave)} bytes."
        )

    # Generar nonce aleatorio (12 bytes es el tama�o recomendado para GCM)
    nonce = get_random_bytes(NONCE_SIZE)

    # Crear cipher AES-GCM
    cipher = AES.new(clave, AES.MODE_GCM, nonce=nonce)

    # Cifrar y obtener tag de autenticaci�n
    datos_cifrados, tag = cipher.encrypt_and_digest(datos)
    
    logger.info("Cifrado completado exitosamente - Datos cifrados: %d bytes", len(datos_cifrados))

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
    logger.info("Iniciando descifrado AES - Tipo: %s, Tamaño de datos cifrados: %d bytes", tipo_aes, len(datos_cifrados))
    
    # Validar tama�o de clave
    tamanio_esperado = TAMANIOS_CLAVE[tipo_aes]
    if len(clave) != tamanio_esperado:
        logger.error("Tamaño de clave inválido en descifrado - Esperado: %d bytes, Recibido: %d bytes", tamanio_esperado, len(clave))
        raise ValueError(
            f"La clave para {tipo_aes} debe tener {tamanio_esperado} bytes. "
            f"Se proporcionaron {len(clave)} bytes."
        )

    # Crear cipher AES-GCM con el mismo nonce
    cipher = AES.new(clave, AES.MODE_GCM, nonce=nonce)

    # Descifrar y verificar tag de autenticaci�n
    try:
        datos_descifrados = cipher.decrypt_and_verify(datos_cifrados, tag)
        logger.info("Descifrado completado exitosamente - Datos descifrados: %d bytes", len(datos_descifrados))
        return datos_descifrados
    except ValueError as e:
        logger.error("Error al descifrar: clave incorrecta o datos manipulados")
        raise ValueError(
            "Error al descifrar: clave incorrecta o datos manipulados. "
            "El tag de autenticaci�n no coincide."
        ) from e


# ============================================================================
# CAPA 2: GENERACI�N Y VALIDACI�N DE CLAVES
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
    logger.info("Generando clave desde password - Tipo: %s", tipo_aes)
    
    # Generar salt si no se proporciona
    if salt is None:
        salt = get_random_bytes(16)  # 16 bytes = 128 bits
        logger.debug("Salt aleatorio generado - Tamaño: 16 bytes")
    else:
        logger.debug("Usando salt proporcionado - Tamaño: %d bytes", len(salt))

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
    
    logger.info("Clave generada exitosamente desde password - Tamaño: %d bytes", len(clave))

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
        logger.warning("Password demasiado corto - Longitud: %d caracteres", len(password))
        raise ValueError(
            "El password debe tener al menos 8 caracteres. "
            f"Proporcionado: {len(password)} caracteres."
        )

    if len(password) > 1000:
        logger.warning("Password demasiado largo - Longitud: %d caracteres", len(password))
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
        logger.debug("Paquete decodificado de base64 - Tamaño total: %d bytes", len(paquete))
    except Exception as e:
        logger.error("Error al decodificar paquete base64: %s", str(e))
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
    
    logger.debug("Datos desempaquetados - Nonce: %d bytes, Cifrado: %d bytes, Tag: %d bytes", 
                len(nonce), len(datos_cifrados), len(tag))

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
        raise ValueError("El salt no es base64 v�lido.") from e


# ============================================================================
# FUNCIONES DE ALTO NIVEL (API SIMPLIFICADA)
# ============================================================================

def cifrar_texto(
    texto: str,
    password: str,
    tipo_aes: TipoAES = "AES-256",
    salt_base64: str | None = None
) -> Tuple[str, str]:
    """
    Cifra un texto usando un password (funci�n de alto nivel).

    Args:
        texto: Texto a cifrar.
        password: Password para derivar la clave.
        tipo_aes: Tipo de AES a usar.
        salt_base64: Salt opcional en base64. Si no se proporciona, se genera automáticamente.

    Returns:
        Tupla (texto_cifrado_base64, salt_base64):
            - texto_cifrado_base64: Texto cifrado empaquetado en base64
            - salt_base64: Salt usado (necesario para descifrar)

    Example:
        >>> # Sin salt (se genera automáticamente)
        >>> cifrado, salt = cifrar_texto("Hola Mundo", "mi_password", "AES-256")
        >>>
        >>> # Con salt personalizado
        >>> cifrado, salt = cifrar_texto("Hola Mundo", "mi_password", "AES-256", "cmFuZG9tc2FsdA==")
    """
    logger.info("Iniciando cifrado de texto - Tipo: %s, Longitud del texto: %d caracteres", tipo_aes, len(texto))

    # Validar password
    validar_password(password)

    # Convertir salt de base64 a bytes si se proporcionó
    salt_bytes = None
    if salt_base64:
        try:
            salt_bytes = desempaquetar_salt(salt_base64)
            logger.info("Usando salt proporcionado por el cliente")
        except ValueError as e:
            logger.error("Salt inválido proporcionado: %s", str(e))
            raise ValueError("El salt proporcionado no es base64 válido") from e
    else:
        logger.info("Generando salt automáticamente")

    # Generar clave desde password (con o sin salt personalizado)
    clave, salt = generar_clave_desde_password(password, tipo_aes, salt_bytes)

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
    
    logger.info("Texto descifrado exitosamente - Longitud: %d caracteres", len(texto_descifrado))
    
    return texto_descifrado


def cifrar_archivo(
    contenido_archivo: bytes,
    password: str,
    tipo_aes: TipoAES = "AES-256",
    salt_base64: str | None = None
) -> Tuple[str, str]:
    """
    Cifra el contenido de un archivo usando un password.

    Args:
        contenido_archivo: Contenido del archivo en bytes.
        password: Password para derivar la clave.
        tipo_aes: Tipo de AES a usar.
        salt_base64: Salt opcional en base64. Si no se proporciona, se genera automáticamente.

    Returns:
        Tupla (archivo_cifrado_base64, salt_base64).

    Example:
        >>> with open("documento.pdf", "rb") as f:
        >>>     contenido = f.read()
        >>> # Sin salt (automático)
        >>> cifrado, salt = cifrar_archivo(contenido, "mi_password", "AES-256")
        >>> # Con salt personalizado
        >>> cifrado, salt = cifrar_archivo(contenido, "mi_password", "AES-256", "cmFuZG9tc2FsdA==")
    """
    logger.info("Iniciando cifrado de archivo - Tipo: %s, Tamaño: %d bytes", tipo_aes, len(contenido_archivo))

    # Validar password
    validar_password(password)

    # Convertir salt de base64 a bytes si se proporcionó
    salt_bytes = None
    if salt_base64:
        try:
            salt_bytes = desempaquetar_salt(salt_base64)
            logger.info("Usando salt proporcionado por el cliente")
        except ValueError as e:
            logger.error("Salt inválido proporcionado: %s", str(e))
            raise ValueError("El salt proporcionado no es base64 válido") from e
    else:
        logger.info("Generando salt automáticamente")

    # Generar clave desde password (con o sin salt personalizado)
    clave, salt = generar_clave_desde_password(password, tipo_aes, salt_bytes)

    # Cifrar datos
    nonce, datos_cifrados, tag = cifrar_aes(contenido_archivo, clave, tipo_aes)

    # Empaquetar y retornar
    archivo_cifrado = empaquetar_datos_cifrados(nonce, datos_cifrados, tag)
    salt_base64 = empaquetar_salt(salt)
    
    logger.info("Archivo cifrado exitosamente")

    return archivo_cifrado, salt_base64


def descifrar_archivo(
    archivo_cifrado_base64: str,
    password: str,
    salt_base64: str,
    tipo_aes: TipoAES = "AES-256"
) -> bytes:
    """
    Descifra un archivo usando un password.

    Args:
        archivo_cifrado_base64: Archivo cifrado empaquetado en base64.
        password: Password usado para cifrar.
        salt_base64: Salt usado en el cifrado.
        tipo_aes: Tipo de AES usado.

    Returns:
        Contenido descifrado del archivo en bytes.

    Example:
        >>> contenido_original = descifrar_archivo(cifrado, "mi_password", salt, "AES-256")
        >>> with open("documento_descifrado.pdf", "wb") as f:
        >>>     f.write(contenido_original)
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

    # Descifrar
    contenido_descifrado = descifrar_aes(datos_cifrados, clave, nonce, tag, tipo_aes)
    
    logger.info("Archivo descifrado exitosamente - Tamaño: %d bytes", len(contenido_descifrado))
    
    return contenido_descifrado


# ============================================================================
# FUNCIONES DE STREAMING (Para archivos grandes)
# ============================================================================

def cifrar_archivo_stream(
    file_stream,
    password: str,
    tipo_aes: TipoAES = "AES-256",
    salt_base64: str | None = None
) -> Tuple[bytearray, str]:
    """
    Cifra un archivo usando streaming (procesa en chunks).
    
    Ideal para archivos grandes (> 10 MB) que no caben en memoria.
    Procesa el archivo en chunks de 64 KB para optimizar el uso de memoria.
    
    NOTA: AES-GCM no soporta cifrado verdaderamente incremental (necesita
    todo el contenido para generar el tag). Esta función lee en chunks
    pero mantiene los datos cifrados en memoria. Aún así, es más eficiente
    que leer todo de una vez.
    
    Args:
        file_stream: Stream del archivo (UploadFile, file object, etc.)
        password: Password para derivar la clave.
        tipo_aes: Tipo de AES a usar.
        salt_base64: Salt opcional en base64.
    
    Returns:
        Tupla (datos_cifrados_completos, salt_base64)
        
    Example:
        >>> with open("archivo_grande.pdf", "rb") as f:
        >>>     cifrado, salt = cifrar_archivo_stream(f, "password", "AES-256")
    """
    logger.info("Iniciando cifrado con streaming - Tipo: %s", tipo_aes)
    
    # Validar password
    validar_password(password)
    
    # Convertir salt si se proporcionó
    salt_bytes = None
    if salt_base64:
        salt_bytes = desempaquetar_salt(salt_base64)
        logger.info("Usando salt proporcionado por el cliente")
    else:
        logger.info("Generando salt automáticamente")
    
    # Generar clave
    clave, salt = generar_clave_desde_password(password, tipo_aes, salt_bytes)
    
    # Leer archivo en chunks
    logger.info("Leyendo archivo en chunks de %d KB", CHUNK_SIZE // 1024)
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
            logger.info("Leídos: %d MB", bytes_leidos // (1024 * 1024))
    
    logger.info("Archivo leído completamente: %d bytes", bytes_leidos)
    
    # Cifrar los datos completos
    nonce, datos_cifrados, tag = cifrar_aes(bytes(contenido), clave, tipo_aes)
    
    # Empaquetar
    texto_cifrado = empaquetar_datos_cifrados(nonce, datos_cifrados, tag)
    salt_base64_resultado = empaquetar_salt(salt)
    
    logger.info("Cifrado con streaming completado")
    
    return texto_cifrado, salt_base64_resultado


async def cifrar_archivo_stream_async(
    file_upload,
    password: str,
    tipo_aes: TipoAES = "AES-256",
    salt_base64: str | None = None
) -> Tuple[str, str]:
    """
    Cifra un archivo usando streaming asíncrono (para FastAPI UploadFile).
    
    Versión asíncrona de cifrar_archivo_stream para usar con FastAPI.
    
    Args:
        file_upload: UploadFile de FastAPI
        password: Password para derivar la clave
        tipo_aes: Tipo de AES
        salt_base64: Salt opcional
    
    Returns:
        Tupla (texto_cifrado_base64, salt_base64)
    
    Example:
        >>> # En un endpoint FastAPI
        >>> file: UploadFile = File(...)
        >>> cifrado, salt = await cifrar_archivo_stream_async(file, "password", "AES-256")
    """
    logger.info("Iniciando cifrado asíncrono con streaming - Tipo: %s, Archivo: %s", 
                tipo_aes, file_upload.filename)
    
    # Validar password
    validar_password(password)
    
    # Convertir salt si se proporcionó
    salt_bytes = None
    if salt_base64:
        salt_bytes = desempaquetar_salt(salt_base64)
        logger.info("Usando salt proporcionado por el cliente")
    else:
        logger.info("Generando salt automáticamente")
    
    # Generar clave
    clave, salt = generar_clave_desde_password(password, tipo_aes, salt_bytes)
    
    # Leer archivo en chunks de manera asíncrona
    logger.info("Leyendo archivo en chunks de %d KB", CHUNK_SIZE // 1024)
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
            logger.info("Leídos: %d MB", bytes_leidos // (1024 * 1024))
    
    logger.info("Archivo leído completamente: %d bytes (%d MB)", 
                bytes_leidos, bytes_leidos // (1024 * 1024))
    
    # Cifrar los datos completos
    nonce, datos_cifrados, tag = cifrar_aes(bytes(contenido), clave, tipo_aes)
    
    # Empaquetar
    texto_cifrado = empaquetar_datos_cifrados(nonce, datos_cifrados, tag)
    salt_base64_resultado = empaquetar_salt(salt)
    
    logger.info("Cifrado asíncrono con streaming completado")
    
    return texto_cifrado, salt_base64_resultado
