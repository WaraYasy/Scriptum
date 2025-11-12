"""
SCHEMAS AES
Modelos Pydantic para requests y responses de los endpoints AES
Autor: Wara
"""
import logging
from typing import Literal
from pydantic import BaseModel, Field

# ============================================================================
# LOGGING
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================================================
# TIPOS Y CONSTANTES
# ============================================================================

TipoAES = Literal["AES-128", "AES-192", "AES-256"]


# ============================================================================
# REQUEST SCHEMAS - TEXTO
# ============================================================================

class CifrarTextoAESRequest(BaseModel):
    """Request para cifrar texto con AES"""
    texto: str = Field(
        ...,
        min_length=1,
        max_length=100_000_000,  # Límite unificado 100 MB
        description="Texto a cifrar"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=1000,
        description="Password para derivar la clave (mínimo 8 caracteres)"
    )
    tipo_aes: TipoAES = Field(
        default="AES-256",
        description="Tipo de cifrado AES: AES-128, AES-192 o AES-256"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto": "Este es un mensaje secreto",
                    "password": "mi_password_seguro_123",
                    "tipo_aes": "AES-256"
                }
            ]
        }
    }


class DescifrarTextoAESRequest(BaseModel):
    """Request para descifrar texto con AES"""
    texto_cifrado: str = Field(
        ...,
        min_length=1,
        description="Texto cifrado en formato base64"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=1000,
        description="Password usado para cifrar"
    )
    salt: str = Field(
        ...,
        min_length=1,
        description="Salt en formato base64 (obtenido al cifrar)"
    )
    tipo_aes: TipoAES = Field(
        default="AES-256",
        description="Tipo de cifrado AES usado"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto_cifrado": "VGhpcyBpcyBhbiBlbmNyeXB0ZWQgdGV4dA==",
                    "password": "mi_password_seguro_123",
                    "salt": "cmFuZG9tc2FsdDEyMzQ1Ng==",
                    "tipo_aes": "AES-256"
                }
            ]
        }
    }


# ============================================================================
# REQUEST SCHEMAS - ARCHIVOS
# ============================================================================

class DescifrarArchivoAESRequest(BaseModel):
    """Request para descifrar archivo con AES (usado con Form)"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=1000,
        description="Password usado para cifrar"
    )
    salt: str = Field(
        ...,
        min_length=1,
        description="Salt en formato base64"
    )
    tipo_aes: TipoAES = Field(
        default="AES-256",
        description="Tipo de cifrado AES usado"
    )


class DescifrarArchivoPaqueteAESRequest(BaseModel):
    """Request para descifrar archivo usando paquete único"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=1000,
        description="Password usado para cifrar el archivo"
    )


# ============================================================================
# RESPONSE SCHEMAS - CIFRADO
# ============================================================================

class CifradoAESResponse(BaseModel):
    """Response para operación de cifrado exitosa"""
    texto_cifrado: str = Field(
        ...,
        description="Texto/archivo cifrado en formato base64"
    )
    salt: str = Field(
        ...,
        description="Salt usado (necesario para descifrar, ¡guárdalo!)"
    )
    tipo_aes: str = Field(
        ...,
        description="Tipo de AES usado (AES-128, AES-192, AES-256)"
    )
    tamanio_original_bytes: int = Field(
        ...,
        description="Tamaño original de los datos en bytes"
    )
    tamanio_cifrado_bytes: int = Field(
        ...,
        description="Tamaño de los datos cifrados (base64) en bytes"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto_cifrado": "VGhpcyBpcyBhbiBlbmNyeXB0ZWQgdGV4dCB3aXRoIEFFUy0yNTY=",
                    "salt": "cmFuZG9tc2FsdDEyMzQ1Ng==",
                    "tipo_aes": "AES-256",
                    "tamanio_original_bytes": 1024,
                    "tamanio_cifrado_bytes": 1152
                }
            ]
        }
    }


class CifradoAESArchivoConMetadataResponse(BaseModel):
    """Response para cifrado de archivo con metadata completa"""
    archivo_cifrado: str = Field(
        ...,
        description="Archivo cifrado en formato base64"
    )
    salt: str = Field(
        ...,
        description="Salt usado (necesario para descifrar, ¡guárdalo!)"
    )
    tipo_aes: str = Field(
        ...,
        description="Tipo de AES usado (AES-128, AES-192, AES-256)"
    )
    nombre_original: str = Field(
        ...,
        description="Nombre original del archivo"
    )
    mime_type: str = Field(
        ...,
        description="Tipo MIME del archivo original"
    )
    tamanio_original_bytes: int = Field(
        ...,
        description="Tamaño original del archivo en bytes"
    )
    tamanio_cifrado_bytes: int = Field(
        ...,
        description="Tamaño del archivo cifrado (base64) en bytes"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "archivo_cifrado": "VGhpcyBpcyBhbiBlbmNyeXB0ZWQgZmlsZSB3aXRoIEFFUy0yNTY=",
                    "salt": "cmFuZG9tc2FsdDEyMzQ1Ng==",
                    "tipo_aes": "AES-256",
                    "nombre_original": "documento.pdf",
                    "mime_type": "application/pdf",
                    "tamanio_original_bytes": 245678,
                    "tamanio_cifrado_bytes": 327570
                }
            ]
        }
    }


