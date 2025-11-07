module es.luna {
    requires javafx.controls;
    requires javafx.fxml;

    opens es.luna to javafx.fxml;
    exports es.luna;
}
