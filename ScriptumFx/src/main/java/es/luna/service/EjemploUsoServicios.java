package es.luna.service;

import es.luna.client.ApiClient;
import javafx.application.Platform;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Clase de ejemplo que muestra cómo usar los servicios de Vigenère y AES
 * desde los controladores de JavaFX.
 * IMPORTANTE: Las peticiones HTTP son asíncronas para no bloquear la UI de JavaFX.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class EjemploUsoServicios {

    private static final Logger logger = LoggerFactory.getLogger(EjemploUsoServicios.class);

    /** URL de la API (configurable) */
    private static final String API_URL = "http://localhost:8000";

    /**
     * Ejemplo de uso del servicio Vigenère para cifrar texto.
     */
    public void ejemploCifrarVigenere() {
        // Crear instancia del servicio
        VigenereService vigenereService = new VigenereService(API_URL);

        // Datos de entrada (estos vendrían de los campos de texto de la UI)
        String textoOriginal = "Hola Mundo";
        String clave = "CLAVE";

        // Realizar cifrado de forma asíncrona
        vigenereService.cifrarTexto(textoOriginal, clave)
                .thenAccept(response -> {
                    // Esta lambda se ejecuta cuando la petición se completa exitosamente
                    // IMPORTANTE: Actualizar la UI en el hilo de JavaFX
                    Platform.runLater(() -> {
                        String textoCifrado = response.getTextoCifrado();
                        logger.info("Texto cifrado: {}", textoCifrado);

                        // Aquí actualizarías los componentes de la UI:
                        // txtResultado.setText(textoCifrado);
                        // lblInfo.setText("Cifrado exitoso con clave: " + response.getClaveUsada());
                    });
                })
                .exceptionally(error -> {
                    // Esta lambda se ejecuta si hay un error
                    Platform.runLater(() -> {
                        logger.error("Error al cifrar", error);

                        // Mostrar error en la UI:
                        // mostrarAlerta("Error", "No se pudo cifrar el texto: " + error.getMessage());
                    });
                    return null;
                });
    }

    /**
     * Ejemplo de uso del servicio Vigenère para descifrar texto.
     */
    public void ejemploDescifrarVigenere() {
        VigenereService vigenereService = new VigenereService(API_URL);

        String textoCifrado = "RIJVSUYVJN";
        String clave = "CLAVE";

        vigenereService.descifrarTexto(textoCifrado, clave)
                .thenAccept(response -> {
                    Platform.runLater(() -> {
                        String textoDescifrado = response.getTextoDescifrado();
                        logger.info("Texto descifrado: {}", textoDescifrado);
                        // Actualizar UI...
                    });
                })
                .exceptionally(error -> {
                    Platform.runLater(() -> {
                        logger.error("Error al descifrar", error);
                        // Mostrar error en UI...
                    });
                    return null;
                });
    }

    /**
     * Ejemplo de uso del servicio AES para cifrar texto.
     */
    public void ejemploCifrarAes() {
        AesService aesService = new AesService(API_URL);

        String textoOriginal = "Este es un mensaje secreto";
        String password = "mi_password_seguro_123";
        String tipoAes = "AES-256";

        aesService.cifrarTexto(textoOriginal, password, tipoAes)
                .thenAccept(response -> {
                    Platform.runLater(() -> {
                        String textoCifrado = response.getTextoCifrado();
                        String salt = response.getSalt();

                        logger.info("Texto cifrado: {}", textoCifrado);
                        logger.info("Salt (GUARDAR!): {}", salt);

                        // IMPORTANTE: El salt debe guardarse para poder descifrar después
                        // txtResultado.setText(textoCifrado);
                        // txtSalt.setText(salt);
                        // mostrarAlerta("Importante", "Guarda el salt para poder descifrar después: " + salt);
                    });
                })
                .exceptionally(error -> {
                    Platform.runLater(() -> {
                        logger.error("Error al cifrar con AES", error);
                        // Mostrar error en UI...
                    });
                    return null;
                });
    }

    /**
     * Ejemplo de uso del servicio AES para descifrar texto.
     */
    public void ejemploDescifrarAes() {
        AesService aesService = new AesService(API_URL);

        String textoCifrado = "VGhpcyBpcyBhbiBlbmNyeXB0ZWQgdGV4dA==";
        String password = "mi_password_seguro_123";
        String salt = "cmFuZG9tc2FsdDEyMzQ1Ng=="; // El salt obtenido al cifrar
        String tipoAes = "AES-256";

        aesService.descifrarTexto(textoCifrado, password, salt, tipoAes)
                .thenAccept(response -> {
                    Platform.runLater(() -> {
                        String textoDescifrado = response.getTextoDescifrado();
                        logger.info("Texto descifrado: {}", textoDescifrado);
                        // Actualizar UI...
                    });
                })
                .exceptionally(error -> {
                    Platform.runLater(() -> {
                        logger.error("Error al descifrar con AES", error);

                        // Analizar tipo de error
                        Throwable cause = error.getCause();
                        if (cause instanceof ApiClient.ApiException) {
                            // Error de la API (clave incorrecta, datos inválidos, etc.)
                            // mostrarAlerta("Error", "Password o salt incorrectos");
                        } else {
                            // Error de red o conexión
                            // mostrarAlerta("Error", "No se pudo conectar con la API");
                        }
                    });
                    return null;
                });
    }

    /**
     * Ejemplo de cómo verificar la conexión con la API antes de hacer operaciones.
     */
    public void ejemploVerificarConexion() {
        VigenereService service = new VigenereService(API_URL);

        service.verificarConexion()
                .thenAccept(conectado -> {
                    Platform.runLater(() -> {
                        if (conectado) {
                            logger.info("✓ Conexión con API exitosa");
                            // lblEstadoApi.setText("API: Conectada");
                            // lblEstadoApi.setStyle("-fx-text-fill: green;");
                        } else {
                            logger.warn("✗ No se pudo conectar con la API");
                            // lblEstadoApi.setText("API: Desconectada");
                            // lblEstadoApi.setStyle("-fx-text-fill: red;");
                        }
                    });
                });
    }

    /**
     * Ejemplo de cómo manejar múltiples operaciones en secuencia.
     * Por ejemplo: cifrar un texto y luego descifrarlo.
     */
    public void ejemploOperacionesEnCadena() {
        VigenereService service = new VigenereService(API_URL);

        String textoOriginal = "Mensaje secreto";
        String clave = "MICLAVE";

        // Primero cifrar
        service.cifrarTexto(textoOriginal, clave)
                .thenCompose(cifradoResponse -> {
                    // Cuando el cifrado se completa, descifrar el resultado
                    String textoCifrado = cifradoResponse.getTextoCifrado();
                    logger.info("1. Texto cifrado: {}", textoCifrado);

                    return service.descifrarTexto(textoCifrado, clave);
                })
                .thenAccept(descifradoResponse -> {
                    Platform.runLater(() -> {
                        String textoDescifrado = descifradoResponse.getTextoDescifrado();
                        logger.info("2. Texto descifrado: {}", textoDescifrado);

                        // Verificar que el resultado es correcto
                        if (textoDescifrado.equalsIgnoreCase(textoOriginal.replaceAll("[^a-zA-Z]", ""))) {
                            logger.info("✓ Cifrado y descifrado exitoso");
                        }
                    });
                })
                .exceptionally(error -> {
                    Platform.runLater(() -> {
                        logger.error("Error en operaciones en cadena", error);
                    });
                    return null;
                });
    }

    /**
     * Ejemplo de cómo manejar la UI durante peticiones asíncronas.
     * Muestra indicadores de carga, deshabilita botones, etc.
     */
    public void ejemploConIndicadoresCarga() {
        VigenereService service = new VigenereService(API_URL);

        // Antes de la petición
        Platform.runLater(() -> {
            // btnCifrar.setDisable(true);
            // progressIndicator.setVisible(true);
            // lblEstado.setText("Cifrando...");
        });

        service.cifrarTexto("Texto de prueba", "CLAVE")
                .thenAccept(response -> {
                    Platform.runLater(() -> {
                        // Operación exitosa
                        // txtResultado.setText(response.getTextoCifrado());
                        // lblEstado.setText("Cifrado completado");

                        // Restaurar UI
                        // btnCifrar.setDisable(false);
                        // progressIndicator.setVisible(false);
                    });
                })
                .exceptionally(error -> {
                    Platform.runLater(() -> {
                        // Error
                        // lblEstado.setText("Error al cifrar");

                        // Restaurar UI
                        // btnCifrar.setDisable(false);
                        // progressIndicator.setVisible(false);
                    });
                    return null;
                });
    }
}
