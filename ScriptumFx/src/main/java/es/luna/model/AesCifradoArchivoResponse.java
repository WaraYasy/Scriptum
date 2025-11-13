package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de cifrado AES de archivos.
 * Corresponde al schema CifradoAESArchivoConMetadataResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-13
 */
public class AesCifradoArchivoResponse {

    /** Archivo cifrado en formato base64 */
    @SerializedName("archivo_cifrado")
    private String archivoCifrado;

    /** Salt usado (necesario para descifrar) */
    @SerializedName("salt")
    private String salt;

    /** Tipo de AES usado */
    @SerializedName("tipo_aes")
    private String tipoAes;

    /** Nombre original del archivo */
    @SerializedName("nombre_original")
    private String nombreOriginal;

    /** Tipo MIME del archivo */
    @SerializedName("mime_type")
    private String mimeType;

    /** Tamaño original del archivo en bytes */
    @SerializedName("tamanio_original_bytes")
    private int tamanioOriginalBytes;

    /** Tamaño del archivo cifrado en bytes */
    @SerializedName("tamanio_cifrado_bytes")
    private int tamanioCifradoBytes;

    /**
     * Constructor vacío.
     */
    public AesCifradoArchivoResponse() {
    }

    // Getters

    public String getArchivoCifrado() {
        return archivoCifrado;
    }

    public String getSalt() {
        return salt;
    }

    public String getTipoAes() {
        return tipoAes;
    }
}
