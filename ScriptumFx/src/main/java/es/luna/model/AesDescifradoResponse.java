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

    /**
     * Obtiene el texto descifrado original.
     *
     * @return el texto descifrado
     */
    public String getTextoDescifrado() {
        return textoDescifrado;
    }

    /**
     * Establece el texto descifrado.
     *
     * @param textoDescifrado el texto descifrado
     */
    public void setTextoDescifrado(String textoDescifrado) {
        this.textoDescifrado = textoDescifrado;
    }

    /**
     * Obtiene el tipo de AES usado en el descifrado.
     *
     * @return el tipo de AES
     */
    public String getTipoAes() {
        return tipoAes;
    }

    /**
     * Establece el tipo de AES usado.
     *
     * @param tipoAes el tipo de AES
     */
    public void setTipoAes(String tipoAes) {
        this.tipoAes = tipoAes;
    }

    /**
     * Obtiene el tamaño del texto descifrado en bytes.
     *
     * @return el tamaño en bytes
     */
    public int getTamanioBytes() {
        return tamanioBytes;
    }

    /**
     * Establece el tamaño del texto descifrado en bytes.
     *
     * @param tamanioBytes el tamaño en bytes
     */
    public void setTamanioBytes(int tamanioBytes) {
        this.tamanioBytes = tamanioBytes;
    }
}
