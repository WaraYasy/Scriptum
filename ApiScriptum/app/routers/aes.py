"""
ROUTER AES
Endpoints para cifrado y descifrado con algoritmo AES
"""
import logging
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import Response

from app.schemas.aes import (
    CifrarTextoAESRequest,
    DescifrarTextoAESRequest,
    CifradoAESResponse,
    CifradoAESArchivoConMetadataResponse,
    CifradoAESArchivoPaqueteResponse,
    DescifradoAESTextoResponse,
    DescifradoAESArchivoResponse,
    InfoAESResponse,
    ErrorAESResponse,
    TipoAES
)
from app.services.aes import (
    cifrar_texto,
    descifrar_texto,
    cifrar_archivo,
    descifrar_archivo,
    crear_paquete_archivo_cifrado,
    extraer_paquete_archivo_cifrado,
    validar_password,
    SMALL_FILE_THRESHOLD
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/aes", tags=["AES"])


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Límite de tamaño unificado para texto y archivos
MAX_SIZE = 100 * 1024 * 1024  # 100 MB

# Extensiones de archivo soportadas
EXTENSIONES_SOPORTADAS = {
    '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.zip', '.rar', '.7z',
    '.csv', '.json', '.xml'
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def manejar_error(e: Exception, operacion: str):
    """
    Centraliza el manejo de errores y los convierte a HTTPException.

    Args:
        e: Excepción capturada
        operacion: Descripción de la operación

    Raises:
        HTTPException: Siempre lanza HTTPException apropiada según el tipo de error
    """
    if isinstance(e, HTTPException):
        raise e

    if isinstance(e, ValueError):
        logger.warning("Error de validación al %s", operacion)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        ) from e

    # Error inesperado
    logger.exception("Error interno al %s", operacion)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"error": f"Error interno al {operacion}"}
    ) from e


async def validar_y_leer_archivo(
    file: UploadFile,
    max_size: int = MAX_SIZE
) -> bytes:
    """
    Valida y lee un archivo de forma segura.

    Args:
        file: Archivo subido
        max_size: Tamaño máximo permitido

    Returns:
        Contenido del archivo en bytes

    Raises:
        HTTPException: Si el archivo es inválido o demasiado grande
    """
    logger.debug("Validando archivo")

    # Validar extensión
    extension = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''

    if extension not in EXTENSIONES_SOPORTADAS:
        logger.warning("Extensión no soportada: %s", extension)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Extensión de archivo no soportada: {extension}",
                "extensiones_soportadas": list(EXTENSIONES_SOPORTADAS),
                "archivo_recibido": file.filename
            }
        )

    # Leer archivo
    contenido = await file.read()
    file_size = len(contenido)

    # Validar tamaño
    if file_size > max_size:
        logger.warning("Archivo demasiado grande - Límite: %.0f MB",
                      max_size / (1024*1024))
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": f"Archivo demasiado grande: {file_size / (1024*1024):.2f} MB",
                "limite": f"{max_size / (1024*1024):.0f} MB"
            }
        )

    if file_size == 0:
        logger.warning("Archivo vacío recibido")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El archivo está vacío"}
        )

    logger.debug("Archivo validado correctamente")

    return contenido


# ============================================================================
# ENDPOINTS DE INFORMACIÓN
# ============================================================================

@router.get(
    "/info",
    response_model=InfoAESResponse,
    summary="Obtener información sobre tipos de AES",
    description="""
    Devuelve información sobre los tipos de AES disponibles y sus características.

    **Tipos disponibles:**
    - **AES-128**: Clave de 128 bits (16 bytes) - Rápido y seguro
    - **AES-192**: Clave de 192 bits (24 bytes) - Balance entre velocidad y seguridad
    - **AES-256**: Clave de 256 bits (32 bytes) - Máxima seguridad (recomendado)

    **Seguridad:**
    Todos los tipos son seguros para uso general. AES-256 es el más resistente
    a ataques de fuerza bruta, pero AES-128 es suficiente para la mayoría de casos.
    """
)
async def obtener_info_aes():
    """
    Obtiene información sobre los tipos de AES disponibles.
    """
    logger.info("Solicitada información sobre tipos de AES")
    return InfoAESResponse(
        tipos_disponibles=["AES-128", "AES-192", "AES-256"],
        recomendacion="AES-256",
        descripcion={
            "AES-128": "Clave de 128 bits (16 bytes) - Rápido y seguro para uso general",
            "AES-192": "Clave de 192 bits (24 bytes) - Balance entre velocidad y seguridad",
            "AES-256": "Clave de 256 bits (32 bytes) - Máxima seguridad (recomendado para datos sensibles)"
        }
    )


