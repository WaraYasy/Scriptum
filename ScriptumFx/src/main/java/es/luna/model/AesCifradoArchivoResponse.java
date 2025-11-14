package es.luna.model;

import com.google.gson.annotations.SerializedName;
import java.util.Map;

/**
 * Response DTO para operación de cifrado AES de archivos.
 * Corresponde al schema CifradoAESArchivoPaqueteResponse de la API.
 * El paquete contiene en un solo campo:
 * - Archivo cifrado
 * - Salt para descifrar
 * - Tipo de AES usado
 * - Nombre original del archivo
 * - MIME type del archivo
 *
 * @author Arantxa
 * @version 2.0
 * @since 2025-11-13
 */
public class AesCifradoArchivoResponse {

    /** Paquete único en base64 */
    @SerializedName("paquete")
    private String paquete;

    /** Tamaño del paquete completo en bytes (antes de base64) */
    @SerializedName("tamanio_paquete_bytes")
    private long tamanioPaqueteBytes;

    /** Información sobre el archivo (nombre, tipo, tamaño original) */
    @SerializedName("info")
    private Map<String, Object> info;

    /**
     * Constructor vacío.
     */
    public AesCifradoArchivoResponse() {
    }

    // Getters

    /**
     * Obtiene el paquete cifrado único en formato base64.
     * El paquete contiene: archivo cifrado, salt, tipo de AES, nombre original y MIME type.
     *
     * @return el paquete en base64
     */
    public String getPaquete() {
        return paquete;
    }

    /**
     * Obtiene el tamaño del paquete completo en bytes (antes de base64).
     *
     * @return el tamaño en bytes
     */
    public long getTamanioPaqueteBytes() {
        return tamanioPaqueteBytes;
    }

    /**
     * Obtiene el mapa con información sobre el archivo.
     * Incluye: nombre_original, tipo_mime, tamanio_original_bytes, etc.
     *
     * @return el mapa de información
     */
    public Map<String, Object> getInfo() {
        return info;
    }

    /**
     * Helper para obtener el nombre original del archivo desde info.
     *
     * @return el nombre original del archivo, o null si no está disponible
     */
    public String getNombreOriginal() {
        if (info != null && info.containsKey("nombre_original")) {
            return (String) info.get("nombre_original");
        }
        return null;
    }

    /**
     * Helper para obtener el tamaño original en bytes desde info.
     *
     * @return el tamaño original en bytes, o null si no está disponible
     */
    public Integer getTamanioOriginalBytes() {
        if (info != null && info.containsKey("tamanio_original_bytes")) {
            Object value = info.get("tamanio_original_bytes");
            if (value instanceof Number) {
                return ((Number) value).intValue();
            }
        }
        return null;
    }
}
