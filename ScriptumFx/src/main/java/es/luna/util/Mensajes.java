package es.luna.util;

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

    static {
        // Por defecto, usar el idioma del sistema
        currentLocale = Locale.getDefault();
        cargarBundle();
    }

    /**
     * Carga o recarga el ResourceBundle con el locale actual.
     */
    private static void cargarBundle() {
        bundle = ResourceBundle.getBundle(BUNDLE_NAME, currentLocale);
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
            return "!" + clave + "!";
        }
    }

    /**
     * Cambia el idioma de la aplicación.
     *
     * @param locale El nuevo locale
     */
    public static void cambiarIdioma(Locale locale) {
        currentLocale = locale;
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
        cambiarIdioma(Locale.forLanguageTag("es-ES"));
    }

    /**
     * Cambia a inglés.
     */
    public static void usarIngles() {
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