# ============================================================================
# ENDPOINTS DE CIFRADO - TEXTO
# ============================================================================

@router.post(
    "/cifrar/texto",
    response_model=CifradoAESResponse,
    responses={
        400: {"model": ErrorAESResponse, "description": "Error en la validación"},
        500: {"model": ErrorAESResponse, "description": "Error interno del servidor"}
    },
    summary="Cifrar texto con AES",
    description="""
    Cifra un texto utilizando AES-GCM (Galois/Counter Mode).

    **Características:**
    - **Confidencialidad**: Los datos están cifrados
    - **Autenticidad**: Detecta manipulaciones
    - **Integridad**: Verifica que no se alteró el contenido

    **¿Cómo funciona?**
    1. El password se convierte en una clave usando PBKDF2 (100,000 iteraciones)
    2. Se genera un salt aleatorio automáticamente (necesario para descifrar)
    3. Los datos se cifran con AES-GCM
    4. Se genera un tag de autenticación para verificar integridad

    **IMPORTANTE:**
    - Guarda el **salt** devuelto, lo necesitas para descifrar
    - Usa un password seguro (mínimo 8 caracteres)
    - El texto cifrado está en formato base64 (fácil de transmitir/guardar)
    - El salt se genera automáticamente por razones de seguridad
    """
)
async def cifrar_texto_endpoint(request: CifrarTextoAESRequest):
    """
    Cifra un texto con AES

    Args:
        request: Objeto con texto, password y tipo de AES

    Returns:
        CifradoAESResponse con el texto cifrado y salt generado automáticamente
    """
    logger.info("Iniciando cifrado de texto - Tipo: %s", request.tipo_aes)
    try:
        # Cifrar texto (salt se genera automáticamente)
        texto_cifrado, salt = cifrar_texto(
            request.texto,
            request.password,
            request.tipo_aes
        )

        # Calcular tamaños
        tamanio_original = len(request.texto.encode('utf-8'))
        tamanio_cifrado = len(texto_cifrado.encode('utf-8'))
        
        logger.info("Texto cifrado exitosamente - Original: %d bytes, Cifrado: %d bytes", 
                   tamanio_original, tamanio_cifrado)

        return CifradoAESResponse(
            texto_cifrado=texto_cifrado,
            salt=salt,
            tipo_aes=request.tipo_aes,
            tamanio_original_bytes=tamanio_original,
            tamanio_cifrado_bytes=tamanio_cifrado
        )
    except Exception as e:
        manejar_error(e, "cifrar texto")


@router.post(
    "/descifrar/texto",
    response_model=DescifradoAESTextoResponse,
    responses={
        400: {"model": ErrorAESResponse, "description": "Error en la validación o password incorrecto"},
        500: {"model": ErrorAESResponse, "description": "Error interno del servidor"}
    },
    summary="Descifrar texto con AES",
    description="""
    Descifra un texto previamente cifrado con AES.

    **Requisitos:**
    - Texto cifrado (obtenido al cifrar)
    - Password (el mismo usado para cifrar)
    - Salt (obtenido al cifrar, **imprescindible**)
    - Tipo de AES (el mismo usado para cifrar)

    **Seguridad:**
    Si el password es incorrecto o los datos fueron manipulados,
    la operación fallará con un error claro.
    """
)
async def descifrar_texto_endpoint(request: DescifrarTextoAESRequest):
    """
    Descifra un texto con AES

    Args:
        request: Objeto con texto cifrado, password, salt y tipo de AES

    Returns:
        DescifradoAESTextoResponse con el texto descifrado
    """
    logger.info("Iniciando descifrado de texto - Tipo: %s", request.tipo_aes)
    try:
        # Descifrar texto
        texto_descifrado = descifrar_texto(
            request.texto_cifrado,
            request.password,
            request.salt,
            request.tipo_aes
        )
        
        tamanio_bytes = len(texto_descifrado.encode('utf-8'))
        logger.info("Texto descifrado exitosamente - Tamaño: %d bytes", tamanio_bytes)

        return DescifradoAESTextoResponse(
            texto_descifrado=texto_descifrado,
            tipo_aes=request.tipo_aes,
            tamanio_bytes=tamanio_bytes
        )
    except Exception as e:
        manejar_error(e, "descifrar texto")


