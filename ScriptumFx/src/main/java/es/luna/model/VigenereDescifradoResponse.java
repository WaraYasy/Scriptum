package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de descifrado Vigenère.
 * Corresponde al schema DescifradoResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class VigenereDescifradoResponse {

    /** Texto descifrado resultante */
    @SerializedName("texto_descifrado")
    private String textoDescifrado;

    /** Clave utilizada (formateada) */
    @SerializedName("clave_usada")
    @SuppressWarnings("FieldCanBeLocal")
    private String claveUsada;

    /**
     * Constructor vacío.
     */
    public VigenereDescifradoResponse() {
    }

    // Getters y Setters

    /**
     * Obtiene el texto descifrado resultante.
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
     * Obtiene la clave utilizada en el descifrado.
     *
     * @return la clave usada
     */
    public String getClaveUsada() {
        return claveUsada;
    }

    /**
     * Establece la clave utilizada.
     *
     * @param claveUsada la clave usada
     */
    public void setClaveUsada(String claveUsada) {
        this.claveUsada = claveUsada;
    }
}
