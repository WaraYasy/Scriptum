package es.luna.model;

import com.google.gson.annotations.SerializedName;

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
    @SerializedName("texto_cifrado")
    private String textoCifrado;

    /** Salt usado (necesario para descifrar) */
    @SerializedName("salt")
    private String salt;

    /** Tipo de AES usado */
    @SerializedName("tipo_aes")
    private String tipoAes;

    /**
     * Constructor vacío.
     */
    public AesCifradoResponse() {
    }

    // Getters

    public String getTextoCifrado() {
        return textoCifrado;
    }

    public String getSalt() {
        return salt;
    }

    public String getTipoAes() {
        return tipoAes;
    }
}
