# Sistema de Chatbot Backend Completo 🤖

## Descripción General

Este módulo implementa un sistema de chatbot completo para el restaurante, con capacidades avanzadas de gestión, analytics, notificaciones y **personalización de temas**. El sistema está diseñado para integrarse perfectamente con la infraestructura existente del proyecto Eterials.

## ✨ Características Principales

### 🎨 **SISTEMA DE PERSONALIZACIÓN DE TEMAS** (ACTUALIZADO v2.1.0)
- **4 Temas Predefinidos**: Eterials Clásico, Minimalista Oscuro, Café Warmth, Neon Nights
- **Creación de Temas Personalizados**: Editor completo desde el dashboard
- **Preview en Tiempo Real**: Vista previa instantánea de cambios
- **Generación CSS Automática**: CSS dinámico basado en propiedades del tema
- **🖼️ FONDOS PERSONALIZADOS** (NUEVO):
  - **Upload de Imágenes**: Subida de fondos personalizados (JPG, PNG, GIF, WEBP)
  - **Miniaturas Automáticas**: Generación automática de thumbnails para preview
  - **Gestión de Archivos**: Sistema robusto de almacenamiento y limpieza
  - **Estadísticas de Uso**: Tracking de fondos más utilizados
  - **Integración con Temas**: Aplicación de fondos personalizados a cualquier tema
- **Categorías de Personalización**:
  - 🎨 **Colores**: Primarios, secundarios, fondos, texto, botones
  - 🔤 **Fuentes**: Principales, secundarias, botones, tamaños
  - 🔘 **Botones**: Bordes, padding, sombras, efectos hover
  - ✨ **Efectos**: Transiciones, animaciones, blur, transformaciones
  - 🖼️ **Fondos**: Gradientes, imágenes personalizadas, overlays, posicionamiento

### 🎯 Gestión de Sesiones
- Seguimiento completo de sesiones de usuarios
- Almacenamiento de preferencias del cliente
- Historial de interacciones por mesa

### ⭐ Sistema de Calificaciones
- Calificaciones de 1-5 estrellas
- Comentarios opcionales de usuarios
- Analytics de satisfacción del cliente

### 💬 Gestión de Comentarios
- Comentarios de clientes con moderación
- Categorización automática
- Respuestas del personal del restaurante

### 🔔 Notificaciones en Tiempo Real
- Notificaciones al personal del restaurante
- Diferentes tipos: urgente, info, solicitud
- Sistema de estado (pendiente, leído, resuelto)

### 📊 Analytics Avanzado
- Métricas de uso del chatbot
- Análisis de satisfacción del cliente
- Reportes de actividad por períodos
- Gráficos en tiempo real

### ⚙️ Configuración Dinámica
- Configuraciones modificables sin reiniciar
- Saludos personalizados por horario
- Timeouts configurables
- Sistema de temas activos

## 🏗️ Arquitectura del Sistema

### Estructura de Archivos
```
modulos/backend/chatbot/
├── models.py                 # 📊 Modelos de base de datos (9 tablas + temas + fondos)
├── api_endpoints.py          # 🌐 APIs REST (25+ endpoints + fondos)
├── admin_dashboard.py        # 👥 Dashboard administrativo + gestión fondos
├── services.py              # 🔧 Servicios auxiliares
├── init_database.py         # 🚀 Inicializador de BD + datos por defecto
├── test_backend.py          # 🧪 Tests automatizados
└── README.md               # 📚 Esta documentación
```

### Base de Datos

#### Tablas Principales
1. **Sesion** - Sesiones de usuarios del chatbot
2. **Calificacion** - Calificaciones de 1-5 estrellas
3. **Comentario** - Comentarios de clientes
4. **NotificacionMesero** - Notificaciones al personal
5. **Analytics** - Eventos y métricas del sistema
6. **ConfiguracionChatbot** - Configuraciones dinámicas

#### Tablas de Personalización (ACTUALIZADO v2.1.0)
7. **TemaPersonalizacion** - Metadatos de temas
8. **PropiedadTema** - Propiedades CSS por tema
9. **🖼️ FondoPersonalizado** - **Fondos de imagen personalizados (NUEVO)**
   - Almacena metadatos de imágenes subidas
   - Miniaturas automáticas y estadísticas de uso
   - Integración completa con sistema de temas