# ============================================================================
# ENDPOINTS DE CIFRADO - ARCHIVOS
# ============================================================================

@router.post(
    "/cifrar/file",
    response_model=CifradoAESArchivoConMetadataResponse,
    responses={
        400: {"model": ErrorAESResponse, "description": "Error en la validación"},
        413: {"model": ErrorAESResponse, "description": "Archivo demasiado grande"},
        500: {"model": ErrorAESResponse, "description": "Error interno del servidor"}
    },
    summary="Cifrar archivo con AES",
    description="""
    Cifra cualquier tipo de archivo con AES-GCM y devuelve metadata completa.

    **Archivos soportados:**
    - Documentos: .txt, .pdf, .doc, .docx, .xls, .xlsx
    - Imágenes: .jpg, .jpeg, .png, .gif, .bmp
    - Comprimidos: .zip, .rar, .7z
    - Datos: .csv, .json, .xml

    **Límites:**
    - Tamaño máximo: 100 MB (texto y archivos)

    **Metadata incluida:**
    - Nombre original del archivo
    - Tipo MIME del archivo
    - Tamaños original y cifrado

    **IMPORTANTE:**
    - Guarda el **salt** devuelto, lo necesitas para descifrar
    - Guarda también el **nombre_original** y **mime_type** para reconstruir el archivo
    - El archivo cifrado está en base64 (cópialo completo)
    - El salt se genera automáticamente por razones de seguridad
    """
)
async def cifrar_archivo_endpoint(
    file: UploadFile = File(..., description="Archivo a cifrar"),
    password: str = Form(..., min_length=8, description="Password para el cifrado"),
    tipo_aes: TipoAES = Form(default="AES-256", description="Tipo de AES")
):
    """
    Cifra un archivo con AES

    Args:
        file: Archivo a cifrar
        password: Password para derivar la clave
        tipo_aes: Tipo de AES a usar

    Returns:
        CifradoAESResponse con el archivo cifrado en base64 y salt
    """
    try:
        # Capturar metadata del archivo original
        nombre_original = file.filename
        mime_type = file.content_type or "application/octet-stream"

        # Leer archivo completo para determinar tamaño
        contenido_temp = await file.read()
        file_size = len(contenido_temp)

        # Resetear posición del archivo para procesar
        await file.seek(0)

        logger.info("Archivo: %s - Tamaño: %d bytes (%d MB)",
                   file.filename, file_size, file_size // (1024 * 1024))

        # Decidir método según tamaño
        if file_size < SMALL_FILE_THRESHOLD:
            # ARCHIVO PEQUEÑO: Procesar en memoria
            logger.info("Usando método en memoria (archivo < 10 MB)")
            contenido = await validar_y_leer_archivo(file)

            archivo_cifrado, salt_resultado = cifrar_archivo(
                contenido,
                password,
                tipo_aes
            )

            tamanio_original = len(contenido)
        else:
            # ARCHIVO GRANDE: Usar streaming
            logger.info("Usando streaming (archivo >= 10 MB)")
            from app.services.aes import cifrar_archivo_stream_async

            # Validar extensión antes de procesar
            extension = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if extension not in EXTENSIONES_SOPORTADAS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": f"Extensión no soportada: {extension}",
                        "extensiones_soportadas": list(EXTENSIONES_SOPORTADAS)
                    }
                )

            archivo_cifrado, salt_resultado = await cifrar_archivo_stream_async(
                file,
                password,
                tipo_aes
            )

            tamanio_original = file_size

        # Calcular tamaño cifrado
        tamanio_cifrado = len(archivo_cifrado.encode('utf-8'))

        logger.info("Archivo cifrado exitosamente: %s", file.filename)

        return CifradoAESArchivoConMetadataResponse(
            archivo_cifrado=archivo_cifrado,
            salt=salt_resultado,
            tipo_aes=tipo_aes,
            nombre_original=nombre_original,
            mime_type=mime_type,
            tamanio_original_bytes=tamanio_original,
            tamanio_cifrado_bytes=tamanio_cifrado
        )
    except Exception as e:
        manejar_error(e, "cifrar archivo")


