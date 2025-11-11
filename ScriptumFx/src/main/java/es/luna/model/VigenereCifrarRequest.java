package es.luna.model;

/**
 * Request DTO para cifrar texto con Vigenère.
 * Corresponde al schema CifrarTextoRequest de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class VigenereCifrarRequest {

    /** Texto a cifrar */
    private String texto;

    /** Clave para el cifrado */
    private String clave;

    /**
     * Constructor vacío.
     */
    public VigenereCifrarRequest() {
    }

    /**
     * Constructor con parámetros.
     *
     * @param texto el texto a cifrar
     * @param clave la clave para el cifrado
     */
    public VigenereCifrarRequest(String texto, String clave) {
        this.texto = texto;
        this.clave = clave;
    }

    // Getters y Setters

    public String getTexto() {
        return texto;
    }

    public void setTexto(String texto) {
        this.texto = texto;
    }

    public String getClave() {
        return clave;
    }

    public void setClave(String clave) {
        this.clave = clave;
    }
}