### APIs REST Disponibles

#### Gestión de Sesiones
- `GET /api/chatbot/sesiones` - Listar sesiones
- `POST /api/chatbot/sesiones` - Crear nueva sesión
- `PUT /api/chatbot/sesiones/{id}` - Actualizar sesión
- `DELETE /api/chatbot/sesiones/{id}` - Finalizar sesión

#### Sistema de Calificaciones
- `GET /api/chatbot/calificaciones` - Obtener calificaciones
- `POST /api/chatbot/calificaciones` - Enviar calificación
- `GET /api/chatbot/calificaciones/promedio` - Promedio por período

#### Gestión de Comentarios
- `GET /api/chatbot/comentarios` - Listar comentarios
- `POST /api/chatbot/comentarios` - Enviar comentario
- `PUT /api/chatbot/comentarios/{id}/moderar` - Moderar comentario

#### Notificaciones
- `GET /api/chatbot/notificaciones` - Obtener notificaciones
- `POST /api/chatbot/notificaciones` - Crear notificación
- `PUT /api/chatbot/notificaciones/{id}/estado` - Cambiar estado

#### Analytics
- `GET /api/chatbot/analytics/resumen` - Resumen de métricas
- `GET /api/chatbot/analytics/graficos` - Datos para gráficos
- `POST /api/chatbot/analytics/evento` - Registrar evento

#### **APIs de Personalización (ACTUALIZADO v2.1.0)**
- `GET /api/chatbot/temas` - Listar todos los temas
- `GET /api/chatbot/temas/{id}` - Detalles de tema específico
- `POST /api/chatbot/temas` - Crear tema personalizado
- `PUT /api/chatbot/temas/{id}/propiedades` - Actualizar propiedades
- `POST /api/chatbot/temas/{id}/activar` - Activar tema
- `DELETE /api/chatbot/temas/{id}` - Eliminar tema
- `GET /api/chatbot/temas/activo/css` - **CSS dinámico del tema activo**

#### **APIs de Fondos Personalizados (NUEVO v2.1.0)**
- `GET /api/chatbot/fondos` - **Listar todos los fondos subidos**
- `POST /api/chatbot/fondos/upload` - **Subir nuevo fondo personalizado**
- `DELETE /api/chatbot/fondos/{id}` - **Eliminar fondo específico**
- `PUT /api/chatbot/temas/{id}/fondo` - **Aplicar fondo a tema específico**

#### Configuración
- `GET /api/chatbot/configuracion` - Obtener configuraciones
- `PUT /api/chatbot/configuracion/{clave}` - Actualizar configuración
- `GET /api/chatbot/saludo` - Obtener saludo personalizado

### Dashboard Administrativo

#### Rutas Principales
- `/admin/chatbot/` - Dashboard principal
- `/admin/chatbot/notificaciones` - Panel de notificaciones
- `/admin/chatbot/analytics` - Panel de analytics
- `/admin/chatbot/configuracion` - Configuración del sistema

#### **Rutas de Gestión de Temas (ACTUALIZADO v2.1.0)**
- `/admin/chatbot/temas` - **Gestión completa de temas**
- `/admin/chatbot/temas/editor/{id}` - **Editor de tema específico**
- `/admin/chatbot/temas/preview` - **Vista previa en tiempo real**
- `/admin/chatbot/fondos` - **🖼️ Gestión de fondos personalizados**
- `/admin/chatbot/temas/{id}/personalizar` - **🎨 Personalización avanzada de temas**

## 🚀 Instalación y Configuración

### 1. Inicializar Base de Datos
```bash
# Ejecutar desde la raíz del proyecto
python modulos/backend/chatbot/init_database.py

# Verificar estado
python modulos/backend/chatbot/init_database.py --verificar
```

### 2. Verificar Integración
```bash
# Ejecutar tests automáticos
python modulos/backend/chatbot/test_backend.py

# Específicos por módulo
python modulos/backend/chatbot/test_backend.py --modulo=temas
python modulos/backend/chatbot/test_backend.py --modulo=sesiones
```

### 3. Registrar Blueprint
En tu `main.py` principal:
```python
from modulos.backend.chatbot.api_endpoints import chatbot_api_bp
from modulos.backend.chatbot.admin_dashboard import chatbot_admin_bp

# Registrar blueprints
app.register_blueprint(chatbot_api_bp)
app.register_blueprint(chatbot_admin_bp)
```