@router.post(
    "/descifrar/file",
    response_model=DescifradoAESArchivoResponse,
    responses={
        400: {"model": ErrorAESResponse, "description": "Error en la validación o password incorrecto"},
        413: {"model": ErrorAESResponse, "description": "Archivo demasiado grande"},
        500: {"model": ErrorAESResponse, "description": "Error interno del servidor"}
    },
    summary="Descifrar archivo con AES",
    description="""
    Descifra un archivo previamente cifrado con AES.

    **Requisitos:**
    - Archivo cifrado (en formato base64, como archivo .txt)
    - Password (el mismo usado para cifrar)
    - Salt (obtenido al cifrar)
    - Tipo de AES (el mismo usado para cifrar)

    **Resultado:**
    El archivo descifrado se devuelve en base64. Para guardarlo:
    1. Copia el contenido de 'archivo_descifrado_base64'
    2. Decodifica de base64 a bytes
    3. Guarda los bytes en un archivo

    **Ejemplo en Python:**
    ```python
    import base64

    # Decodificar
    archivo_bytes = base64.b64decode(response['archivo_descifrado_base64'])

    # Guardar
    with open('archivo_descifrado.pdf', 'wb') as f:
        f.write(archivo_bytes)
    ```
    """
)
async def descifrar_archivo_endpoint(
    file: UploadFile = File(..., description="Archivo cifrado (base64 en .txt)"),
    password: str = Form(..., min_length=8, description="Password usado para cifrar"),
    salt: str = Form(..., description="Salt obtenido al cifrar"),
    tipo_aes: TipoAES = Form(default="AES-256", description="Tipo de AES usado")
):
    """
    Descifra un archivo con AES

    Args:
        file: Archivo cifrado en base64
        password: Password usado para cifrar
        salt: Salt usado en el cifrado
        tipo_aes: Tipo de AES usado

    Returns:
        DescifradoAESArchivoResponse con el archivo descifrado en base64
    """
    try:
        # Leer archivo cifrado
        contenido_cifrado = await file.read()

        # Decodificar de bytes a string
        try:
            archivo_cifrado_base64 = contenido_cifrado.decode('utf-8').strip()
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "El archivo cifrado debe ser texto UTF-8"}
            ) from exc

        logger.info("Descifrando archivo: %s con %s", file.filename, tipo_aes)

        # Descifrar archivo
        archivo_descifrado = descifrar_archivo(
            archivo_cifrado_base64,
            password,
            salt,
            tipo_aes
        )

        # Convertir a base64 para devolver
        archivo_descifrado_base64 = base64.b64encode(archivo_descifrado).decode('utf-8')

        logger.info("Archivo descifrado exitosamente: %s (%d bytes)", file.filename, len(archivo_descifrado))

        return DescifradoAESArchivoResponse(
            archivo_descifrado_base64=archivo_descifrado_base64,
            tipo_aes=tipo_aes,
            tamanio_bytes=len(archivo_descifrado),
            mensaje="Archivo descifrado exitosamente. Descarga el contenido desde 'archivo_descifrado_base64'"
        )
    except Exception as e:
        manejar_error(e, "descifrar archivo")


# ============================================================================
# ENDPOINTS DE ARCHIVOS CON PAQUETES (TODO EN UNO)
# ============================================================================

