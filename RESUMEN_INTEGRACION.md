# Resumen de Integración Backend-Frontend

## Lo que se ha implementado

### 1. Estructura de clases creada

```
ScriptumFx/src/main/java/es/luna/
├── client/
│   └── ApiClient.java                    # Cliente HTTP centralizado con HttpClient nativo
├── config/
│   └── ApiConfig.java                    # Configuración de URL de la API
├── model/                                # DTOs para comunicación con la API
│   ├── VigenereCifrarRequest.java
│   ├── VigenereCifradoResponse.java
│   ├── VigenereDescifrarRequest.java
│   ├── VigenereDescifradoResponse.java
│   ├── AesCifrarRequest.java
│   ├── AesCifradoResponse.java
│   ├── AesDescifrarRequest.java
│   ├── AesDescifradoResponse.java
│   └── ApiErrorResponse.java
├── service/                              # Servicios de negocio
│   ├── VigenereService.java              # Operaciones de cifrado Vigenère
│   ├── AesService.java                   # Operaciones de cifrado AES
│   └── EjemploUsoServicios.java          # Ejemplos completos de uso
└── VentanaController.java                # Controlador existente
```

### 2. Dependencias agregadas

- **Gson 2.10.1**: Para serialización/deserialización JSON
- **java.net.http**: Cliente HTTP nativo de Java (incluido en JDK 11+)

### 3. Configuración realizada

#### Frontend (ScriptumFx)
- ✅ Actualizado `pom.xml` con Gson
- ✅ Actualizado `module-info.java` con módulos necesarios
- ✅ Configurado Java 21 LTS + JavaFX 23
- ✅ Proyecto compila exitosamente

#### Backend (ApiScriptum)
- ✅ Actualizado CORS en `app/config.py` para permitir conexiones de escritorio

## Arquitectura de la solución

### Flujo de comunicación

```
┌─────────────────────────────────────┐
│  UI (FXML + VentanaController)      │
│  - Recoger datos del usuario        │
│  - Mostrar resultados               │
└────────────┬────────────────────────┘
             │
             │ (Llama a servicios)
             ▼
┌─────────────────────────────────────┐
│  Services (VigenereService/AesService│
│  - Validaciones                     │
│  - Lógica de negocio                │
│  - Manejo asíncrono                 │
└────────────┬────────────────────────┘
             │
             │ (Peticiones HTTP)
             ▼
┌─────────────────────────────────────┐
│  ApiClient                          │
│  - HTTP POST/GET                    │
│  - Serialización JSON               │
│  - Manejo de errores                │
└────────────┬────────────────────────┘
             │
             │ (HTTP/JSON)
             ▼
┌─────────────────────────────────────┐
│  FastAPI Backend (ApiScriptum)      │
│  - /vigenere/cifrar-texto           │
│  - /vigenere/descifrar-texto        │
│  - /aes/cifrar-texto                │
│  - /aes/descifrar-texto             │
│  - /health                          │
└─────────────────────────────────────┘
```

## Características principales

### 1. Peticiones asíncronas
- ✅ No bloquea la UI de JavaFX
- ✅ Usa `CompletableFuture` para manejo asíncrono
- ✅ Callbacks con `thenAccept` y `exceptionally`

### 2. Manejo robusto de errores
- ✅ Validaciones locales (texto vacío, password corto, etc.)
- ✅ Captura de errores de la API (con mensajes detallados)
- ✅ Manejo de errores de red/conexión

### 3. Type-safe
- ✅ DTOs fuertemente tipados
- ✅ Gson deserializa automáticamente JSON → Objetos Java
- ✅ Compilación garantiza compatibilidad

### 4. Configurable
- ✅ URL de API configurable (variable de entorno, propiedad del sistema, o por defecto)
- ✅ Timeouts configurables
- ✅ Logging completo con SLF4J

## Cómo usar

### Iniciar el backend

```bash
cd ApiScriptum
python main.py
```

Backend disponible en: http://localhost:8000

### Compilar el frontend

```bash
cd ScriptumFx
mvn clean compile
```

### Ejecutar el frontend

```bash
cd ScriptumFx
mvn javafx:run
```

### Ejemplo de uso en un controlador

