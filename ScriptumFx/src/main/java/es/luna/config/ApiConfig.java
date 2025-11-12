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
                logger.warn("No se encontró application.properties");
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
     * 2. Archivo application.properties
     */
    public static final String API_BASE_URL = getApiUrl();

    /**
     * Obtiene la URL de la API basada en variables de entorno o application.properties.
     * Orden de prioridad:
     * 1. Variable de entorno SCRIPTUM_API_URL
     * 2. Archivo application.properties
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

        // 2. Obtener de application.properties
        apiUrl = properties.getProperty("scriptum.api.url");
        if (apiUrl != null && !apiUrl.isEmpty()) {
            logger.info("Usando URL de application.properties: {}", apiUrl);
            return apiUrl;
        }

        // Si no hay configuración, lanzar error
        throw new IllegalStateException(
            "No se encontró configuración de URL. " +
            "Configure SCRIPTUM_API_URL o scriptum.api.url en application.properties"
        );
    }
}
