"""
ROUTER VIGENÈRE
Endpoints para cifrado y descifrado con algoritmo Vigenère
"""
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
    cifrar_vigenere_file,
    descifrar_vigenere_file
)

router = APIRouter(prefix="/vigenere", tags=["Vigenère"])


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
        texto_cifrado = cifrar_vigenere(request.texto, request.clave)

        return CifradoResponse(
            texto_cifrado=texto_cifrado,
            clave_usada=''.join(c.upper() for c in request.clave if c.isalpha()),
            texto_original_length=len(request.texto)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e), "detalle": "Verifica que el texto y clave sean válidos"}
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno al cifrar", "detalle": str(e)}
        ) from e


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
        texto_descifrado = descifrar_vigenere(request.texto_cifrado, request.clave)

        return DescifradoResponse(
            texto_descifrado=texto_descifrado,
            clave_usada=''.join(c.upper() for c in request.clave if c.isalpha())
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e), "detalle": "Verifica que el texto cifrado y clave sean válidos"}
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno al descifrar", "detalle": str(e)}
        ) from e


# ============================================================================
# ENDPOINTS DE ARCHIVOS
# ============================================================================

@router.post(
    "/cifrar/file",
    response_model=CifradoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Error en la validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Cifrar archivo de texto",
    description="""
    Cifra el contenido de un archivo .txt con Vigenère.

    **Nota:** Solo se aceptan archivos con extensión .txt
    
    El contenido del archivo se cifra y se devuelve como texto en la respuesta JSON.
    No se guardan archivos en el servidor.
    """
)
async def cifrar_archivo(
    file: UploadFile = File(..., description="Archivo .txt a cifrar"),
    clave: str = Form(..., description="Clave para el cifrado")
):
    """
    Cifra un archivo de texto con Vigenère

    Args:
        file: Archivo .txt subido
        clave: Clave para el cifrado

    Returns:
        CifradoResponse con el contenido cifrado del archivo
    """
    try:
        # Leer el contenido original para obtener la longitud
        contenido_bytes = await file.read()
        longitud_original = len(contenido_bytes.decode('utf-8'))
        
        # Resetear el puntero del archivo
        await file.seek(0)
        
        # Cifrar el archivo
        texto_cifrado = await cifrar_vigenere_file(file, clave)

        return CifradoResponse(
            texto_cifrado=texto_cifrado,
            clave_usada=''.join(c.upper() for c in clave if c.isalpha()),
            texto_original_length=longitud_original
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e), "detalle": "Verifica que el archivo sea .txt y la clave válida"}
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno al cifrar archivo", "detalle": str(e)}
        ) from e


@router.post(
    "/descifrar/file",
    response_model=DescifradoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Error en la validación"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Descifrar archivo de texto",
    description="""
    Descifra el contenido de un archivo .txt cifrado con Vigenère.

    **Nota:** Solo se aceptan archivos con extensión .txt
    
    El contenido del archivo se descifra y se devuelve como texto en la respuesta JSON.
    No se guardan archivos en el servidor.
    """
)
async def descifrar_archivo(
    file: UploadFile = File(..., description="Archivo .txt cifrado a descifrar"),
    clave: str = Form(..., description="Clave para el descifrado")
):
    """
    Descifra un archivo de texto con Vigenère

    Args:
        file: Archivo .txt cifrado subido
        clave: Clave para el descifrado

    Returns:
        DescifradoResponse con el contenido descifrado del archivo
    """
    try:
        texto_descifrado = await descifrar_vigenere_file(file, clave)

        return DescifradoResponse(
            texto_descifrado=texto_descifrado,
            clave_usada=''.join(c.upper() for c in clave if c.isalpha())
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e), "detalle": "Verifica que el archivo sea .txt y la clave válida"}
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno al descifrar archivo", "detalle": str(e)}
        ) from e