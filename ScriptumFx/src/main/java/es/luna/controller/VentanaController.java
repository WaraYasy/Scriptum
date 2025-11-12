package es.luna.controller;

import es.luna.config.ApiConfig;
import es.luna.model.*;
import es.luna.service.AesService;
import es.luna.service.VigenereService;
import es.luna.util.Mensajes;
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
import java.util.Objects;
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
                Mensajes.obtener("error.inicializacion.titulo"),
                Mensajes.obtener("error.inicializacion.mensaje"),
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
        comboModo.setItems(FXCollections.observableArrayList(
            Mensajes.obtener("modo.cifrar"),
            Mensajes.obtener("modo.descifrar")
        ));
        comboModo.setValue(Mensajes.obtener("modo.cifrar"));

        // Combo de metodo (Vigenère/AES)
        comboMetodo.setItems(FXCollections.observableArrayList(
            Mensajes.obtener("metodo.vigenere"),
            Mensajes.obtener("metodo.aes")
        ));
        comboMetodo.setValue(Mensajes.obtener("metodo.vigenere"));

        // Combo de tipo AES
        comboTipoAes.setItems(FXCollections.observableArrayList(
            Mensajes.obtener("aes.tipo.128"),
            Mensajes.obtener("aes.tipo.192"),
            Mensajes.obtener("aes.tipo.256")
        ));
        comboTipoAes.setValue(Mensajes.obtener("aes.tipo.256"));

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
        lblEstadoApi.setText(Mensajes.obtener("api.estado.verificando"));
        lblEstadoApi.setStyle("-fx-text-fill: orange;");
        progressConexion.setVisible(true);

        vigenereService.verificarConexion()
            .thenAccept(conectado -> Platform.runLater(() -> {
                progressConexion.setVisible(false);
                if (conectado) {
                    lblEstadoApi.setText(Mensajes.obtener("api.estado.conectada"));
                    lblEstadoApi.setStyle("-fx-text-fill: green;");
                    logger.info("Conexión con API exitosa");
                } else {
                    lblEstadoApi.setText(Mensajes.obtener("api.estado.desconectada"));
                    lblEstadoApi.setStyle("-fx-text-fill: red;");
                    logger.warn("No se pudo conectar con la API");
                    mostrarAlerta(
                        Mensajes.obtener("error.conexion.titulo"),
                        Mensajes.obtener("error.conexion.mensaje", ApiConfig.API_BASE_URL),
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
        if (Mensajes.obtener("modo.cifrar").equals(modo)) {
            btnAccion.setText(Mensajes.obtener("boton.cifrar"));
            lblResultado.setText(Mensajes.obtener("salida.resultado.cifrado"));
        } else {
            btnAccion.setText(Mensajes.obtener("boton.descifrar"));
            lblResultado.setText(Mensajes.obtener("salida.resultado.descifrado"));
        }

        // Mostrar/ocultar campo de salt para AES
        if (Mensajes.obtener("metodo.aes").equals(metodo)) {
            boolean esDescifrado = Mensajes.obtener("modo.descifrar").equals(modo);
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

        if (Mensajes.obtener("metodo.vigenere").equals(metodo)) {
            lblDescripcionMetodo.setText(Mensajes.obtener("metodo.descripcion.vigenere"));
        } else if (Mensajes.obtener("metodo.aes").equals(metodo)) {
            lblDescripcionMetodo.setText(Mensajes.obtener("metodo.descripcion.aes"));
        }
    }

    /**
     * Muestra/oculta campos según el metodo seleccionado.
     */
    private void actualizarCamposSegunMetodo() {
        String metodo = comboMetodo.getValue();
        String modo = comboModo.getValue();

        if (Mensajes.obtener("metodo.vigenere").equals(metodo)) {
            // Mostrar campos de Vigenère
            vboxClaveVigenere.setManaged(true);
            vboxClaveVigenere.setVisible(true);

            // Ocultar campos de AES
            vboxCamposAes.setManaged(false);
            vboxCamposAes.setVisible(false);

        } else if (Mensajes.obtener("metodo.aes").equals(metodo)) {
            // Ocultar campos de Vigenère
            vboxClaveVigenere.setManaged(false);
            vboxClaveVigenere.setVisible(false);

            // Mostrar campos de AES
            vboxCamposAes.setManaged(true);
            vboxCamposAes.setVisible(true);

            // Mostrar/ocultar salt según modo
            boolean esDescifrado = Mensajes.obtener("modo.descifrar").equals(modo);
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
            mostrarAlerta(
                Mensajes.obtener("validacion.campo.vacio.titulo"),
                Mensajes.obtener("validacion.campo.vacio.mensaje"),
                Alert.AlertType.WARNING
            );
            return;
        }

        // Ejecutar la operación correspondiente
        if (Mensajes.obtener("metodo.vigenere").equals(metodo)) {
            if (Mensajes.obtener("modo.cifrar").equals(modo)) {
                cifrarVigenere(texto);
            } else {
                descifrarVigenere(texto);
            }
        } else if (Mensajes.obtener("metodo.aes").equals(metodo)) {
            if (Mensajes.obtener("modo.cifrar").equals(modo)) {
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
        String clave = validarClave();
        if (clave == null) return;

        mostrarCargando(true);
        lblMensajeEstado.setText(Mensajes.obtener("estado.cifrando.vigenere"));

        vigenereService.cifrarTexto(texto, clave)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoCifrado());
                mostrarExito(Mensajes.obtener("estado.cifrado.exitoso", response.getClaveUsada()));
                logger.info("Cifrado Vigenère exitoso");
            }))
            .exceptionally(error -> manejarErrorOperacion(error, Mensajes.obtener("error.cifrar")));
    }

    /**
     * Descifra texto con Vigenère.
     */
    private void descifrarVigenere(String textoCifrado) {
        String clave = validarClave();
        if (clave == null) return;

        mostrarCargando(true);
        lblMensajeEstado.setText(Mensajes.obtener("estado.descifrando.vigenere"));

        vigenereService.descifrarTexto(textoCifrado, clave)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoDescifrado());
                mostrarExito(Mensajes.obtener("estado.descifrado.exitoso"));
                logger.info("Descifrado Vigenère exitoso");
            }))
            .exceptionally(error -> manejarErrorOperacion(error, Mensajes.obtener("error.descifrar")));
    }

    /**
     * Cifra texto con AES.
     */
    private void cifrarAes(String texto) {
        String password = validarPassword();
        if (password == null) return;

        String tipoAes = comboTipoAes.getValue();
        mostrarCargando(true);
        lblMensajeEstado.setText(Mensajes.obtener("estado.cifrando.aes", tipoAes));

        aesService.cifrarTexto(texto, password, tipoAes)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoCifrado());
                mostrarExito(Mensajes.obtener("estado.cifrado.exitoso.aes", response.getTipoAes()));
                mostrarAlertaSaltConBotonCopiar(response.getSalt());
                logger.info("Cifrado AES exitoso");
            }))
            .exceptionally(error -> manejarErrorOperacion(error, Mensajes.obtener("error.cifrar")));
    }

    /**
     * Descifra texto con AES.
     */
    private void descifrarAes(String textoCifrado) {
        String password = validarPassword();
        if (password == null) return;

        String salt = validarSalt();
        if (salt == null) return;

        String tipoAes = comboTipoAes.getValue();
        mostrarCargando(true);
        lblMensajeEstado.setText(Mensajes.obtener("estado.descifrando.aes", tipoAes));

        aesService.descifrarTexto(textoCifrado, password, salt, tipoAes)
            .thenAccept(response -> Platform.runLater(() -> {
                txtSalida.setText(response.getTextoDescifrado());
                mostrarExito(Mensajes.obtener("estado.descifrado.exitoso"));
                logger.info("Descifrado AES exitoso");
            }))
            .exceptionally(this::manejarErrorAesDescifrado);
    }

    /**
     * Sube un archivo de texto.
     */
    @FXML
    private void onSubirArchivo() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle(Mensajes.obtener("entrada.titulo.dialogo.archivo"));
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter(Mensajes.obtener("entrada.filtro.archivo"), "*.txt")
        );

        File archivo = fileChooser.showOpenDialog(root.getScene().getWindow());

        if (archivo != null) {
            try {
                String contenido = Files.readString(archivo.toPath());
                txtEntrada.setText(contenido);
                logger.info("Archivo cargado: {}", archivo.getName());
            } catch (IOException e) {
                logger.error("Error al leer archivo", e);
                mostrarAlerta(
                    Mensajes.obtener("error.archivo.leer.titulo"),
                    Mensajes.obtener("error.archivo.leer.mensaje"),
                    Alert.AlertType.ERROR
                );
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

            lblMensajeEstado.setText(Mensajes.obtener("estado.copiado"));
            lblMensajeEstado.setStyle("-fx-text-fill: green;");
            logger.info("Texto copiado al portapapeles");
        } else {
            mostrarAlerta(
                Mensajes.obtener("validacion.no.texto.copiar.titulo"),
                Mensajes.obtener("validacion.no.texto.copiar.mensaje"),
                Alert.AlertType.WARNING
            );
        }
    }

    /**
     * Descarga el resultado como archivo.
     */
    @FXML
    private void onDescargar() {
        String texto = txtSalida.getText();
        if (texto == null || texto.isEmpty()) {
            mostrarAlerta(
                Mensajes.obtener("validacion.no.texto.descargar.titulo"),
                Mensajes.obtener("validacion.no.texto.descargar.mensaje"),
                Alert.AlertType.WARNING
            );
            return;
        }

        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle(Mensajes.obtener("salida.titulo.dialogo.guardar"));
        fileChooser.setInitialFileName(Mensajes.obtener("salida.archivo.nombre"));
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter(Mensajes.obtener("entrada.filtro.archivo"), "*.txt")
        );

        File archivo = fileChooser.showSaveDialog(root.getScene().getWindow());

        if (archivo != null) {
            try {
                Files.writeString(archivo.toPath(), texto);
                lblMensajeEstado.setText(Mensajes.obtener("estado.archivo.guardado", archivo.getName()));
                lblMensajeEstado.setStyle("-fx-text-fill: green;");
                logger.info("Archivo guardado: {}", archivo.getAbsolutePath());
            } catch (IOException e) {
                logger.error("Error al guardar archivo", e);
                mostrarAlerta(
                    Mensajes.obtener("error.archivo.guardar.titulo"),
                    Mensajes.obtener("error.archivo.guardar.mensaje"),
                    Alert.AlertType.ERROR
                );
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
                    menuThemeToggle.setText(Mensajes.obtener("menu.tema.claro"));
                }
            } else {
                var cssClaro = getClass().getResource("/es/luna/css/estilos_claro.css");
                if (cssClaro != null) {
                    scene.getStylesheets().add(cssClaro.toExternalForm());
                    menuThemeToggle.setText(Mensajes.obtener("menu.tema.oscuro"));
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
                """
                        Versión: 1.0
                        
                        Aplicación de cifrado y descifrado de mensajes
                        utilizando diferentes métodos criptográficos.
                        
                        Métodos soportados:
                        • Vigenère (cifrado clásico)
                        • AES-128/192/256 (cifrado moderno)
                        
                        Autoras:
                        • Arantxa
                        • Wara
                        
                        © 2025 - Todos los derechos reservados"""
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
     * Valida que la clave de Vigenère no esté vacía.
     * @return La clave si es válida, null si no lo es.
     */
    private String validarClave() {
        String clave = txtClaveVigenere.getText();
        if (clave == null || clave.trim().isEmpty()) {
            mostrarAlerta(
                Mensajes.obtener("validacion.clave.vacia.titulo"),
                Mensajes.obtener("validacion.clave.vacia.mensaje"),
                Alert.AlertType.WARNING
            );
            return null;
        }
        return clave;
    }

    /**
     * Valida que el password de AES tenga al menos 8 caracteres.
     * @return El password si es válido, null si no lo es.
     */
    private String validarPassword() {
        String password = txtPasswordAes.getText();
        if (password == null || password.length() < 8) {
            mostrarAlerta(
                Mensajes.obtener("validacion.password.invalido.titulo"),
                Mensajes.obtener("validacion.password.invalido.mensaje"),
                Alert.AlertType.WARNING
            );
            return null;
        }
        return password;
    }

    /**
     * Valida que el salt no esté vacío.
     * @return El salt si es válido, null si no lo es.
     */
    private String validarSalt() {
        String salt = txtSaltAes.getText();
        if (salt == null || salt.trim().isEmpty()) {
            mostrarAlerta(
                Mensajes.obtener("validacion.salt.vacio.titulo"),
                Mensajes.obtener("validacion.salt.vacio.mensaje"),
                Alert.AlertType.WARNING
            );
            return null;
        }
        return salt;
    }

    /**
     * Muestra un mensaje de éxito y oculta el indicador de carga.
     */
    private void mostrarExito(String mensaje) {
        lblMensajeEstado.setText(mensaje);
        lblMensajeEstado.setStyle("-fx-text-fill: green;");
        mostrarCargando(false);
    }

    /**
     * Maneja errores de operaciones asíncronas de cifrado/descifrado.
     * @return null (requerido por CompletableFuture.exceptionally)
     */
    private Void manejarErrorOperacion(Throwable error, String tituloError) {
        Platform.runLater(() -> {
            String mensaje = obtenerMensajeError(error);
            lblMensajeEstado.setText("✗ Error: " + mensaje);
            lblMensajeEstado.setStyle("-fx-text-fill: red;");
            mostrarCargando(false);
            mostrarAlerta(tituloError, mensaje, Alert.AlertType.ERROR);
        });
        return null;
    }

    /**
     * Maneja errores específicos del descifrado AES.
     * @return null (requerido por CompletableFuture.exceptionally)
     */
    private Void manejarErrorAesDescifrado(Throwable error) {
        Platform.runLater(() -> {
            String mensaje = obtenerMensajeError(error);
            lblMensajeEstado.setText("✗ Error: " + mensaje);
            lblMensajeEstado.setStyle("-fx-text-fill: red;");
            mostrarCargando(false);

            // Mensaje más específico para errores de AES
            if (mensaje.contains("autenticación") || mensaje.contains("tag")) {
                mostrarAlerta(
                    "Error al descifrar",
                        """
                                Password o salt incorrectos.

                                Verifica que:
                                • El password sea el mismo que usaste al cifrar
                                • El salt sea exactamente el que se generó al cifrar
                                • El tipo de AES sea el correcto""",
                    Alert.AlertType.ERROR
                );
            } else {
                mostrarAlerta("Error al descifrar", mensaje, Alert.AlertType.ERROR);
            }
        });
        return null;
    }

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
        return Objects.requireNonNullElse(causa, error).getMessage();
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
