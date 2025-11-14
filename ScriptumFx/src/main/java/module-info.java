/**
 * Módulo de la aplicación ScriptumFX.
 * <p>
 * Aplicación JavaFX para cifrado y descifrado de textos y archivos
 * utilizando los algoritmos Vigenère y AES.
 * </p>
 * 
 * <h2>Dependencias:</h2>
 * <ul>
 *   <li>javafx.controls - Controles de interfaz de usuario de JavaFX</li>
 *   <li>javafx.fxml - Soporte para archivos FXML</li>
 *   <li>org.slf4j - Framework de logging</li>
 *   <li>com.google.gson - Serialización/deserialización JSON</li>
 *   <li>java.net.http - Cliente HTTP para comunicación con API</li>
 *   <li>org.kordamp.ikonli.javafx - Iconos para la interfaz</li>
 * </ul>
 *
 */
module es.luna {
    requires javafx.controls;
    requires javafx.fxml;
    requires org.slf4j;
    requires com.google.gson;
    requires java.net.http;
    requires org.kordamp.ikonli.javafx;

    opens es.luna to javafx.fxml;
    opens es.luna.model to com.google.gson;

    exports es.luna;
    exports es.luna.client;
    exports es.luna.config;
    exports es.luna.model;
    exports es.luna.service;
    exports es.luna.controller;
    opens es.luna.controller to javafx.fxml;
}