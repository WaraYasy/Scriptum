# 🚂 Deploy en Railway - Scriptum API

Guía completa para desplegar tu API de cifrado en Railway.

---

## ✅ Archivos Necesarios (Ya Configurados)

Tu proyecto ya tiene todos los archivos necesarios:

- ✅ **Dockerfile** - Configuración de la imagen Docker
- ✅ **start.sh** - Script de inicio que lee la variable PORT
- ✅ **railway.json** - Configuración específica de Railway
- ✅ **.dockerignore** - Archivos a excluir del build
- ✅ **requirements.txt** - Dependencias de Python
- ✅ **main.py** - Aplicación FastAPI configurada

---

## 📋 Pasos para Deploy en Railway

### 1. Crear Cuenta en Railway

1. Ve a [railway.app](https://railway.app)
2. Regístrate con GitHub (recomendado) o email
3. Verifica tu email

### 2. Conectar Repositorio

**Opción A: Desde GitHub** (Recomendado)

1. Sube tu código a GitHub:
   ```bash
   git add .
   git commit -m "FEAT: Preparar deploy en Railway"
   git push origin main
   ```

2. En Railway:
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Autoriza Railway a acceder a tus repos
   - Selecciona el repo `ApiScriptum`

**Opción B: Desde CLI**

1. Instala Railway CLI:
   ```bash
   npm i -g @railway/cli
   # o con Homebrew
   brew install railway
   ```

2. Autentica:
   ```bash
   railway login
   ```

3. Despliega:
   ```bash
   railway init
   railway up
   ```

### 3. Configurar Variables de Entorno

Railway detectará automáticamente el Dockerfile y expondrá la variable `PORT`.

**Variables adicionales (opcionales):**

En el dashboard de Railway > Variables:

```env
DEBUG=False
ALLOWED_ORIGINS=["https://tu-cliente.railway.app","http://localhost:3000"]
```

**Nota**: Railway inyecta automáticamente la variable `PORT`, no la configures manualmente.

### 4. Verificar Deploy

1. Railway iniciará el build automáticamente
2. Espera a que termine (2-5 minutos)
3. Railway te asignará un dominio: `https://tu-proyecto.up.railway.app`
4. Verifica el health check:
   ```bash
   curl https://tu-proyecto.up.railway.app/health
   ```

---

## 🔧 Configuración Automática de Railway

Railway detecta automáticamente:

### Del `Dockerfile`:
```dockerfile
EXPOSE 8000          # Railway ignora esto, usa su propia variable PORT
HEALTHCHECK ...      # Railway usa esto para verificar que la app esté viva
```

### Del `railway.json`:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

### Del `start.sh`:
```bash
PORT=${PORT:-8000}  # Lee PORT de Railway, usa 8000 como fallback
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
```

---

## 🌐 Endpoints Disponibles

Una vez desplegado, tendrás acceso a:

```
https://tu-proyecto.up.railway.app/
https://tu-proyecto.up.railway.app/docs          # Swagger UI
https://tu-proyecto.up.railway.app/redoc         # ReDoc
https://tu-proyecto.up.railway.app/health        # Health check
https://tu-proyecto.up.railway.app/aes/info      # Info de AES
https://tu-proyecto.up.railway.app/vigenere/info # Info de Vigenère
```

---

## 🎯 Prueba Rápida

```bash
# Verificar que la API está funcionando
curl https://tu-proyecto.up.railway.app/health

# Probar cifrado AES
curl -X POST "https://tu-proyecto.up.railway.app/aes/cifrar/texto" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "Hola desde Railway",
    "password": "password123",
    "tipo_aes": "AES-256"
  }'
```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real:

**Desde el Dashboard:**
1. Ve a tu proyecto en Railway
2. Click en "Deployments"
3. Click en el último deployment
4. Ve a la pestaña "Logs"

**Desde CLI:**
```bash
railway logs
```

### Métricas:

Railway muestra automáticamente:
- ✅ CPU usage
- ✅ Memory usage
- ✅ Network traffic
- ✅ Deploy status
- ✅ Build time

---

## 🔒 Variables de Entorno Recomendadas

```env
# Producción
DEBUG=False

# CORS - Añade el dominio de tu cliente
ALLOWED_ORIGINS=["https://tu-cliente.com","https://tu-cliente.railway.app"]

# Puerto (Railway lo maneja automáticamente)
# PORT=8000  ← NO configures esto, Railway lo inyecta automáticamente
```

---

## 🚀 Dominio Personalizado (Opcional)

### Usar tu propio dominio:

1. En Railway > Settings > Domains
2. Click en "Custom Domain"
3. Añade tu dominio (ej: `api.tudominio.com`)
4. Railway te dará registros DNS para configurar:

```
Type: CNAME
Name: api
Value: tu-proyecto.up.railway.app
```

5. Añade el registro en tu proveedor DNS (Cloudflare, Namecheap, etc.)
6. Espera propagación (5-60 minutos)

### Actualizar CORS:

```env
ALLOWED_ORIGINS=["https://api.tudominio.com","https://tuapp.com"]
```

---

## 🔄 Actualizaciones Automáticas

Railway redespliega automáticamente cuando:

1. Haces `git push` a la rama configurada (main)
2. Cambias variables de entorno
3. Usas `railway up` desde CLI

**No necesitas hacer nada manualmente** - cada push a GitHub despliega automáticamente.

---

## 💰 Costos

Railway ofrece:

- **Plan Gratis**:
  - $5 USD de crédito mensual
  - Suficiente para proyectos pequeños/medianos
  - ~500 horas de ejecución

- **Plan Pro** ($20/mes):
  - $20 USD de crédito
  - Más recursos
  - Soporte prioritario

**Estimado de uso para tu API:**
- API pequeña/mediana: ~$3-5 USD/mes
- API con tráfico alto: ~$10-15 USD/mes

---

## 🐛 Troubleshooting

### Error: "Application failed to respond"

**Causa**: La app no está escuchando en el puerto correcto.

**Solución**: Verifica que `start.sh` esté usando `$PORT`:
```bash
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
```

### Error: "Healthcheck failed"

**Causa**: El endpoint `/health` no responde.

**Solución**: Verifica que el router de health esté registrado:
```python
# main.py
from app.routers import health
app.include_router(health.router, tags=["Health"])
```

### Error: "Build failed"

**Causa**: Error al construir la imagen Docker.

**Solución**: Revisa los logs de build en Railway y verifica que `requirements.txt` esté completo.

### Error: CORS

**Causa**: El origen del cliente no está en ALLOWED_ORIGINS.

**Solución**: Añade el dominio a la variable de entorno:
```env
ALLOWED_ORIGINS=["https://tu-cliente.railway.app","https://tudominio.com"]
```

---

## 📝 Checklist de Deploy

Antes de desplegar, verifica:

- [ ] Código subido a GitHub
- [ ] `DEBUG=False` en producción
- [ ] CORS configurado con los dominios correctos
- [ ] Endpoint `/health` funcionando
- [ ] `requirements.txt` completo
- [ ] `Dockerfile` sin errores
- [ ] Tests pasando localmente

---

## 🎉 ¡Listo!

Tu API de Scriptum está lista para producción en Railway con:

✅ **Deploy automático** desde GitHub
✅ **HTTPS** incluido
✅ **Healthchecks** automáticos
✅ **Logs** en tiempo real
✅ **Escalado** horizontal disponible
✅ **Dominio personalizado** (opcional)

---

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Railway Discord](https://discord.gg/railway)
- [FastAPI en Railway](https://docs.railway.app/guides/fastapi)

---

## 🔗 Links Útiles

Una vez desplegado:

- **Dashboard**: https://railway.app/dashboard
- **Proyecto**: https://railway.app/project/tu-proyecto-id
- **API Docs**: https://tu-proyecto.up.railway.app/docs
- **Health**: https://tu-proyecto.up.railway.app/health
