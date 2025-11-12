# Integración Frontend JavaFX - Backend FastAPI

Esta guía explica cómo usar la integración entre el frontend JavaFX (ScriptumFx) y el backend FastAPI (ApiScriptum).

## Arquitectura de la integración

```
┌─────────────────────────────────────────┐
│         JavaFX Frontend                 │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   VentanaController.java         │  │
│  │   (UI - Maneja eventos)          │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │   VigenereService / AesService   │  │
│  │   (Lógica de negocio)            │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │   ApiClient.java                 │  │
│  │   (HTTP Client - Gson)           │  │
│  └────────────┬─────────────────────┘  │
│               │ HTTP/JSON              │
└───────────────┼─────────────────────────┘
                │
                │ POST /vigenere/cifrar-texto
                │ POST /aes/cifrar-texto
                │ GET  /health
                ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│         (ApiScriptum)                   │
│                                         │
│  /vigenere  →  Cifrado Vigenère        │
│  /aes       →  Cifrado AES             │
│  /health    →  Estado de la API        │
└─────────────────────────────────────────┘
```

## Estructura de paquetes

```
es.luna/
├── client/
│   └── ApiClient.java              # Cliente HTTP centralizado
├── config/
│   └── ApiConfig.java              # Configuración de la API
├── model/
│   ├── VigenereCifrarRequest.java
│   ├── VigenereCifradoResponse.java
│   ├── VigenereDescifrarRequest.java
│   ├── VigenereDescifradoResponse.java
│   ├── AesCifrarRequest.java
│   ├── AesCifradoResponse.java
│   ├── AesDescifrarRequest.java
│   ├── AesDescifradoResponse.java
│   └── ApiErrorResponse.java
├── service/
│   ├── VigenereService.java        # Servicio para Vigenère
│   ├── AesService.java             # Servicio para AES
│   └── EjemploUsoServicios.java    # Ejemplos de uso
└── VentanaController.java          # Controlador de la UI
```

## Dependencias

El proyecto usa las siguientes dependencias (ya configuradas en `pom.xml`):

- **Gson 2.10.1**: Para serialización/deserialización JSON
- **HttpClient**: Cliente HTTP nativo de Java 11+
- **SLF4J + Logback**: Para logging

## Configuración inicial

### 1. Iniciar el backend

```bash
cd ApiScriptum
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

El backend estará disponible en: `http://localhost:8000`

### 2. Configurar la URL de la API (opcional)

Por defecto, la aplicación se conecta a `http://localhost:8000`.

Para cambiar la URL, puedes:

**Opción A: Variable de entorno**
```bash
export SCRIPTUM_API_URL=http://tu-servidor:8000
```

**Opción B: Propiedad del sistema**
```bash
java -Dscriptum.api.url=http://tu-servidor:8000 -jar ScriptumFX.jar
```

**Opción C: Modificar `ApiConfig.java`**
```java
public static final String API_BASE_URL = "http://tu-servidor:8000";
```

## Uso en controladores

### Ejemplo básico: Cifrar con Vigenère

```java
import es.luna.config.ApiConfig;
import es.luna.service.VigenereService;
import javafx.application.Platform;

public class MiControlador {

    private VigenereService vigenereService;

    @FXML
    public void initialize() {
        // Inicializar el servicio
        vigenereService = new VigenereService(ApiConfig.API_BASE_URL);
    }

    @FXML
    private void onCifrarClick() {
        String texto = txtTextoOriginal.getText();
        String clave = txtClave.getText();

        // Mostrar indicador de carga
        progressIndicator.setVisible(true);
        btnCifrar.setDisable(true);

        // Llamada asíncrona a la API
        vigenereService.cifrarTexto(texto, clave)
            .thenAccept(response -> {
                // Actualizar UI en el hilo de JavaFX
                Platform.runLater(() -> {
                    txtResultado.setText(response.getTextoCifrado());
                    lblInfo.setText("Cifrado con clave: " + response.getClaveUsada());

                    // Ocultar indicador de carga
                    progressIndicator.setVisible(false);
                    btnCifrar.setDisable(false);
                });
            })
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    mostrarAlerta("Error", "Error al cifrar: " + error.getMessage());
                    progressIndicator.setVisible(false);
                    btnCifrar.setDisable(false);
                });
                return null;
            });
    }
}
```

### Ejemplo: Cifrar con AES

```java
import es.luna.config.ApiConfig;
import es.luna.service.AesService;
import javafx.application.Platform;

public class MiControlador {

    private AesService aesService;

    @FXML
    public void initialize() {
        aesService = new AesService(ApiConfig.API_BASE_URL);
    }

    @FXML
    private void onCifrarAesClick() {
        String texto = txtTextoOriginal.getText();
        String password = txtPassword.getText();
        String tipoAes = comboTipoAes.getValue(); // "AES-256", "AES-192", "AES-128"

        aesService.cifrarTexto(texto, password, tipoAes)
            .thenAccept(response -> {
                Platform.runLater(() -> {
                    txtResultado.setText(response.getTextoCifrado());
                    txtSalt.setText(response.getSalt());

                    // IMPORTANTE: Avisar al usuario que guarde el salt
                    mostrarAlerta(
                        "Importante",
                        "Guarda el SALT para poder descifrar después:\n" + response.getSalt()
                    );
                });
            })
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    mostrarAlerta("Error", error.getMessage());
                });
                return null;
            });
    }

    @FXML
    private void onDescifrarAesClick() {
        String textoCifrado = txtTextoCifrado.getText();
        String password = txtPassword.getText();
        String salt = txtSalt.getText();
        String tipoAes = comboTipoAes.getValue();

        aesService.descifrarTexto(textoCifrado, password, salt, tipoAes)
            .thenAccept(response -> {
                Platform.runLater(() -> {
                    txtResultado.setText(response.getTextoDescifrado());
                });
            })
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    // Manejar error de password/salt incorrecto
                    mostrarAlerta(
                        "Error",
                        "Password o salt incorrectos. Verifica los datos."
                    );
                });
                return null;
            });
    }
}
```

