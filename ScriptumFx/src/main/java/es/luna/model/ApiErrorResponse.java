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

    // Getters y Setters

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public String getDetalle() {
        return detalle;
    }

    public void setDetalle(String detalle) {
        this.detalle = detalle;
    }

    @Override
    public String toString() {
        return "ApiErrorResponse{" +
                "error='" + error + '\'' +
                ", detalle='" + detalle + '\'' +
                '}';
    }
}
