package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Request DTO para descifrar texto con Vigenère.
 * Corresponde al schema DescifrarTextoRequest de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class VigenereDescifrarRequest {

    /** Texto cifrado a descifrar */
    @SerializedName("texto_cifrado")
    private String textoCifrado;

    /** Clave para el descifrado */
    @SerializedName("clave")
    private String clave;

    /**
     * Constructor vacío.
     */
    public VigenereDescifrarRequest() {
    }

    /**
     * Constructor con parámetros.
     *
     * @param textoCifrado el texto cifrado a descifrar
     * @param clave la clave para el descifrado
     */
    public VigenereDescifrarRequest(String textoCifrado, String clave) {
        this.textoCifrado = textoCifrado;
        this.clave = clave;
    }

    // Getters y Setters

    public String getTextoCifrado() {
        return textoCifrado;
    }

    public void setTextoCifrado(String textoCifrado) {
        this.textoCifrado = textoCifrado;
    }

    public String getClave() {
        return clave;
    }

    public void setClave(String clave) {
        this.clave = clave;
    }
}
