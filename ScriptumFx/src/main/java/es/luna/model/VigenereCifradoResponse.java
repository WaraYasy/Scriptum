package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de cifrado Vigenère.
 * Corresponde al schema CifradoResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class VigenereCifradoResponse {

    /** Texto cifrado resultante */
    @SerializedName("texto_cifrado")
    private String textoCifrado;

    /** Clave utilizada (formateada) */
    @SerializedName("clave_usada")
    private String claveUsada;

    /** Longitud del texto original */
    @SerializedName("texto_original_length")
    private int textoOriginalLength;

    /**
     * Constructor vacío.
     */
    public VigenereCifradoResponse() {
    }

    // Getters y Setters

    public String getTextoCifrado() {
        return textoCifrado;
    }

    public void setTextoCifrado(String textoCifrado) {
        this.textoCifrado = textoCifrado;
    }

    public String getClaveUsada() {
        return claveUsada;
    }

    public void setClaveUsada(String claveUsada) {
        this.claveUsada = claveUsada;
    }
}
