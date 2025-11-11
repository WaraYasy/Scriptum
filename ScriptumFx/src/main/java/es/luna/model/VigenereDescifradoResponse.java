package es.luna.model;

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
    private String textoDescifrado;

    /** Clave utilizada (formateada) */
    private String claveUsada;

    /**
     * Constructor vacío.
     */
    public VigenereDescifradoResponse() {
    }

    // Getters y Setters

    public String getTextoDescifrado() {
        return textoDescifrado;
    }

    public void setTextoDescifrado(String textoDescifrado) {
        this.textoDescifrado = textoDescifrado;
    }

    public String getClaveUsada() {
        return claveUsada;
    }

    public void setClaveUsada(String claveUsada) {
        this.claveUsada = claveUsada;
    }
}
