package es.luna.service;

import es.luna.client.ApiClient;
import es.luna.model.AesCifradoResponse;
import es.luna.model.AesCifrarRequest;
import es.luna.model.AesDescifradoResponse;
import es.luna.model.AesDescifrarRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.CompletableFuture;

/**
 * Servicio para operaciones de cifrado y descifrado con el algoritmo AES.
 * Gestiona la comunicación con el backend de la API para las operaciones AES.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class AesService {

    private static final Logger logger = LoggerFactory.getLogger(AesService.class);

    /** Cliente HTTP para comunicarse con la API */
    private final ApiClient apiClient;

    /** Endpoint base para operaciones AES */
    private static final String BASE_ENDPOINT = "/aes";

    /** Longitud mínima del password */
    private static final int MIN_PASSWORD_LENGTH = 8;

    /**
     * Constructor que inicializa el servicio con la URL de la API.
     *
     * @param apiUrl la URL base de la API (ej: "http://localhost:8000")
     */
    public AesService(String apiUrl) {
        this.apiClient = new ApiClient(apiUrl);
        logger.info("AesService inicializado con API: {}", apiUrl);
    }

    /**
     * Constructor que acepta un ApiClient personalizado (útil para testing).
     *
     * @param apiClient el cliente HTTP a usar
     */
    public AesService(ApiClient apiClient) {
        this.apiClient = apiClient;
        logger.info("AesService inicializado con ApiClient personalizado");
    }

    /**
     * Cifra un texto usando el algoritmo AES de forma asíncrona.
     *
     * @param texto el texto a cifrar
     * @param password el password para derivar la clave
     * @param tipoAes el tipo de AES (AES-128, AES-192, AES-256)
     * @return CompletableFuture con la respuesta del cifrado
     */
    public CompletableFuture<AesCifradoResponse> cifrarTexto(String texto, String password, String tipoAes) {
        logger.debug("Cifrando texto con AES - Texto length: {}, Tipo: {}", texto.length(), tipoAes);

        // Validaciones básicas
        if (texto == null || texto.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El texto no puede estar vacío")
            );
        }

        if (password == null || password.length() < MIN_PASSWORD_LENGTH) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El password debe tener al menos " + MIN_PASSWORD_LENGTH + " caracteres")
            );
        }

        // Crear request
        AesCifrarRequest request = new AesCifrarRequest(texto, password, tipoAes);

        // Realizar petición asíncrona
        return apiClient.postAsync(
                BASE_ENDPOINT + "/cifrar/texto",
                request,
                AesCifradoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.error("Error al cifrar texto con AES", error);
            } else {
                logger.info("Texto cifrado exitosamente con AES-{}", tipoAes);
            }
        });
    }

    /**
     * Cifra un texto usando AES-256 por defecto.
     *
     * @param texto el texto a cifrar
     * @param password el password para derivar la clave
     * @return CompletableFuture con la respuesta del cifrado
     */
    public CompletableFuture<AesCifradoResponse> cifrarTexto(String texto, String password) {
        return cifrarTexto(texto, password, "AES-256");
    }

    /**
     * Descifra un texto cifrado con AES de forma asíncrona.
     *
     * @param textoCifrado el texto cifrado en base64
     * @param password el password usado para cifrar
     * @param salt el salt en base64 obtenido al cifrar
     * @param tipoAes el tipo de AES usado
     * @return CompletableFuture con la respuesta del descifrado
     */
    public CompletableFuture<AesDescifradoResponse> descifrarTexto(
            String textoCifrado,
            String password,
            String salt,
            String tipoAes
    ) {
        logger.debug("Descifrando texto con AES - Tipo: {}", tipoAes);

        // Validaciones básicas
        if (textoCifrado == null || textoCifrado.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El texto cifrado no puede estar vacío")
            );
        }

        if (password == null || password.length() < MIN_PASSWORD_LENGTH) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El password debe tener al menos " + MIN_PASSWORD_LENGTH + " caracteres")
            );
        }

        if (salt == null || salt.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El salt no puede estar vacío")
            );
        }

        // Crear request
        AesDescifrarRequest request = new AesDescifrarRequest(textoCifrado, password, salt, tipoAes);

        // Realizar petición asíncrona
        return apiClient.postAsync(
                BASE_ENDPOINT + "/descifrar/texto",
                request,
                AesDescifradoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.error("Error al descifrar texto con AES", error);
            } else {
                logger.info("Texto descifrado exitosamente con AES");
            }
        });
    }

    /**
     * Descifra un texto usando AES-256 por defecto.
     *
     * @param textoCifrado el texto cifrado en base64
     * @param password el password usado para cifrar
     * @param salt el salt en base64 obtenido al cifrar
     * @return CompletableFuture con la respuesta del descifrado
     */
    public CompletableFuture<AesDescifradoResponse> descifrarTexto(
            String textoCifrado,
            String password,
            String salt
    ) {
        return descifrarTexto(textoCifrado, password, salt, "AES-256");
    }

    /**
     * Verifica la conectividad con el backend.
     *
     * @return CompletableFuture<Boolean> true si la conexión es exitosa
     */
    public CompletableFuture<Boolean> verificarConexion() {
        logger.debug("Verificando conexión con la API");

        return apiClient.getAsync("/health", Object.class)
                .thenApply(response -> {
                    logger.info("Conexión con API verificada exitosamente");
                    return true;
                })
                .exceptionally(error -> {
                    logger.error("Error al verificar conexión con la API", error);
                    return false;
                });
    }
}
