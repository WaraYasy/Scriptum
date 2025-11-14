# 🔐 Scriptum - Guía del Usuario

<div align="center">

**Tu herramienta de cifrado seguro y fácil de usar**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

[¿Qué es Scriptum?](#-qué-es-scriptum) •
[Tipos de Cifrado](#-tipos-de-cifrado-disponibles) •
[Límites](#-límites-y-restricciones) •
[Cómo Usar](#-cómo-usar-la-api) •
[Ejemplos](#-ejemplos-prácticos)

</div>

---

## 📖 ¿Qué es Scriptum?

**Scriptum** es una API de cifrado y descifrado que te permite proteger tus datos de forma segura y sencilla. Puedes cifrar:

- 📝 **Textos** - Mensajes, notas, contraseñas
- 📄 **Archivos** - Documentos, imágenes, PDFs, archivos comprimidos

Todo se hace a través de una API REST simple y potente, diseñada para ser fácil de integrar en cualquier aplicación (web, móvil, desktop).

---

## 🔐 Tipos de Cifrado Disponibles

### 1. AES (Advanced Encryption Standard) - ⭐ RECOMENDADO

El estándar de cifrado más seguro y utilizado en el mundo. Usado por gobiernos y empresas.

#### Variantes Disponibles:

| Tipo | Seguridad | Velocidad | Uso Recomendado |
|------|-----------|-----------|-----------------|
| **AES-128** | ⭐⭐⭐⭐ Muy Alta | ⚡⚡⚡ Muy Rápida | Documentos generales, archivos grandes |
| **AES-192** | ⭐⭐⭐⭐⭐ Súper Alta | ⚡⚡ Rápida | Balance perfecto entre seguridad y velocidad |
| **AES-256** | ⭐⭐⭐⭐⭐+ Ultra Alta | ⚡ Normal | 🏆 **Datos sensibles, máxima seguridad** |

#### ✨ Características Especiales de AES:

- ✅ **Modo GCM**: Cifrado + Autenticación + Integridad en uno
- ✅ **PBKDF2**: 100,000 iteraciones para derivar claves (resistente a ataques)
- ✅ **SHA-256**: Verificación automática de integridad del archivo
- ✅ **Empaquetado único**: Todo en un solo campo (no pierdes el salt ni metadatos)
- ✅ **Streaming**: Optimizado para archivos grandes (≥10 MB)

### 2. Vigenère - 📚 EDUCATIVO

Cifrado clásico mejorado, ideal para aprender criptografía o uso académico.

#### Características:

- 📖 Fácil de entender y explicar
- 🎓 Perfecto para educación y demostraciones
- ⚠️ **No recomendado para datos sensibles** (usa AES para eso)
- 🚀 Muy rápido para textos

---

## 📏 Límites y Restricciones

### Límites de Tamaño

| Tipo de Cifrado | Textos | Archivos | Streaming |
|-----------------|--------|----------|-----------|
| **AES** | 100 MB | 100 MB | ✅ Sí (≥10 MB) |
| **Vigenère** | 100 MB | 500 MB | ✅ Sí (≥10 MB) |

### Límites de Texto

- **Mínimo**: 1 carácter
- **Máximo**: 100,000,000 caracteres (~100 MB de texto)

### Límites de Password

- **Mínimo**: 8 caracteres
- **Máximo**: 1,000 caracteres
- **Recomendación**: Usa contraseñas fuertes con letras, números y símbolos

### Extensiones de Archivo Soportadas (AES)

#### 📄 Documentos:
- `.txt` - Texto plano
- `.pdf` - Documentos PDF
- `.doc`, `.docx` - Microsoft Word
- `.xls`, `.xlsx` - Microsoft Excel
- `.csv` - Valores separados por comas
- `.json` - JSON
- `.xml` - XML

#### 🖼️ Imágenes:
- `.jpg`, `.jpeg` - JPEG
- `.png` - PNG
- `.gif` - GIF animados
- `.bmp` - Bitmap

#### 🗜️ Archivos Comprimidos:
- `.zip` - ZIP
- `.rar` - RAR
- `.7z` - 7-Zip

**Nota:** Vigenère soporta cualquier tipo de archivo binario.

---

## 🚀 Cómo Usar la API

### URL Base

```
http://localhost:8000    (desarrollo local)
https://tu-dominio.com   (producción)
```

### 1️⃣ Cifrar un Texto con AES

**Endpoint:** `POST /aes/cifrar/texto`

```bash
curl -X POST "http://localhost:8000/aes/cifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "Este es mi mensaje secreto",
    "password": "mi_password_seguro_123",
    "tipo_aes": "AES-256"
  }'
```

**Respuesta:**
```json
{
  "texto_cifrado": "U2FsdGVkX19vR2J...",
  "salt": "cmFuZG9tc2FsdDE...",
  "tipo_aes": "AES-256",
  "tamanio_original_bytes": 27,
  "tamanio_cifrado_bytes": 64
}
```

**💾 Guarda:** `texto_cifrado`, `salt`, y `tipo_aes` para poder descifrar después.

---

### 2️⃣ Descifrar un Texto con AES

**Endpoint:** `POST /aes/descifrar/texto`

```bash
curl -X POST "http://localhost:8000/aes/descifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{
    "texto_cifrado": "U2FsdGVkX19vR2J...",
    "password": "mi_password_seguro_123",
    "salt": "cmFuZG9tc2FsdDE...",
    "tipo_aes": "AES-256"
  }'
```

**Respuesta:**
```json
{
  "texto_descifrado": "Este es mi mensaje secreto",
  "tipo_aes": "AES-256",
  "tamanio_bytes": 27
}
```

---

### 3️⃣ Cifrar un Archivo con AES (⭐ Método Recomendado)

**Endpoint:** `POST /aes/cifrar/file`

```bash
curl -X POST "http://localhost:8000/aes/cifrar/file" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@mi_documento.pdf" \
  -F "password=mi_password_seguro_123" \
  -F "tipo_aes=AES-256"
```

**Respuesta:**
```json
{
  "paquete": "U0NSSVBUVU0BAwAQcmFuZG9tc2FsdDEyMzQ1NgAIZm90by5qcGc...",
  "tamanio_paquete_bytes": 256078,
  "info": {
    "nombre_original": "mi_documento.pdf",
    "mime_type": "application/pdf",
    "tamanio_original_bytes": 245678,
    "tipo_aes": "AES-256"
  }
}
```

**✅ IMPORTANTE: Solo necesitas guardar el campo `paquete`**

Todo lo demás (salt, nombre, tipo de archivo, tipo de AES) está incluido en el paquete. ¡No puedes perder nada!

---

### 4️⃣ Descifrar un Archivo con AES

**Endpoint:** `POST /aes/descifrar/file`

```bash
curl -X POST "http://localhost:8000/aes/descifrar/file" \
  -H "Content-Type: multipart/form-data" \
  -F "paquete=U0NSSVBUVU0B..." \
  -F "password=mi_password_seguro_123" \
  --output archivo_descifrado.pdf
```

**Respuesta:** Archivo binario descifrado con headers especiales:
- `Content-Disposition: attachment; filename="mi_documento.pdf"`
- `X-Original-Filename: mi_documento.pdf`
- `X-Original-MimeType: application/pdf`
- `X-SHA256-Verified: true` - ✅ Integridad verificada
- `X-AES-Type: AES-256`

---

### 5️⃣ Cifrar con Vigenère

**Endpoint:** `POST /vigenere/cifrar/texto`

```bash
curl -X POST "http://localhost:8000/vigenere/cifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "HOLA MUNDO",
    "clave": "SECRETO"
  }'
```

**Respuesta:**
```json
{
  "texto_cifrado": "ZINL QYGVI",
  "clave_usada": "SECRETO",
  "tamanio_bytes": 10
}
```

---

### 6️⃣ Descifrar con Vigenère

**Endpoint:** `POST /vigenere/descifrar/texto`

```bash
curl -X POST "http://localhost:8000/vigenere/descifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{
    "texto_cifrado": "ZINL QYGVI",
    "clave": "SECRETO"
  }'
```

**Respuesta:**
```json
{
  "texto_descifrado": "HOLA MUNDO",
  "clave_usada": "SECRETO",
  "tamanio_bytes": 10
}
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Proteger un Mensaje Privado

**Escenario:** Quieres enviar un mensaje privado a alguien.

1. **Cifra el mensaje:**
   ```json
   POST /aes/cifrar/texto
   {
     "texto": "Te espero mañana a las 3",
     "password": "palabraSecreta123",
     "tipo_aes": "AES-256"
   }
   ```

2. **Recibes:** `texto_cifrado` y `salt`

3. **Envías por cualquier medio** (email, WhatsApp, SMS):
   - El texto cifrado
   - El salt
   - La contraseña por un canal separado y seguro

4. **El destinatario descifra:**
   ```json
   POST /aes/descifrar/texto
   {
     "texto_cifrado": "...",
     "password": "palabraSecreta123",
     "salt": "...",
     "tipo_aes": "AES-256"
   }
   ```

---

### Ejemplo 2: Cifrar Documentos Confidenciales

**Escenario:** Tienes un PDF con información sensible y quieres guardarlo cifrado.

1. **Cifra el archivo:**
   ```bash
   curl -X POST "http://localhost:8000/aes/cifrar/file" \
     -F "file=@contrato_confidencial.pdf" \
     -F "password=MiPassword123!" \
     -F "tipo_aes=AES-256"
   ```

2. **Recibes:** Un `paquete` (un solo campo en base64)

3. **Guardas** el paquete en:
   - Tu base de datos
   - localStorage (aplicación web)
   - Un archivo .txt
   - La nube (Dropbox, Google Drive)

4. **Cuando lo necesites, descifras:**
   ```bash
   curl -X POST "http://localhost:8000/aes/descifrar/file" \
     -F "paquete=TU_PAQUETE_AQUI" \
     -F "password=MiPassword123!" \
     --output contrato_confidencial.pdf
   ```

5. **El archivo se reconstruye automáticamente** con su nombre y tipo original.

---

### Ejemplo 3: Subir Archivos Cifrados a la Nube

**Escenario:** Quieres subir fotos privadas a Google Drive pero cifradas.

**Flujo:**
```
Tu Foto → Cifrar con Scriptum → Paquete cifrado → Subir a Drive
```

**Ventajas:**
- ✅ Google no puede ver el contenido
- ✅ Si hackean tu cuenta, el archivo sigue cifrado
- ✅ Solo tú con la contraseña puedes verlo

**Implementación:**

1. Cifra localmente con Scriptum
2. Sube el paquete a Drive (es solo texto)
3. Para ver: Descarga → Descifra con Scriptum → Visualiza

---

### Ejemplo 4: App de Notas Seguras

**Escenario:** Aplicación móvil de notas cifradas.

```javascript
// Guardar nota cifrada
async function guardarNota(texto, password) {
  const respuesta = await fetch('https://api.scriptum.com/aes/cifrar/texto', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      texto: texto,
      password: password,
      tipo_aes: 'AES-256'
    })
  })

  const data = await respuesta.json()

  // Guardar en base de datos local
  await db.notas.add({
    id: uuid(),
    titulo: 'Mi nota',
    texto_cifrado: data.texto_cifrado,
    salt: data.salt,
    tipo_aes: data.tipo_aes,
    fecha: new Date()
  })
}

// Leer nota cifrada
async function leerNota(notaId, password) {
  const nota = await db.notas.get(notaId)

  const respuesta = await fetch('https://api.scriptum.com/aes/descifrar/texto', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      texto_cifrado: nota.texto_cifrado,
      password: password,
      salt: nota.salt,
      tipo_aes: nota.tipo_aes
    })
  })

  const data = await respuesta.json()
  return data.texto_descifrado
}
```

---

## 🛡️ Seguridad y Mejores Prácticas

### ✅ Recomendaciones de Seguridad

1. **Usa AES-256** para datos sensibles
   - Máxima seguridad disponible
   - Solo un poco más lento que AES-128

2. **Contraseñas fuertes**
   ```
   ❌ Mala: "password123"
   ❌ Mala: "12345678"
   ✅ Buena: "M!Contr@s3ñ@S3gur@2024"
   ✅ Buena: "Frase-Larga-Con-Simbolos-99!"
   ```

3. **Guarda el salt**
   - Sin el salt, NO puedes descifrar
   - Guárdalo junto al texto cifrado
   - No es secreto, pero es necesario

4. **Verifica la integridad**
   - En archivos AES, se verifica automáticamente con SHA-256
   - Si el archivo fue modificado, recibirás un error

5. **No compartas la contraseña**
   - Usa canales seguros y separados
   - Considera usar contraseñas temporales

6. **HTTPS en producción**
   - Siempre usa HTTPS para llamadas a la API
   - Evita interceptación de datos

---

## ⚠️ Errores Comunes y Soluciones

### Error 1: "Password incorrecto"

**Causa:** La contraseña no coincide con la usada al cifrar.

**Solución:**
- Verifica que la contraseña sea exactamente la misma
- Las contraseñas son case-sensitive: `Password123` ≠ `password123`

---

### Error 2: "Formato de paquete inválido"

**Causa:** El paquete está corrupto o incompleto.

**Solución:**
- Verifica que copiaste el paquete completo
- Asegúrate de no haber añadido espacios o saltos de línea

---

### Error 3: "Archivo demasiado grande"

**Causa:** El archivo excede el límite de 100 MB (AES) o 500 MB (Vigenère).

**Solución:**
- Comprime el archivo antes de cifrarlo (.zip, .7z)
- Divide archivos muy grandes en partes más pequeñas
- Considera usar AES para mejor seguridad con límite de 100 MB

---

### Error 4: "Extensión no permitida"

**Causa:** La extensión del archivo no está en la lista de permitidas (solo AES).

**Solución:**
- Verifica la lista de extensiones soportadas
- Cambia la extensión si es apropiado
- O usa Vigenère que acepta cualquier archivo binario

---

### Error 5: "Verificación SHA-256 falló"

**Causa:** El archivo descifrado no coincide con el hash original (corrupto o manipulado).

**Solución:**
- El archivo cifrado fue modificado o está corrupto
- Obtén una copia nueva del archivo cifrado original
- Verifica que el paquete no fue alterado durante transmisión/almacenamiento

---

## 📊 Comparación: ¿Cuál Debo Usar?

| Necesidad | Recomendación | Por qué |
|-----------|---------------|---------|
| Documentos confidenciales | **AES-256** | Máxima seguridad |
| Mensajes personales | **AES-256** | Balance seguridad/velocidad |
| Archivos grandes (>100 MB) | **Vigenère** | Límite de 500 MB |
| Aprendizaje de criptografía | **Vigenère** | Más simple de entender |
| Contratos legales | **AES-256** | Integridad verificada (SHA-256) |
| Fotos/videos privados | **AES-256** | Seguridad + verificación |
| Prototipos/demos | **AES-128** | Rápido y suficientemente seguro |
| App de producción | **AES-256** | Estándar de la industria |

---

## 🌐 Documentación Interactiva

Una vez que tengas la API ejecutándose, puedes explorar todos los endpoints de forma interactiva:

### Swagger UI
**URL:** `http://localhost:8000/docs`

