package es.luna.service;

import es.luna.client.ApiClient;
import es.luna.model.AesCifradoArchivoResponse;
import es.luna.model.AesCifradoResponse;
import es.luna.model.AesCifrarRequest;
import es.luna.model.AesDescifradoArchivoResponse;
import es.luna.model.AesDescifradoResponse;
import es.luna.model.AesDescifrarRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Servicio para operaciones de cifrado y descifrado con el algoritmo AES.
 * Gestiona la comunicación con el backend de la API para las operaciones AES.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
@SuppressWarnings("ClassCanBeRecord")
public class AesService {

    private static final Logger logger = LoggerFactory.getLogger(AesService.class);

    /** Cliente HTTP para comunicarse con la API */
    private final ApiClient apiClient;

    /** Endpoint base para operaciones AES */
    private static final String BASE_ENDPOINT = "/aes";

    /** Longitud mínima del password */
    private static final int MIN_PASSWORD_LENGTH = 8;

    /** Umbral de tamaño para usar streaming en backend (9.5 MB en bytes) */
    private static final long STREAMING_THRESHOLD = (long) (9.5 * 1024 * 1024); // 9.5 MB

    /**
     * Constructor que inicializa el servicio con la URL de la API.
     *
     * @param apiUrl la URL base de la API
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
        if (texto.trim().isEmpty()) {
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
                logger.warn("Error al cifrar texto con AES: {}", error.getMessage());
            } else {
                logger.info("Texto cifrado exitosamente con AES-{}", tipoAes);
            }
        });
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
                logger.warn("Error al descifrar texto con AES: {}", error.getMessage());
            } else {
                logger.info("Texto descifrado exitosamente con AES");
            }
        });
    }

    /**
     * Cifra un archivo usando el algoritmo AES de forma asíncrona.
     *
     * @param archivo el archivo a cifrar
     * @param password el password para derivar la clave
     * @param tipoAes el tipo de AES (AES-128, AES-192, AES-256)
     * @return CompletableFuture con la respuesta del cifrado
     */
    public CompletableFuture<AesCifradoArchivoResponse> cifrarArchivo(File archivo, String password, String tipoAes) {
        long fileSize = archivo.length();
        boolean willUseStreaming = fileSize >= STREAMING_THRESHOLD;

        logger.debug("Cifrando archivo con AES - Archivo: {}, Tamaño: {} bytes, Tipo: {}",
                archivo.getName(), fileSize, tipoAes);

        if (willUseStreaming) {
            logger.info("Archivo grande detectado ({} MB), el backend usará streaming automático",
                    fileSize / (1024.0 * 1024.0));
        } else {
            logger.info("Archivo pequeño ({} MB), el backend procesará en memoria",
                    fileSize / (1024.0 * 1024.0));
        }

        // Validaciones básicas
        if (!archivo.exists()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El archivo no existe")
            );
        }

        if (password == null || password.length() < MIN_PASSWORD_LENGTH) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El password debe tener al menos " + MIN_PASSWORD_LENGTH + " caracteres")
            );
        }

        // Crear form data
        Map<String, String> formData = new HashMap<>();
        formData.put("password", password);
        formData.put("tipo_aes", tipoAes);

        // Realizar petición asíncrona multipart
        return apiClient.postMultipartAsync(
                BASE_ENDPOINT + "/cifrar/file",
                archivo,
                formData,
                AesCifradoArchivoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.warn("Error al cifrar archivo con AES: {}", error.getMessage());
            } else {
                logger.info("Archivo cifrado exitosamente con AES-{} (streaming: {})",
                        tipoAes, willUseStreaming ? "sí" : "no");
            }
        });
    }

    /**
     * Descifra un archivo cifrado con AES de forma asíncrona.
     *
     * @param archivoCifrado el archivo cifrado a descifrar
     * @param password el password usado para cifrar
     * @param salt el salt en base64 obtenido al cifrar
     * @param tipoAes el tipo de AES usado
     * @return CompletableFuture con la respuesta del descifrado
     */
    public CompletableFuture<AesDescifradoArchivoResponse> descifrarArchivo(
            File archivoCifrado,
            String password,
            String salt,
            String tipoAes
    ) {
        long fileSize = archivoCifrado.length();
        boolean willUseStreaming = fileSize >= STREAMING_THRESHOLD;

        logger.debug("Descifrando archivo con AES - Archivo: {}, Tamaño: {} bytes, Tipo: {}",
                archivoCifrado.getName(), fileSize, tipoAes);

        if (willUseStreaming) {
            logger.info("Archivo grande detectado ({} MB), el backend usará streaming automático",
                    fileSize / (1024.0 * 1024.0));
        } else {
            logger.info("Archivo pequeño ({} MB), el backend procesará en memoria",
                    fileSize / (1024.0 * 1024.0));
        }

        // Validaciones básicas
        if (!archivoCifrado.exists()) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El archivo no existe")
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

        // Crear form data
        Map<String, String> formData = new HashMap<>();
        formData.put("password", password);
        formData.put("salt", salt);
        formData.put("tipo_aes", tipoAes);

        // Realizar petición asíncrona multipart
        return apiClient.postMultipartAsync(
                BASE_ENDPOINT + "/descifrar/file",
                archivoCifrado,
                formData,
                AesDescifradoArchivoResponse.class
        ).whenComplete((response, error) -> {
            if (error != null) {
                logger.warn("Error al descifrar archivo con AES: {}", error.getMessage());
            } else {
                logger.info("Archivo descifrado exitosamente con AES (streaming: {})",
                        willUseStreaming ? "sí" : "no");
            }
        });
    }
}
