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

    /**
     * Constructor con parámetros.
     *
     * @param error el mensaje de error
     * @param detalle detalles adicionales del error
     */
    public ApiErrorResponse(String error, String detalle) {
        this.error = error;
        this.detalle = detalle;
    }

    // Getters y Setters

    /**
     * Obtiene el mensaje de error.
     *
     * @return el mensaje de error
     */
    public String getError() {
        return error;
    }

    /**
     * Establece el mensaje de error.
     *
     * @param error el mensaje de error
     */
    public void setError(String error) {
        this.error = error;
    }

    /**
     * Obtiene los detalles adicionales del error.
     *
     * @return los detalles del error
     */
    public String getDetalle() {
        return detalle;
    }

    /**
     * Establece los detalles adicionales del error.
     *
     * @param detalle los detalles del error
     */
    public void setDetalle(String detalle) {
        this.detalle = detalle;
    }

    /**
     * Representación en cadena del error de la API.
     *
     * @return la representación en String
     */
    @Override
    public String toString() {
        return "ApiErrorResponse{" +
                "error='" + error + '\'' +
                ", detalle='" + detalle + '\'' +
                '}';
    }
}
