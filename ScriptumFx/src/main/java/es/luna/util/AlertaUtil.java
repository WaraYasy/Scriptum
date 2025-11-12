package es.luna.util;

import javafx.scene.control.Alert;
import javafx.scene.control.ButtonType;
import javafx.scene.control.DialogPane;
import javafx.stage.Window;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Optional;

/**
 * Clase utilitaria para crear y mostrar alertas personalizadas en ScriptumFX.
 * Proporciona métodos convenientes para mostrar diferentes tipos de alertas
 * con estilos consistentes y soporte para temas claro/oscuro.
 *
 * @author Wara
 * @version 1.0
 * @since 2025-11-12
 */
public class AlertaUtil {

    private static final Logger logger = LoggerFactory.getLogger(AlertaUtil.class);
    private static final String CSS_CLARO = "/es/luna/css/estilos_claro.css";
    private static final String CSS_OSCURO = "/es/luna/css/estilos_oscuro.css";

    // Variable estática para mantener el tema actual
    private static boolean temaClaro = true;

    /**
     * Establece el tema actual para las alertas.
     *
     * @param esClaro true para tema claro, false para tema oscuro
     */
    public static void setTemaClaro(boolean esClaro) {
        temaClaro = esClaro;
        logger.debug("Tema de alertas cambiado a: {}", esClaro ? "claro" : "oscuro");
    }

    /**
     * Muestra una alerta de información con owner.
     *
     * @param owner La ventana propietaria (puede ser null)
     * @param titulo El título de la alerta
     * @param mensaje El mensaje a mostrar
     */
    public static void mostrarInfo(Window owner, String titulo, String mensaje) {
        logger.debug("Mostrando alerta INFO: {}", titulo);
        Alert alert = crearAlerta(Alert.AlertType.INFORMATION, titulo, null, mensaje);
        if (owner != null) {
            alert.initOwner(owner);
        }
        aplicarEstilo(alert);
        alert.showAndWait();
    }


    /**
     * Muestra una alerta de advertencia con owner.
     *
     * @param owner La ventana propietaria (puede ser null)
     * @param titulo El título de la alerta
     * @param mensaje El mensaje a mostrar
     */
    public static void mostrarAdvertencia(Window owner, String titulo, String mensaje) {
        logger.debug("Mostrando alerta ADVERTENCIA: {}", titulo);
        Alert alert = crearAlerta(Alert.AlertType.WARNING, titulo, null, mensaje);
        if (owner != null) {
            alert.initOwner(owner);
        }
        aplicarEstilo(alert);
        alert.showAndWait();
    }

    /**
     * Muestra una alerta de error.
     *
     * @param titulo El título de la alerta
     * @param mensaje El mensaje a mostrar
     */
    @Deprecated
    public static void mostrarError(String titulo, String mensaje) {
        mostrarError(null, titulo, mensaje);
    }

    /**
     * Muestra una alerta de error con owner.
     *
     * @param owner La ventana propietaria (puede ser null)
     * @param titulo El título de la alerta
     * @param mensaje El mensaje a mostrar
     */
    public static void mostrarError(Window owner, String titulo, String mensaje) {
        logger.warn("Mostrando alerta ERROR: {} - {}", titulo, mensaje);
        Alert alert = crearAlerta(Alert.AlertType.ERROR, titulo, null, mensaje);
        if (owner != null) {
            alert.initOwner(owner);
        }
        aplicarEstilo(alert);
        alert.showAndWait();
    }

    /**
     * Muestra una alerta de confirmación y retorna true si el usuario acepta.
     *
     * @param titulo El título de la alerta
     * @param mensaje El mensaje a mostrar
     * @return true si el usuario seleccionó OK, false en caso contrario
     */
    @Deprecated
    public static boolean mostrarConfirmacion(String titulo, String mensaje) {
        return mostrarConfirmacion(null, titulo, mensaje);
    }

    /**
     * Muestra una alerta de confirmación con owner y retorna true si el usuario acepta.
     *
     * @param owner La ventana propietaria (puede ser null)
     * @param titulo El título de la alerta
     * @param mensaje El mensaje a mostrar
     * @return true si el usuario eligió OK, false en caso contrario
     */
    public static boolean mostrarConfirmacion(Window owner, String titulo, String mensaje) {
        logger.debug("Mostrando alerta CONFIRMACIÓN: {}", titulo);
        Alert alert = crearAlerta(Alert.AlertType.CONFIRMATION, titulo, null, mensaje);
        if (owner != null) {
            alert.initOwner(owner);
        }
        aplicarEstilo(alert);

        Optional<ButtonType> resultado = alert.showAndWait();
        boolean confirmado = resultado.isPresent() && resultado.get() == ButtonType.OK;
        logger.debug("Resultado de confirmación: {}", confirmado ? "Aceptado" : "Cancelado");
        return confirmado;
    }

    /**
     * Muestra una alerta de confirmación con header personalizado.
     *
     * @param titulo El título de la alerta
     * @param header El texto del header
     * @param mensaje El mensaje a mostrar
     * @return true si el usuario seleccionó OK, false en caso contrario
     */
    @Deprecated
    public static boolean mostrarConfirmacionConHeader(String titulo, String header, String mensaje) {
        return mostrarConfirmacionConHeader(null, titulo, header, mensaje);
    }

