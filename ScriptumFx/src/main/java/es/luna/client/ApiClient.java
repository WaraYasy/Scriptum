package es.luna.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSyntaxException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.time.Duration;
import java.util.Map;
import java.util.UUID;
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
     * @param baseUrl la URL base de la API
     */
    public ApiClient(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(DEFAULT_TIMEOUT)
                .version(HttpClient.Version.HTTP_1_1)  // Forzar HTTP/1.1, no HTTP/2
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
                // Serializar el request body a JSON
                String jsonBody = gson.toJson(requestBody);

                logger.debug("POST {} - Body size: {} bytes", endpoint, jsonBody.getBytes(java.nio.charset.StandardCharsets.UTF_8).length);

                // Construir la petición HTTP
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(baseUrl + endpoint))
                        .timeout(DEFAULT_TIMEOUT)
                        .header("Content-Type", "application/json")
                        .header("Accept", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(jsonBody, java.nio.charset.StandardCharsets.UTF_8))
                        .build();

                logger.debug("POST {} - Sending request to: {}", endpoint, request.uri());

                // Enviar la petición
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

                logger.debug("POST {} - Status: {}", endpoint, response.statusCode());

                // Manejar respuestas de error HTTP
                if (response.statusCode() >= 400) {
                    handleErrorResponse(response);
                }

                // Deserializar el response body
                T responseObject = gson.fromJson(response.body(), responseClass);
                logger.info("POST {} - Success", endpoint);
                return responseObject;

            } catch (ApiException e) {
                // ApiException ya fue registrada en handleErrorResponse, solo relanzar
                throw e;
            } catch (JsonSyntaxException e) {
                logger.error("Error al parsear JSON en POST {}: {}", endpoint, e.getMessage());
                throw new ApiException("Error al parsear la respuesta JSON: " + e.getMessage(), e);
            } catch (Exception e) {
                logger.error("Error inesperado en petición POST {}: {}", endpoint, e.getMessage());
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

                logger.debug("GET {} - Status: {}", endpoint, response.statusCode());

                // Manejar respuestas de error HTTP
                if (response.statusCode() >= 400) {
                    handleErrorResponse(response);
                }

                // Deserializar el response body
                T responseObject = gson.fromJson(response.body(), responseClass);
                logger.info("GET {} - Success", endpoint);
                return responseObject;

            } catch (ApiException e) {
                // ApiException ya fue registrada en handleErrorResponse, solo relanzar
                throw e;
            } catch (JsonSyntaxException e) {
                logger.error("Error al parsear JSON en GET {}: {}", endpoint, e.getMessage());
                throw new ApiException("Error al parsear la respuesta JSON: " + e.getMessage(), e);
            } catch (Exception e) {
                logger.error("Error inesperado en petición GET {}: {}", endpoint, e.getMessage());
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
            int statusCode = response.statusCode();
            String responseBody = response.body();
            String errorMsg = null;

            // Intentar parsear como objeto con estructura FastAPI: {"detail": {"error": "..."}}
            try {
                com.google.gson.JsonObject jsonObject = gson.fromJson(responseBody, com.google.gson.JsonObject.class);

                // Caso 1: {"detail": {"error": "mensaje"}}
                if (jsonObject.has("detail")) {
                    com.google.gson.JsonElement detailElement = jsonObject.get("detail");
                    if (detailElement.isJsonObject()) {
                        com.google.gson.JsonObject detailObj = detailElement.getAsJsonObject();
                        if (detailObj.has("error")) {
                            errorMsg = detailObj.get("error").getAsString();
                        }
                    } else if (detailElement.isJsonPrimitive()) {
                        // Caso 2: {"detail": "mensaje"}
                        errorMsg = detailElement.getAsString();
                    }
                }

                // Caso 3: {"error": "mensaje", "detalle": "..."}
                if (errorMsg == null && jsonObject.has("error")) {
                    errorMsg = jsonObject.get("error").getAsString();
                    if (jsonObject.has("detalle")) {
                        String detalle = jsonObject.get("detalle").getAsString();
                        if (detalle != null && !detalle.isEmpty()) {
                            errorMsg += " - " + detalle;
                        }
                    }
                }

            } catch (Exception e) {
                logger.debug("No se pudo parsear como JSON estructurado, usando cuerpo completo");
            }

            // Si no se pudo extraer mensaje, usar el cuerpo completo
            if (errorMsg == null || errorMsg.isEmpty()) {
                errorMsg = "Error HTTP " + statusCode + ": " + responseBody;
            }

            // Diferenciar entre errores de cliente (4xx) y servidor (5xx)
            if (statusCode >= 400 && statusCode < 500) {
                // Errores 4xx son de validación/cliente - WARN sin stack trace
                logger.warn("Error de validación de API ({}): {}", statusCode, errorMsg);
            } else {
                // Errores 5xx son del servidor - ERROR
                logger.error("Error del servidor API ({}): {}", statusCode, errorMsg);
            }

            throw new ApiException(errorMsg);

        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            // Si falla lo demás, lanzar error genérico
            String errorMsg = "Error HTTP " + response.statusCode() + ": " + response.body();
            logger.error(errorMsg);
            throw new ApiException(errorMsg);
        }
    }

    /**
     * Realiza una petición POST multipart/form-data de forma asíncrona.
     * Útil para enviar archivos al servidor.
     *
     * @param endpoint el endpoint a llamar (ej: "/vigenere/cifrar/file")
     * @param file el archivo a enviar
     * @param formData campos adicionales del formulario (ej: clave, password, etc.)
     * @param responseClass la clase del objeto response esperado
     * @param <T> el tipo del response
     * @return CompletableFuture con el objeto response deserializado
     */
    public <T> CompletableFuture<T> postMultipartAsync(
            String endpoint,
            File file,
            Map<String, String> formData,
            Class<T> responseClass
    ) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Generar boundary único para multipart
                String boundary = "----WebKitFormBoundary" + UUID.randomUUID().toString().replace("-", "");

                // Construir el body multipart manualmente
                StringBuilder bodyBuilder = new StringBuilder();

                // Agregar campos del formulario
                if (formData != null) {
                    for (Map.Entry<String, String> entry : formData.entrySet()) {
                        bodyBuilder.append("--").append(boundary).append("\r\n");
                        bodyBuilder.append("Content-Disposition: form-data; name=\"")
                                .append(entry.getKey()).append("\"\r\n\r\n");
                        bodyBuilder.append(entry.getValue()).append("\r\n");
                    }
                }

                // Agregar archivo
                bodyBuilder.append("--").append(boundary).append("\r\n");
                bodyBuilder.append("Content-Disposition: form-data; name=\"file\"; filename=\"")
                        .append(file.getName()).append("\"\r\n");
                bodyBuilder.append("Content-Type: text/plain\r\n\r\n");

                // Leer contenido del archivo
                byte[] fileBytes = Files.readAllBytes(file.toPath());
                String fileContent = new String(fileBytes, java.nio.charset.StandardCharsets.UTF_8);
                bodyBuilder.append(fileContent).append("\r\n");

                // Cerrar boundary
                bodyBuilder.append("--").append(boundary).append("--\r\n");

                String body = bodyBuilder.toString();

                logger.debug("POST multipart {} - Body size: {} bytes", endpoint, body.getBytes(java.nio.charset.StandardCharsets.UTF_8).length);

                // Construir la petición HTTP
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(baseUrl + endpoint))
                        .timeout(DEFAULT_TIMEOUT)
                        .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                        .header("Accept", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(body, java.nio.charset.StandardCharsets.UTF_8))
                        .build();

                logger.debug("POST multipart {} - Sending request to: {}", endpoint, request.uri());

                // Enviar la petición
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

                logger.debug("POST multipart {} - Status: {}", endpoint, response.statusCode());

                // Manejar respuestas de error HTTP
                if (response.statusCode() >= 400) {
                    handleErrorResponse(response);
                }

                // Deserializar el response body
                T responseObject = gson.fromJson(response.body(), responseClass);
                logger.info("POST multipart {} - Success", endpoint);
                return responseObject;

            } catch (ApiException e) {
                // ApiException ya fue registrada en handleErrorResponse, solo relanzar
                throw e;
            } catch (JsonSyntaxException e) {
                logger.error("Error al parsear JSON en POST multipart {}: {}", endpoint, e.getMessage());
                throw new ApiException("Error al parsear la respuesta JSON: " + e.getMessage(), e);
            } catch (IOException e) {
                logger.error("Error de I/O al leer archivo en POST multipart {}: {}", endpoint, e.getMessage());
                throw new ApiException("Error al leer el archivo: " + e.getMessage(), e);
            } catch (Exception e) {
                logger.error("Error inesperado en petición POST multipart {}: {}", endpoint, e.getMessage());
                throw new ApiException("Error en la petición HTTP: " + e.getMessage(), e);
            }
        });
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