- 🎮 Interfaz interactiva para probar endpoints
- 📝 Documentación automática de todos los parámetros
- 💡 Ejemplos de requests y responses
- ⚡ Ejecuta peticiones directamente desde el navegador

### ReDoc
**URL:** `http://localhost:8000/redoc`

- 📖 Documentación más visual y organizada
- 📚 Mejor para lectura y referencia
- 🔍 Búsqueda rápida de endpoints

---

## 📚 Recursos Adicionales

### Documentación Técnica Completa

- 📦 **[Empaquetado de Archivos](./EMPAQUETADO_ARCHIVOS.md)**
  - Formato binario del paquete
  - Ejemplos de código en JS, Python, Flutter
  - Casos de uso avanzados

- 🌊 **[Guía de Streaming](./STREAMING_GUIA.md)**
  - Cómo funciona el streaming de archivos grandes
  - Optimización de memoria

- 📝 **[Sistema de Logging](./LOGGING_SISTEMA.md)**
  - Logs y debugging
  - Monitoreo de la API

---

## 🔗 Enlaces Útiles

- 🏠 [Repositorio GitHub](https://github.com/WaraYasy/Scriptum)
- 🐛 [Reportar un Bug](https://github.com/WaraYasy/Scriptum/issues)
- 📱 [Aplicación ScriptumFX](../ScriptumFX/)
- 💬 [Discusiones](https://github.com/WaraYasy/Scriptum/discussions)

---

## 🆘 Soporte

¿Necesitas ayuda?

1. 📖 Revisa esta guía
2. 🔍 Busca en la [documentación técnica](./EMPAQUETADO_ARCHIVOS.md)
3. 💡 Prueba los ejemplos en Swagger UI (`/docs`)
4. 🐛 [Abre un issue](https://github.com/WaraYasy/Scriptum/issues) en GitHub

---

## 👥 Créditos

Desarrollado con ❤️ por:

- 🧙🏻‍♀️ **Arantxa** - [@arantxaMain](https://github.com/arantxaMain)
- 🧙🏽‍♀️ **Wara** - [@WaraYasy](https://github.com/WaraYasy)

---

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](../../LICENSE) para más detalles.

---

<div align="center">

**🔐 Mantén tus datos seguros con Scriptum 🔐**

Hecho con ❤️, ☕ y mucha criptografía

</div>
