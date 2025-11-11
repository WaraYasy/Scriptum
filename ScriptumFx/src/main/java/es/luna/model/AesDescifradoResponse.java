package es.luna.model;

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
    private String textoDescifrado;

    /** Tipo de AES usado */
    private String tipoAes;

    /** Tamaño del texto descifrado en bytes */
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

    public void setTextoDescifrado(String textoDescifrado) {
        this.textoDescifrado = textoDescifrado;
    }

    public String getTipoAes() {
        return tipoAes;
    }

    public void setTipoAes(String tipoAes) {
        this.tipoAes = tipoAes;
    }

    public int getTamanioBytes() {
        return tamanioBytes;
    }

    public void setTamanioBytes(int tamanioBytes) {
        this.tamanioBytes = tamanioBytes;
    }
}
