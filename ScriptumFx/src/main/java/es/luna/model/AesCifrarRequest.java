package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Request DTO para cifrar texto con AES.
 * Corresponde al schema CifrarTextoAESRequest de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
@SuppressWarnings("FieldCanBeLocal")
public class AesCifrarRequest {

    /** Texto a cifrar */
    @SerializedName("texto")
    private String texto;

    /** Password para derivar la clave */
    @SerializedName("password")
    private String password;

    /** Tipo de cifrado AES (AES-128, AES-192, AES-256) */
    @SerializedName("tipo_aes")
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
}
