package es.luna.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.MessageFormat;
import java.util.Locale;
import java.util.ResourceBundle;

/**
 * Clase utilitaria para cargar mensajes internacionalizados.
 * Gestiona el acceso al archivo de propiedades de mensajes.
 *
 * @author Wara
 * @version 1.0
 * @since 2025-11-12
 */
public class Mensajes {

    private static final String BUNDLE_NAME = "mensajes";
    private static ResourceBundle bundle;
    private static Locale currentLocale;
    private static final Logger logger = LoggerFactory.getLogger(Mensajes.class);
    static {
        // Por defecto, usar el idioma del sistema
        currentLocale = Locale.getDefault();
        logger.info("Inicializando sistema de mensajes con locale del sistema: {}", currentLocale);
        cargarBundle();
    }

    /**
     * Carga o recarga el ResourceBundle con el locale actual.
     */
    private static void cargarBundle() {
        try {
            bundle = ResourceBundle.getBundle(BUNDLE_NAME, currentLocale);
            logger.info("ResourceBundle cargado exitosamente para locale: {}", currentLocale);
        } catch (Exception e) {
            logger.error("Error al cargar ResourceBundle para locale: {}", currentLocale, e);
            throw e;
        }
    }

    /**
     * Obtiene un mensaje del archivo de propiedades.
     *
     * @param clave La clave del mensaje
     * @return El mensaje correspondiente a la clave
     */
    public static String obtener(String clave) {
        try {
            return bundle.getString(clave);
        } catch (Exception e) {
            logger.warn("Clave de mensaje no encontrada: '{}' en locale: {}", clave, currentLocale);
            return "!" + clave + "!";
        }
    }

    /**
     * Obtiene un mensaje del archivo de propiedades y lo formatea con parámetros.
     * Usa MessageFormat para reemplazar {0}, {1}, etc.
     *
     * @param clave La clave del mensaje
     * @param parametros Los parámetros para formatear el mensaje
     * @return El mensaje formateado
     */
    public static String obtener(String clave, Object... parametros) {
        try {
            String mensaje = bundle.getString(clave);
            return MessageFormat.format(mensaje, parametros);
        } catch (Exception e) {
            logger.warn("Error al obtener/formatear mensaje con clave '{}': {}", clave, e.getMessage());
            return "!" + clave + "!";
        }
    }

    /**
     * Cambia el idioma de la aplicación.
     *
     * @param locale El nuevo locale
     */
    public static void cambiarIdioma(Locale locale) {
        Locale previousLocale = currentLocale;
        currentLocale = locale;
        logger.info("Cambiando idioma de {} a {}", previousLocale, locale);
        cargarBundle();
    }

    /**
     * Obtiene el locale actual.
     *
     * @return El locale actual
     */
    public static Locale getLocaleActual() {
        return currentLocale;
    }

    /**
     * Cambia a español.
     */
    public static void usarEspanol() {
        logger.debug("Solicitado cambio a idioma español");
        cambiarIdioma(Locale.forLanguageTag("es-ES"));
    }

    /**
     * Cambia a inglés.
     */
    public static void usarIngles() {
        logger.debug("Solicitado cambio a idioma inglés");
        cambiarIdioma(Locale.forLanguageTag("en-US"));
    }

    /**
     * Obtiene el ResourceBundle actual.
     * Útil para asignarlo al FXMLLoader.
     *
     * @return El ResourceBundle actual
     */
    public static ResourceBundle getResourceBundle() {
        return bundle;
    }
}