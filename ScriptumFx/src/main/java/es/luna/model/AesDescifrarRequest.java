package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Request DTO para descifrar texto con AES.
 * Corresponde al schema DescifrarTextoAESRequest de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */

@SuppressWarnings("FieldCanBeLocal")
public class AesDescifrarRequest {

    /** Texto cifrado en formato base64 */
    @SerializedName("texto_cifrado")
    private String textoCifrado;

    /** Password usado para cifrar */
    @SerializedName("password")
    private String password;

    /** Salt en formato base64 */
    @SerializedName("salt")
    private String salt;

    /** Tipo de cifrado AES usado */
    @SerializedName("tipo_aes")
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

    /**
     * Obtiene el texto cifrado a descifrar.
     *
     * @return el texto cifrado en formato base64
     */
    public String getTextoCifrado() {
        return textoCifrado;
    }

    /**
     * Establece el texto cifrado a descifrar.
     *
     * @param textoCifrado el texto cifrado
     */
    public void setTextoCifrado(String textoCifrado) {
        this.textoCifrado = textoCifrado;
    }

    /**
     * Obtiene el password usado para cifrar.
     *
     * @return el password
     */
    public String getPassword() {
        return password;
    }

    /**
     * Establece el password usado para cifrar.
     *
     * @param password el password
     */
    public void setPassword(String password) {
        this.password = password;
    }

    /**
     * Obtiene el salt usado al cifrar.
     *
     * @return el salt en formato base64
     */
    public String getSalt() {
        return salt;
    }

    /**
     * Establece el salt usado al cifrar.
     *
     * @param salt el salt
     */
    public void setSalt(String salt) {
        this.salt = salt;
    }

    /**
     * Obtiene el tipo de cifrado AES usado.
     *
     * @return el tipo de AES
     */
    public String getTipoAes() {
        return tipoAes;
    }

    /**
     * Establece el tipo de cifrado AES usado.
     *
     * @param tipoAes el tipo de AES
     */
    public void setTipoAes(String tipoAes) {
        this.tipoAes = tipoAes;
    }
}
