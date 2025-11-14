package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para operación de descifrado AES de archivos.
 * Corresponde al schema DescifradoAESArchivoResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-13
 */
public class AesDescifradoArchivoResponse {

    /** Archivo descifrado en formato base64 */
    @SerializedName("archivo_descifrado_base64")
    private String archivoDescifradoBase64;

    /** Tipo de AES usado */
    @SerializedName("tipo_aes")
    private String tipoAes;

    /** Tamaño del archivo descifrado en bytes */
    @SerializedName("tamanio_bytes")
    private int tamanioBytes;

    /** Mensaje informativo */
    @SerializedName("mensaje")
    private String mensaje;

    /**
     * Constructor vacío.
     */
    public AesDescifradoArchivoResponse() {
    }

    // Getters

    /**
     * Obtiene el archivo descifrado en formato base64.
     *
     * @return el archivo descifrado en base64
     */
    public String getArchivoDescifradoBase64() {
        return archivoDescifradoBase64;
    }

    /**
     * Establece el archivo descifrado en base64.
     *
     * @param archivoDescifradoBase64 el archivo en base64
     */
    public void setArchivoDescifradoBase64(String archivoDescifradoBase64) {
        this.archivoDescifradoBase64 = archivoDescifradoBase64;
    }

    /**
     * Obtiene el tipo de AES usado en el descifrado.
     *
     * @return el tipo de AES
     */
    public String getTipoAes() {
        return tipoAes;
    }

    /**
     * Establece el tipo de AES usado.
     *
     * @param tipoAes el tipo de AES
     */
    public void setTipoAes(String tipoAes) {
        this.tipoAes = tipoAes;
    }

    /**
     * Obtiene el tamaño del archivo descifrado en bytes.
     *
     * @return el tamaño en bytes
     */
    public int getTamanioBytes() {
        return tamanioBytes;
    }

    /**
     * Establece el tamaño del archivo descifrado.
     *
     * @param tamanioBytes el tamaño en bytes
     */
    public void setTamanioBytes(int tamanioBytes) {
        this.tamanioBytes = tamanioBytes;
    }

    /**
     * Obtiene el mensaje informativo del descifrado.
     *
     * @return el mensaje
     */
    public String getMensaje() {
        return mensaje;
    }

    /**
     * Establece el mensaje informativo.
     *
     * @param mensaje el mensaje
     */
    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }
}
