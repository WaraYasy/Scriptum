package es.luna.model;

/**
 * Request DTO para cifrar texto con AES.
 * Corresponde al schema CifrarTextoAESRequest de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class AesCifrarRequest {

    /** Texto a cifrar */
    private String texto;

    /** Password para derivar la clave */
    private String password;

    /** Salt en base64 (opcional) */
    private String salt;

    /** Tipo de cifrado AES (AES-128, AES-192, AES-256) */
    private String tipoAes;

    /**
     * Constructor vacío.
     */
    public AesCifrarRequest() {
        this.tipoAes = "AES-256"; // Valor por defecto
    }

    /**
     * Constructor con parámetros.
     *
     * @param texto el texto a cifrar
     * @param password el password para derivar la clave
     * @param tipoAes el tipo de AES a usar
     */
    public AesCifrarRequest(String texto, String password, String tipoAes) {
        this.texto = texto;
        this.password = password;
        this.tipoAes = tipoAes;
    }

    // Getters y Setters

    public String getTexto() {
        return texto;
    }

    public void setTexto(String texto) {
        this.texto = texto;
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
