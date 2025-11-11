package es.luna;

import javafx.fxml.FXML;
import javafx.scene.control.Alert;
import javafx.scene.control.ButtonType;
import javafx.scene.control.MenuItem;
import javafx.scene.layout.VBox;
import javafx.scene.Scene;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Optional;

/**
 * Controlador para la ventana principal de ScriptumFX.
 * Gestiona los eventos de la interfaz de usuario.
 *
 * @version 1.0
 * @since 2025-11-11
 */
public class VentanaController {

    /** Logger para registrar eventos del controlador */
    private static final Logger logger = LoggerFactory.getLogger(VentanaController.class);

    @FXML
    @SuppressWarnings("unused") // Inyectado por JavaFX desde el FXML
    private VBox root;

    @FXML
    @SuppressWarnings("unused") // Inyectado por JavaFX desde el FXML
    private MenuItem menuThemeToggle;

    @FXML
    @SuppressWarnings("unused") // Inyectado por JavaFX desde el FXML
    private MenuItem menuAbout;

    @FXML
    @SuppressWarnings("unused") // Inyectado por JavaFX desde el FXML
    private MenuItem menuExit;

    /** Estado actual del tema (true = claro, false = oscuro) */
    private boolean temaClaro = true;

    /**
     * Metodo de inicialización del controlador.
     * Se ejecuta automáticamente después de que se hayan cargado los elementos FXML.
     */
    @FXML
    @SuppressWarnings("unused") // Llamado automáticamente por JavaFX
    public void initialize() {
        logger.debug("Inicializando controlador VentanaController");

        // Configurar evento para cambiar tema
        if (menuThemeToggle != null) {
            menuThemeToggle.setOnAction(e -> cambiarTema());
        }

        // Configurar evento para "Acerca de"
        if (menuAbout != null) {
            menuAbout.setOnAction(e -> mostrarAcercaDe());
        }

        // Configurar evento para "Salir"
        if (menuExit != null) {
            menuExit.setOnAction(e -> salirAplicacion());
        }

        // Cargar CSS inicial (tema claro) después de que la ventana esté lista
        root.sceneProperty().addListener((obs, oldVal, newScene) -> {
            if (newScene != null) {
                aplicarTemaInicial();
            }
        });

        logger.info("Controlador inicializado correctamente");
    }

    /**
     * Aplica el tema claro inicial cuando la escena está lista.
     */
    private void aplicarTemaInicial() {
        try {
            Scene scene = root.getScene();
            if (scene != null) {
                var cssClaro = getClass().getResource("/es/luna/css/estilos_claro.css");
                if (cssClaro != null) {
                    scene.getStylesheets().add(cssClaro.toExternalForm());
                    logger.info("Tema claro inicial aplicado");
                } else {
                    logger.warn("No se encontró el CSS para el tema claro inicial");
                }
            }
        } catch (Exception e) {
            logger.error("Error al aplicar tema inicial", e);
        }
    }

    /**
     * Cambia entre el tema claro y oscuro de la aplicación.
     */
    @FXML
    private void cambiarTema() {
        try {
            logger.info("=== Iniciando cambio de tema ===");
            logger.info("Estado actual temaClaro: {}", temaClaro);

            if (root == null) {
                logger.error("root es null, no se puede cambiar el tema");
                return;
            }
            logger.info("root OK: {}", root.getClass().getName());

            Scene scene = root.getScene();
            if (scene == null) {
                logger.error("scene es null, no se puede cambiar el tema");
                return;
            }
            logger.info("scene OK");

            logger.info("Stylesheets actuales antes de clear: {}", scene.getStylesheets());
            scene.getStylesheets().clear();
            logger.info("Stylesheets después de clear: {}", scene.getStylesheets());

            if (temaClaro) {
                // Cambiar a tema oscuro
                var cssOscuro = getClass().getResource("/es/luna/css/estilos_oscuro.css");
                logger.info("URL CSS oscuro: {}", cssOscuro);
                if (cssOscuro != null) {
                    String cssPath = cssOscuro.toExternalForm();
                    logger.info("Añadiendo CSS oscuro: {}", cssPath);
                    scene.getStylesheets().add(cssPath);
                    logger.info("Stylesheets después de añadir oscuro: {}", scene.getStylesheets());
                    menuThemeToggle.setText("Cambiar a Modo Claro");
                    logger.info("Tema cambiado a oscuro");
                } else {
                    logger.warn("No se encontró el archivo CSS para tema oscuro");
                }
            } else {
                // Cambiar a tema claro
                var cssClaro = getClass().getResource("/es/luna/css/estilos_claro.css");
                logger.info("URL CSS claro: {}", cssClaro);
                if (cssClaro != null) {
                    String cssPath = cssClaro.toExternalForm();
                    logger.info("Añadiendo CSS claro: {}", cssPath);
                    scene.getStylesheets().add(cssPath);
                    logger.info("Stylesheets después de añadir claro: {}", scene.getStylesheets());
                    menuThemeToggle.setText("Cambiar a Modo Oscuro");
                    logger.info("Tema cambiado a claro");
                } else {
                    logger.warn("No se encontró el archivo CSS para tema claro");
                }
            }

            temaClaro = !temaClaro;
            logger.info("Nuevo estado temaClaro: {}", temaClaro);

        } catch (Exception e) {
            logger.error("Error al cambiar el tema", e);
        }
    }

    /**
     * Muestra el diálogo "Acerca de" con información de la aplicación.
     */
    @FXML
    private void mostrarAcercaDe() {
        logger.debug("Mostrando ventana 'Acerca de'");

        // Crear diálogo de información
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Acerca de ScriptumFX");
        alert.setHeaderText("ScriptumFX - Aplicación de Cifrado");

        // Contenido con información de la aplicación
        String contenido = """
                Versión: 1.0

                Aplicación de cifrado y descifrado de mensajes
                utilizando diferentes métodos criptográficos.

                Autoras:
                • Arantxa
                • Wara

                © 2025 - Todos los derechos reservados
                """;

        alert.setContentText(contenido);

        // Mostrar diálogo
        alert.showAndWait();

        logger.info("Diálogo 'Acerca de' mostrado");
    }

    /**
     * Cierra la aplicación mostrando un diálogo de confirmación.
     */
    @FXML
    private void salirAplicacion() {
        logger.debug("Solicitando confirmación para cerrar la aplicación");

        // Crear diálogo de confirmación
        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("Confirmar salida");
        alert.setHeaderText("¿Desea salir de ScriptumFX?");
        alert.setContentText("Se perderán los datos no guardados.");

        // Personalizar botones
        ButtonType buttonSalir = new ButtonType("Salir");
        ButtonType buttonCancelar = new ButtonType("Cancelar");
        alert.getButtonTypes().setAll(buttonSalir, buttonCancelar);

        // Mostrar diálogo y esperar respuesta
        Optional<ButtonType> resultado = alert.showAndWait();

        if (resultado.isPresent() && resultado.get() == buttonSalir) {
            logger.info("Usuario confirmó salida - Cerrando aplicación");
            System.exit(0);
        } else {
            logger.info("Usuario canceló salida");
        }
    }
}