@router.post(
    "/cifrar/file/paquete",
    response_model=CifradoAESArchivoPaqueteResponse,
    responses={
        400: {"model": ErrorAESResponse, "description": "Error en la validación"},
        413: {"model": ErrorAESResponse, "description": "Archivo demasiado grande"},
        500: {"model": ErrorAESResponse, "description": "Error interno del servidor"}
    },
    summary="Cifrar archivo (Paquete único - RECOMENDADO)",
    description="""
    Cifra un archivo y devuelve UN SOLO PAQUETE con TODO incluido.

    **¿Qué incluye el paquete?**
    - Archivo cifrado
    - Salt para descifrar
    - Tipo de AES usado
    - Nombre original del archivo
    - MIME type del archivo

    **Ventajas:**
    - El usuario solo guarda UN campo (el paquete)
    - Imposible perder el salt o metadatos
    - Formato binario eficiente (~30% más compacto que JSON)
    - Descifrado automático con reconstrucción del archivo original

    **Uso:**
    ```javascript
    // Cifrar
    const response = await fetch('/aes/cifrar/file/paquete', {
        method: 'POST',
        body: formData  // file + password
    })
    const data = await response.json()

    // Guardar UN SOLO campo
    localStorage.setItem('archivo', data.paquete)

    // Descifrar más tarde
    const paquete = localStorage.getItem('archivo')
    // Enviar paquete + password al endpoint de descifrado
    // Recibes el archivo con nombre y tipo originales ✅
    ```

    **Formato del paquete:**
    - Header sin cifrar con metadatos (nombre, MIME, salt, tipo AES)
    - Body cifrado con el contenido del archivo
    - Todo empaquetado en base64

    **Límites:**
    - Tamaño máximo: 100 MB
    """
)
async def cifrar_archivo_paquete_endpoint(
    file: UploadFile = File(..., description="Archivo a cifrar"),
    password: str = Form(..., min_length=8, description="Password para el cifrado"),
    tipo_aes: TipoAES = Form(default="AES-256", description="Tipo de AES")
):
    """
    Cifra un archivo y devuelve un paquete único con TODO incluido.

    El paquete contiene:
    - Archivo cifrado
    - Salt (generado automáticamente)
    - Tipo de AES
    - Nombre original
    - MIME type

    El usuario solo necesita guardar el campo 'paquete'.
    """
    try:
        # Leer archivo completo para determinar tamaño
        contenido_temp = await file.read()
        file_size = len(contenido_temp)

        # Resetear posición del archivo para procesar
        await file.seek(0)

        logger.info("Cifrado con paquete - Archivo: %s, Tamaño: %d bytes (%d MB)",
                   file.filename, file_size, file_size // (1024 * 1024))

        # Obtener MIME type
        mime_type = file.content_type or "application/octet-stream"

        # Decidir método según tamaño
        if file_size < SMALL_FILE_THRESHOLD:
            # ARCHIVO PEQUEÑO: Procesar en memoria
            logger.info("Usando método en memoria (archivo < 10 MB)")
            contenido = await validar_y_leer_archivo(file)

            archivo_cifrado, salt_resultado = cifrar_archivo(
                contenido,
                password,
                tipo_aes
            )

            tamanio_original = len(contenido)
        else:
            # ARCHIVO GRANDE: Usar streaming
            logger.info("Usando streaming (archivo >= 10 MB)")
            from app.services.aes import cifrar_archivo_stream_async

            # Validar extensión antes de procesar
            extension = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if extension not in EXTENSIONES_SOPORTADAS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": f"Extensión no soportada: {extension}",
                        "extensiones_soportadas": list(EXTENSIONES_SOPORTADAS)
                    }
                )

            archivo_cifrado, salt_resultado = await cifrar_archivo_stream_async(
                file,
                password,
                tipo_aes
            )

            tamanio_original = file_size

        # Crear paquete único con metadatos
        paquete = crear_paquete_archivo_cifrado(
            contenido_cifrado=archivo_cifrado,
            salt=salt_resultado,
            tipo_aes=tipo_aes,
            nombre_archivo=file.filename,
            mime_type=mime_type
        )

        # Calcular tamaño del paquete (antes de base64)

        tamanio_paquete = len(base64.b64decode(paquete))

        logger.info("Paquete creado exitosamente: %s", file.filename)

        return CifradoAESArchivoPaqueteResponse(
            paquete=paquete,
            tamanio_paquete_bytes=tamanio_paquete,
            info={
                "nombre_original": file.filename,
                "mime_type": mime_type,
                "tamanio_original_bytes": tamanio_original,
                "tipo_aes": tipo_aes
            }
        )
    except Exception as e:
        manejar_error(e, "cifrar archivo con paquete")


