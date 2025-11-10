"""
ROUTER VIGENÈRE
Endpoints para cifrado y descifrado con algoritmo Vigenère
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
import logging

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

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vigenere", tags=["Vigenère"])

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
    # Validar extensión
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Solo se aceptan archivos .txt",
                "archivo_recibido": file.filename
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
        logger.warning(f"Error de validación al {operacion}: {str(e)}")
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )

    # Error inesperado - solo logear detalles, no exponerlos
    logger.error(f"Error interno al {operacion}: {str(e)}", exc_info=True)
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
        raise manejar_error(e, "cifrar texto")


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
        raise manejar_error(e, "descifrar texto")


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
        raise manejar_error(e, "cifrar archivo")


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
        raise manejar_error(e, "descifrar archivo")


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
    try:
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
    except HTTPException:
        # Re-lanzar la excepción de validación
        raise


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
    - Magic Header configurable (default: MAGICv1\\n)
    - Detección automática de caracteres invisibles en la clave

    **Canary Check:** Verifica que la clave sea correcta descifrando
    un pequeño fragmento antes de procesar todo el archivo, ahorrando tiempo
    y recursos si la clave es incorrecta.
    """
)
async def descifrar_archivo_grande(
    file: UploadFile = File(..., description="Archivo .txt cifrado grande"),
    clave: str = Form(..., description="Clave para el descifrado"),
    magic_header: str = Form(default="MAGICv1\n", description="Header esperado al inicio del archivo descifrado"),
    skip_canary: bool = Form(default=False, description="Omitir verificación de canary (no recomendado)")
):
    """
    Descifra archivo grande con validaciones de seguridad

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
        logger.info(f"Descifrado de archivo grande iniciado - Tamaño: {file.filename}")

        # 2. Leer y validar archivo (usa MAX_FILE_SIZE por defecto: 500 MB)
        contenido_bytes = await leer_archivo_seguro(file, max_size=MAX_FILE_SIZE)
        file_size = len(contenido_bytes)

        # 3. CANARY CHECK - Verificar primeros bytes
        canary_status = "skipped"
        if not skip_canary:
            canary_bytes = contenido_bytes[:CANARY_SIZE]

            try:
                canary_text = canary_bytes.decode('utf-8')
                canary_descifrado = descifrar_vigenere(canary_text, clave)

                if not canary_descifrado.startswith(magic_header):
                    logger.warning("Canary check failed - clave incorrecta o formato inválido")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Canary check failed: clave incorrecta o formato inválido",
                            "esperado": f"Archivo debe comenzar con: {repr(magic_header)}",
                            "recibido": f"{repr(canary_descifrado[:50])}...",
                            "sugerencia": "Verifica que la clave sea correcta y que el archivo esté cifrado correctamente"
                        }
                    )
                canary_status = "passed"
                logger.info("Canary check passed")
            except UnicodeDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "El archivo no es texto válido UTF-8",
                        "sugerencia": "Este endpoint solo acepta archivos de texto"
                    }
                ) from exc

        # 4. Descifrar archivo completo
        contenido = contenido_bytes.decode('utf-8')
        texto_descifrado = descifrar_vigenere(contenido, clave)

        logger.info(f"Archivo grande descifrado exitosamente - {file_size / (1024*1024):.2f} MB")

        return {
            "texto_descifrado": texto_descifrado,
            "clave_usada": ''.join(c.upper() for c in clave if c.isalpha()),
            "tamanio_archivo_bytes": file_size,
            "tamanio_archivo_mb": round(file_size / (1024*1024), 2),
            "canary_check": canary_status,
            "mensaje": "Archivo descifrado exitosamente"
        }

    except Exception as e:
        raise manejar_error(e, "descifrar archivo grande")