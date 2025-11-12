package es.luna.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Configuración centralizada para la conexión con la API de Scriptum.
 * Lee la configuración desde application.properties con fallback a variables de entorno.
 *
 * @author Arantxa
 * @version 2.0
 * @since 2025-11-11
 */
public class ApiConfig {

    private static final Logger logger = LoggerFactory.getLogger(ApiConfig.class);
    private static final Properties properties = new Properties();

    // Cargar propiedades al inicializar la clase
    static {
        try (InputStream input = ApiConfig.class.getClassLoader()
                .getResourceAsStream("application.properties")) {

            if (input == null) {
                logger.warn("No se encontró application.properties, usando valores por defecto");
            } else {
                properties.load(input);
                logger.info("Configuración cargada desde application.properties");
            }
        } catch (IOException e) {
            logger.error("Error al cargar application.properties", e);
        }
    }

    /**
     * URL base de la API.
     * Se obtiene en orden de prioridad:
     * 1. Variable de entorno SCRIPTUM_API_URL
     * 2. Propiedad del sistema scriptum.api.url
     * 3. Archivo application.properties
     */
    public static final String API_BASE_URL = getApiUrl();

    /**
     * Puerto por defecto de la API.
     */
    public static final int API_PORT = getIntProperty("scriptum.api.port", 8000);

    /**
     * Timeout por defecto para las peticiones (en segundos).
     */
    public static final int REQUEST_TIMEOUT_SECONDS = getIntProperty("scriptum.api.timeout", 30);

    /**
     * Obtiene la URL de la API basada en variables de entorno, propiedades del sistema,
     * o archivo application.properties.
     * Orden de prioridad:
     * 1. Variable de entorno SCRIPTUM_API_URL
     * 2. Propiedad del sistema -Dscriptum.api.url
     * 3. Archivo application.properties
     * 4. Valor por defecto (localhost)
     *
     * @return la URL de la API
     */
    private static String getApiUrl() {
        // 1. Intentar obtener de variable de entorno
        String apiUrl = System.getenv("SCRIPTUM_API_URL");
        if (apiUrl != null && !apiUrl.isEmpty()) {
            logger.info("Usando URL de variable de entorno: {}", apiUrl);
            return apiUrl;
        }

        // 2. Intentar obtener de propiedad del sistema
        apiUrl = System.getProperty("scriptum.api.url");
        if (apiUrl != null && !apiUrl.isEmpty()) {
            logger.info("Usando URL de propiedad del sistema: {}", apiUrl);
            return apiUrl;
        }

        // 3. Intentar obtener de application.properties
        apiUrl = properties.getProperty("scriptum.api.url");
        if (apiUrl != null && !apiUrl.isEmpty()) {
            logger.info("Usando URL de application.properties: {}", apiUrl);
            return apiUrl;
        }

        // 4. Valor por defecto
        logger.warn("No se encontró configuración de URL, usando localhost");
        return "http://localhost:" + getIntProperty("scriptum.api.port", 8000);
    }

    /**
     * Obtiene una propiedad entera del archivo de configuración.
     *
     * @param key el nombre de la propiedad
     * @param defaultValue el valor por defecto si no se encuentra
     * @return el valor de la propiedad o el valor por defecto
     */
    private static int getIntProperty(String key, int defaultValue) {
        try {
            String value = properties.getProperty(key);
            return value != null ? Integer.parseInt(value) : defaultValue;
        } catch (NumberFormatException e) {
            logger.warn("Error al parsear propiedad {}, usando valor por defecto: {}", key, defaultValue);
            return defaultValue;
        }
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