## 🎨 Uso del Sistema de Temas

### Activar un Tema Predefinido
```javascript
// Via API REST
fetch('/api/chatbot/temas/1/activar', {
    method: 'POST'
})
.then(response => response.json())
.then(data => console.log('Tema activado:', data));
```

### Crear Tema Personalizado
```javascript
const nuevoTema = {
    nombre: 'mi_tema_especial',
    descripcion: 'Tema personalizado para eventos',
    propiedades: {
        colores: {
            color_primario: '#ff6b6b',
            color_secundario: '#4ecdc4',
            color_fondo: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)'
        },
        fuentes: {
            fuente_principal: 'Poppins, sans-serif',
            tamaño_titulo: '3rem'
        },
        botones: {
            boton_border_radius: '30px',
            boton_padding: '15px 30px'
        }
    }
};

fetch('/api/chatbot/temas', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(nuevoTema)
});
```

### Aplicar CSS Dinámico
```html
<!-- En el template del chatbot -->
<link rel="stylesheet" href="/api/chatbot/temas/activo/css">

<!-- El CSS se genera automáticamente con las variables del tema activo -->
<div class="chatbot-container">
    <h1 class="chatbot-title">¡Bienvenido!</h1>
    <button class="btn-chatbot">Iniciar Chat</button>
</div>
```

### 🖼️ Gestión de Fondos Personalizados (NUEVO v2.1.0)

#### Subir Nuevo Fondo
```javascript
// Subir archivo de imagen como fondo personalizado
const formData = new FormData();
formData.append('archivo', imagenFile);
formData.append('nombre', 'Mi Fondo Personalizado');

fetch('/api/chatbot/fondos/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Fondo subido:', data.fondo);
    // { id: 1, nombre: 'Mi Fondo', archivo_url: '/chatbot/static/fondos/abc123.jpg' }
});
```

#### Aplicar Fondo a Tema
```javascript
// Aplicar fondo personalizado a un tema específico
const configuracionFondo = {
    fondo_id: 1,              // ID del fondo subido
    overlay: 'rgba(0,0,0,0.4)', // Overlay para legibilidad
    attachment: 'fixed',       // 'fixed' o 'scroll'
    size: 'cover'             // 'cover', 'contain', 'auto'
};

fetch('/api/chatbot/temas/3/fondo', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(configuracionFondo)
});
```

#### Listar Fondos Disponibles
```javascript
// Obtener todos los fondos subidos con estadísticas
fetch('/api/chatbot/fondos')
.then(response => response.json())
.then(fondos => {
    fondos.forEach(fondo => {
        console.log(`${fondo.nombre}: ${fondo.contador_uso} usos`);
        console.log(`Dimensiones: ${fondo.dimensiones}`);
        console.log(`Miniatura: ${fondo.miniatura_url}`);
    });
});
```

## 🔧 Configuración Avanzada

### Temas Predefinidos Incluidos

#### 1. **Eterials Clásico** (Por defecto)
- Colores dorados y azules elegantes
- Fuentes serif clásicas (Playfair Display)
- Efectos suaves y profesionales

#### 2. **Minimalista Oscuro**
- Colores oscuros con verde azulado
- Fuentes sans-serif modernas (Inter)
- Líneas limpias y minimalistas

#### 3. **Café Warmth**
- Tonos cálidos marrones y cremas
- Fuentes cursivas (Dancing Script)
- Efectos amigables y acogedores

#### 4. **Neon Nights**
- Colores neón futuristas
- Fuentes tecnológicas (Orbitron)
- Efectos brillantes y modernos

### Configuraciones por Defecto
```python
CONFIGURACIONES_DEFAULT = [
    {
        'clave': 'saludo_manana',
        'valor': 'Buenos días',
        'tipo': 'string',
        'descripcion': 'Saludo para horas de la mañana (6:00 - 11:59)'
    },
    {
        'clave': 'tema_activo',
        'valor': 'eterials_clasico',
        'tipo': 'string',
        'descripcion': 'Tema actualmente activo en el chatbot'
    }
    # ... más configuraciones
]
```

## 📊 Analytics y Métricas

