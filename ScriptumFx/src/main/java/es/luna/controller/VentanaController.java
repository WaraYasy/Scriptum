package es.luna.controller;

import es.luna.config.ApiConfig;
import es.luna.model.*;
import es.luna.service.AesService;
import es.luna.service.VigenereService;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.fxml.FXML;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.input.Clipboard;
import javafx.scene.input.ClipboardContent;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Optional;

/**
 * Controlador para la ventana principal de ScriptumFX.
 * Gestiona los eventos de la interfaz de usuario y las operaciones de cifrado/descifrado.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class VentanaController {

    private static final Logger logger = LoggerFactory.getLogger(VentanaController.class);

    // ========== Elementos del menú ==========
    @FXML private VBox root;
    @FXML private MenuItem menuThemeToggle;
    @FXML private MenuItem menuAbout;
    @FXML private MenuItem menuExit;

    // ========== Estado de la API ==========
    @FXML private Label lblEstadoApi;
    @FXML private ProgressIndicator progressConexion;

    // ========== Campos de entrada/salida ==========
    @FXML private TextArea txtEntrada;
    @FXML private TextArea txtSalida;
    @FXML private Button btnSubirArchivo;
    @FXML private Button btnVaciarEntrada;
    @FXML private Button btnCopiar;
    @FXML private Button btnDescargar;
    @FXML private Button btnVaciarSalida;

    // ========== Configuración de cifrado ==========
    @FXML private ComboBox<String> comboModo;
    @FXML private ComboBox<String> comboMetodo;
    @FXML private Label lblDescripcionMetodo;
    @FXML private Label lblResultado;
    @FXML private ProgressIndicator progressOperacion;

    // ========== Campos específicos de Vigenère ==========
    @FXML private VBox vboxClaveVigenere;
    @FXML private TextField txtClaveVigenere;

    // ========== Campos específicos de AES ==========
    @FXML private VBox vboxCamposAes;
    @FXML private TextField txtPasswordAes;
    @FXML private ComboBox<String> comboTipoAes;
    @FXML private VBox vboxSaltAes;
    @FXML private TextField txtSaltAes;

    // ========== Botón de acción ==========
    @FXML private Button btnAccion;
    @FXML private Label lblMensajeEstado;

    // ========== Servicios ==========
    private VigenereService vigenereService;
    private AesService aesService;

    // ========== Estado ==========
    private boolean temaClaro = true;
    private String ultimoSaltGenerado = null; // Para guardar el salt del último cifrado AES

    /**
     * Inicialización del controlador.
     * Se ejecuta automáticamente al cargar el FXML.
     */
    @FXML
    public void initialize() {
        logger.info("=== Inicializando VentanaController ===");

        // Inicializar servicios
        inicializarServicios();

        // Configurar elementos del menú
        configurarMenu();

        // Configurar combos
        configurarCombos();

        // Configurar tema inicial
        configurarTemaInicial();

        // Verificar conexión con la API
        verificarConexionApi();

        logger.info("Controlador inicializado correctamente");
    }

    /**
     * Inicializa los servicios de Vigenère y AES.
     */
    private void inicializarServicios() {
        try {
            String apiUrl = ApiConfig.API_BASE_URL;
            logger.info("Inicializando servicios con API URL: {}", apiUrl);

            vigenereService = new VigenereService(apiUrl);
            aesService = new AesService(apiUrl);

            logger.info("Servicios inicializados correctamente");
        } catch (Exception e) {
            logger.error("Error al inicializar servicios", e);
            mostrarAlerta(
                "Error de inicialización",
                "No se pudieron inicializar los servicios de cifrado",
                Alert.AlertType.ERROR
            );
        }
    }

    /**
     * Configura el menú de la aplicación.
     */
    private void configurarMenu() {
        if (menuThemeToggle != null) {
            menuThemeToggle.setOnAction(e -> cambiarTema());
        }

        if (menuAbout != null) {
            menuAbout.setOnAction(e -> mostrarAcercaDe());
        }

        if (menuExit != null) {
            menuExit.setOnAction(e -> salirAplicacion());
        }
    }

    /**
     * Configura los ComboBox con sus opciones.
     */
    private void configurarCombos() {
        // Combo de modo (Cifrar/Descifrar)
        comboModo.setItems(FXCollections.observableArrayList("Cifrar", "Descifrar"));
        comboModo.setValue("Cifrar");

        // Combo de metodo (Vigenère/AES)
        comboMetodo.setItems(FXCollections.observableArrayList("Vigenère", "AES"));
        comboMetodo.setValue("Vigenère");

        // Combo de tipo AES
        comboTipoAes.setItems(FXCollections.observableArrayList("AES-128", "AES-192", "AES-256"));
        comboTipoAes.setValue("AES-256");

        // Actualizar descripción inicial
        actualizarDescripcionMetodo();
        actualizarCamposSegunMetodo();
    }

    /**
     * Configura el tema inicial.
     */
    private void configurarTemaInicial() {
        root.sceneProperty().addListener((obs, oldVal, newScene) -> {
            if (newScene != null) {
                aplicarTemaInicial();
            }
        });
    }

    /**
     * Aplica el tema claro inicial.
     */
    private void aplicarTemaInicial() {
        try {
            Scene scene = root.getScene();
            if (scene != null) {
                var cssClaro = getClass().getResource("/es/luna/css/estilos_claro.css");
                if (cssClaro != null) {
                    scene.getStylesheets().add(cssClaro.toExternalForm());
                    logger.info("Tema claro inicial aplicado");
                }
            }
        } catch (Exception e) {
            logger.error("Error al aplicar tema inicial", e);
        }
    }

    /**
     * Verifica la conexión con la API al iniciar.
     */
    private void verificarConexionApi() {
        lblEstadoApi.setText("Verificando...");
        lblEstadoApi.setStyle("-fx-text-fill: orange;");
        progressConexion.setVisible(true);

        vigenereService.verificarConexion()
            .thenAccept(conectado -> Platform.runLater(() -> {
                progressConexion.setVisible(false);
                if (conectado) {
                    lblEstadoApi.setText("✓ Conectada");
                    lblEstadoApi.setStyle("-fx-text-fill: green;");
                    logger.info("Conexión con API exitosa");
                } else {
                    lblEstadoApi.setText("✗ Desconectada");
                    lblEstadoApi.setStyle("-fx-text-fill: red;");
                    logger.warn("No se pudo conectar con la API");
                    mostrarAlerta(
                        "Error de conexión",
                        "No se pudo conectar con la API en " + ApiConfig.API_BASE_URL +
                        "\n\nAsegúrate de que el backend esté ejecutándose.",
                        Alert.AlertType.WARNING
                    );
                }
            }));
    }

    // ==================== EVENTOS DE LA UI ====================

    /**
     * Maneja el cambio de modo (Cifrar/Descifrar).
     */
    @FXML
    private void onModoChanged() {
        String modo = comboModo.getValue();
        String metodo = comboMetodo.getValue();

        // Actualizar texto del botón
        if ("Cifrar".equals(modo)) {
            btnAccion.setText("🔒 Cifrar");
            lblResultado.setText("Resultado del cifrado");
        } else {
            btnAccion.setText("🔓 Descifrar");
            lblResultado.setText("Resultado del descifrado");
        }

        // Mostrar/ocultar campo de salt para AES
        if ("AES".equals(metodo)) {
            boolean esDescifrado = "Descifrar".equals(modo);
            vboxSaltAes.setManaged(esDescifrado);
            vboxSaltAes.setVisible(esDescifrado);
        }

        logger.debug("Modo cambiado a: {}", modo);
    }

    /**
     * Maneja el cambio de metodo (Vigenère/AES).
     */
    @FXML
    private void onMetodoChanged() {
        actualizarDescripcionMetodo();
        actualizarCamposSegunMetodo();
    }

    /**
     * Actualiza la descripción del metodo seleccionado.
     */
    private void actualizarDescripcionMetodo() {
        String metodo = comboMetodo.getValue();

        if ("Vigenère".equals(metodo)) {
            lblDescripcionMetodo.setText(
                "Vigenère: Cifrado clásico polialfabético que usa una clave repetida " +
                "para desplazar letras con patrones variables. Seguro para mensajes de texto."
            );
        } else if ("AES".equals(metodo)) {
            lblDescripcionMetodo.setText(
                "AES: Cifrado simétrico moderno de nivel militar. Extremadamente seguro, " +
                "soporta AES-128, AES-192 y AES-256 bits. Recomendado para datos sensibles."
            );
        }
    }

    /**
     * Muestra/oculta campos según el metodo seleccionado.
     */
    private void actualizarCamposSegunMetodo() {
        String metodo = comboMetodo.getValue();
        String modo = comboModo.getValue();

        if ("Vigenère".equals(metodo)) {
            // Mostrar campos de Vigenère
            vboxClaveVigenere.setManaged(true);
            vboxClaveVigenere.setVisible(true);

            // Ocultar campos de AES
            vboxCamposAes.setManaged(false);
            vboxCamposAes.setVisible(false);

        } else if ("AES".equals(metodo)) {
            // Ocultar campos de Vigenère
            vboxClaveVigenere.setManaged(false);
            vboxClaveVigenere.setVisible(false);

            // Mostrar campos de AES
            vboxCamposAes.setManaged(true);
            vboxCamposAes.setVisible(true);

            // Mostrar/ocultar salt según modo
            boolean esDescifrado = "Descifrar".equals(modo);
            vboxSaltAes.setManaged(esDescifrado);
            vboxSaltAes.setVisible(esDescifrado);
        }
    }

    /**
     * Acción principal: Cifrar o Descifrar según la configuración.
     */
    @FXML
    private void onAccionPrincipal() {
        String modo = comboModo.getValue();
        String metodo = comboMetodo.getValue();

        logger.info("Ejecutando acción: {} con {}", modo, metodo);

        // Validar que haya texto de entrada
        String texto = txtEntrada.getText();
        if (texto == null || texto.trim().isEmpty()) {
            mostrarAlerta("Campo vacío", "Por favor, introduce un texto", Alert.AlertType.WARNING);
            return;
        }

        // Ejecutar la operación correspondiente
        if ("Vigenère".equals(metodo)) {
            if ("Cifrar".equals(modo)) {
                cifrarVigenere(texto);
            } else {
                descifrarVigenere(texto);
            }
        } else if ("AES".equals(metodo)) {
            if ("Cifrar".equals(modo)) {
                cifrarAes(texto);
            } else {
                descifrarAes(texto);
            }
        }
    }

    /**
     * Cifra texto con Vigenère.
     */
    private void cifrarVigenere(String texto) {
        String clave = txtClaveVigenere.getText();

        if (clave == null || clave.trim().isEmpty()) {
            mostrarAlerta("Clave vacía", "Por favor, introduce una clave", Alert.AlertType.WARNING);
            return;
        }

        // Mostrar indicador de carga
        mostrarCargando(true);
        lblMensajeEstado.setText("Cifrando con Vigenère...");

        // Llamada asíncrona
        vigenereService.cifrarTexto(texto, clave)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoCifrado());
                lblMensajeEstado.setText("✓ Cifrado exitoso con clave: " + response.getClaveUsada());
                lblMensajeEstado.setStyle("-fx-text-fill: green;");
                mostrarCargando(false);
                logger.info("Cifrado Vigenère exitoso");
            }))
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    String mensaje = obtenerMensajeError(error);
                    lblMensajeEstado.setText("✗ Error: " + mensaje);
                    lblMensajeEstado.setStyle("-fx-text-fill: red;");
                    mostrarCargando(false);
                    mostrarAlerta("Error al cifrar", mensaje, Alert.AlertType.ERROR);
                });
                return null;
            });
    }

    /**
     * Descifra texto con Vigenère.
     */
    private void descifrarVigenere(String textoCifrado) {
        String clave = txtClaveVigenere.getText();

        if (clave == null || clave.trim().isEmpty()) {
            mostrarAlerta("Clave vacía", "Por favor, introduce una clave", Alert.AlertType.WARNING);
            return;
        }

        // Mostrar indicador de carga
        mostrarCargando(true);
        lblMensajeEstado.setText("Descifrando con Vigenère...");

        // Llamada asíncrona
        vigenereService.descifrarTexto(textoCifrado, clave)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoDescifrado());
                lblMensajeEstado.setText("✓ Descifrado exitoso");
                lblMensajeEstado.setStyle("-fx-text-fill: green;");
                mostrarCargando(false);
                logger.info("Descifrado Vigenère exitoso");
            }))
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    String mensaje = obtenerMensajeError(error);
                    lblMensajeEstado.setText("✗ Error: " + mensaje);
                    lblMensajeEstado.setStyle("-fx-text-fill: red;");
                    mostrarCargando(false);
                    mostrarAlerta("Error al descifrar", mensaje, Alert.AlertType.ERROR);
                });
                return null;
            });
    }

    /**
     * Cifra texto con AES.
     */
    private void cifrarAes(String texto) {
        String password = txtPasswordAes.getText();
        String tipoAes = comboTipoAes.getValue();

        if (password == null || password.length() < 8) {
            mostrarAlerta(
                "Password inválido",
                "El password debe tener al menos 8 caracteres",
                Alert.AlertType.WARNING
            );
            return;
        }

        // Mostrar indicador de carga
        mostrarCargando(true);
        lblMensajeEstado.setText("Cifrando con " + tipoAes + "...");

        // Llamada asíncrona
        aesService.cifrarTexto(texto, password, tipoAes)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoCifrado());
                ultimoSaltGenerado = response.getSalt();

                lblMensajeEstado.setText("✓ Cifrado exitoso con " + response.getTipoAes());
                lblMensajeEstado.setStyle("-fx-text-fill: green;");
                mostrarCargando(false);

                // Mostrar alert con el salt y opción de copiar
                mostrarAlertaSaltConBotonCopiar(response.getSalt());

                logger.info("Cifrado AES exitoso");
            }))
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    String mensaje = obtenerMensajeError(error);
                    lblMensajeEstado.setText("✗ Error: " + mensaje);
                    lblMensajeEstado.setStyle("-fx-text-fill: red;");
                    mostrarCargando(false);
                    mostrarAlerta("Error al cifrar", mensaje, Alert.AlertType.ERROR);
                });
                return null;
            });
    }

    /**
     * Descifra texto con AES.
     */
    private void descifrarAes(String textoCifrado) {
        String password = txtPasswordAes.getText();
        String salt = txtSaltAes.getText();
        String tipoAes = comboTipoAes.getValue();

        if (password == null || password.length() < 8) {
            mostrarAlerta(
                "Password inválido",
                "El password debe tener al menos 8 caracteres",
                Alert.AlertType.WARNING
            );
            return;
        }

        if (salt == null || salt.trim().isEmpty()) {
            mostrarAlerta(
                "Salt vacío",
                "Por favor, introduce el salt que obtuviste al cifrar",
                Alert.AlertType.WARNING
            );
            return;
        }

        // Mostrar indicador de carga
        mostrarCargando(true);
        lblMensajeEstado.setText("Descifrando con " + tipoAes + "...");

        // Llamada asíncrona
        aesService.descifrarTexto(textoCifrado, password, salt, tipoAes)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoDescifrado());
                lblMensajeEstado.setText("✓ Descifrado exitoso");
                lblMensajeEstado.setStyle("-fx-text-fill: green;");
                mostrarCargando(false);
                logger.info("Descifrado AES exitoso");
            }))
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    String mensaje = obtenerMensajeError(error);
                    lblMensajeEstado.setText("✗ Error: " + mensaje);
                    lblMensajeEstado.setStyle("-fx-text-fill: red;");
                    mostrarCargando(false);

                    // Mensaje más específico para errores de AES
                    if (mensaje.contains("autenticación") || mensaje.contains("tag")) {
                        mostrarAlerta(
                            "Error al descifrar",
                            "Password o salt incorrectos.\n\nVerifica que:\n" +
                            "• El password sea el mismo que usaste al cifrar\n" +
                            "• El salt sea exactamente el que se generó al cifrar\n" +
                            "• El tipo de AES sea el correcto",
                            Alert.AlertType.ERROR
                        );
                    } else {
                        mostrarAlerta("Error al descifrar", mensaje, Alert.AlertType.ERROR);
                    }
                });
                return null;
            });
    }

    /**
     * Sube un archivo de texto.
     */
    @FXML
    private void onSubirArchivo() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Seleccionar archivo de texto");
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter("Archivos de texto", "*.txt")
        );

        File archivo = fileChooser.showOpenDialog(root.getScene().getWindow());

        if (archivo != null) {
            try {
                String contenido = Files.readString(archivo.toPath());
                txtEntrada.setText(contenido);
                logger.info("Archivo cargado: {}", archivo.getName());
            } catch (IOException e) {
                logger.error("Error al leer archivo", e);
                mostrarAlerta("Error", "No se pudo leer el archivo", Alert.AlertType.ERROR);
            }
        }
    }

    /**
     * Vacía el campo de entrada.
     */
    @FXML
    private void onVaciarEntrada() {
        txtEntrada.clear();
    }

    /**
     * Vacía el campo de salida.
     */
    @FXML
    private void onVaciarSalida() {
        txtSalida.clear();
        lblMensajeEstado.setText("");
    }

    /**
     * Copia el resultado al portapapeles.
     */
    @FXML
    private void onCopiar() {
        String texto = txtSalida.getText();
        if (texto != null && !texto.isEmpty()) {
            Clipboard clipboard = Clipboard.getSystemClipboard();
            ClipboardContent content = new ClipboardContent();
            content.putString(texto);
            clipboard.setContent(content);

            lblMensajeEstado.setText("✓ Texto copiado al portapapeles");
            lblMensajeEstado.setStyle("-fx-text-fill: green;");
            logger.info("Texto copiado al portapapeles");
        } else {
            mostrarAlerta("Campo vacío", "No hay texto para copiar", Alert.AlertType.WARNING);
        }
    }

    /**
     * Descarga el resultado como archivo.
     */
    @FXML
    private void onDescargar() {
        String texto = txtSalida.getText();
        if (texto == null || texto.isEmpty()) {
            mostrarAlerta("Campo vacío", "No hay texto para descargar", Alert.AlertType.WARNING);
            return;
        }

        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Guardar resultado");
        fileChooser.setInitialFileName("resultado.txt");
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter("Archivos de texto", "*.txt")
        );

        File archivo = fileChooser.showSaveDialog(root.getScene().getWindow());

        if (archivo != null) {
            try {
                Files.writeString(archivo.toPath(), texto);
                lblMensajeEstado.setText("✓ Archivo guardado: " + archivo.getName());
                lblMensajeEstado.setStyle("-fx-text-fill: green;");
                logger.info("Archivo guardado: {}", archivo.getAbsolutePath());
            } catch (IOException e) {
                logger.error("Error al guardar archivo", e);
                mostrarAlerta("Error", "No se pudo guardar el archivo", Alert.AlertType.ERROR);
            }
        }
    }

    // ==================== FUNCIONES DEL MENÚ ====================

    /**
     * Cambia entre tema claro y oscuro.
     */
    private void cambiarTema() {
        try {
            Scene scene = root.getScene();
            if (scene == null) return;

            scene.getStylesheets().clear();

            if (temaClaro) {
                var cssOscuro = getClass().getResource("/es/luna/css/estilos_oscuro.css");
                if (cssOscuro != null) {
                    scene.getStylesheets().add(cssOscuro.toExternalForm());
                    menuThemeToggle.setText("Cambiar a Modo Claro");
                }
            } else {
                var cssClaro = getClass().getResource("/es/luna/css/estilos_claro.css");
                if (cssClaro != null) {
                    scene.getStylesheets().add(cssClaro.toExternalForm());
                    menuThemeToggle.setText("Cambiar a Modo Oscuro");
                }
            }

            temaClaro = !temaClaro;
            logger.info("Tema cambiado a: {}", temaClaro ? "claro" : "oscuro");

        } catch (Exception e) {
            logger.error("Error al cambiar tema", e);
        }
    }

    /**
     * Muestra el diálogo "Acerca de".
     */
    private void mostrarAcercaDe() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Acerca de ScriptumFX");
        alert.setHeaderText("ScriptumFX - Aplicación de Cifrado");
        alert.setContentText(
            "Versión: 1.0\n\n" +
            "Aplicación de cifrado y descifrado de mensajes\n" +
            "utilizando diferentes métodos criptográficos.\n\n" +
            "Métodos soportados:\n" +
            "• Vigenère (cifrado clásico)\n" +
            "• AES-128/192/256 (cifrado moderno)\n\n" +
            "Autoras:\n" +
            "• Arantxa\n" +
            "• Wara\n\n" +
            "© 2025 - Todos los derechos reservados"
        );
        alert.showAndWait();
    }

    /**
     * Sale de la aplicación con confirmación.
     */
    private void salirAplicacion() {
        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("Confirmar salida");
        alert.setHeaderText("¿Desea salir de ScriptumFX?");
        alert.setContentText("Se perderán los datos no guardados.");

        ButtonType buttonSalir = new ButtonType("Salir");
        ButtonType buttonCancelar = new ButtonType("Cancelar");
        alert.getButtonTypes().setAll(buttonSalir, buttonCancelar);

        Optional<ButtonType> resultado = alert.showAndWait();

        if (resultado.isPresent() && resultado.get() == buttonSalir) {
            logger.info("Cerrando aplicación");
            System.exit(0);
        }
    }

    // ==================== UTILIDADES ====================

    /**
     * Muestra/oculta indicadores de carga.
     */
    private void mostrarCargando(boolean mostrar) {
        progressOperacion.setVisible(mostrar);
        btnAccion.setDisable(mostrar);
    }

    /**
     * Extrae el mensaje de error de una excepción.
     */
    private String obtenerMensajeError(Throwable error) {
        Throwable causa = error.getCause();
        if (causa != null) {
            return causa.getMessage();
        }
        return error.getMessage();
    }

    /**
     * Muestra un diálogo de alerta.
     */
    private void mostrarAlerta(String titulo, String mensaje, Alert.AlertType tipo) {
        Alert alert = new Alert(tipo);
        alert.setTitle(titulo);
        alert.setHeaderText(null);
        alert.setContentText(mensaje);
        alert.showAndWait();
    }

    /**
     * Muestra una alerta especial para el salt con opción de copiarlo al portapapeles.
     */
    private void mostrarAlertaSaltConBotonCopiar(String salt) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Cifrado exitoso");
        alert.setHeaderText("¡IMPORTANTE! Guarda este SALT");
        alert.setContentText(
            "Necesitarás este SALT para poder descifrar el mensaje:\n\n" +
            salt + "\n\n" +
            "Sin el salt no podrás recuperar el mensaje original."
        );

        // Crear botón personalizado para copiar
        ButtonType btnCopiarSalt = new ButtonType("Copiar SALT");
        ButtonType btnCerrar = new ButtonType("Cerrar", ButtonBar.ButtonData.CANCEL_CLOSE);

        alert.getButtonTypes().setAll(btnCopiarSalt, btnCerrar);

        // Manejar la acción del botón
        Optional<ButtonType> resultado = alert.showAndWait();

        if (resultado.isPresent() && resultado.get() == btnCopiarSalt) {
            // Copiar salt al portapapeles
            Clipboard clipboard = Clipboard.getSystemClipboard();
            ClipboardContent content = new ClipboardContent();
            content.putString(salt);
            clipboard.setContent(content);

            // Mostrar confirmación
            lblMensajeEstado.setText("✓ SALT copiado al portapapeles");
            lblMensajeEstado.setStyle("-fx-text-fill: green;");
            logger.info("SALT copiado al portapapeles");
        }
    }
}
