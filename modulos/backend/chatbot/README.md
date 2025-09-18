# Backend del Chatbot - Documentación Técnica

## 🏗️ Arquitectura General

### Componentes Principales

1. **`models.py`** - Modelos SQLAlchemy
   - `Sesion` - Tracking de usuarios por mesa
   - `Calificacion` - Sistema de calificaciones 1-5 estrellas
   - `Comentario` - Comentarios y sugerencias
   - `NotificacionMesero` - Sistema de notificaciones al personal
   - `Analytics` - Métricas y eventos del chatbot
   - `ConfiguracionChatbot` - Configuraciones dinámicas

2. **`api_endpoints.py`** - APIs REST
   - `/api/chatbot/sesion/*` - Gestión de sesiones
   - `/api/chatbot/calificacion` - Calificaciones
   - `/api/chatbot/comentario` - Comentarios
   - `/api/chatbot/notificacion/*` - Notificaciones
   - `/api/chatbot/analytics/*` - Analytics
   - `/api/chatbot/configuracion` - Configuración

3. **`admin_dashboard.py`** - Dashboard administrativo
   - `/admin/chatbot/` - Panel principal
   - `/admin/chatbot/notificaciones` - Gestión notificaciones
   - `/admin/chatbot/analytics` - Reportes y gráficos
   - APIs para dashboard en tiempo real

4. **`services.py`** - Servicios y utilidades
   - Inicialización de tablas
   - Configuración por defecto
   - Verificación de estado
   - Scripts de migración

5. **`test_backend.py`** - Testing automatizado
   - Suite completa de tests
   - Verificación de todos los endpoints
   - Validación de funcionalidades

## 🔄 Flujo de Trabajo

### Fase 1: Desarrollo Backend (ACTUAL)
- ✅ Arquitectura diseñada
- ✅ Modelos de datos creados
- ✅ APIs implementadas
- ✅ Dashboard administrativo
- ✅ Testing automatizado

### Fase 2: Inicialización y Testing
- [ ] Crear tablas en base de datos
- [ ] Inicializar configuraciones
- [ ] Ejecutar tests completos
- [ ] Verificar funcionalidades

### Fase 3: Migración Frontend
- [ ] Conectar JavaScript actual con APIs
- [ ] Migrar configuraciones hardcodeadas
- [ ] Implementar persistencia de datos
- [ ] Testing de integración

### Fase 4: Deployment
- [ ] Subir cambios a Render.com
- [ ] Verificar funcionamiento en producción
- [ ] Monitoreo y analytics

## 📊 Base de Datos

### Tablas Nuevas
```sql
-- Sesiones de usuarios
chatbot_sesiones
- id, mesa, nombre_cliente, fecha_inicio, fecha_ultimo_acceso
- dispositivo, ip_cliente, activa

-- Calificaciones
chatbot_calificaciones  
- id, sesion_id, estrellas, fecha_calificacion, categoria

-- Comentarios
chatbot_comentarios
- id, sesion_id, texto_comentario, tipo, fecha_comentario, moderado

-- Notificaciones al personal
chatbot_notificaciones
- id, sesion_id, tipo_notificacion, mensaje, fecha_notificacion
- atendida, atendida_por, fecha_atencion, prioridad

-- Analytics y métricas
chatbot_analytics
- id, fecha, mesa, evento, valor_numerico, valor_texto, metadatos

-- Configuración dinámica
chatbot_configuracion
- id, clave, valor, tipo, descripcion, fecha_modificacion
```

## 🔧 APIs Principales

### Sesiones
- `POST /api/chatbot/sesion/iniciar` - Crear sesión
- `PUT /api/chatbot/sesion/{id}/actualizar` - Actualizar sesión

### Calificaciones
- `POST /api/chatbot/calificacion` - Guardar calificación

### Comentarios  
- `POST /api/chatbot/comentario` - Guardar comentario

### Notificaciones
- `POST /api/chatbot/notificacion/mesero` - Llamar mesero
- `GET /api/chatbot/notificaciones/pendientes` - Ver pendientes

### Analytics
- `GET /api/chatbot/analytics/resumen` - Resumen de métricas
- `GET /api/chatbot/saludo` - Saludo dinámico

### Configuración
- `GET /api/chatbot/configuracion` - Obtener configuración

## 🎯 Beneficios del Backend

### Para el Restaurante
- **Datos persistentes** - No se pierden calificaciones ni comentarios
- **Analytics en tiempo real** - Métricas de satisfacción por mesa
- **Notificaciones efectivas** - Sistema real de llamada al mesero
- **Configuración flexible** - Cambiar textos sin código

### Para el Personal
- **Dashboard centralizado** - Ver todas las notificaciones
- **Priorización automática** - Urgentes vs normales
- **Histórico completo** - Seguimiento de atención al cliente
- **Reportes automáticos** - Analytics de rendimiento

### Para los Clientes
- **Experiencia mejorada** - Respuestas más rápidas
- **Personalización** - Saludos y configuración dinámica
- **Seguimiento efectivo** - Sus solicitudes no se pierden

## 🚀 Comandos de Inicialización

```python
# Crear tablas del backend
from modulos.backend.chatbot.services import crear_tablas_chatbot
crear_tablas_chatbot()

# Inicializar configuración
from modulos.backend.chatbot.services import inicializar_configuracion_default
inicializar_configuracion_default()

# Verificar estado
from modulos.backend.chatbot.services import verificar_estado_backend
estado = verificar_estado_backend()
print(estado)

# Testing completo
python modulos/backend/chatbot/test_backend.py
```

## 📈 Métricas Disponibles

### Dashboard Principal
- Sesiones activas por mesa
- Calificación promedio
- Comentarios sin moderar
- Notificaciones pendientes

### Analytics Avanzados
- Actividad por día/hora
- Distribución de calificaciones
- Tipos de notificaciones más comunes
- Mesas con mayor actividad
- Tiempos de respuesta del personal

## 🔒 Consideraciones de Seguridad

- Validación de todos los inputs
- Sanitización de comentarios
- Rate limiting en APIs críticas
- Logs de auditoría para notificaciones
- Configuración protegida por permisos

## 🎨 Integración Frontend

### JavaScript Actual → Backend
```javascript
// Antes (solo frontend)
sessionStorage.setItem("nombreCliente", nombre);

// Después (con backend)
await fetch('/api/chatbot/sesion/iniciar', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        mesa: mesa,
        nombre_cliente: nombre,
        dispositivo: navigator.userAgent,
        ip_cliente: 'auto'
    })
});
```

### Calificaciones Actual → Backend
```javascript
// Antes (solo alerta)
alert(`¡Gracias por tu calificación de ${estrellas} estrella(s)!`);

// Después (persistente)
await fetch('/api/chatbot/calificacion', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        sesion_id: sesionActual,
        estrellas: estrellas,
        categoria: 'general'
    })
});
```

## 🔄 Plan de Migración

### Estrategia Gradual
1. **Backend funcionando** ✅ (completado)
2. **Testing local** ⏳ (próximo paso)
3. **Migración APIs** (sin cambiar UI)
4. **Nuevas funcionalidades** (dashboard admin)
5. **Deployment producción**

### Compatibilidad
- Frontend actual seguirá funcionando
- Backend funciona en paralelo
- Migración gradual sin interrupciones
- Rollback disponible si hay problemas

---

**Estado:** 🏗️ **BACKEND COMPLETO - LISTO PARA TESTING**
**Próximo paso:** Inicializar tablas y ejecutar tests