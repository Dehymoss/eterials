# 🚀 GUÍA COMPLETA DE MIGRACIÓN A RENDER.COM

## 📋 RESUMEN EJECUTIVO

**Servidor Recomendado**: RENDER.COM  
**Costo**: $0 (Plan gratuito permanente)  
**Tiempo de configuración**: 10-15 minutos  
**Tiempo de deploy**: 5-8 minutos  
**URL final**: https://eterials-restaurant.onrender.com  

---

## ✅ PREPARACIÓN COMPLETADA

El proyecto ya está listo para migrar con los siguientes archivos:

- ✅ `requirements.txt` - Dependencias Python
- ✅ `render.yaml` - Configuración automática de Render
- ✅ `.env.example` - Variables de entorno template
- ✅ `main.py` - Modificado para producción
- ✅ `preparar_deploy.py` - Script de verificación

---

## 🎯 PASO A PASO - MIGRACIÓN A RENDER.COM

### **PASO 1: PREPARAR REPOSITORIO (5 min)**

```bash
# En tu terminal local
cd "g:\Mi unidad\eterials-chatbot"

# Inicializar Git si no existe
git init

# Agregar todos los archivos
git add .

# Commit inicial
git commit -m "Sistema de restaurante Eterials - Listo para deploy"

# Crear repositorio en GitHub
# Ve a github.com → New repository → "eterials-restaurant"

# Conectar con GitHub
git remote add origin https://github.com/TU_USUARIO/eterials-restaurant.git
git branch -M main
git push -u origin main
```

### **PASO 2: CONFIGURAR RENDER.COM (3 min)**

1. **Crear cuenta**: Ve a [render.com](https://render.com) → Sign up
2. **Conectar GitHub**: Dashboard → Connect GitHub
3. **Nuevo servicio**: Dashboard → New → Web Service
4. **Seleccionar repo**: Buscar "eterials-restaurant" → Connect

### **PASO 3: CONFIGURACIÓN AUTOMÁTICA (2 min)**

Render detectará automáticamente:
- ✅ `render.yaml` → Configuración completa
- ✅ `requirements.txt` → Dependencias
- ✅ `main.py` → Punto de entrada
- ✅ Puerto 8080 → Variable de entorno

**Configuración manual (si es necesaria)**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Plan**: Free
- **Environment Variables**:
  - `PORT` = `8080`
  - `FLASK_ENV` = `production`

### **PASO 4: DEPLOY AUTOMÁTICO (5-8 min)**

1. **Iniciar deploy**: Click "Create Web Service"
2. **Monitor progreso**: Ver logs en tiempo real
3. **Verificar deploy**: Estado "Live" indica éxito
4. **Obtener URL**: https://eterials-restaurant.onrender.com

---

## 🌐 URLs DESPUÉS DEL DEPLOY

Una vez desplegado, tu sistema estará disponible en:

- **🏠 Principal**: https://eterials-restaurant.onrender.com/
- **👨‍💼 Panel Admin**: https://eterials-restaurant.onrender.com/admin
- **🍽️ Gestión Menú**: https://eterials-restaurant.onrender.com/menu-admin/admin
- **🍳 Dashboard Cocina**: https://eterials-restaurant.onrender.com/cocina
- **📱 Menú Cliente**: https://eterials-restaurant.onrender.com/menu
- **🤖 Chatbot**: https://eterials-restaurant.onrender.com/chatbot

---

## 🔧 CONFIGURACIONES OPCIONALES

### **APIs Externas de Imágenes (Opcional)**

Si quieres habilitar la búsqueda automática de imágenes:

1. **Dashboard Render** → Environment Variables
2. **Agregar las siguientes** (obtener keys es gratis):

```
UNSPLASH_ACCESS_KEY=tu_clave_unsplash
PEXELS_API_KEY=tu_clave_pexels  
PIXABAY_API_KEY=tu_clave_pixabay
```

**Dónde obtener las claves**:
- Unsplash: https://unsplash.com/developers
- Pexels: https://www.pexels.com/api/
- Pixabay: https://pixabay.com/api/docs/

### **Dominio Personalizado (Opcional)**

1. **Dashboard Render** → Settings → Custom Domains
2. **Agregar**: `tu-restaurante.com`
3. **Configurar DNS**: Apuntar CNAME a Render
4. **SSL automático**: Render lo configura gratis

---

## 📊 CARACTERÍSTICAS DEL PLAN GRATUITO

### **✅ INCLUIDO:**
- **750 horas/mes**: Suficiente para restaurante (24/7 = 720h)
- **512MB RAM**: Perfecto para tu proyecto Flask
- **100GB bandwidth/mes**: Más que suficiente
- **SSL/HTTPS**: Certificado automático gratis
- **Custom domains**: Dominio personalizado incluido
- **Auto-deploy**: Deploy automático con Git push
- **Logs en tiempo real**: Debugging completo
- **Zero downtime deployments**: Sin interrupciones

### **⚠️ LIMITACIONES:**
- **Sleep después 15 min**: Normal para restaurantes (se reactiva en <1 seg)
- **No persistent disk**: SQLite se mantiene en memoria (OK para tu caso)
- **1 concurrent build**: Un deploy a la vez

---

## 🚀 PROCESO DE DEPLOY AUTOMÁTICO

Una vez configurado, cada vez que hagas cambios:

```bash
# En tu computadora local
git add .
git commit -m "Descripción del cambio"
git push

# Render automáticamente:
# 1. Detecta el push
# 2. Inicia nuevo build
# 3. Instala dependencias
# 4. Ejecuta tests (si los hay)
# 5. Deploy sin downtime
# 6. Tu app se actualiza en ~3-5 minutos
```

---

## 🆔 ALTERNATIVAS DE RESPALDO

### **Si Render no funciona:**

**OPCIÓN B: Railway.app**
- $5 crédito mensual gratis
- Deploy: https://railway.app
- Configuración similar

**OPCIÓN C: PythonAnywhere**
- Plan gratuito permanente
- Deploy: https://pythonanywhere.com
- Ideal para proyectos pequeños

---

## 📞 SOPORTE Y TROUBLESHOOTING

### **Problemas Comunes:**

**1. Error en Build**:
- Verificar `requirements.txt`
- Revisar logs de build en Render

**2. App no inicia**:
- Verificar `main.py` está correcto
- Confirmar puerto 8080 en variables de entorno

**3. Base de datos vacía**:
- Ejecutar `python migrar_db.py` localmente
- Hacer commit y push de la BD actualizada

**4. Archivos estáticos no cargan**:
- Verificar rutas en templates
- Confirmar estructura de carpetas `static/`

### **Contacto Render Support:**
- Email: support@render.com  
- Discord: https://discord.gg/render
- Docs: https://render.com/docs

---

## 🎉 ¡LISTO PARA PRODUCCIÓN!

Tu sistema de gestión de restaurante estará disponible 24/7 en internet con:

- ✅ **Panel administrativo completo**
- ✅ **Menú público responsive** 
- ✅ **Sistema de códigos QR móvil**
- ✅ **Dashboard para cocina**
- ✅ **Chatbot integrado**
- ✅ **Upload de imágenes**
- ✅ **Gestión de categorías y productos**
- ✅ **SSL/HTTPS seguro**
- ✅ **Costo: $0**

**¿Necesitas ayuda con el deploy? ¡Continúa con la simulación paso a paso!**
