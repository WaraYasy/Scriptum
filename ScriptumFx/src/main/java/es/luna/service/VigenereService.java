package es.luna.service;

import es.luna.client.ApiClient;
import es.luna.model.VigenereCifradoLargeResponse;
import es.luna.model.VigenereCifradoResponse;
import es.luna.model.VigenereCifrarRequest;
import es.luna.model.VigenereDescifradoLargeResponse;
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

    /** Umbral de tamaño para usar endpoint /large (9.5 MB en bytes) */
    private static final long LARGE_FILE_THRESHOLD = (long) (9.5 * 1024 * 1024); // 9.5 MB

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
        logger.debug("Cifrando texto con Vigenère - Texto length: {}", texto.length());

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
        logger.debug("Descifrando texto con Vigenère - Texto cifrado length: {}", textoCifrado.length());

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
     * Detecta automáticamente el tamaño y usa el endpoint /large si es necesario.
     *
     * @param archivo el archivo a cifrar
     * @param clave la clave para el cifrado
     * @return CompletableFuture con la respuesta del cifrado
     */
    public CompletableFuture<VigenereCifradoResponse> cifrarArchivo(File archivo, String clave) {
        return cifrarArchivo(archivo, clave, "MAGICV1\n", true);
    }

    /**
     * Cifra un archivo usando el algoritmo Vigenère de forma asíncrona con parámetros del magic header.
     * Detecta automáticamente el tamaño y usa el endpoint /large si es necesario.
     *
     * @param archivo el archivo a cifrar
     * @param clave la clave para el cifrado
     * @param magicHeader el header mágico a agregar al inicio del archivo (para canary check posterior)
     * @param addHeader si se debe agregar el magic header al inicio
     * @return CompletableFuture con la respuesta del cifrado
     */
    public CompletableFuture<VigenereCifradoResponse> cifrarArchivo(
            File archivo,
            String clave,
            String magicHeader,
            boolean addHeader
    ) {
        logger.debug("Cifrando archivo con Vigenère - Archivo: {}, Tamaño: {} bytes",
                archivo.getName(), archivo.length());

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

        // Detectar si es un archivo grande
        long fileSize = archivo.length();
        boolean isLargeFile = fileSize >= LARGE_FILE_THRESHOLD;

        if (isLargeFile) {
            logger.info("Archivo grande detectado ({} MB), usando endpoint /large con streaming",
                    fileSize / (1024.0 * 1024.0));

            // Crear form data con parámetros adicionales para el endpoint large
            Map<String, String> formData = new HashMap<>();
            formData.put("clave", clave);
            formData.put("magic_header", magicHeader);
            formData.put("add_header", String.valueOf(addHeader));

            // Usar endpoint /large que devuelve una respuesta diferente
            return apiClient.postMultipartAsync(
                    BASE_ENDPOINT + "/cifrar/file/large",
                    archivo,
                    formData,
                    VigenereCifradoLargeResponse.class
            ).thenApply(largeResponse -> {
                // Convertir VigenereCifradoLargeResponse a VigenereCifradoResponse
                return createCifradoResponse(largeResponse.getTextoCifrado(), largeResponse.getClaveUsada());
            }).whenComplete((response, error) -> {
                if (error != null) {
                    logger.warn("Error al cifrar archivo grande con Vigenère: {}", error.getMessage());
                } else {
                    logger.info("Archivo grande cifrado exitosamente con Vigenère (magic header: {})",
                            addHeader ? "agregado" : "omitido");
                }
            });
        } else {
            logger.info("Archivo pequeño ({} MB), usando endpoint estándar", fileSize / (1024.0 * 1024.0));

            // Crear form data
            Map<String, String> formData = new HashMap<>();
            formData.put("clave", clave);

            // Realizar petición asíncrona multipart con endpoint estándar
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
    }

    /**
     * Crea una instancia de VigenereCifradoResponse a partir de los valores.
     * Helper method para convertir la respuesta del endpoint large.
     */
    private VigenereCifradoResponse createCifradoResponse(String textoCifrado, String claveUsada) {
        VigenereCifradoResponse response = new VigenereCifradoResponse();
        response.setTextoCifrado(textoCifrado);
        response.setClaveUsada(claveUsada);
        return response;
    }

    /**
     * Descifra un archivo cifrado con Vigenère de forma asíncrona.
     * Detecta automáticamente el tamaño y usa el endpoint /large si es necesario.
     *
     * @param archivoCifrado el archivo cifrado a descifrar
     * @param clave la clave para el descifrado
     * @return CompletableFuture con la respuesta del descifrado
     */
    public CompletableFuture<VigenereDescifradoResponse> descifrarArchivo(File archivoCifrado, String clave) {
        return descifrarArchivo(archivoCifrado, clave, "MAGICV1\n", false);
    }

    /**
     * Descifra un archivo cifrado con Vigenère de forma asíncrona con parámetros del canary check.
     * Detecta automáticamente el tamaño y usa el endpoint /large si es necesario.
     *
     * @param archivoCifrado el archivo cifrado a descifrar
     * @param clave la clave para el descifrado
     * @param magicHeader el header mágico esperado al inicio del archivo descifrado
     * @param skipCanary si se debe omitir el canary check
     * @return CompletableFuture con la respuesta del descifrado
     */
    public CompletableFuture<VigenereDescifradoResponse> descifrarArchivo(
            File archivoCifrado,
            String clave,
            String magicHeader,
            boolean skipCanary
    ) {
        logger.debug("Descifrando archivo con Vigenère - Archivo: {}, Tamaño: {} bytes",
                archivoCifrado.getName(), archivoCifrado.length());

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

        // Detectar si es un archivo grande
        long fileSize = archivoCifrado.length();
        boolean isLargeFile = fileSize >= LARGE_FILE_THRESHOLD;

        if (isLargeFile) {
            logger.info("Archivo grande detectado ({} MB), usando endpoint /large con canary check",
                    fileSize / (1024.0 * 1024.0));

            // Crear form data con parámetros adicionales para el endpoint large
            Map<String, String> formData = new HashMap<>();
            formData.put("clave", clave);
            formData.put("magic_header", magicHeader);
            formData.put("skip_canary", String.valueOf(skipCanary));

            // Usar endpoint /large que devuelve una respuesta diferente
            return apiClient.postMultipartAsync(
                    BASE_ENDPOINT + "/descifrar/file/large",
                    archivoCifrado,
                    formData,
                    VigenereDescifradoLargeResponse.class
            ).thenApply(largeResponse -> {
                // Convertir VigenereDescifradoLargeResponse a VigenereDescifradoResponse
                // Usar reflexión o crear un metodo setter en el modelo
                // Por ahora, crear una instancia con los valores necesarios
                return createDescifradoResponse(largeResponse.getTextoDescifrado(), largeResponse.getClaveUsada());
            }).whenComplete((response, error) -> {
                if (error != null) {
                    logger.warn("Error al descifrar archivo grande con Vigenère: {}", error.getMessage());
                } else {
                    logger.info("Archivo grande descifrado exitosamente con Vigenère (canary: {})",
                            skipCanary ? "skipped" : "passed");
                }
            });
        } else {
            logger.info("Archivo pequeño ({} MB), usando endpoint estándar", fileSize / (1024.0 * 1024.0));

            // Crear form data
            Map<String, String> formData = new HashMap<>();
            formData.put("clave", clave);

            // Realizar petición asíncrona multipart con endpoint estándar
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
    }

    /**
     * Crea una instancia de VigenereDescifradoResponse a partir de los valores.
     * Helper method para convertir la respuesta del endpoint large.
     */
    private VigenereDescifradoResponse createDescifradoResponse(String textoDescifrado, String claveUsada) {
        VigenereDescifradoResponse response = new VigenereDescifradoResponse();
        response.setTextoDescifrado(textoDescifrado);
        response.setClaveUsada(claveUsada);
        return response;
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
