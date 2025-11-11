package es.luna.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSyntaxException;
import es.luna.model.ApiErrorResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;

/**
 * Cliente HTTP centralizado para comunicarse con la API de Scriptum.
 * Utiliza el HttpClient nativo de Java 11+ y Gson para el manejo de JSON.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class ApiClient {

    private static final Logger logger = LoggerFactory.getLogger(ApiClient.class);

    /** URL base de la API */
    private final String baseUrl;

    /** Cliente HTTP reutilizable */
    private final HttpClient httpClient;

    /** Instancia de Gson para serialización/deserialización JSON */
    private final Gson gson;

    /** Timeout por defecto para las peticiones (30 segundos) */
    private static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(30);

    /**
     * Constructor que crea un cliente HTTP con configuración por defecto.
     *
     * @param baseUrl la URL base de la API (ej: "http://localhost:8000")
     */
    public ApiClient(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(DEFAULT_TIMEOUT)
                .build();
        this.gson = new GsonBuilder()
                .setPrettyPrinting()
                .create();

        logger.info("ApiClient inicializado con baseUrl: {}", this.baseUrl);
    }

    /**
     * Realiza una petición POST de forma asíncrona.
     *
     * @param endpoint el endpoint a llamar (ej: "/vigenere/cifrar-texto")
     * @param requestBody el objeto request a enviar (será serializado a JSON)
     * @param responseClass la clase del objeto response esperado
     * @param <T> el tipo del response
     * @return CompletableFuture con el objeto response deserializado
     */
    public <T> CompletableFuture<T> postAsync(String endpoint, Object requestBody, Class<T> responseClass) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                logger.debug("POST {} - Request: {}", endpoint, requestBody);

                // Serializar el request body a JSON
                String jsonBody = gson.toJson(requestBody);

                // Construir la petición HTTP
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(baseUrl + endpoint))
                        .timeout(DEFAULT_TIMEOUT)
                        .header("Content-Type", "application/json")
                        .header("Accept", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                        .build();

                // Enviar la petición
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

                logger.debug("POST {} - Status: {} - Response: {}", endpoint, response.statusCode(), response.body());

                // Manejar respuestas de error HTTP
                if (response.statusCode() >= 400) {
                    handleErrorResponse(response);
                }

                // Deserializar el response body
                T responseObject = gson.fromJson(response.body(), responseClass);
                logger.info("POST {} - Success", endpoint);
                return responseObject;

            } catch (JsonSyntaxException e) {
                logger.error("Error al parsear JSON en POST {}", endpoint, e);
                throw new ApiException("Error al parsear la respuesta JSON: " + e.getMessage(), e);
            } catch (Exception e) {
                logger.error("Error en petición POST {}", endpoint, e);
                throw new ApiException("Error en la petición HTTP: " + e.getMessage(), e);
            }
        });
    }

    /**
     * Realiza una petición GET de forma asíncrona.
     *
     * @param endpoint el endpoint a llamar
     * @param responseClass la clase del objeto response esperado
     * @param <T> el tipo del response
     * @return CompletableFuture con el objeto response deserializado
     */
    public <T> CompletableFuture<T> getAsync(String endpoint, Class<T> responseClass) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                logger.debug("GET {}", endpoint);

                // Construir la petición HTTP
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(baseUrl + endpoint))
                        .timeout(DEFAULT_TIMEOUT)
                        .header("Accept", "application/json")
                        .GET()
                        .build();

                // Enviar la petición
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

                logger.debug("GET {} - Status: {} - Response: {}", endpoint, response.statusCode(), response.body());

                // Manejar respuestas de error HTTP
                if (response.statusCode() >= 400) {
                    handleErrorResponse(response);
                }

                // Deserializar el response body
                T responseObject = gson.fromJson(response.body(), responseClass);
                logger.info("GET {} - Success", endpoint);
                return responseObject;

            } catch (JsonSyntaxException e) {
                logger.error("Error al parsear JSON en GET {}", endpoint, e);
                throw new ApiException("Error al parsear la respuesta JSON: " + e.getMessage(), e);
            } catch (Exception e) {
                logger.error("Error en petición GET {}", endpoint, e);
                throw new ApiException("Error en la petición HTTP: " + e.getMessage(), e);
            }
        });
    }

    /**
     * Maneja las respuestas de error HTTP, intentando extraer el mensaje de error de la API.
     *
     * @param response la respuesta HTTP con error
     * @throws ApiException con el mensaje de error extraído
     */
    private void handleErrorResponse(HttpResponse<String> response) throws ApiException {
        try {
            ApiErrorResponse errorResponse = gson.fromJson(response.body(), ApiErrorResponse.class);
            String errorMsg = errorResponse.getError();
            String detalle = errorResponse.getDetalle();

            String fullErrorMsg = errorMsg;
            if (detalle != null && !detalle.isEmpty()) {
                fullErrorMsg += " - " + detalle;
            }

            logger.error("Error de API ({}): {}", response.statusCode(), fullErrorMsg);
            throw new ApiException(fullErrorMsg);

        } catch (JsonSyntaxException e) {
            // Si no se puede parsear como error JSON, lanzar error genérico
            String errorMsg = "Error HTTP " + response.statusCode() + ": " + response.body();
            logger.error(errorMsg);
            throw new ApiException(errorMsg);
        }
    }

    /**
     * Excepción personalizada para errores de la API.
     */
    public static class ApiException extends RuntimeException {
        public ApiException(String message) {
            super(message);
        }

        public ApiException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
