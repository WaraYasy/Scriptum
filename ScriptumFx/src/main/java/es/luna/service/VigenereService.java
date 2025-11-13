package es.luna.service;

import es.luna.client.ApiClient;
import es.luna.model.VigenereCifradoResponse;
import es.luna.model.VigenereCifrarRequest;
import es.luna.model.VigenereDescifradoResponse;
import es.luna.model.VigenereDescifrarRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Servicio para operaciones de cifrado y descifrado con el algoritmo Vigenère.
 * Gestiona la comunicación con el backend de la API para las operaciones Vigenère.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
@SuppressWarnings("ClassCanBeRecord")
public class VigenereService {

    private static final Logger logger = LoggerFactory.getLogger(VigenereService.class);

    /** Cliente HTTP para comunicarse con la API */
    private final ApiClient apiClient;

    /** Endpoint base para operaciones Vigenère */
    private static final String BASE_ENDPOINT = "/vigenere";

    /**
     * Constructor que inicializa el servicio con la URL de la API.
     *
     * @param apiUrl la URL base de la API
     */
    public VigenereService(String apiUrl) {
        this.apiClient = new ApiClient(apiUrl);
        logger.info("VigenereService inicializado con API: {}", apiUrl);
    }

    /**
     * Constructor que acepta un ApiClient personalizado (útil para testing).
     *
     * @param apiClient el cliente HTTP a usar
     */
    public VigenereService(ApiClient apiClient) {
        this.apiClient = apiClient;
        logger.info("VigenereService inicializado con ApiClient personalizado");
    }

    /**
     * Cifra un texto usando el algoritmo Vigenère de forma asíncrona.
     *
     * @param texto el texto a cifrar
     * @param clave la clave para el cifrado
     * @return CompletableFuture con la respuesta del cifrado
     */
    public CompletableFuture<VigenereCifradoResponse> cifrarTexto(String texto, String clave) {
        logger.debug("Cifrando texto con Vigenère - Texto length: {}, Clave length: {}", texto.length(), clave.length());

        // Validaciones básicas
        if (texto.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El texto no puede estar vacío")
            );
        }

        if (clave.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("La clave no puede estar vacía")
            );
        }

        // Crear request
        VigenereCifrarRequest request = new VigenereCifrarRequest(texto, clave);

        // Realizar petición asíncrona
        return apiClient.postAsync(
                BASE_ENDPOINT + "/cifrar/texto",
                request,
                VigenereCifradoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.warn("Error al cifrar texto con Vigenère: {}", error.getMessage());
            } else {
                logger.info("Texto cifrado exitosamente con Vigenère");
            }
        });
    }

    /**
     * Descifra un texto cifrado con Vigenère de forma asíncrona.
     *
     * @param textoCifrado el texto cifrado a descifrar
     * @param clave la clave para el descifrado
     * @return CompletableFuture con la respuesta del descifrado
     */
    public CompletableFuture<VigenereDescifradoResponse> descifrarTexto(String textoCifrado, String clave) {
        logger.debug("Descifrando texto con Vigenère - Texto length: {}, Clave length: {}", textoCifrado.length(), clave.length());

        // Validaciones básicas
        if (textoCifrado.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El texto cifrado no puede estar vacío")
            );
        }

        if (clave.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("La clave no puede estar vacía")
            );
        }

        // Crear request
        VigenereDescifrarRequest request = new VigenereDescifrarRequest(textoCifrado, clave);

        // Realizar petición asíncrona
        return apiClient.postAsync(
                BASE_ENDPOINT + "/descifrar/texto",
                request,
                VigenereDescifradoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.warn("Error al descifrar texto con Vigenère: {}", error.getMessage());
            } else {
                logger.info("Texto descifrado exitosamente con Vigenère");
            }
        });
    }

    /**
     * Cifra un archivo usando el algoritmo Vigenère de forma asíncrona.
     *
     * @param archivo el archivo a cifrar
     * @param clave la clave para el cifrado
     * @return CompletableFuture con la respuesta del cifrado
     */
    public CompletableFuture<VigenereCifradoResponse> cifrarArchivo(File archivo, String clave) {
        logger.debug("Cifrando archivo con Vigenère - Archivo: {}, Clave length: {}", archivo.getName(), clave.length());

        // Validaciones básicas
        if (!archivo.exists()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El archivo no existe")
            );
        }

        if (clave.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("La clave no puede estar vacía")
            );
        }

        // Crear form data
        Map<String, String> formData = new HashMap<>();
        formData.put("clave", clave);

        // Realizar petición asíncrona multipart
        return apiClient.postMultipartAsync(
                BASE_ENDPOINT + "/cifrar/file",
                archivo,
                formData,
                VigenereCifradoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.warn("Error al cifrar archivo con Vigenère: {}", error.getMessage());
            } else {
                logger.info("Archivo cifrado exitosamente con Vigenère");
            }
        });
    }

    /**
     * Descifra un archivo cifrado con Vigenère de forma asíncrona.
     *
     * @param archivoCifrado el archivo cifrado a descifrar
     * @param clave la clave para el descifrado
     * @return CompletableFuture con la respuesta del descifrado
     */
    public CompletableFuture<VigenereDescifradoResponse> descifrarArchivo(File archivoCifrado, String clave) {
        logger.debug("Descifrando archivo con Vigenère - Archivo: {}, Clave length: {}", archivoCifrado.getName(), clave.length());

        // Validaciones básicas
        if (!archivoCifrado.exists()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El archivo no existe")
            );
        }

        if (clave.trim().isEmpty()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("La clave no puede estar vacía")
            );
        }

        // Crear form data
        Map<String, String> formData = new HashMap<>();
        formData.put("clave", clave);

        // Realizar petición asíncrona multipart
        return apiClient.postMultipartAsync(
                BASE_ENDPOINT + "/descifrar/file",
                archivoCifrado,
                formData,
                VigenereDescifradoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.warn("Error al descifrar archivo con Vigenère: {}", error.getMessage());
            } else {
                logger.info("Archivo descifrado exitosamente con Vigenère");
            }
        });
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
