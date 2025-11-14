# ⚡ Guía Rápida de Scriptum

> 🔐 Referencia rápida para usar la API de cifrado Scriptum

---

## 🎯 Lo Esencial

### Tipos de Cifrado

| Cifrado | Seguridad | Límite Texto | Límite Archivos |
|---------|-----------|--------------|-----------------|
| **AES-256** | ⭐⭐⭐⭐⭐ | 100 MB | 100 MB |
| **AES-192** | ⭐⭐⭐⭐ | 100 MB | 100 MB |
| **AES-128** | ⭐⭐⭐⭐ | 100 MB | 100 MB |
| **Vigenère** | ⭐⭐ | 100 MB | 500 MB |

**Recomendación:** Usa **AES-256** para máxima seguridad.

---

## 📋 Endpoints Principales

### 🔐 Cifrado AES

#### Cifrar Texto
```bash
POST /aes/cifrar/texto
{
  "texto": "mensaje",
  "password": "password123",
  "tipo_aes": "AES-256"
}
```

#### Descifrar Texto
```bash
POST /aes/descifrar/texto
{
  "texto_cifrado": "...",
  "password": "password123",
  "salt": "...",
  "tipo_aes": "AES-256"
}
```

#### Cifrar Archivo
```bash
POST /aes/cifrar/file
Form-Data:
  - file: [archivo]
  - password: "password123"
  - tipo_aes: "AES-256"

→ Respuesta: { "paquete": "...", "info": {...} }
```

#### Descifrar Archivo
```bash
POST /aes/descifrar/file
Form-Data:
  - paquete: "..."
  - password: "password123"

→ Respuesta: [archivo binario]
```

---

### 📝 Cifrado Vigenère

#### Cifrar
```bash
POST /vigenere/cifrar/texto
{
  "texto": "HOLA",
  "clave": "SECRETO"
}
```

#### Descifrar
```bash
POST /vigenere/descifrar/texto
{
  "texto_cifrado": "ZINL",
  "clave": "SECRETO"
}
```

---

## 💡 Consejos Rápidos

### ✅ Buenas Prácticas

1. **Contraseña mínima:** 8 caracteres
2. **Usa AES-256** para datos sensibles
3. **Guarda el salt** al cifrar texto
4. **Para archivos:** Solo guarda el `paquete` (todo está incluido)
5. **HTTPS en producción:** Siempre

### ⚠️ Restricciones

- Password: 8-1000 caracteres
- AES: 100 MB máximo
- Vigenère: 500 MB máximo
- Streaming automático: ≥10 MB

### 📄 Extensiones Soportadas (AES)

`.txt` `.pdf` `.doc` `.docx` `.xls` `.xlsx` `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.zip` `.rar` `.7z` `.csv` `.json` `.xml`

---

## 🚀 Ejemplo Completo: Cifrar y Descifrar

### JavaScript

```javascript
// CIFRAR
const response = await fetch('http://localhost:8000/aes/cifrar/texto', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    texto: 'Mensaje secreto',
    password: 'MiPassword123',
    tipo_aes: 'AES-256'
  })
})

const { texto_cifrado, salt, tipo_aes } = await response.json()

// DESCIFRAR
const response2 = await fetch('http://localhost:8000/aes/descifrar/texto', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    texto_cifrado,
    password: 'MiPassword123',
    salt,
    tipo_aes
  })
})

const { texto_descifrado } = await response2.json()
console.log(texto_descifrado) // "Mensaje secreto"
```

### Python

```python
import requests

# CIFRAR
response = requests.post('http://localhost:8000/aes/cifrar/texto', json={
    'texto': 'Mensaje secreto',
    'password': 'MiPassword123',
    'tipo_aes': 'AES-256'
})

data = response.json()

# DESCIFRAR
response2 = requests.post('http://localhost:8000/aes/descifrar/texto', json={
    'texto_cifrado': data['texto_cifrado'],
    'password': 'MiPassword123',
    'salt': data['salt'],
    'tipo_aes': data['tipo_aes']
})

print(response2.json()['texto_descifrado'])  # "Mensaje secreto"
```

### cURL

```bash
# CIFRAR
curl -X POST "http://localhost:8000/aes/cifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{"texto":"Mensaje secreto","password":"MiPassword123","tipo_aes":"AES-256"}'

# DESCIFRAR
curl -X POST "http://localhost:8000/aes/descifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{"texto_cifrado":"...","password":"MiPassword123","salt":"...","tipo_aes":"AES-256"}'
```

---

## 📚 Documentación Completa

- 📖 **[Guía Completa del Usuario](./GUIA_USUARIO.md)** - Explicación detallada con ejemplos
- 📦 **[Empaquetado de Archivos](./EMPAQUETADO_ARCHIVOS.md)** - Formato binario y casos de uso
- 🌐 **[Swagger UI](http://localhost:8000/docs)** - Documentación interactiva

---

## 🆘 Errores Comunes

| Error | Solución |
|-------|----------|
| Password incorrecto | Verifica que sea exactamente la misma (case-sensitive) |
| Archivo muy grande | Comprime o usa Vigenère (500 MB) |
| Extensión no permitida | Verifica lista de extensiones o usa Vigenère |
| SHA-256 falló | Archivo corrupto, obtén copia original |

---

<div align="center">

**¿Necesitas más ayuda?**

📖 [Guía Completa](./GUIA_USUARIO.md) • 🐛 [Issues](https://github.com/WaraYasy/Scriptum/issues) • 💬 [Discusiones](https://github.com/WaraYasy/Scriptum/discussions)

</div>
