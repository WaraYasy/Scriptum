module es.luna {
    requires javafx.controls;
    requires javafx.fxml;
    requires org.slf4j;

    opens es.luna to javafx.fxml;
    exports es.luna;
}