module es.luna {
    requires javafx.controls;
    requires javafx.fxml;
    requires org.slf4j;
    requires com.google.gson;
    requires java.net.http;

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