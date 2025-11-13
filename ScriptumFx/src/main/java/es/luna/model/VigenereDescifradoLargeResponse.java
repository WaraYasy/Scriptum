package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de descifrado Vigenère de archivos grandes.
 * Corresponde a la respuesta del endpoint /vigenere/descifrar/file/large.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-13
 */
public class VigenereDescifradoLargeResponse {

    /** Texto descifrado */
    @SerializedName("texto_descifrado")
    private String textoDescifrado;

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

    /** Estado del canary check */
    @SerializedName("canary_check")
    private String canaryCheck;

    /** Mensaje informativo */
    @SerializedName("mensaje")
    private String mensaje;

    /**
     * Constructor vacío.
     */
    public VigenereDescifradoLargeResponse() {
    }

    // Getters

    public String getTextoDescifrado() {
        return textoDescifrado;
    }

    public String getClaveUsada() {
        return claveUsada;
    }

    public String getMensaje() {
        return mensaje;
    }
}
