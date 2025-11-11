package es.luna;

/**
 * Clase lanzadora de la aplicación ScriptumFX.
 * <p>
 * Esta clase sirve como punto de entrada alternativo para ejecutar la aplicación JavaFX.
 * Es necesaria para evitar problemas cuando se ejecuta desde un JAR sin que JavaFX
 * esté en el module-path. Delega la ejecución a {@link ScriptumApp}.
 * </p>
 *
 * @version 1.0
 * @since 2025-11-11
 */
public class Lanzador {

    /**
     * Metodo principal que lanza la aplicación JavaFX.
     * <p>
     * Invoca el metodo main de {@link ScriptumApp}, permitiendo que la aplicación
     * se ejecute correctamente incluso cuando JavaFX no está en el module-path.
     * </p>
     *
     * @param args argumentos de línea de comandos pasados a la aplicación.
     */
    public static void main(String[] args) {
        ScriptumApp.main(args);
    }
}