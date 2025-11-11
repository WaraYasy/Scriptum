package es.luna.model;

/**
 * Response DTO para operación de cifrado AES.
 * Corresponde al schema CifradoAESResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class AesCifradoResponse {

    /** Texto cifrado en formato base64 */
    private String textoCifrado;

    /** Salt usado (necesario para descifrar) */
    private String salt;

    /** Tipo de AES usado */
    private String tipoAes;

    /** Tamaño original de los datos en bytes */
    private int tamanioOriginalBytes;

    /** Tamaño de los datos cifrados en bytes */
    private int tamanioCifradoBytes;

    /**
     * Constructor vacío.
     */
    public AesCifradoResponse() {
    }

    // Getters y Setters

    public String getTextoCifrado() {
        return textoCifrado;
    }

    public void setTextoCifrado(String textoCifrado) {
        this.textoCifrado = textoCifrado;
    }

    public String getSalt() {
        return salt;
    }

    public void setSalt(String salt) {
        this.salt = salt;
    }

    public String getTipoAes() {
        return tipoAes;
    }

    public void setTipoAes(String tipoAes) {
        this.tipoAes = tipoAes;
    }

    public int getTamanioOriginalBytes() {
        return tamanioOriginalBytes;
    }

    public void setTamanioOriginalBytes(int tamanioOriginalBytes) {
        this.tamanioOriginalBytes = tamanioOriginalBytes;
    }

    public int getTamanioCifradoBytes() {
        return tamanioCifradoBytes;
    }

    public void setTamanioCifradoBytes(int tamanioCifradoBytes) {
        this.tamanioCifradoBytes = tamanioCifradoBytes;
    }
}
