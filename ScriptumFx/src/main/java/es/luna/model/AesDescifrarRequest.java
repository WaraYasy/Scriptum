package es.luna.model;

/**
 * Request DTO para descifrar texto con AES.
 * Corresponde al schema DescifrarTextoAESRequest de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class AesDescifrarRequest {

    /** Texto cifrado en formato base64 */
    private String textoCifrado;

    /** Password usado para cifrar */
    private String password;

    /** Salt en formato base64 */
    private String salt;

    /** Tipo de cifrado AES usado */
    private String tipoAes;

    /**
     * Constructor vacío.
     */
    public AesDescifrarRequest() {
        this.tipoAes = "AES-256"; // Valor por defecto
    }

    /**
     * Constructor con parámetros.
     *
     * @param textoCifrado el texto cifrado a descifrar
     * @param password el password usado para cifrar
     * @param salt el salt usado al cifrar
     * @param tipoAes el tipo de AES usado
     */
    public AesDescifrarRequest(String textoCifrado, String password, String salt, String tipoAes) {
        this.textoCifrado = textoCifrado;
        this.password = password;
        this.salt = salt;
        this.tipoAes = tipoAes;
    }

    // Getters y Setters

    public String getTextoCifrado() {
        return textoCifrado;
    }

    public void setTextoCifrado(String textoCifrado) {
        this.textoCifrado = textoCifrado;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
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
}