    /**
     * Muestra una alerta de confirmación con header personalizado y owner.
     *
     * @param owner La ventana propietaria (puede ser null)
     * @param titulo El título de la alerta
     * @param header El texto del header
     * @param mensaje El mensaje a mostrar
     * @return true si el usuario seleccionó OK, false en caso contrario
     */
    public static boolean mostrarConfirmacionConHeader(Window owner, String titulo, String header, String mensaje) {
        logger.debug("Mostrando alerta CONFIRMACIÓN con header: {}", titulo);
        Alert alert = crearAlerta(Alert.AlertType.CONFIRMATION, titulo, header, mensaje);
        if (owner != null) {
            alert.initOwner(owner);
        }
        aplicarEstilo(alert);

        Optional<ButtonType> resultado = alert.showAndWait();
        boolean confirmado = resultado.isPresent() && resultado.get() == ButtonType.OK;
        logger.debug("Resultado: {}", confirmado ? "Aceptado" : "Cancelado");
        return confirmado;
    }

    /**
     * Muestra una alerta personalizada con header.
     *
     * @param tipo El tipo de alerta
     * @param titulo El título de la alerta
     * @param header El texto del header
     * @param mensaje El mensaje a mostrar
     */
    @Deprecated
    public static void mostrarAlertaConHeader(Alert.AlertType tipo, String titulo, String header, String mensaje) {
        mostrarAlertaConHeader(null, tipo, titulo, header, mensaje);
    }

    /**
     * Muestra una alerta personalizada con header y owner.
     *
     * @param owner La ventana propietaria (puede ser null)
     * @param tipo El tipo de alerta
     * @param titulo El título de la alerta
     * @param header El texto del header
     * @param mensaje El mensaje a mostrar
     */
    public static void mostrarAlertaConHeader(Window owner, Alert.AlertType tipo, String titulo,
                                             String header, String mensaje) {
        logger.debug("Mostrando alerta personalizada ({}): {}", tipo, titulo);
        Alert alert = crearAlerta(tipo, titulo, header, mensaje);
        if (owner != null) {
            alert.initOwner(owner);
        }
        aplicarEstilo(alert);
        alert.showAndWait();
    }

    /**
     * Crea una alerta básica sin mostrarla.
     *
     * @param tipo El tipo de alerta
     * @param titulo El título de la alerta
     * @param header El texto del header (puede ser null)
     * @param mensaje El mensaje a mostrar
     * @return La alerta creada
     */
    private static Alert crearAlerta(Alert.AlertType tipo, String titulo, String header, String mensaje) {
        Alert alert = new Alert(tipo);
        alert.setTitle(titulo);
        alert.setHeaderText(header);
        alert.setContentText(mensaje);
        return alert;
    }

    /**
     * Aplica el estilo CSS correspondiente al tema actual.
     *
     * @param alert La alerta a la que aplicar el estilo
     */
    private static void aplicarEstilo(Alert alert) {
        try {
            DialogPane dialogPane = alert.getDialogPane();
            dialogPane.getStylesheets().clear();

            String cssPath = temaClaro ? CSS_CLARO : CSS_OSCURO;
            var cssResource = AlertaUtil.class.getResource(cssPath);

            if (cssResource != null) {
                String cssUrl = cssResource.toExternalForm();
                dialogPane.getStylesheets().add(cssUrl);
                logger.debug("Aplicado estilo CSS a alerta: {}", cssPath);
            } else {
                logger.warn("No se pudo encontrar el archivo CSS en: {}", cssPath);
            }
        } catch (Exception e) {
            logger.warn("Error al aplicar el estilo CSS a la alerta: {}", e.getMessage());
        }
    }

    /**
     * Muestra una alerta con mensaje internacionalizado.
     *
     * @param tipo El tipo de alerta
     * @param claveTitulo La clave del título en el archivo de mensajes
     * @param claveMensaje La clave del mensaje en el archivo de mensajes
     */
    @Deprecated
    public static void mostrarAlertaI18n(Alert.AlertType tipo, String claveTitulo, String claveMensaje) {
        mostrarAlertaI18n(null, tipo, claveTitulo, claveMensaje);
    }

    /**
     * Muestra una alerta con mensaje internacionalizado y owner.
     *
     * @param owner La ventana propietaria (puede ser null)
     * @param tipo El tipo de alerta
     * @param claveTitulo La clave del título en el archivo de mensajes
     * @param claveMensaje La clave del mensaje en el archivo de mensajes
     */
    public static void mostrarAlertaI18n(Window owner, Alert.AlertType tipo,
                                        String claveTitulo, String claveMensaje) {
        String titulo = Mensajes.obtener(claveTitulo);
        String mensaje = Mensajes.obtener(claveMensaje);

        Alert alert = crearAlerta(tipo, titulo, null, mensaje);
        if (owner != null) {
            alert.initOwner(owner);
        }
        aplicarEstilo(alert);
        alert.showAndWait();
    }
}