```java
import es.luna.config.ApiConfig;
import es.luna.service.VigenereService;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;

public class MiControlador {

    @FXML
    private TextField txtTexto;

    @FXML
    private TextField txtClave;

    @FXML
    private TextArea txtResultado;

    private VigenereService vigenereService;

    @FXML
    public void initialize() {
        // Crear servicio con URL de config
        vigenereService = new VigenereService(ApiConfig.API_BASE_URL);
    }

    @FXML
    private void onCifrarClick() {
        String texto = txtTexto.getText();
        String clave = txtClave.getText();

        // Petición asíncrona
        vigenereService.cifrarTexto(texto, clave)
            .thenAccept(response -> {
                Platform.runLater(() -> {
                    txtResultado.setText(response.getTextoCifrado());
                });
            })
            .exceptionally(error -> {
                Platform.runLater(() -> {
                    txtResultado.setText("ERROR: " + error.getMessage());
                });
                return null;
            });
    }
}
```

## Endpoints disponibles

### Vigenère

**POST /vigenere/cifrar-texto**
```json
Request:
{
  "texto": "Hola Mundo",
  "clave": "CLAVE"
}

Response:
{
  "texto_cifrado": "JSTKCYQDS",
  "clave_usada": "CLAVE",
  "texto_original_length": 10
}
```

**POST /vigenere/descifrar-texto**
```json
Request:
{
  "texto_cifrado": "JSTKCYQDS",
  "clave": "CLAVE"
}

Response:
{
  "texto_descifrado": "HOLAMUNDO",
  "clave_usada": "CLAVE"
}
```

### AES

**POST /aes/cifrar-texto**
```json
Request:
{
  "texto": "Mensaje secreto",
  "password": "password123",
  "tipo_aes": "AES-256"
}

Response:
{
  "texto_cifrado": "VGhpcyBpcyBhbiBlbmNyeXB0ZWQgdGV4dA==",
  "salt": "cmFuZG9tc2FsdDEyMzQ1Ng==",
  "tipo_aes": "AES-256",
  "tamanio_original_bytes": 15,
  "tamanio_cifrado_bytes": 44
}
```

**POST /aes/descifrar-texto**
```json
Request:
{
  "texto_cifrado": "VGhpcyBpcyBhbiBlbmNyeXB0ZWQgdGV4dA==",
  "password": "password123",
  "salt": "cmFuZG9tc2FsdDEyMzQ1Ng==",
  "tipo_aes": "AES-256"
}

Response:
{
  "texto_descifrado": "Mensaje secreto",
  "tipo_aes": "AES-256",
  "tamanio_bytes": 15
}
```

### Health Check

**GET /health**
```json
Response:
{
  "status": "healthy"
}
```

## Documentación adicional

- **Guía completa de integración**: `ScriptumFx/INTEGRACION_API.md`
- **Ejemplos de código**: `es.luna.service.EjemploUsoServicios.java`
- **Documentación de la API**: http://localhost:8000/docs (cuando el backend está ejecutándose)

## Próximos pasos sugeridos

1. **Crear la UI en ventana.fxml** con:
   - Campos para texto y clave
   - Botones para cifrar/descifrar
   - Área de resultados
   - Indicadores de carga
   - Selector de tipo de AES

2. **Integrar los servicios en VentanaController.java**
   - Conectar eventos de botones
   - Mostrar indicadores de carga
   - Manejar errores con alertas visuales

3. **Añadir funcionalidad de archivos**
   - Upload de archivos .txt
   - Cifrado/descifrado de archivos
   - Download de resultados

4. **Mejoras opcionales**:
   - Historial de operaciones
   - Configuración de URL de API desde la UI
   - Guardar configuraciones localmente
   - Tests unitarios para los servicios

## Ventajas de esta implementación

✅ **Moderna**: Usa HttpClient nativo (Java 11+), no requiere librerías externas pesadas

✅ **Asíncrona**: No bloquea la UI, mejor experiencia de usuario

✅ **Type-safe**: Errores de tipos se detectan en compilación

✅ **Mantenible**: Separación clara de responsabilidades (UI → Service → Client → API)

✅ **Escalable**: Fácil agregar nuevos endpoints y servicios

✅ **Testeable**: Servicios pueden recibir ApiClient mock para testing

✅ **Portable**: JAR ejecutable funciona sin configuración adicional

## Notas técnicas

- **Java**: 21 LTS (compatible con Java 11+)
- **JavaFX**: 23 (compatible con Java 21)
- **Gson**: 2.10.1
- **Backend**: FastAPI (Python 3.11+)
- **Arquitectura**: Clean Architecture con capas bien definidas

---

**Fecha de implementación**: 2025-11-11
**Autora**: Arantxa
**Versión**: 1.0
