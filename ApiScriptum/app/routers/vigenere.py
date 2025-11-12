"""
ROUTER VIGENÈRE
Endpoints para cifrado y descifrado con algoritmo Vigenère
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.schemas.vigenere import (
    CifrarTextoRequest,
    DescifrarTextoRequest,
    CifradoResponse,
    DescifradoResponse,
    ErrorResponse
)
from app.services.vigenere import (
    cifrar_vigenere,
    descifrar_vigenere,
    validar_y_formatear_clave
)


router = APIRouter(prefix="/vigenere", tags=["Vigenère"])

# ============================================================================
# LOGGING
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Límites de tamaño
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
SMALL_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
CANARY_SIZE = 1024  # 1 KB para verificación

# Caracteres invisibles a detectar
CARACTERES_INVISIBLES = {
    '\u200B': 'Zero-Width Space',
    '\u200C': 'Zero-Width Non-Joiner',
    '\u200D': 'Zero-Width Joiner',
    '\uFEFF': 'Zero-Width No-Break Space',
    '\u00A0': 'Non-Breaking Space'
}


# ============================================================================
# FUNCIONES AUXILIARES (Reducen duplicación)
# ============================================================================

def detectar_caracteres_invisibles(texto: str) -> list:
    """
    Detecta caracteres invisibles en un texto.

    Returns:
        Lista de diccionarios con información de cada carácter invisible encontrado
    """
    warnings = []
    for i, char in enumerate(texto):
        if char in CARACTERES_INVISIBLES:
            warnings.append({
                'posicion': i,
                'caracter': f'U+{ord(char):04X}',
                'nombre': CARACTERES_INVISIBLES[char]
            })
    return warnings


async def leer_archivo_seguro(file: UploadFile, max_size: int = MAX_FILE_SIZE) -> bytes:
    """
    Lee un archivo de forma segura con validaciones.

    Args:
        file: Archivo subido
        max_size: Tamaño máximo permitido en bytes

    Returns:
        Contenido del archivo en bytes

    Raises:
        HTTPException: Si el archivo es demasiado grande o inválido
    """
    # Validar que el archivo tenga nombre
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El archivo debe tener un nombre"}
        )

    # Asignar nombre a variable local para type narrowing
    filename = file.filename

    # Validar extensión
    if not filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Solo se aceptan archivos .txt",
                "archivo_recibido": filename
            }
        )

    # Leer y validar tamaño
    contenido = await file.read()
    file_size = len(contenido)

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": f"Archivo demasiado grande: {file_size / (1024*1024):.2f} MB",
                "limite": f"{max_size / (1024*1024):.0f} MB"
            }
        )

    # Validar que sea UTF-8 válido
    try:
        contenido.decode('utf-8')
    except UnicodeDecodeError as exc:
        logger.exception("Error al decodificar archivo UTF-8: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El archivo no es texto UTF-8 válido"}
        ) from exc

    return contenido


def validar_clave_sin_caracteres_invisibles(clave: str) -> None:
    """
    Valida que la clave no contenga caracteres invisibles.

    Raises:
        HTTPException: Si se encuentran caracteres invisibles
    """
    warnings = detectar_caracteres_invisibles(clave)

    if warnings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "La clave contiene caracteres invisibles",
                "caracteres_detectados": warnings,
                "sugerencia": "Elimina los caracteres invisibles y vuelve a intentar"
            }
        )


def manejar_error(e: Exception, operacion: str) -> HTTPException:
    """
    Centraliza el manejo de errores para evitar duplicación.

    Args:
        e: Excepción capturada
        operacion: Descripción de la operación (ej: "cifrar texto", "descifrar archivo")

    Returns:
        HTTPException apropiada según el tipo de error
    """
    if isinstance(e, HTTPException):
        return e

    if isinstance(e, ValueError):
        logger.warning("Error de validación al %s: %s", operacion, str(e))
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )

    # Error inesperado - solo logear detalles, no exponerlos
    logger.exception("Error interno al %s", operacion)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"error": f"Error interno al {operacion}"}
    )


# ============================================================================
# ENDPOINTS DE TEXTO
# ============================================================================

@router.post(
    "/cifrar/texto",
    response_model=CifradoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Error en la validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Cifrar texto con Vigenère",
    description="""
    Cifra un texto utilizando el algoritmo de cifrado Vigenère.

    **¿Cómo funciona?**
    - El texto se limpia (solo letras, mayúsculas, sin espacios)
    - La clave se repite cíclicamente para igualar la longitud del texto
    - Cada letra se desplaza según la letra correspondiente de la clave

    **Ejemplo:**
    - Texto: "Hola Mundo"
    - Clave: "clave"
    - Resultado: "JSVEQZVIS"
    """
)
async def cifrar_texto(request: CifrarTextoRequest):
    """
    Cifra un texto con Vigenère

    Args:
        request: Objeto con texto y clave

    Returns:
        CifradoResponse con el texto cifrado
    """
    try:
        # Validar que la clave no tenga caracteres invisibles
        validar_clave_sin_caracteres_invisibles(request.clave)

        # Cifrar el texto
        texto_cifrado = cifrar_vigenere(request.texto, request.clave)

        return CifradoResponse(
            texto_cifrado=texto_cifrado,
            clave_usada=''.join(c.upper() for c in request.clave if c.isalpha()),
            texto_original_length=len(request.texto)
        )
    except Exception as e:
        raise manejar_error(e, "cifrar texto") from e


@router.post(
    "/descifrar/texto",
    response_model=DescifradoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Error en la validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Descifrar texto con Vigenère",
    description="""
    Descifra un texto previamente cifrado con el algoritmo Vigenère.

    **Importante:** Debes usar la misma clave que usaste para cifrar.

    **Ejemplo:**
    - Texto cifrado: "JSVEQZVIS"
    - Clave: "clave"
    - Resultado: "HOLAMUNDO"
    """
)
async def descifrar_texto(request: DescifrarTextoRequest):
    """
    Descifra un texto con Vigenère

    Args:
        request: Objeto con texto cifrado y clave

    Returns:
        DescifradoResponse con el texto descifrado
    """
    try:
        # Validar que la clave no tenga caracteres invisibles
        validar_clave_sin_caracteres_invisibles(request.clave)

        # Descifrar el texto
        texto_descifrado = descifrar_vigenere(request.texto_cifrado, request.clave)

        return DescifradoResponse(
            texto_descifrado=texto_descifrado,
            clave_usada=''.join(c.upper() for c in request.clave if c.isalpha())
        )
    except Exception as e:
        raise manejar_error(e, "descifrar texto") from e


# ============================================================================
# ENDPOINTS DE ARCHIVOS
# ============================================================================

@router.post(
    "/cifrar/file",
    response_model=CifradoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Error en la validación"},
        413: {"model": ErrorResponse, "description": "Archivo demasiado grande"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Cifrar archivo de texto",
    description="""
    Cifra el contenido de un archivo .txt con Vigenère.

    **Características:**
    - Solo archivos .txt (máximo 10 MB)
    - Validación automática de caracteres invisibles en la clave
    - Detección de encoding UTF-8 inválido
    - No se guardan archivos en el servidor

    Para archivos grandes (10-500 MB), usa el endpoint `/cifrar/file/large`
    """
)
async def cifrar_archivo(
    file: UploadFile = File(..., description="Archivo .txt a cifrar"),
    clave: str = Form(..., description="Clave para el cifrado")
):
    """
    Cifra un archivo de texto con Vigenère (hasta 10 MB)

    Args:
        file: Archivo .txt subido
        clave: Clave para el cifrado

    Returns:
        CifradoResponse con el contenido cifrado del archivo
    """
    try:
        # Validar la clave
        validar_clave_sin_caracteres_invisibles(clave)

        # Leer archivo de forma segura (con validaciones)
        contenido_bytes = await leer_archivo_seguro(file, max_size=SMALL_FILE_SIZE)

        # Decodificar contenido
        contenido = contenido_bytes.decode('utf-8')
        longitud_original = len(contenido)

        # Cifrar el contenido
        texto_cifrado = cifrar_vigenere(contenido, clave)

        return CifradoResponse(
            texto_cifrado=texto_cifrado,
            clave_usada=''.join(c.upper() for c in clave if c.isalpha()),
            texto_original_length=longitud_original
        )
    except Exception as e:
        raise manejar_error(e, "cifrar archivo") from e


@router.post(
    "/descifrar/file",
    response_model=DescifradoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Error en la validación"},
        413: {"model": ErrorResponse, "description": "Archivo demasiado grande"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Descifrar archivo de texto",
    description="""
    Descifra el contenido de un archivo .txt cifrado con Vigenère.

    **Características:**
    - Solo archivos .txt (máximo 10 MB)
    - Validación automática de caracteres invisibles en la clave
    - Detección de encoding UTF-8 inválido
    - No se guardan archivos en el servidor

    Para archivos grandes (10-500 MB), usa el endpoint `/descifrar/file/large`
    """
)
async def descifrar_archivo(
    file: UploadFile = File(..., description="Archivo .txt cifrado a descifrar"),
    clave: str = Form(..., description="Clave para el descifrado")
):
    """
    Descifra un archivo de texto con Vigenère (hasta 10 MB)

    Args:
        file: Archivo .txt cifrado subido
        clave: Clave para el descifrado

    Returns:
        DescifradoResponse con el contenido descifrado del archivo
    """
    try:
        # Validar la clave
        validar_clave_sin_caracteres_invisibles(clave)

        # Leer archivo de forma segura (con validaciones)
        contenido_bytes = await leer_archivo_seguro(file, max_size=SMALL_FILE_SIZE)

        # Decodificar y descifrar
        contenido = contenido_bytes.decode('utf-8')
        texto_descifrado = descifrar_vigenere(contenido, clave)

        return DescifradoResponse(
            texto_descifrado=texto_descifrado,
            clave_usada=''.join(c.upper() for c in clave if c.isalpha())
        )
    except Exception as e:
        raise manejar_error(e, "descifrar archivo") from e


# ============================================================================
# VALIDACIÓN Y UTILIDADES
# ============================================================================

@router.post(
    "/validar-clave",
    responses={
        200: {"description": "Validación exitosa"},
        400: {"model": ErrorResponse, "description": "Clave contiene caracteres problemáticos"}
    },
    summary="Validar clave antes de usar",
    description="""
    Valida una clave antes de cifrar/descifrar, detectando caracteres invisibles.

    **Detecta 5 tipos de caracteres invisibles:**
    - Zero-Width Space (U+200B)
    - Zero-Width Non-Joiner (U+200C)
    - Zero-Width Joiner (U+200D)
    - Zero-Width No-Break Space (U+FEFF)
    - Non-Breaking Space (U+00A0)

    **Útil para evitar errores causados por caracteres copiados de documentos.**
    """
)
async def validar_clave(clave: str = Form(...)):
    """
    Valida una clave detectando caracteres invisibles

    Args:
        clave: Clave a validar

    Returns:
        Información sobre la clave y advertencias si las hay
    """
    # Reutilizamos la función auxiliar
    validar_clave_sin_caracteres_invisibles(clave)

    # Si llegamos aquí, la clave es válida
    clave_limpia = ''.join(c.upper() for c in clave if c.isalpha())
    return {
        "valida": True,
        "clave_length": len(clave),
        "clave_limpia": clave_limpia,
        "mensaje": "Clave válida sin caracteres invisibles"
    }


@router.post(
    "/descifrar/file/large",
    responses={
        200: {"description": "Archivo descifrado exitosamente"},
        400: {"model": ErrorResponse, "description": "Error en la validación"},
        413: {"model": ErrorResponse, "description": "Archivo demasiado grande"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Descifrar archivo grande con validaciones avanzadas",
    description="""
    Descifra archivos grandes (10-500 MB) con validaciones de seguridad adicionales.

    **Características:**
    - Límite: 500 MB
    - Canary Check: valida los primeros 1KB antes de procesar todo
    - Magic Header configurable (default: MAGICV1\\n todo en mayúsculas)
    - Detección automática de caracteres invisibles en la clave

    **Canary Check:** Verifica que la clave sea correcta descifrando
    un pequeño fragmento antes de procesar todo el archivo, ahorrando tiempo
    y recursos si la clave es incorrecta.
    """
)
async def descifrar_archivo_grande(
    file: UploadFile = File(..., description="Archivo .txt cifrado grande"),
    clave: str = Form(..., description="Clave para el descifrado"),
    magic_header: str = Form(default="MAGICV1\n",
                             description="Header esperado al inicio del archivo descifrado (todo en mayúsculas)"),
    skip_canary: bool = Form(default=False, description="Omitir verificación de canary (no recomendado)")
):
    """
    Descifra archivo grande con validaciones de seguridad EN STREAMING

    Args:
        file: Archivo grande a descifrar
        clave: Clave de descifrado
        magic_header: Header esperado en el archivo descifrado
        skip_canary: Si True, omite el canary check

    Returns:
        Texto descifrado y metadatos
    """
    try:
        # 1. Validar la clave
        validar_clave_sin_caracteres_invisibles(clave)
        clave_formateada = validar_y_formatear_clave(clave)

        # 2. Validar que el archivo tenga nombre
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "El archivo debe tener un nombre"}
            )

        # Asignar nombre a variable local para type narrowing
        filename = file.filename
        logger.info("Descifrado de archivo grande iniciado - %s", filename)

        # 3. Validar extensión del archivo
        if not filename.endswith('.txt'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Solo se aceptan archivos .txt",
                    "archivo_recibido": filename
                }
            )

        # 4. CANARY CHECK - Leer solo los primeros bytes para validar
        canary_status = "skipped"
        canary_descifrado = ""  # Inicializar para type safety
        posicion_clave = 0

        if not skip_canary:
            logger.info("Realizando canary check...")
            # Leer solo el canary (1 KB)
            canary_bytes = await file.read(CANARY_SIZE)

            if len(canary_bytes) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": "El archivo está vacío"}
                )

            try:
                canary_text = canary_bytes.decode('utf-8')
            except UnicodeDecodeError as exc:
                logger.exception("Error al decodificar canary como UTF-8")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "El archivo no es texto válido UTF-8",
                        "sugerencia": "Este endpoint solo acepta archivos de texto"
                    }
                ) from exc

            # Descifrar el canary PRESERVANDO caracteres no alfabéticos (como \n)
            canary_descifrado_chars = []
            for char in canary_text:
                if char.isalpha():
                    # Descifrar solo letras
                    base = ord('A')
                    char_index = ord(char.upper()) - base
                    key_index = ord(clave_formateada[posicion_clave]) - base
                    descifrado_index = (char_index - key_index) % 26
                    canary_descifrado_chars.append(chr(base + descifrado_index))
                    posicion_clave = (posicion_clave + 1) % len(clave_formateada)
                else:
                    # Preservar caracteres no alfabéticos (espacios, \n, etc.)
                    canary_descifrado_chars.append(char)

            canary_descifrado = ''.join(canary_descifrado_chars)

            # Verificar magic header (normalizar line endings para compatibilidad Windows/Unix)
            # Normalizar ambos a \n para comparación
            canary_normalizado = canary_descifrado.replace('\r\n', '\n').replace('\r', '\n')
            magic_normalizado = magic_header.replace('\r\n', '\n').replace('\r', '\n')

            if not canary_normalizado.startswith(magic_normalizado):
                logger.warning("Canary check failed - clave incorrecta o formato inválido")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Canary check failed: clave incorrecta o formato inválido",
                        "esperado": f"Archivo debe comenzar con: {repr(magic_normalizado)}",
                        "recibido": f"{repr(canary_normalizado[:50])}...",
                        "sugerencia": "Verifica que la clave sea correcta y que el archivo esté cifrado correctamente"
                    }
                )

            canary_status = "passed"
            logger.info("Canary check passed")

        # 5. STREAMING: Procesar el resto del archivo por bloques SIN cargarlo completo en memoria
        BLOCK_SIZE = 1 * 1024 * 1024  # 1 MB por bloque
        texto_descifrado_completo = []
        bytes_procesados = CANARY_SIZE if not skip_canary else 0

        # Si no skip_canary, agregar el canary descifrado al resultado
        if not skip_canary:
            texto_descifrado_completo.append(canary_descifrado)

        # Si skipped canary, resetear la posición del archivo
        if skip_canary:
            await file.seek(0)
            posicion_clave = 0  # Resetear posición de clave también

        logger.info("Iniciando descifrado en streaming por bloques...")

        bloque_numero = 0
        while True:
            # Leer siguiente bloque EN STREAMING (sin cargar todo en memoria)
            bloque_bytes = await file.read(BLOCK_SIZE)

            if not bloque_bytes:
                # Fin del archivo
                break

            bytes_procesados += len(bloque_bytes)
            bloque_numero += 1

            # Validar que sea UTF-8 válido
            try:
                bloque_texto = bloque_bytes.decode('utf-8')
            except UnicodeDecodeError as exc:
                logger.exception("Error al decodificar bloque %d como UTF-8", bloque_numero)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": f"Error de encoding en bloque {bloque_numero}",
                        "sugerencia": "El archivo contiene caracteres no válidos UTF-8"
                    }
                ) from exc

            # Validar tamaño máximo (500 MB)
            if bytes_procesados > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": f"Archivo demasiado grande: {bytes_procesados / (1024*1024):.2f} MB",
                        "limite": f"{MAX_FILE_SIZE / (1024*1024):.0f} MB"
                    }
                )

            # Descifrar bloque manteniendo posición de clave y PRESERVANDO caracteres no alfabéticos
            texto_descifrado_bloque = []
            for char in bloque_texto:
                if char.isalpha():
                    # Descifrar letras
                    base = ord('A')
                    char_index = ord(char.upper()) - base
                    key_index = ord(clave_formateada[posicion_clave]) - base
                    descifrado_index = (char_index - key_index) % 26
                    texto_descifrado_bloque.append(chr(base + descifrado_index))
                    posicion_clave = (posicion_clave + 1) % len(clave_formateada)
                else:
                    # Preservar caracteres no alfabéticos (espacios, \n, etc.)
                    texto_descifrado_bloque.append(char)

            texto_descifrado_completo.append(''.join(texto_descifrado_bloque))

            # Log de progreso cada 10 bloques (cada 10 MB)
            if bloque_numero % 10 == 0:
                logger.info("Procesados %.2f MB en %d bloques", bytes_procesados / (1024*1024), bloque_numero)

        texto_descifrado = ''.join(texto_descifrado_completo)
        logger.info("Archivo grande descifrado exitosamente - %.2f MB en %d bloques",
                    bytes_procesados / (1024*1024), bloque_numero)

        return {
            "texto_descifrado": texto_descifrado,
            "clave_usada": clave_formateada,
            "tamanio_archivo_bytes": bytes_procesados,
            "tamanio_archivo_mb": round(bytes_procesados / (1024*1024), 2),
            "bloques_procesados": bloque_numero,
            "canary_check": canary_status,
            "mensaje": "Archivo descifrado exitosamente en streaming (memoria estable)"
        }

    except Exception as e:
        raise manejar_error(e, "descifrar archivo grande") from e
