# 📚 Documentación de Scriptum API

Bienvenido a la documentación completa de Scriptum API. Aquí encontrarás guías, tutoriales y referencias técnicas.

---

## 🎯 ¿Qué estás buscando?

### 👤 Soy un Usuario

**Quiero aprender a usar la API para cifrar mis datos**

➡️ Comienza aquí:
1. 📖 **[Guía del Usuario](./GUIA_USUARIO.md)** - Tutorial completo con ejemplos paso a paso
2. ⚡ **[Guía Rápida](./GUIA_RAPIDA.md)** - Referencia rápida de endpoints y comandos

---

### 👨‍💻 Soy un Desarrollador

**Quiero integrar Scriptum en mi aplicación**

➡️ Sigue este orden:
1. ⚡ **[Guía Rápida](./GUIA_RAPIDA.md)** - Referencia de endpoints y límites
2. 📦 **[Empaquetado de Archivos](./EMPAQUETADO_ARCHIVOS.md)** - Formato binario con ejemplos de código
3. 🌐 **[Swagger UI](http://localhost:8000/docs)** - Documentación interactiva

---

### 🔧 Quiero Entender los Detalles Técnicos

**Necesito información técnica avanzada**

➡️ Lee estas guías:
1. 📦 **[Empaquetado de Archivos](./EMPAQUETADO_ARCHIVOS.md)** - Formato binario, estructura, seguridad
2. 🌊 **[Streaming](./STREAMING_GUIA.md)** - Manejo de archivos grandes
3. 📝 **[Sistema de Logging](./LOGGING_SISTEMA.md)** - Logs y debugging

---

### 🚀 Quiero Desplegar la API

**Necesito poner la API en producción**

➡️ Sigue esta ruta:
1. 📖 **[README Principal](../README.md)** - Instalación y configuración
2. 🚂 **[Deploy en Railway](./RAILWAY_DEPLOY.md)** - Despliegue en la nube
3. 📝 **[Sistema de Logging](./LOGGING_SISTEMA.md)** - Monitoreo en producción

---

## 📋 Índice de Documentación

### Para Usuarios

| Documento | Descripción | Nivel | Tiempo de lectura |
|-----------|-------------|-------|-------------------|
| [Guía del Usuario](./GUIA_USUARIO.md) | Tutorial completo con ejemplos prácticos | Principiante | 30 min |
| [Guía Rápida](./GUIA_RAPIDA.md) | Referencia rápida de endpoints | Todos | 5 min |

### Para Desarrolladores

| Documento | Descripción | Nivel | Tiempo de lectura |
|-----------|-------------|-------|-------------------|
| [Empaquetado de Archivos](./EMPAQUETADO_ARCHIVOS.md) | Formato binario y casos de uso | Intermedio | 45 min |
| [Streaming](./STREAMING_GUIA.md) | Manejo de archivos grandes | Avanzado | 20 min |
| [Sistema de Logging](./LOGGING_SISTEMA.md) | Configuración de logs | Intermedio | 15 min |
| [Deploy en Railway](./RAILWAY_DEPLOY.md) | Despliegue en producción | Intermedio | 20 min |

### Documentación Interactiva

| Recurso | Descripción | URL |
|---------|-------------|-----|
| Swagger UI | Interfaz interactiva para probar endpoints | http://localhost:8000/docs |
| ReDoc | Documentación visual y organizada | http://localhost:8000/redoc |
| Health Check | Verificar estado de la API | http://localhost:8000/health |

---

## 🎓 Rutas de Aprendizaje

### Ruta 1: Usuario Básico (30 min)

```
Guía del Usuario → Swagger UI → ¡Empieza a cifrar!
```

**Objetivos:**
- ✅ Entender qué es Scriptum
- ✅ Cifrar y descifrar texto
- ✅ Cifrar y descifrar archivos
- ✅ Conocer límites y mejores prácticas

---

### Ruta 2: Desarrollador Frontend (1 hora)

```
Guía Rápida → Empaquetado de Archivos → Swagger UI → Implementar
```

**Objetivos:**
- ✅ Integrar API en aplicación web
- ✅ Manejar archivos cifrados
- ✅ Implementar UI de cifrado
- ✅ Manejar errores correctamente

---

### Ruta 3: Desarrollador Backend (1.5 horas)

```
README Principal → Empaquetado → Streaming → Logging → Deploy
```

**Objetivos:**
- ✅ Instalar y configurar la API
- ✅ Entender formato binario del paquete
- ✅ Optimizar para archivos grandes
- ✅ Configurar logging
- ✅ Desplegar en producción

---

### Ruta 4: Arquitecto de Software (2 horas)

```
Todo lo anterior + Código fuente + Tests
```

**Objetivos:**
- ✅ Comprender arquitectura completa
- ✅ Evaluar seguridad criptográfica
- ✅ Optimizar rendimiento
- ✅ Diseñar integración robusta

---

## 🔍 Buscar por Tema

### Cifrado y Seguridad

- 🔐 [Tipos de AES (128/192/256)](./GUIA_USUARIO.md#-tipos-de-cifrado-disponibles)
- 🛡️ [Verificación de integridad SHA-256](./EMPAQUETADO_ARCHIVOS.md#️-verificación-de-integridad)
- 🔑 [Mejores prácticas de contraseñas](./GUIA_USUARIO.md#-seguridad-y-mejores-prácticas)
- 📦 [Formato del paquete cifrado](./EMPAQUETADO_ARCHIVOS.md#-formato-del-paquete)

### Archivos

- 📁 [Extensiones soportadas](./GUIA_USUARIO.md#extensiones-de-archivo-soportadas-aes)
- 📏 [Límites de tamaño](./GUIA_USUARIO.md#-límites-y-restricciones)
- 🌊 [Streaming de archivos grandes](./STREAMING_GUIA.md)
- 📦 [Empaquetado binario](./EMPAQUETADO_ARCHIVOS.md)

### Integración

- 💻 [Ejemplos JavaScript](./EMPAQUETADO_ARCHIVOS.md#javascripttypescript-react-vue-angular)
- 🐍 [Ejemplos Python](./EMPAQUETADO_ARCHIVOS.md#python-cliente-desktopbackend)
- 📱 [Ejemplos Flutter/Dart](./EMPAQUETADO_ARCHIVOS.md#flutterdart-app-móvil)
- 🌐 [Endpoints de la API](./GUIA_RAPIDA.md#-endpoints-principales)

### Desarrollo y Deploy

- 🏗️ [Estructura del proyecto](../README.md#️-estructura-del-proyecto)
- 🧪 [Testing](../README.md#-testing)
- 📝 [Sistema de logging](./LOGGING_SISTEMA.md)
- 🚂 [Deploy en Railway](./RAILWAY_DEPLOY.md)

### Solución de Problemas

- ❗ [Errores comunes](./GUIA_USUARIO.md#️-errores-comunes-y-soluciones)
- 🐛 [Debugging con logs](./LOGGING_SISTEMA.md)
- 🔧 [Troubleshooting](../README.md#-solución-de-problemas)

---

## 📊 Comparación de Guías

| Si necesitas... | Lee esto | Por qué |
|----------------|----------|---------|
| Empezar rápido | Guía Rápida | Resumen de 1 página |
| Tutorial completo | Guía del Usuario | Explicación paso a paso |
| Integrar en app | Empaquetado de Archivos | Código de ejemplo |
| Archivos >10 MB | Streaming | Optimización de memoria |
| Poner en producción | Deploy en Railway | Instrucciones de deploy |
| Depurar problemas | Sistema de Logging | Logs y debugging |

---

## 🆘 ¿Aún Tienes Dudas?

### 1️⃣ Busca en la Documentación
Usa **Ctrl+F** o **Cmd+F** para buscar términos específicos en las guías.

### 2️⃣ Prueba con Swagger UI
Accede a http://localhost:8000/docs y experimenta con la API de forma interactiva.

### 3️⃣ Revisa los Ejemplos
Cada guía incluye ejemplos de código completos que puedes copiar y adaptar.

### 4️⃣ Reporta un Issue
Si encontraste un bug o algo no funciona, [abre un issue en GitHub](https://github.com/WaraYasy/Scriptum/issues).

### 5️⃣ Únete a la Discusión
Pregunta en [GitHub Discussions](https://github.com/WaraYasy/Scriptum/discussions) para ayuda de la comunidad.

---

## 📝 Contribuir a la Documentación

¿Encontraste un error o quieres mejorar la documentación?

1. 🍴 Fork el repositorio
2. 📝 Edita los archivos en `ApiScriptum/docs/`
3. 🔍 Verifica ortografía y formato
4. 📤 Envía un Pull Request

**Archivos de documentación:**
```
docs/
├── README.md                    (este archivo)
├── GUIA_USUARIO.md             (guía completa)
├── GUIA_RAPIDA.md              (referencia rápida)
├── EMPAQUETADO_ARCHIVOS.md     (formato binario)
├── STREAMING_GUIA.md           (archivos grandes)
├── LOGGING_SISTEMA.md          (sistema de logs)
└── RAILWAY_DEPLOY.md           (despliegue)
```

---

## 🔗 Enlaces Útiles

- 🏠 [Repositorio GitHub](https://github.com/WaraYasy/Scriptum)
- 📱 [ScriptumFX - Aplicación Desktop](../../ScriptumFX/)
- 🐛 [Reportar Issues](https://github.com/WaraYasy/Scriptum/issues)
- 💬 [Discusiones](https://github.com/WaraYasy/Scriptum/discussions)

---

## 👥 Créditos

Documentación creada y mantenida por:

- 🧙🏻‍♀️ **Arantxa** - [@arantxaMain](https://github.com/arantxaMain)
- 🧙🏽‍♀️ **Wara** - [@WaraYasy](https://github.com/WaraYasy)

---

<div align="center">

**📚 ¿Listo para empezar?**

[Guía del Usuario](./GUIA_USUARIO.md) • [Guía Rápida](./GUIA_RAPIDA.md) • [Swagger UI](http://localhost:8000/docs)

---

Hecho con ❤️ y ☕

</div>
