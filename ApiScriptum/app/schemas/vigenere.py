"""
SCHEMAS VIGENÈRE
Modelos Pydantic para requests y responses de los endpoints Vigenère
"""
from pydantic import BaseModel, Field


class CifrarTextoRequest(BaseModel):
    """Request para cifrar texto con Vigenère"""
    texto: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,  # Límite 1 MB para prevenir DoS
        description="Texto a cifrar (máximo 1 MB)"
    )
    clave: str = Field(
        ...,
        min_length=1,
        max_length=1000,  # Claves razonablemente largas
        description="Clave para el cifrado (solo letras, máximo 1000 caracteres)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto": "Hola Mundo",
                    "clave": "clave"
                }
            ]
        }
    }


class DescifrarTextoRequest(BaseModel):
    """Request para descifrar texto con Vigenère"""
    texto_cifrado: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,  # Límite 1 MB para prevenir DoS
        description="Texto cifrado a descifrar (máximo 1 MB)"
    )
    clave: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Clave para el descifrado (solo letras, máximo 1000 caracteres)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto_cifrado": "RIJVSUYVJN",
                    "clave": "KEY"
                }
            ]
        }
    }


class CifradoResponse(BaseModel):
    """Response para operación de cifrado exitosa"""
    #Definición de los campos del response, con descripciones
    texto_cifrado: str = Field(..., description="Texto cifrado resultante")
    clave_usada: str = Field(..., description="Clave utilizada (formateada)")
    texto_original_length: int = Field(
        ..., description="Longitud del texto original (sin formatear)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto_cifrado": "RIJVSUYVJN",
                    "clave_usada": "KEY",
                    "texto_original_length": 11
                }
            ]
        }
    }


class DescifradoResponse(BaseModel):
    """Response para operación de descifrado exitosa"""
    #Definición de los campos del response, con descripciones
    texto_descifrado: str = Field(..., description="Texto descifrado resultante")
    clave_usada: str = Field(..., description="Clave utilizada (formateada)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto_descifrado": "HOLAMUNDO",
                    "clave_usada": "CLAVE"
                }
            ]
        }
    }


class ArchivoResponse(BaseModel):
    """Response para operación con archivos"""
    #Definición de los campos del response, con descripciones
    mensaje: str = Field(..., description="Mensaje de confirmación")
    archivo_salida: str = Field(..., description="Nombre del archivo generado")
    ruta: str = Field(..., description="Ruta donde se guardó el archivo")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mensaje": "Archivo cifrado exitosamente",
                    "archivo_salida": "mensaje_cifrado.txt",
                    "ruta": "/app/data/mensaje_cifrado.txt"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Response para errores"""
    error: str = Field(..., description="Mensaje de error")
    detalle: str = Field(None, description="Detalles adicionales del error")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "La clave no puede estar vacía",
                    "detalle": "Proporciona una clave válida con al menos una letra"
                }
            ]
        }
    }
