package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de cifrado Vigenère de archivos grandes.
 * Corresponde a la respuesta del endpoint /vigenere/cifrar/file/large.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-13
 */
public class VigenereCifradoLargeResponse {

    /** Texto cifrado */
    @SerializedName("texto_cifrado")
    private String textoCifrado;

    /** Clave usada (formateada) */
    @SerializedName("clave_usada")
    private String claveUsada;

    /** Tamaño del archivo en bytes */
    @SerializedName("tamanio_archivo_bytes")
    private long tamanioArchivoBytes;

    /** Tamaño del archivo en MB */
    @SerializedName("tamanio_archivo_mb")
    private double tamanioArchivoMb;

    /** Número de bloques procesados */
    @SerializedName("bloques_procesados")
    private int bloquesProcesados;

    /** Indica si se agregó magic header */
    @SerializedName("magic_header_agregado")
    private boolean magicHeaderAgregado;

    /** Mensaje informativo */
    @SerializedName("mensaje")
    private String mensaje;

    /**
     * Constructor vacío.
     */
    public VigenereCifradoLargeResponse() {
    }

    // Getters

    public String getTextoCifrado() {
        return textoCifrado;
    }

    public String getClaveUsada() {
        return claveUsada;
    }

    public String getMensaje() {
        return mensaje;
    }
}
