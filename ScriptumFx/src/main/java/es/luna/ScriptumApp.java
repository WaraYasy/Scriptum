package es.luna;

import es.luna.util.Mensajes;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Clase principal de la aplicación JavaFX ScriptumFX.
 * Se encarga de inicializar y mostrar la ventana principal con su FXML.
 *
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class ScriptumApp extends Application {

    /** Logger para registrar eventos y errores de la aplicación */
    private static final Logger logger = LoggerFactory.getLogger(ScriptumApp.class);

    /**
     * Constructor público por defecto.
     * Requerido por el framework JavaFX para instanciar la aplicación.
     */
    public ScriptumApp() {
        // Constructor vacío requerido por JavaFX
    }

    /**
     * Metodo de inicio de la aplicación JavaFX.
     * <p>
     * Es llamado automáticamente por el sistema de lanzamiento de JavaFX tras invocar {@link #launch(String...)}.
     * Se encarga de crear y configurar la ventana principal, cargar el FXML de la vista
     * y aplicar la hoja de estilos CSS.
     * </p>
     *
     * @param primaryStage la ventana principal (stage) proporcionada por el sistema JavaFX.
     * @throws Exception si ocurre un error durante la inicialización de la interfaz gráfica.
     */
    @Override
    public void start(Stage primaryStage) throws Exception {
        try {
            // Cargar archivo FXML con la definición de la interfaz
            logger.debug("Cargando archivo FXML: fxml/ventana.fxml");
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("/es/luna/fxml/ventana.fxml"));

            // Asignar ResourceBundle para internacionalización
            fxmlLoader.setResources(Mensajes.getResourceBundle());
            logger.debug("ResourceBundle asignado al FXMLLoader: {}", Mensajes.getLocaleActual());

            Scene scene = new Scene(fxmlLoader.load());
            logger.info("Archivo FXML cargado exitosamente");

            // Configurar el stage
            primaryStage.setTitle("ScriptumFX - Cifrado de Mensajes");
            primaryStage.setScene(scene);

            // Configurar icono de la aplicación
            var iconResource = ScriptumApp.class.getResource("/es/luna/img/ScriptumIcon.png");
            if (iconResource != null) {
                Image icon = new Image(iconResource.toExternalForm());
                primaryStage.getIcons().add(icon);
                logger.debug("Icono de aplicación cargado correctamente");
            } else {
                logger.warn("No se pudo encontrar el icono de la aplicación en: /es/luna/img/ScriptumIcon.png");
            }

            // Tamaños mínimos
            primaryStage.setMinWidth(1000);
            // No establecer altura mínima para permitir ajuste automático al contenido

            // Centrar la ventana en la pantalla
            primaryStage.centerOnScreen();

            // Mostrar ventana principal
            primaryStage.show();
            logger.info("Ventana principal mostrada correctamente");

        } catch (Exception e) {
            logger.error("Error al iniciar la aplicación", e);
            System.err.println("No se ha podido abrir la ventana.");
            throw e;
        }
    }

    /**
     * Metodo principal de inicio de la aplicación.
     * <p>
     * Este punto de entrada invoca el metodo {@link #launch(String...)} de {@link Application},
     * iniciando el ciclo de vida estándar de una aplicación JavaFX.
     * </p>
     *
     * @param args argumentos de línea de comandos, si los hubiera.
     */
    public static void main(String[] args) {
        logger.info("=== INICIO DE SCRIPTUM FX ===");
        launch(args);
    }
}
