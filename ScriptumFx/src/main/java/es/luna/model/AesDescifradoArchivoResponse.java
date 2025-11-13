package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de descifrado AES de archivos.
 * Corresponde al schema DescifradoAESArchivoResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-13
 */
public class AesDescifradoArchivoResponse {

    /** Archivo descifrado en formato base64 */
    @SerializedName("archivo_descifrado_base64")
    private String archivoDescifradoBase64;

    /** Tipo de AES usado */
    @SerializedName("tipo_aes")
    private String tipoAes;

    /** Tamaño del archivo descifrado en bytes */
    @SerializedName("tamanio_bytes")
    private int tamanioBytes;

    /** Mensaje informativo */
    @SerializedName("mensaje")
    private String mensaje;

    /**
     * Constructor vacío.
     */
    public AesDescifradoArchivoResponse() {
    }

    // Getters

    public String getArchivoDescifradoBase64() {
        return archivoDescifradoBase64;
    }
}
