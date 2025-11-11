# 📊 Flujo: Cómo la App Guarda Imágenes Cifradas

## 🔐 FLUJO DE CIFRADO

```
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO                              │
│                                                             │
│  1. Selecciona imagen (foto.jpg)                           │
│  2. Ingresa password: "mipassword123"                       │
│  3. Click en "Cifrar"                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    APLICACIÓN CLIENTE                        │
│                                                             │
│  • Lee archivo: foto.jpg (bytes)                           │
│  • Crea FormData:                                          │
│    - file: foto.jpg                                        │
│    - password: "mipassword123"                             │
│    - tipo_aes: "AES-256"                                   │
│                                                             │
│  • Envía HTTP POST a:                                      │
│    http://localhost:8000/aes/cifrar/file                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                        API AES                              │
│                                                             │
│  1. Recibe imagen (bytes)                                  │
│  2. Deriva clave de password (PBKDF2)                      │
│  3. Genera salt aleatorio                                  │
│  4. Cifra con AES-256-GCM                                  │
│  5. Convierte a base64                                     │
│                                                             │
│  • Responde JSON:                                          │
│    {                                                       │
│      "texto_cifrado": "YWJjZGVm...",  ← Imagen cifrada    │
│      "salt": "cmFuZG9tc2FsdA==",       ← ¡Importante!     │
│      "tipo_aes": "AES-256",                               │
│      "tamanio_original_bytes": 245678                     │
│    }                                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              APLICACIÓN CLIENTE - GUARDAR                   │
│                                                             │
│  📥 RECIBE:                                                │
│     • texto_cifrado: "YWJjZGVm..." (base64)                │
│     • salt: "cmFuZG9tc2FsdA=="                             │
│                                                             │
│  💾 GUARDA:                                                │
│                                                             │
│     1. ARCHIVO: foto_cifrada.txt                           │
│        Contenido: YWJjZGVm...                              │
│        (texto_cifrado completo)                            │
│                                                             │
│     2. ARCHIVO: foto_salt.txt                              │
│        Contenido: cmFuZG9tc2FsdA==                         │
│        (salt necesario para descifrar)                     │
│                                                             │
│  ✅ MÉTODOS DE GUARDADO:                                   │
│                                                             │
│     • Opción 1: Crear Blob + Descargar                    │
│       const blob = new Blob([texto_cifrado])              │
│       descargar(blob, 'foto_cifrada.txt')                 │
│                                                             │
│     • Opción 2: LocalStorage (navegador)                  │
│       localStorage.setItem('cifrado', texto_cifrado)      │
│       localStorage.setItem('salt', salt)                  │
│                                                             │
│     • Opción 3: Base de Datos                             │
│       db.guardar({                                        │
│         cifrado: texto_cifrado,                           │
│         salt: salt,                                       │
│         fecha: new Date()                                 │
│       })                                                  │
│                                                             │
│     • Opción 4: Servidor propio                           │
│       fetch('/api/guardar', {                             │
│         body: JSON.stringify({cifrado, salt})            │
│       })                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔓 FLUJO DE DESCIFRADO

```
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO                              │
│                                                             │
│  1. Selecciona archivo: foto_cifrada.txt                   │
│  2. Ingresa password: "mipassword123"                       │
│  3. Ingresa salt: "cmFuZG9tc2FsdA=="                        │
│  4. Click en "Descifrar"                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    APLICACIÓN CLIENTE                        │
│                                                             │
│  • Lee archivo: foto_cifrada.txt                           │
│  • Crea FormData:                                          │
│    - file: foto_cifrada.txt                                │
│    - password: "mipassword123"                             │
│    - salt: "cmFuZG9tc2FsdA=="                              │
│    - tipo_aes: "AES-256"                                   │
│                                                             │
│  • Envía HTTP POST a:                                      │
│    http://localhost:8000/aes/descifrar/file                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                        API AES                              │
│                                                             │
│  1. Recibe texto cifrado (base64)                          │
│  2. Deriva clave de password + salt                        │
│  3. Desempaqueta nonce + datos + tag                       │
│  4. Descifra con AES-256-GCM                               │
│  5. Verifica autenticidad (tag)                            │
│  6. Convierte bytes a base64                               │
│                                                             │
│  • Responde JSON:                                          │
│    {                                                       │
│      "archivo_descifrado_base64": "iVBORw0KG...",         │
│      "tipo_aes": "AES-256",                               │
│      "tamanio_bytes": 245678                              │
│    }                                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         APLICACIÓN CLIENTE - RESTAURAR IMAGEN               │
│                                                             │
│  📥 RECIBE:                                                │
│     • archivo_descifrado_base64: "iVBORw0KG..."           │
│       (imagen original en base64)                          │
│                                                             │
│  🔄 CONVIERTE:                                             │
│     base64 → bytes → archivo de imagen                     │
│                                                             │
│     JavaScript:                                            │
│     ────────────                                           │
│     const bytes = atob(base64Data)                        │
│     const array = new Uint8Array(bytes.length)            │
│     for (let i = 0; i < bytes.length; i++) {              │
│       array[i] = bytes.charCodeAt(i)                      │
│     }                                                      │
│     const blob = new Blob([array], {type: 'image/png'})   │
│                                                             │
│     Python:                                                │
│     ───────                                                │
│     imagen_bytes = base64.b64decode(base64Data)           │
│                                                             │
│  💾 GUARDA:                                                │
│                                                             │
│     1. DESCARGAR: foto_descifrada.png                      │
│        const url = URL.createObjectURL(blob)              │
│        const a = document.createElement('a')              │
│        a.href = url                                       │
│        a.download = 'foto_descifrada.png'                 │
│        a.click()                                          │
│                                                             │
│     2. MOSTRAR EN PANTALLA:                               │
│        <img src="data:image/png;base64,iVBORw0KG...">     │
│                                                             │
│     3. GUARDAR EN DISCO (Python):                         │
│        with open('foto_descifrada.png', 'wb') as f:       │
│            f.write(imagen_bytes)                          │
│                                                             │
│  ✅ RESULTADO:                                             │
│     Imagen original restaurada perfectamente              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 RESUMEN SIMPLE

