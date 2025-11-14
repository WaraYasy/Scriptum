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

    /**
     * Obtiene el texto descifrado resultante.
     *
     * @return el texto descifrado
     */
    public String getTextoDescifrado() {
        return textoDescifrado;
    }

    /**
     * Establece el texto descifrado.
     *
     * @param textoDescifrado el texto descifrado
     */
    public void setTextoDescifrado(String textoDescifrado) {
        this.textoDescifrado = textoDescifrado;
    }

    /**
     * Obtiene la clave usada (formateada) en el descifrado.
     *
     * @return la clave usada
     */
    public String getClaveUsada() {
        return claveUsada;
    }

    /**
     * Establece la clave usada.
     *
     * @param claveUsada la clave usada
     */
    public void setClaveUsada(String claveUsada) {
        this.claveUsada = claveUsada;
    }

    /**
     * Obtiene el tamaño del archivo en bytes.
     *
     * @return el tamaño en bytes
     */
    public long getTamanioArchivoBytes() {
        return tamanioArchivoBytes;
    }

    /**
     * Establece el tamaño del archivo en bytes.
     *
     * @param tamanioArchivoBytes el tamaño en bytes
     */
    public void setTamanioArchivoBytes(long tamanioArchivoBytes) {
        this.tamanioArchivoBytes = tamanioArchivoBytes;
    }

    /**
     * Obtiene el tamaño del archivo en megabytes.
     *
     * @return el tamaño en MB
     */
    public double getTamanioArchivoMb() {
        return tamanioArchivoMb;
    }

    /**
     * Establece el tamaño del archivo en MB.
     *
     * @param tamanioArchivoMb el tamaño en MB
     */
    public void setTamanioArchivoMb(double tamanioArchivoMb) {
        this.tamanioArchivoMb = tamanioArchivoMb;
    }

    /**
     * Obtiene el número de bloques procesados durante el descifrado.
     *
     * @return el número de bloques
     */
    public int getBloquesProcesados() {
        return bloquesProcesados;
    }

    /**
     * Establece el número de bloques procesados.
     *
     * @param bloquesProcesados el número de bloques
     */
    public void setBloquesProcesados(int bloquesProcesados) {
        this.bloquesProcesados = bloquesProcesados;
    }

    /**
     * Obtiene el estado del canary check realizado durante el descifrado.
     * El canary check verifica que la clave usada sea correcta.
     *
     * @return el estado del canary check
     */
    public String getCanaryCheck() {
        return canaryCheck;
    }

    /**
     * Establece el estado del canary check.
     *
     * @param canaryCheck el estado del canary check
     */
    public void setCanaryCheck(String canaryCheck) {
        this.canaryCheck = canaryCheck;
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
