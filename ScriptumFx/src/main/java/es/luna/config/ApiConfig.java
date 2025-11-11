package es.luna.config;

/**
 * Configuración centralizada para la conexión con la API de Scriptum.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class ApiConfig {

    /**
     * URL base de la API.
     * Cambiar según el entorno (desarrollo, producción).
     */
    public static final String API_BASE_URL = getApiUrl();

    /**
     * Puerto por defecto de la API.
     */
    public static final int API_PORT = 8000;

    /**
     * Timeout por defecto para las peticiones (en segundos).
     */
    public static final int REQUEST_TIMEOUT_SECONDS = 30;

    /**
     * Obtiene la URL de la API basada en variables de entorno o configuración por defecto.
     *
     * @return la URL de la API
     */
    private static String getApiUrl() {
        // Intentar obtener de variable de entorno
        String apiUrl = System.getenv("SCRIPTUM_API_URL");

        if (apiUrl != null && !apiUrl.isEmpty()) {
            return apiUrl;
        }

        // Intentar obtener de propiedad del sistema
        apiUrl = System.getProperty("scriptum.api.url");

        if (apiUrl != null && !apiUrl.isEmpty()) {
            return apiUrl;
        }

        // Por defecto: localhost
        return "http://localhost:" + API_PORT;
    }

    /**
     * Verifica si la aplicación está en modo desarrollo.
     *
     * @return true si está en modo desarrollo
     */
    public static boolean isDevelopmentMode() {
        return API_BASE_URL.contains("localhost") || API_BASE_URL.contains("127.0.0.1");
    }
}