@router.post(
    "/descifrar/file/paquete",
    responses={
        200: {"description": "Archivo descifrado", "content": {"application/octet-stream": {}}},
        400: {"model": ErrorAESResponse, "description": "Error en validación o password incorrecto"},
        500: {"model": ErrorAESResponse, "description": "Error interno del servidor"}
    },
    summary="Descifrar archivo desde paquete único",
    description="""
    Descifra un archivo desde un paquete único y devuelve el archivo original.

    **¿Qué necesitas?**
    - El paquete (obtenido al cifrar)
    - El password

    **¿Qué obtienes?**
    - Archivo descifrado con nombre original
    - MIME type correcto
    - Listo para descargar

    **Ventajas:**
    - No necesitas recordar el salt ni metadatos
    - Todo está en el paquete
    - El archivo se reconstruye automáticamente con su nombre y tipo originales

    **Uso:**
    ```javascript
    const formData = new FormData()
    formData.append('paquete', paquete)  // Paquete guardado
    formData.append('password', 'pass123')

    const response = await fetch('/aes/descifrar/file/paquete', {
        method: 'POST',
        body: formData
    })

    // Descargar archivo
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)

    // El nombre viene en Content-Disposition header
    const filename = response.headers.get('Content-Disposition')
        .split('filename=')[1].replace(/"/g, '')

    const a = document.createElement('a')
    a.href = url
    a.download = filename  // Nombre original restaurado ✅
    a.click()
    ```
    """
)
async def descifrar_archivo_paquete_endpoint(
    paquete: str = Form(..., description="Paquete cifrado (obtenido al cifrar)"),
    password: str = Form(..., min_length=8, description="Password usado para cifrar")
):
    """
    Descifra un archivo desde un paquete único.

    Extrae metadatos del paquete, descifra el archivo y lo devuelve
    con su nombre y tipo MIME originales.
    """
    try:
        logger.info("Descifrando archivo desde paquete")

        # Extraer datos del paquete
        datos = extraer_paquete_archivo_cifrado(paquete)

        contenido_cifrado = datos["contenido_cifrado"]
        salt = datos["salt"]
        tipo_aes = datos["tipo_aes"]
        metadata = datos["metadata"]

        logger.info("Paquete extraído: archivo=%s, tipo=%s, aes=%s",
                   metadata["nombre_original"], metadata["mime_type"], tipo_aes)

        # Descifrar el archivo
        archivo_descifrado = descifrar_archivo(
            contenido_cifrado,
            password,
            salt,
            tipo_aes
        )

        logger.info("Archivo descifrado exitosamente: %s (%d bytes)",
                   metadata["nombre_original"], len(archivo_descifrado))

        # Devolver como archivo con metadatos originales
        return Response(
            content=archivo_descifrado,
            media_type=metadata["mime_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{metadata["nombre_original"]}"',
                "X-Original-Filename": metadata["nombre_original"],
                "X-Original-MimeType": metadata["mime_type"]
            }
        )

    except ValueError as e:
        logger.warning("Error al extraer/descifrar paquete")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"Paquete inválido o corrupto: {str(e)}"}
        ) from e
    except Exception as e:
        manejar_error(e, "descifrar archivo desde paquete")


# ============================================================================
# ENDPOINTS AVANZADOS
# ============================================================================

@router.post(
    "/validar-password",
    responses={
        200: {"description": "Password válido"},
        400: {"model": ErrorAESResponse, "description": "Password no cumple requisitos"}
    },
    summary="Validar password antes de usar",
    description="""
    Valida que un password cumpla con los requisitos mínimos de seguridad.

    **Requisitos:**
    - Longitud mínima: 8 caracteres
    - Longitud máxima: 1000 caracteres

    **Útil para validar antes de cifrar y evitar errores.**
    """
)
async def validar_password_endpoint(password: str = Form(...)):
    """
    Valida un password

    Args:
        password: Password a validar

    Returns:
        Información sobre la validez del password
    """
    logger.info("Validando password")
    try:
        validar_password(password)

        logger.info("Password validado correctamente")

        return {
            "valido": True,
            "longitud": len(password),
            "mensaje": "Password válido y cumple con los requisitos de seguridad"
        }
    except ValueError as e:
        logger.warning("Password inválido")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        ) from e