class CifradoAESArchivoPaqueteResponse(BaseModel):
    """Response para cifrado de archivo con paquete único (TODO EN UNO)"""
    paquete: str = Field(
        ...,
        description="""
        Paquete único en base64 que contiene TODO:
        - Archivo cifrado
        - Salt para descifrar
        - Tipo de AES usado
        - Nombre original del archivo
        - MIME type del archivo

        El usuario solo necesita guardar este campo.
        Para descifrar, envía el paquete + password al endpoint de descifrado.
        """
    )
    tamanio_paquete_bytes: int = Field(
        ...,
        description="Tamaño del paquete completo en bytes (antes de base64)"
    )
    info: dict = Field(
        ...,
        description="Información sobre el archivo (nombre, tipo, tamaño original)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "paquete": "U0NSSVBUVU0BAwAQcmFuZG9tc2FsdDEyMzQ1NgAIZm90by5qcGcACmltYWdlL2pwZWdVMkZzZEdWa1gxOTRZbU14TWpNNE56UkZibU55...",
                    "tamanio_paquete_bytes": 256078,
                    "info": {
                        "nombre_original": "foto.jpg",
                        "mime_type": "image/jpeg",
                        "tamanio_original_bytes": 245678,
                        "tipo_aes": "AES-256"
                    }
                }
            ]
        }
    }


# ============================================================================
# RESPONSE SCHEMAS - DESCIFRADO
# ============================================================================

class DescifradoAESTextoResponse(BaseModel):
    """Response para operación de descifrado de texto"""
    texto_descifrado: str = Field(
        ...,
        description="Texto descifrado original"
    )
    tipo_aes: str = Field(
        ...,
        description="Tipo de AES usado"
    )
    tamanio_bytes: int = Field(
        ...,
        description="Tamaño del texto descifrado en bytes"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto_descifrado": "Este es un mensaje secreto",
                    "tipo_aes": "AES-256",
                    "tamanio_bytes": 27
                }
            ]
        }
    }


class DescifradoAESArchivoResponse(BaseModel):
    """Response para operación de descifrado de archivo"""
    archivo_descifrado_base64: str = Field(
        ...,
        description="Contenido del archivo descifrado en base64"
    )
    tipo_aes: str = Field(
        ...,
        description="Tipo de AES usado"
    )
    tamanio_bytes: int = Field(
        ...,
        description="Tamaño del archivo descifrado en bytes"
    )
    mensaje: str = Field(
        ...,
        description="Mensaje informativo"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "archivo_descifrado_base64": "UEsDBAoAAAAAAA...",
                    "tipo_aes": "AES-256",
                    "tamanio_bytes": 2048,
                    "mensaje": "Archivo descifrado exitosamente. Descarga el contenido desde 'archivo_descifrado_base64'"
                }
            ]
        }
    }


# ============================================================================
# RESPONSE SCHEMAS - INFORMACIÓN
# ============================================================================

class InfoAESResponse(BaseModel):
    """Response con información sobre los tipos de AES disponibles"""
    tipos_disponibles: list[str] = Field(
        ...,
        description="Lista de tipos de AES disponibles"
    )
    recomendacion: str = Field(
        ...,
        description="Tipo recomendado para uso general"
    )
    descripcion: dict = Field(
        ...,
        description="Descripción de cada tipo de AES"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tipos_disponibles": ["AES-128", "AES-192", "AES-256"],
                    "recomendacion": "AES-256",
                    "descripcion": {
                        "AES-128": "Clave de 128 bits (16 bytes) - Rápido y seguro",
                        "AES-192": "Clave de 192 bits (24 bytes) - Balance entre velocidad y seguridad",
                        "AES-256": "Clave de 256 bits (32 bytes) - Máxima seguridad (recomendado)"
                    }
                }
            ]
        }
    }


# ============================================================================
# ERROR RESPONSE
# ============================================================================

class ErrorAESResponse(BaseModel):
    """Response para errores"""
    error: str = Field(
        ...,
        description="Mensaje de error"
    )
    detalle: str | None = Field(
        None,
        description="Detalles adicionales del error"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Error al descifrar: clave incorrecta o datos manipulados",
                    "detalle": "El tag de autenticación no coincide"
                }
            ]
        }
    }