### Verificar conexión con la API

```java
@FXML
public void initialize() {
    vigenereService = new VigenereService(ApiConfig.API_BASE_URL);

    // Verificar conexión al iniciar
    vigenereService.verificarConexion()
        .thenAccept(conectado -> {
            Platform.runLater(() -> {
                if (conectado) {
                    lblEstadoApi.setText("✓ API conectada");
                    lblEstadoApi.setStyle("-fx-text-fill: green;");
                } else {
                    lblEstadoApi.setText("✗ API desconectada");
                    lblEstadoApi.setStyle("-fx-text-fill: red;");

                    mostrarAlerta(
                        "Error de conexión",
                        "No se pudo conectar con la API. Verifica que esté ejecutándose."
                    );
                }
            });
        });
}
```

## Manejo de errores

La integración maneja diferentes tipos de errores:

### 1. Errores de validación

```java
vigenereService.cifrarTexto("", "clave")
    .exceptionally(error -> {
        // error.getCause() instanceof IllegalArgumentException
        // "El texto no puede estar vacío"
        return null;
    });
```

### 2. Errores de la API

```java
vigenereService.cifrarTexto("texto", "")
    .exceptionally(error -> {
        // error.getCause() instanceof ApiClient.ApiException
        // "La clave no puede estar vacía - Proporciona una clave válida..."
        return null;
    });
```

### 3. Errores de red/conexión

```java
// Si la API no está disponible
vigenereService.cifrarTexto("texto", "clave")
    .exceptionally(error -> {
        // Connection refused, timeout, etc.
        Platform.runLater(() -> {
            mostrarAlerta(
                "Error de conexión",
                "No se pudo conectar con la API. Verifica que esté ejecutándose."
            );
        });
        return null;
    });
```

## Operaciones asíncronas

**IMPORTANTE**: Todas las operaciones son asíncronas para no bloquear la UI.

### ¿Por qué asíncrono?

```java
// ❌ MAL - Bloquea la UI de JavaFX
String resultado = vigenereService.cifrarTexto(texto, clave).get(); // ¡NO HACER ESTO!

// ✅ BIEN - No bloquea la UI
vigenereService.cifrarTexto(texto, clave)
    .thenAccept(response -> {
        Platform.runLater(() -> {
            // Actualizar UI cuando llegue la respuesta
        });
    });
```

### Operaciones en cadena

```java
// Cifrar y luego descifrar
vigenereService.cifrarTexto(texto, clave)
    .thenCompose(cifradoResp -> {
        // Cuando termina el cifrado, descifrar
        return vigenereService.descifrarTexto(cifradoResp.getTextoCifrado(), clave);
    })
    .thenAccept(descifradoResp -> {
        Platform.runLater(() -> {
            // Mostrar resultado final
        });
    });
```

## Testing

### Probar la conexión manualmente

```bash
# Verificar health endpoint
curl http://localhost:8000/health

# Cifrar con Vigenère
curl -X POST http://localhost:8000/vigenere/cifrar-texto \
  -H "Content-Type: application/json" \
  -d '{"texto": "Hola Mundo", "clave": "CLAVE"}'

# Cifrar con AES
curl -X POST http://localhost:8000/aes/cifrar-texto \
  -H "Content-Type: application/json" \
  -d '{"texto": "Mensaje secreto", "password": "password123", "tipo_aes": "AES-256"}'
```

## Compilar y ejecutar

```bash
# Compilar el proyecto
cd ScriptumFx
mvn clean compile

# Ejecutar en desarrollo
mvn javafx:run

# Generar JAR ejecutable
mvn clean package

# Ejecutar el JAR
java -jar target/ScriptumFX-1.0-SNAPSHOT.jar
```

## Documentación de la API

Una vez iniciado el backend, la documentación interactiva está disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Error: "Connection refused"

**Solución**: Verifica que el backend esté ejecutándose en `http://localhost:8000`

```bash
cd ApiScriptum
python main.py
```

### Error: "CORS policy"

**Solución**: Ya está configurado en `ApiScriptum/app/config.py`. Verifica que incluya `"*"` en ALLOWED_ORIGINS.

### Error: "Password debe tener al menos 8 caracteres" (AES)

**Solución**: El password para AES debe tener mínimo 8 caracteres.

### Error: "Tag de autenticación no coincide" (AES)

**Solución**: El password o salt son incorrectos. Verifica que uses el mismo password y salt que al cifrar.

## Próximos pasos

1. Implementar la UI en `ventana.fxml` con campos para cifrar/descifrar
2. Agregar soporte para cifrado de archivos
3. Implementar almacenamiento local de configuraciones
4. Agregar historial de operaciones
5. Implementar tests unitarios para los servicios

## Contacto

Para más información, consulta:
- Documentación de la API: `ApiScriptum/README.md`
- Ejemplos de uso: `EjemploUsoServicios.java`
