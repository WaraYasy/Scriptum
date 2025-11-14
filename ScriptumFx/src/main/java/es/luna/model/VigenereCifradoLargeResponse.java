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

    /**
     * Obtiene el texto cifrado resultante.
     *
     * @return el texto cifrado
     */
    public String getTextoCifrado() {
        return textoCifrado;
    }

    /**
     * Establece el texto cifrado.
     *
     * @param textoCifrado el texto cifrado
     */
    public void setTextoCifrado(String textoCifrado) {
        this.textoCifrado = textoCifrado;
    }

    /**
     * Obtiene la clave usada (formateada) en el cifrado.
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
     * Obtiene el número de bloques procesados durante el cifrado.
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
     * Indica si se agregó un magic header al archivo cifrado.
     *
     * @return true si se agregó header, false en caso contrario
     */
    public boolean isMagicHeaderAgregado() {
        return magicHeaderAgregado;
    }

    /**
     * Establece si se agregó magic header.
     *
     * @param magicHeaderAgregado true si se agregó header
     */
    public void setMagicHeaderAgregado(boolean magicHeaderAgregado) {
        this.magicHeaderAgregado = magicHeaderAgregado;
    }

    /**
     * Obtiene el mensaje informativo del cifrado.
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
