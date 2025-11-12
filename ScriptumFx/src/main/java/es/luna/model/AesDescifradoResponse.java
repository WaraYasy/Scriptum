package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de descifrado AES.
 * Corresponde al schema DescifradoAESTextoResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class AesDescifradoResponse {

    /** Texto descifrado original */
    @SerializedName("texto_descifrado")
    private String textoDescifrado;

    /** Tipo de AES usado */
    @SerializedName("tipo_aes")
    private String tipoAes;

    /** Tamaño del texto descifrado en bytes */
    @SerializedName("tamanio_bytes")
    private int tamanioBytes;

    /**
     * Constructor vacío.
     */
    public AesDescifradoResponse() {
    }

    // Getters y Setters

    public String getTextoDescifrado() {
        return textoDescifrado;
    }
}