### Eventos Rastreados
- **Sesiones iniciadas/finalizadas**
- **Calificaciones enviadas**
- **Comentarios publicados**
- **Temas activados** (NUEVO)
- **Configuraciones modificadas**
- **Notificaciones generadas**

### Métricas Disponibles
- Sesiones activas en tiempo real
- Promedio de calificaciones por día/semana/mes
- Comentarios pendientes de moderación
- Notificaciones por resolver
- **Temas más utilizados** (NUEVO)
- Tiempo promedio de sesión

## 🧪 Testing

### Tests Automatizados Incluidos
```bash
# Ejecutar suite completa
python test_backend.py

# Tests específicos
python test_backend.py --test=test_crear_sesion
python test_backend.py --test=test_sistema_calificaciones
python test_backend.py --test=test_notificaciones_tiempo_real
python test_backend.py --test=test_analytics_basico
python test_backend.py --test=test_configuracion_dinamica
python test_backend.py --test=test_temas_personalizacion  # NUEVO
```

### Casos de Prueba
- ✅ Creación y gestión de sesiones
- ✅ Sistema de calificaciones 1-5 estrellas
- ✅ Comentarios con moderación
- ✅ Notificaciones en tiempo real
- ✅ Analytics y métricas
- ✅ Configuración dinámica
- ✅ **Gestión completa de temas** (NUEVO)
- ✅ **Generación CSS dinámico** (NUEVO)

## 🔗 Integración con Frontend

### Variables CSS Disponibles (Tema Activo)
```css
:root {
    --color-primario: #FFD700;
    --color-secundario: #1e3c72;
    --color-fondo: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --fuente-principal: 'Playfair Display, serif';
    --boton-border-radius: 25px;
    --transicion: 0.3s ease;
    /* ... todas las propiedades del tema activo */
}
```

### Clases CSS Recomendadas
```css
.chatbot-container { /* Usar variables del tema */ }
.btn-chatbot { /* Botones con estilos del tema */ }
.chatbot-title { /* Títulos con fuentes del tema */ }
.message-card { /* Tarjetas con colores del tema */ }
```

## 📈 Roadmap Futuro

### Próximas Funcionalidades
- 🎮 **Editor visual de temas** con drag & drop
- 🌙 **Temas automáticos** por horario (día/noche)
- 🎨 **Paletas de colores** automáticas
- 📱 **Temas específicos** para móviles
- 🎵 **Integración con música** ambiente
- 🖼️ **Fondos personalizados** por tema
- 🌈 **Gradientes dinámicos** generados automáticamente

### Integraciones Planificadas
- 📧 Email notifications para comentarios críticos
- 🔔 Push notifications para notificaciones urgentes
- 📊 Integración con Google Analytics
- 💾 Backup automático de configuraciones
- 🌐 API externa para compartir temas

## 🆘 Soporte y Documentación

### Logs del Sistema
```bash
# Ver logs de actividad
tail -f logs/chatbot_backend.log

# Logs específicos de temas
grep "tema_" logs/chatbot_backend.log
```

### Debugging Común
- **Error de tema no encontrado**: Verificar que exista en BD
- **CSS no se aplica**: Verificar cache del navegador
- **Propiedades faltantes**: Ejecutar inicializador de datos

### Estado del Sistema
```bash
# Verificar estado completo
python init_database.py --verificar

# Estadísticas rápidas
curl http://localhost:8080/api/chatbot/analytics/resumen
```

---

## 📞 Contacto y Contribución

Este sistema fue diseñado como parte del proyecto **Eterials Chatbot** con foco en escalabilidad, mantenibilidad y **personalización avanzada**. 

**Características únicas del sistema de temas:**
- 🎨 4 temas predefinidos profesionales
- 🛠️ Editor completo desde dashboard 
- ⚡ Preview en tiempo real
- 🔧 CSS generado dinámicamente
- 📱 Responsive y optimizado
- 🎯 Categorización de propiedades

Para contribuciones, reportes de bugs o nuevas funcionalidades, utilizar el sistema de issues del proyecto principal.

---

**Versión:** 2.0.0 (Con Sistema de Personalización de Temas)  
**Última actualización:** Diciembre 2024  
**Compatibilidad:** Python 3.8+, Flask 2.0+, SQLAlchemy 1.4+