package es.luna;

/**
 * Clase lanzadora de la aplicación ScriptumFX.
 * <p>
 * Esta clase sirve como punto de entrada alternativo para ejecutar la aplicación JavaFX.
 * Es necesaria para evitar problemas cuando se ejecuta desde un JAR sin que JavaFX
 * esté dentro de module-path. Delega la ejecución a {@link ScriptumApp}.
 * </p>
 * @author Arantxa
 * @version 1.0
 * @since 2025-11-11
 */
public class Lanzador {

    /**
     * Constructor privado para evitar instanciación.
     * Esta clase solo contiene el método main para lanzar la aplicación.
     */
    private Lanzador() {
        throw new UnsupportedOperationException("Esta es una clase lanzadora y no debe ser instanciada");
    }

    /**
     * Metodo principal que lanza la aplicación JavaFX.
     * <p>
     * Invoca a la función main de {@link ScriptumApp}, permitiendo que la aplicación
     * se ejecute correctamente incluso cuando JavaFX no está en module-path.
     * </p>
     *
     * @param args argumentos de línea de comandos pasados a la aplicación.
     */
    public static void main(String[] args) {
        ScriptumApp.main(args);
    }
}