### Al Cifrar:
```
Imagen → API → Respuesta con 2 cosas:
                1. texto_cifrado (base64)
                2. salt (base64)

App guarda:
  ✓ texto_cifrado en archivo .txt
  ✓ salt en archivo .txt (o muestra al usuario)
```

### Al Descifrar:
```
archivo.txt + password + salt → API → archivo_descifrado_base64

App convierte:
  base64 → bytes → imagen

App guarda:
  ✓ Descarga como .png/.jpg
  ✓ O muestra en pantalla
```

---

## 🔑 CONCEPTOS CLAVE

### ¿Qué es base64?
```
Formato que convierte bytes binarios a texto

Ejemplo:
  Bytes: [0xFF, 0xD8, 0xFF, 0xE0]  (binario)
  Base64: "/9j/4AAQ..."            (texto)

Ventajas:
  ✓ Se puede enviar por HTTP
  ✓ Se puede guardar en .txt
  ✓ Fácil de copiar/pegar
```

### ¿Por qué guardar en .txt?
```
La imagen cifrada es texto (base64), no binario

foto.jpg (original)     → bytes binarios
  ↓ cifrar
foto_cifrada.txt        → texto base64
  ↓ descifrar
foto_descifrada.jpg     → bytes binarios (idénticos al original)
```

### ¿Qué es el salt?
```
Valor aleatorio que hace única cada clave

Sin salt:
  password "hola" siempre → misma clave

Con salt:
  password "hola" + salt1 → clave única 1
  password "hola" + salt2 → clave única 2

⚠️ IMPORTANTE: Sin el salt, no puedes descifrar
```

---

## 💡 EJEMPLO COMPLETO EN CÓDIGO

### JavaScript (Navegador):

```javascript
// CIFRAR
async function cifrarYGuardar(imagenFile, password) {
  const formData = new FormData();
  formData.append('file', imagenFile);
  formData.append('password', password);
  formData.append('tipo_aes', 'AES-256');

  const response = await fetch('http://localhost:8000/aes/cifrar/file', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();

  // Guardar archivos
  descargar(data.texto_cifrado, 'imagen_cifrada.txt');
  descargar(data.salt, 'salt.txt');

  return data.salt; // Devolver salt para usar después
}

// DESCIFRAR
async function descifrarYMostrar(archivoCifrado, password, salt) {
  const formData = new FormData();
  formData.append('file', archivoCifrado);
  formData.append('password', password);
  formData.append('salt', salt);
  formData.append('tipo_aes', 'AES-256');

  const response = await fetch('http://localhost:8000/aes/descifrar/file', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();

  // Opción 1: Mostrar en pantalla
  const img = document.getElementById('miImagen');
  img.src = `data:image/png;base64,${data.archivo_descifrado_base64}`;

  // Opción 2: Descargar
  const bytes = base64ToBytes(data.archivo_descifrado_base64);
  const blob = new Blob([bytes], {type: 'image/png'});
  descargarBlob(blob, 'imagen_descifrada.png');
}

// Utilidad: descargar texto
function descargar(texto, nombre) {
  const blob = new Blob([texto], {type: 'text/plain'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(url);
}

// Utilidad: base64 a bytes
function base64ToBytes(base64) {
  const chars = atob(base64);
  const bytes = new Uint8Array(chars.length);
  for (let i = 0; i < chars.length; i++) {
    bytes[i] = chars.charCodeAt(i);
  }
  return bytes;
}
```

---

¿Te queda más claro cómo la app guarda las imágenes? 🎯
