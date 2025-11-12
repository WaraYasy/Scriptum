package es.luna.model;

import com.google.gson.annotations.SerializedName;

/**
 * Response DTO para errores de la API.
 * Corresponde al schema ErrorResponse de la API.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class ApiErrorResponse {

    /** Mensaje de error */
    @SerializedName("error")
    private String error;

    /** Detalles adicionales del error */
    @SerializedName("detalle")
    private String detalle;

    /**
     * Constructor vacío.
     */
    public ApiErrorResponse() {
    }

    @Override
    public String toString() {
        return "ApiErrorResponse{" +
                "error='" + error + '\'' +
                ", detalle='" + detalle + '\'' +
                '}';
    }
}
