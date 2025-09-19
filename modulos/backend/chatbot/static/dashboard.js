/**
 * Dashboard Chatbot Administrativo - JavaScript
 * Eterials Restaurant Management System
 */

class ChatbotDashboard {
    constructor() {
        this.currentSection = 'resumen';
        this.updateInterval = null;
        this.charts = {};
        
        this.init();
    }

    init() {
        console.log('🚀 Inicializando Dashboard Chatbot...');
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Cargar datos iniciales
        this.cargarDatosIniciales();
        
        // Configurar actualizaciones automáticas
        this.setupAutoUpdate();
        
        console.log('✅ Dashboard inicializado correctamente');
    }

    setupEventListeners() {
        // Upload de fondos
        const inputFondos = document.getElementById('input-fondos');
        const zonaSubida = document.getElementById('zona-subida-fondos');
        
        if (inputFondos && zonaSubida) {
            inputFondos.addEventListener('change', (e) => this.handleFileUpload(e));
            
            // Drag and drop
            zonaSubida.addEventListener('dragover', (e) => {
                e.preventDefault();
                zonaSubida.classList.add('drag-over');
            });
            
            zonaSubida.addEventListener('dragleave', (e) => {
                e.preventDefault();
                zonaSubida.classList.remove('drag-over');
            });
            
            zonaSubida.addEventListener('drop', (e) => {
                e.preventDefault();
                zonaSubida.classList.remove('drag-over');
                this.handleFileUpload(e);
            });
        }

        // Formulario de configuración
        const formConfig = document.getElementById('form-configuracion');
        if (formConfig) {
            formConfig.addEventListener('submit', (e) => this.guardarConfiguracion(e));
        }

        // Formulario de tema
        const formTema = document.getElementById('form-tema');
        if (formTema) {
            formTema.addEventListener('submit', (e) => this.guardarTema(e));
        }

        // Filtros
        const filtroCalificacion = document.getElementById('filtro-calificacion');
        const filtroCategoria = document.getElementById('filtro-categoria');
        if (filtroCalificacion) {
            filtroCalificacion.addEventListener('change', () => this.aplicarFiltros());
        }
        if (filtroCategoria) {
            filtroCategoria.addEventListener('change', () => this.aplicarFiltros());
        }
    }

    async cargarDatosIniciales() {
        console.log('📊 Cargando datos iniciales...');
        
        try {
            // Cargar resumen del dashboard
            await this.cargarResumenDashboard();
            
            // Cargar datos de la sección actual
            await this.cargarDatosSeccion(this.currentSection);
            
        } catch (error) {
            console.error('❌ Error cargando datos iniciales:', error);
            this.mostrarError('Error cargando datos del dashboard');
        }
    }

    async cargarResumenDashboard() {
        try {
            const response = await fetch('/admin/chatbot/api/dashboard/resumen');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // Actualizar métricas
            document.getElementById('sesiones-activas').textContent = data.sesiones_activas || '0';
            document.getElementById('calificacion-promedio').textContent = data.calificacion_promedio || '0.0';
            document.getElementById('notificaciones-pendientes').textContent = data.notificaciones_pendientes || '0';
            document.getElementById('visitas-hoy').textContent = data.visitas_hoy || '0';
            
            // Actualizar gráfico de actividad
            this.actualizarGraficoActividad(data.actividad_24h || []);
            
        } catch (error) {
            console.error('❌ Error cargando resumen:', error);
        }
    }

    async cargarDatosSeccion(seccion) {
        console.log(`📋 Cargando datos de sección: ${seccion}`);
        
        switch (seccion) {
            case 'sesiones':
                await this.cargarSesiones();
                break;
            case 'calificaciones':
                await this.cargarCalificaciones();
                break;
            case 'notificaciones':
                await this.cargarNotificaciones();
                break;
            case 'temas':
                await this.cargarTemas();
                break;
            case 'fondos':
                await this.cargarFondos();
                break;
            case 'configuracion':
                await this.cargarConfiguracion();
                break;
        }
    }

    async cargarSesiones() {
        try {
            const response = await fetch('/api/chatbot/sesiones/activas');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const sesiones = await response.json();
            const tbody = document.getElementById('tabla-sesiones');
            
            if (sesiones.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #666;">No hay sesiones activas</td></tr>';
                return;
            }
            
            tbody.innerHTML = sesiones.map(sesion => `
                <tr>
                    <td><strong>Mesa ${sesion.mesa}</strong></td>
                    <td>${sesion.nombre_cliente || 'Sin nombre'}</td>
                    <td>${this.formatearFecha(sesion.fecha_inicio)}</td>
                    <td>${this.formatearFecha(sesion.fecha_ultimo_acceso)}</td>
                    <td><span class="device-badge">${sesion.dispositivo}</span></td>
                    <td><span class="status-badge ${sesion.activa ? 'active' : 'inactive'}">${sesion.activa ? 'Activa' : 'Inactiva'}</span></td>
                    <td>
                        <button onclick="verDetallesSesion(${sesion.id})" class="btn-small">Ver</button>
                        <button onclick="cerrarSesion(${sesion.id})" class="btn-small btn-danger">Cerrar</button>
                    </td>
                </tr>
            `).join('');
            
        } catch (error) {
            console.error('❌ Error cargando sesiones:', error);
            document.getElementById('tabla-sesiones').innerHTML = '<tr><td colspan="7" style="text-align: center; color: #e53e3e;">Error cargando sesiones</td></tr>';
        }
    }

    async cargarCalificaciones() {
        try {
            const response = await fetch('/api/chatbot/calificaciones');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const calificaciones = await response.json();
            const container = document.getElementById('lista-calificaciones');
            
            if (calificaciones.length === 0) {
                container.innerHTML = '<div class="loading-message">No hay calificaciones disponibles</div>';
                return;
            }
            
            container.innerHTML = calificaciones.map(cal => `
                <div class="review-item">
                    <div class="review-header">
                        <div>
                            <div class="review-stars">${'★'.repeat(cal.estrellas)}${'☆'.repeat(5-cal.estrellas)}</div>
                            <small>Mesa ${cal.sesion?.mesa} - ${cal.sesion?.nombre_cliente || 'Anónimo'}</small>
                        </div>
                        <div class="review-date">${this.formatearFecha(cal.fecha_calificacion)}</div>
                    </div>
                    <div class="review-text">${cal.comentarios?.[0]?.texto_comentario || 'Sin comentarios'}</div>
                    <div style="margin-top: 0.5rem;">
                        <span class="category-badge">${cal.categoria}</span>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('❌ Error cargando calificaciones:', error);
            document.getElementById('lista-calificaciones').innerHTML = '<div class="loading-message" style="color: #e53e3e;">Error cargando calificaciones</div>';
        }
    }

    async cargarNotificaciones() {
        try {
            const response = await fetch('/api/chatbot/notificaciones');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const notificaciones = await response.json();
            const container = document.getElementById('lista-notificaciones');
            
            if (notificaciones.length === 0) {
                container.innerHTML = '<div class="loading-message">No hay notificaciones pendientes</div>';
                return;
            }
            
            container.innerHTML = notificaciones.map(notif => `
                <div class="notification-item ${notif.prioridad}" ${!notif.atendida ? 'style="opacity: 0.6;"' : ''}>
                    <div class="notification-icon">
                        <i class="fas ${this.getNotificationIcon(notif.tipo_notificacion)}"></i>
                    </div>
                    <div class="notification-content">
                        <h4>${notif.tipo_notificacion.replace('_', ' ').toUpperCase()}</h4>
                        <p>${notif.mensaje}</p>
                        <div class="notification-meta">
                            <span>Mesa ${notif.sesion?.mesa}</span>
                            <span>${this.formatearFecha(notif.fecha_notificacion)}</span>
                            <span>Prioridad: ${notif.prioridad}</span>
                        </div>
                        ${!notif.atendida ? `
                            <button onclick="marcarAtendida(${notif.id})" class="btn-small btn-primary" style="margin-top: 0.5rem;">
                                Marcar como Atendida
                            </button>
                        ` : `
                            <small style="color: #22c55e;">✓ Atendida por ${notif.atendida_por}</small>
                        `}
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('❌ Error cargando notificaciones:', error);
            document.getElementById('lista-notificaciones').innerHTML = '<div class="loading-message" style="color: #e53e3e;">Error cargando notificaciones</div>';
        }
    }

    async cargarTemas() {
        try {
            const response = await fetch('/api/chatbot/temas');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const temas = await response.json();
            const container = document.getElementById('grid-temas');
            
            if (temas.length === 0) {
                container.innerHTML = '<div class="loading-message">No hay temas disponibles</div>';
                return;
            }
            
            container.innerHTML = temas.map(tema => `
                <div class="theme-card ${tema.activo ? 'active' : ''}">
                    <div class="theme-preview" style="background: ${this.generarPreviewTema(tema)}">
                        ${tema.activo ? '<div style="position: absolute; top: 10px; right: 10px; background: #22c55e; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem;">ACTIVO</div>' : ''}
                    </div>
                    <div class="theme-title">${tema.nombre}</div>
                    <div class="theme-description">${tema.descripcion}</div>
                    <div class="theme-actions">
                        ${!tema.activo ? `<button class="btn-activate" onclick="activarTema(${tema.id})">Activar</button>` : ''}
                        <button class="btn-edit" onclick="editarTema(${tema.id})">Editar</button>
                        ${!tema.predefinido ? `<button class="btn-delete" onclick="eliminarTema(${tema.id})">Eliminar</button>` : ''}
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('❌ Error cargando temas:', error);
            document.getElementById('grid-temas').innerHTML = '<div class="loading-message" style="color: #e53e3e;">Error cargando temas</div>';
        }
    }

    async cargarFondos() {
        try {
            const response = await fetch('/api/chatbot/fondos');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const fondos = await response.json();
            const container = document.getElementById('galeria-fondos');
            
            if (fondos.length === 0) {
                container.innerHTML = '<div class="loading-message">No hay fondos personalizados</div>';
                return;
            }
            
            container.innerHTML = fondos.map(fondo => `
                <div class="background-item">
                    <img src="${fondo.archivo_url}" alt="${fondo.nombre}" loading="lazy" style="max-width: 100%; height: 150px; object-fit: cover;">
                    <div class="background-overlay">
                        <button onclick="aplicarFondoChatbot(${fondo.id}, '${fondo.archivo_url}')" title="Aplicar al Chatbot" style="background: #28a745; color: white;">
                            <i class="fas fa-paint-brush"></i>
                        </button>
                        <button onclick="previsualizarFondo('${fondo.archivo_url}')" title="Previsualizar">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="eliminarFondo(${fondo.id})" title="Eliminar" style="color: #e53e3e;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div class="background-info">
                        <h4>${fondo.nombre}</h4>
                        <small>${fondo.archivo_original || 'Imagen personalizada'}</small>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('❌ Error cargando fondos:', error);
            document.getElementById('galeria-fondos').innerHTML = '<div class="loading-message" style="color: #e53e3e;">Error cargando fondos</div>';
        }
    }

    async cargarConfiguracion() {
        try {
            const response = await fetch('/api/chatbot/configuracion');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const config = await response.json();
            
            // Rellenar formulario con configuraciones
            Object.keys(config).forEach(key => {
                const element = document.getElementById(key.replace('_', '-'));
                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = config[key] === 'true';
                    } else {
                        element.value = config[key] || '';
                    }
                }
            });
            
        } catch (error) {
            console.error('❌ Error cargando configuración:', error);
            this.mostrarError('Error cargando configuración');
        }
    }

    // Funciones de navegación
    mostrarSeccion(seccion) {
        console.log(`🔄 Cambiando a sección: ${seccion}`);
        
        // Ocultar todas las secciones
        document.querySelectorAll('.dashboard-section').forEach(s => s.classList.remove('active'));
        
        // Mostrar sección seleccionada
        document.getElementById(`seccion-${seccion}`).classList.add('active');
        
        // Actualizar navegación
        document.querySelectorAll('.dashboard-nav a').forEach(a => a.classList.remove('nav-active'));
        document.querySelector(`[onclick="mostrarSeccion('${seccion}')"]`).classList.add('nav-active');
        
        // Guardar sección actual
        this.currentSection = seccion;
        
        // Cargar datos de la sección
        this.cargarDatosSeccion(seccion);
    }

    // Funciones de archivos
    async handleFileUpload(event) {
        const files = event.target?.files || event.dataTransfer?.files;
        if (!files || files.length === 0) return;
        
        console.log(`📤 Subiendo ${files.length} archivo(s)...`);
        
        for (let file of files) {
            if (!file.type.startsWith('image/')) {
                this.mostrarError(`${file.name} no es una imagen válida`);
                continue;
            }
            
            if (file.size > 20 * 1024 * 1024) {
                this.mostrarError(`${file.name} es demasiado grande (máximo 20MB)`);
                continue;
            }
            
            await this.subirFondo(file);
        }
        
        // Limpiar input
        if (event.target) event.target.value = '';
    }

    async subirFondo(file) {
        try {
            const formData = new FormData();
            formData.append('archivo', file);
            formData.append('nombre', file.name.split('.')[0]);
            
            const response = await fetch('/api/chatbot/fondos/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const resultado = await response.json();
            console.log('✅ Fondo subido:', resultado);
            
            this.mostrarExito(`Fondo "${file.name}" subido correctamente`);
            
            // Recargar galería
            if (this.currentSection === 'fondos') {
                await this.cargarFondos();
            }
            
        } catch (error) {
            console.error('❌ Error subiendo fondo:', error);
            this.mostrarError(`Error subiendo ${file.name}`);
        }
    }

    // Funciones de formularios
    async guardarConfiguracion(event) {
        event.preventDefault();
        
        console.log('💾 Guardando configuración...');
        
        try {
            const formData = new FormData(event.target);
            const configuracion = {};
            
            for (let [key, value] of formData.entries()) {
                configuracion[key.replace('-', '_')] = value;
            }
            
            // Añadir checkboxes
            const checkboxes = event.target.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => {
                configuracion[cb.id.replace('-', '_')] = cb.checked.toString();
            });
            
            const response = await fetch('/api/chatbot/configuracion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configuracion)
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            this.mostrarExito('Configuración guardada correctamente');
            
        } catch (error) {
            console.error('❌ Error guardando configuración:', error);
            this.mostrarError('Error guardando configuración');
        }
    }

    async guardarTema(event) {
        event.preventDefault();
        
        console.log('🎨 Guardando tema...');
        
        try {
            const formData = new FormData(event.target);
            const tema = {
                nombre: formData.get('tema-nombre'),
                descripcion: formData.get('tema-descripcion'),
                propiedades: {}
            };
            
            // Recopilar propiedades del tema
            const propiedades = document.querySelectorAll('#propiedades-tema input');
            propiedades.forEach(input => {
                tema.propiedades[input.name] = input.value;
            });
            
            const response = await fetch('/api/chatbot/temas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tema)
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            this.mostrarExito('Tema guardado correctamente');
            this.cerrarModal();
            
            // Recargar temas
            if (this.currentSection === 'temas') {
                await this.cargarTemas();
            }
            
        } catch (error) {
            console.error('❌ Error guardando tema:', error);
            this.mostrarError('Error guardando tema');
        }
    }

    // Funciones de utilidades
    actualizarGraficoActividad(datos) {
        const canvas = document.getElementById('grafico-actividad');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Limpiar canvas
        ctx.clearRect(0, 0, width, height);
        
        if (datos.length === 0) {
            ctx.fillStyle = '#666';
            ctx.font = '14px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('No hay datos disponibles', width/2, height/2);
            return;
        }
        
        // Configuración del gráfico
        const padding = 40;
        const chartWidth = width - 2 * padding;
        const chartHeight = height - 2 * padding;
        const maxValue = Math.max(...datos.map(d => d.value)) || 1;
        
        // Dibujar ejes
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 1;
        
        // Eje Y
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.stroke();
        
        // Eje X
        ctx.beginPath();
        ctx.moveTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();
        
        // Dibujar línea de datos
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        datos.forEach((punto, index) => {
            const x = padding + (index / (datos.length - 1)) * chartWidth;
            const y = height - padding - (punto.value / maxValue) * chartHeight;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Dibujar puntos
        ctx.fillStyle = '#667eea';
        datos.forEach((punto, index) => {
            const x = padding + (index / (datos.length - 1)) * chartWidth;
            const y = height - padding - (punto.value / maxValue) * chartHeight;
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
        });
    }

    generarPreviewTema(tema) {
        // Generar preview basado en las propiedades del tema
        const propiedades = tema.propiedades || {};
        const fondo = propiedades.background_color || '#f0f0f0';
        const acento = propiedades.accent_color || '#667eea';
        
        return `linear-gradient(135deg, ${fondo} 0%, ${acento} 100%)`;
    }

    getNotificationIcon(tipo) {
        const iconos = {
            'llamar_mesero': 'fa-bell',
            'queja': 'fa-exclamation-triangle',
            'consulta': 'fa-question-circle',
            'emergencia': 'fa-ambulance',
            'pedido_especial': 'fa-utensils'
        };
        return iconos[tipo] || 'fa-info-circle';
    }

    formatearFecha(fecha) {
        if (!fecha) return 'N/A';
        return new Date(fecha).toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    setupAutoUpdate() {
        // Actualizar cada 30 segundos
        this.updateInterval = setInterval(() => {
            if (this.currentSection === 'resumen') {
                this.cargarResumenDashboard();
            }
        }, 30000);
    }

    // Funciones de interfaz
    mostrarError(mensaje) {
        console.error('❌', mensaje);
        // Aquí podrías implementar un sistema de notificaciones toast
        alert(`Error: ${mensaje}`);
    }

    mostrarExito(mensaje) {
        console.log('✅', mensaje);
        // Aquí podrías implementar un sistema de notificaciones toast
        alert(`Éxito: ${mensaje}`);
    }

    cerrarModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
    }
}

// Funciones globales para el HTML
let dashboard;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new ChatbotDashboard();
});

// Funciones globales llamadas desde el HTML
function mostrarSeccion(seccion) {
    if (dashboard) dashboard.mostrarSeccion(seccion);
}

function actualizarDashboard() {
    if (dashboard) dashboard.cargarDatosIniciales();
}

function aplicarFiltros() {
    if (dashboard) dashboard.cargarDatosSeccion(dashboard.currentSection);
}

function seleccionarArchivo() {
    document.getElementById('input-fondos').click();
}

function crearTema() {
    // Mostrar modal de tema
    document.getElementById('modal-tema').classList.add('show');
    document.getElementById('modal-titulo').textContent = 'Crear Nuevo Tema';
}

function cerrarModal() {
    if (dashboard) dashboard.cerrarModal();
}

function resetearConfiguracion() {
    if (confirm('¿Estás seguro de que quieres resetear la configuración?')) {
        if (dashboard) dashboard.cargarConfiguracion();
    }
}

function resetearTemas() {
    if (confirm('¿Estás seguro de que quieres restaurar los temas por defecto?')) {
        // Implementar reseteo de temas
    }
}

function marcarTodasLeidas() {
    if (confirm('¿Marcar todas las notificaciones como leídas?')) {
        // Implementar marcar todas como leídas
    }
}

// Funciones específicas para elementos
function verDetallesSesion(id) {
    console.log('Ver detalles de sesión:', id);
}

function cerrarSesion(id) {
    if (confirm('¿Cerrar esta sesión?')) {
        console.log('Cerrar sesión:', id);
    }
}

function activarTema(id) {
    console.log('Activar tema:', id);
}

function editarTema(id) {
    console.log('Editar tema:', id);
}

function eliminarTema(id) {
    if (confirm('¿Eliminar este tema?')) {
        console.log('Eliminar tema:', id);
    }
}

function marcarAtendida(id) {
    console.log('Marcar notificación como atendida:', id);
}

function previsualizarFondo(url) {
    console.log('Previsualizar fondo:', url);
}

function activarFondo(id) {
    console.log('Activar fondo:', id);
}

function eliminarFondo(id) {
    if (confirm('¿Eliminar este fondo?')) {
        console.log('Eliminar fondo:', id);
    }
}

/* ======================================================
   🎨 FUNCIONES PERSONALIZACIÓN MANUAL DE TEMAS
   ====================================================== */

/**
 * Cambiar entre pestañas de personalización manual
 */
function cambiarTabPersonalizacion(tab) {
    console.log(`🎨 Cambiando a pestaña: ${tab}`);
    
    // Remover clase activa de todas las pestañas
    document.querySelectorAll('.config-tab').forEach(tabElement => {
        tabElement.classList.remove('active');
    });
    
    // Ocultar todos los paneles
    document.querySelectorAll('.config-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Activar pestaña seleccionada
    const tabButton = document.querySelector(`[data-tab="${tab}"]`);
    if (tabButton) {
        tabButton.classList.add('active');
    }
    
    // Mostrar panel correspondiente
    const panel = document.getElementById(`panel-${tab}`);
    if (panel) {
        panel.classList.add('active');
    } else {
        console.warn(`⚠️ Panel no encontrado: panel-${tab}`);
    }
}

/**
 * Aplicar color seleccionado
 */
function aplicarColor(tipo) {
    const input = document.querySelector(`#color-${tipo}`);
    if (!input) {
        console.error(`❌ Input de color no encontrado: #color-${tipo}`);
        return;
    }
    
    const color = input.value;
    const textInput = input.parentElement.querySelector('input[type="text"]');
    
    console.log(`🎨 Aplicando color ${tipo}: ${color}`);
    
    // Sincronizar inputs
    if (textInput) {
        textInput.value = color.toUpperCase();
    }
    
    // Aplicar color inmediatamente para preview
    document.documentElement.style.setProperty(`--color-${tipo}`, color);
    
    // Mostrar notificación
    mostrarNotificacion(`Color ${tipo} aplicado: ${color}`, 'success');
}

/**
 * Aplicar tipografía seleccionada
 */
function aplicarTipografia(tipo, select) {
    const fuente = select.value;
    console.log(`📝 Aplicando tipografía ${tipo}: ${fuente}`);
    
    // Aplicar fuente al preview
    const preview = document.getElementById('typography-preview');
    if (preview) {
        if (tipo === 'principal') {
            preview.querySelector('.preview-primary').style.fontFamily = fuente;
        } else if (tipo === 'secundaria') {
            preview.querySelector('.preview-secondary').style.fontFamily = fuente;
        } else if (tipo === 'acento') {
            preview.querySelector('.preview-accent').style.fontFamily = fuente;
        }
    }
    
    mostrarNotificacion(`Tipografía ${tipo} aplicada: ${fuente}`, 'success');
}

/**
 * Vista previa de cambios
 */
function previsualizarCambios() {
    console.log('👁️ Previsualizando cambios...');
    
    // Recopilar todos los valores actuales
    const configuracion = {
        colores: {
            primario: document.querySelector('#color-primary')?.value,
            secundario: document.querySelector('#color-secondary')?.value,
            acento: document.querySelector('#color-accent')?.value,
            textoClaro: document.querySelector('#color-light-text')?.value,
            textoOscuro: document.querySelector('#color-dark-text')?.value
        },
        tipografias: {
            principal: document.querySelector('#font-primary')?.value,
            secundaria: document.querySelector('#font-secondary')?.value,
            acento: document.querySelector('#font-accent')?.value
        }
    };
    
    console.log('📋 Configuración actual:', configuracion);
    
    // Aplicar todos los cambios
    Object.entries(configuracion.colores).forEach(([key, value]) => {
        if (value) {
            document.documentElement.style.setProperty(`--color-${key}`, value);
        }
    });
    
    mostrarNotificacion('Vista previa aplicada', 'success');
}

/**
 * Guardar tema personalizado
 */
function guardarTemaPersonalizado(tipo) {
    console.log(`💾 Guardando tema personalizado: ${tipo}`);
    
    // Recopilar configuración según el tipo
    let configuracion = {};
    
    if (tipo === 'colores') {
        configuracion = {
            tipo: 'colores',
            colores: {
                primario: document.querySelector('#color-primary')?.value || '#d4af37',
                secundario: document.querySelector('#color-secondary')?.value || '#2c1810',
                acento: document.querySelector('#color-accent')?.value || '#f4e4c1',
                textoClaro: document.querySelector('#color-light-text')?.value || '#ffffff',
                textoOscuro: document.querySelector('#color-dark-text')?.value || '#2c1810'
            }
        };
    } else if (tipo === 'tipografia') {
        configuracion = {
            tipo: 'tipografia',
            tipografias: {
                principal: document.querySelector('#font-primary')?.value || 'Dancing Script',
                secundaria: document.querySelector('#font-secondary')?.value || 'Patrick Hand',
                acento: document.querySelector('#font-accent')?.value || 'Merriweather'
            }
        };
    }
    
    // Simular guardado (aquí puedes agregar llamada API)
    console.log('📝 Configuración a guardar:', configuracion);
    
    // Mostrar estado de carga
    const boton = event.target;
    const textoOriginal = boton.textContent;
    boton.classList.add('btn-loading');
    boton.textContent = '';
    
    setTimeout(() => {
        boton.classList.remove('btn-loading');
        boton.classList.add('success');
        boton.textContent = '✅ Guardado';
        
        setTimeout(() => {
            boton.classList.remove('success');
            boton.textContent = textoOriginal;
        }, 2000);
        
        mostrarNotificacion(`Tema ${tipo} guardado correctamente`, 'success');
    }, 1500);
}

/**
 * Resetear tema a valores por defecto
 */
function resetearTema() {
    if (!confirm('¿Deseas resetear todos los valores a los predeterminados?')) {
        return;
    }
    
    console.log('🔄 Reseteando tema...');
    
    // Valores por defecto de Eterials
    const valoresPorDefecto = {
        colores: {
            primario: '#d4af37',
            secundario: '#2c1810',
            acento: '#f4e4c1',
            textoClaro: '#ffffff',
            textoOscuro: '#2c1810'
        },
        tipografias: {
            principal: 'Dancing Script',
            secundaria: 'Patrick Hand',
            acento: 'Merriweather'
        }
    };
    
    // Aplicar valores por defecto a los inputs
    Object.entries(valoresPorDefecto.colores).forEach(([key, value]) => {
        const input = document.querySelector(`#color-${key === 'primario' ? 'primary' : key === 'secundario' ? 'secondary' : key === 'acento' ? 'accent' : key === 'textoClaro' ? 'light-text' : 'dark-text'}`);
        if (input) {
            input.value = value;
            // Sincronizar input de texto
            const textInput = input.parentElement.querySelector('input[type="text"]');
            if (textInput) {
                textInput.value = value.toUpperCase();
            }
        }
        // Aplicar al CSS
        document.documentElement.style.setProperty(`--color-${key}`, value);
    });
    
    Object.entries(valoresPorDefecto.tipografias).forEach(([key, value]) => {
        const select = document.querySelector(`#font-${key === 'principal' ? 'primary' : key === 'secundaria' ? 'secondary' : 'accent'}`);
        if (select) {
            select.value = value;
        }
    });
    
    mostrarNotificacion('Tema reseteado a valores predeterminados', 'success');
}

/**
 * Mostrar notificación toast
 */
function mostrarNotificacion(mensaje, tipo = 'success') {
    // Remover notificaciones existentes
    const existentes = document.querySelectorAll('.toast-notification');
    existentes.forEach(toast => toast.remove());
    
    // Crear nueva notificación
    const toast = document.createElement('div');
    toast.className = `toast-notification ${tipo}`;
    toast.textContent = mensaje;
    
    // Agregar al DOM
    document.body.appendChild(toast);
    
    // Mostrar con animación
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 3000);
}

/**
 * Sincronizar input color con input texto
 */
function sincronizarColor(input) {
    const colorInput = input.parentElement.querySelector('input[type="color"]');
    if (colorInput && input.value.match(/^#[0-9A-F]{6}$/i)) {
        colorInput.value = input.value;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Inicializando funciones de personalización...');
    
    // Configurar eventos para inputs de color
    document.querySelectorAll('input[type="color"]').forEach(input => {
        input.addEventListener('change', function() {
            const textInput = this.parentElement.querySelector('input[type="text"]');
            if (textInput) {
                textInput.value = this.value.toUpperCase();
            }
        });
    });
    
    // Configurar eventos para inputs de texto
    document.querySelectorAll('.color-input-group input[type="text"]').forEach(input => {
        input.addEventListener('input', function() {
            sincronizarColor(this);
        });
    });
    
    console.log('✅ Funciones de personalización inicializadas');
});

/**
 * Aplicar fondo al chatbot y generar paleta de colores automática
 */
async function aplicarFondoChatbot(fondoId, imagenUrl) {
    try {
        console.log(`🎨 Aplicando fondo ${fondoId} al chatbot...`);
        
        // 1. Extraer colores dominantes de la imagen
        const colores = await extraerColoresDominantes(imagenUrl);
        
        // 2. Aplicar fondo al chatbot
        const response = await fetch(`/api/chatbot/fondos/${fondoId}/aplicar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                colores_automaticos: colores
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const resultado = await response.json();
        console.log('✅ Fondo aplicado:', resultado);
        
        mostrarNotificacion(`Fondo aplicado al chatbot con paleta automática`, 'success');
        
        // 3. Actualizar vista previa si está visible
        actualizarVistaPreviaChatbot();
        
        // 4. Notificar al chatbot para que actualice el tema
        notificarCambioDeTema();
        
    } catch (error) {
        console.error('❌ Error aplicando fondo:', error);
        mostrarNotificacion(`Error aplicando fondo: ${error.message}`, 'error');
    }
}

/**
 * Extraer colores dominantes de una imagen base64
 */
function extraerColoresDominantes(imagenUrl) {
    return new Promise((resolve) => {
        // Crear canvas temporal para analizar la imagen
        const img = new Image();
        img.crossOrigin = 'anonymous';
        
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Redimensionar para análisis más rápido
            const size = 50;
            canvas.width = size;
            canvas.height = size;
            
            // Dibujar imagen redimensionada
            ctx.drawImage(img, 0, 0, size, size);
            
            // Obtener datos de píxeles
            const imageData = ctx.getImageData(0, 0, size, size);
            const data = imageData.data;
            
            // Analizar colores (simplificado)
            let r = 0, g = 0, b = 0;
            let pixelCount = 0;
            
            for (let i = 0; i < data.length; i += 4) {
                r += data[i];
                g += data[i + 1];
                b += data[i + 2];
                pixelCount++;
            }
            
            // Calcular color promedio
            r = Math.round(r / pixelCount);
            g = Math.round(g / pixelCount);
            b = Math.round(b / pixelCount);
            
            // Generar paleta basada en el color promedio
            const paleta = generarPaletaColores(r, g, b);
            resolve(paleta);
        };
        
        img.onerror = function() {
            // Si hay error, usar paleta por defecto
            resolve({
                primario: '#1a365d',
                secundario: '#2d3748', 
                acento: '#3182ce',
                texto_claro: '#ffffff',
                texto_oscuro: '#1a202c'
            });
        };
        
        img.src = imagenUrl;
    });
}

/**
 * Generar paleta de colores basada en RGB
 */
function generarPaletaColores(r, g, b) {
    // Convertir a HSL para manipular mejor
    const hsl = rgbToHsl(r, g, b);
    
    return {
        primario: `hsl(${hsl[0]}, ${Math.max(hsl[1], 50)}%, ${Math.max(hsl[2] - 20, 20)}%)`,
        secundario: `hsl(${(hsl[0] + 30) % 360}, ${Math.max(hsl[1], 40)}%, ${Math.max(hsl[2] - 10, 30)}%)`,
        acento: `hsl(${(hsl[0] + 60) % 360}, ${Math.max(hsl[1], 60)}%, ${Math.min(hsl[2] + 10, 70)}%)`,
        texto_claro: '#ffffff',
        texto_oscuro: hsl[2] > 50 ? '#1a202c' : '#f7fafc'
    };
}

/**
 * Convertir RGB a HSL
 */
function rgbToHsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0;
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }

    return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
}

/**
 * Actualizar vista previa del chatbot
 */
function actualizarVistaPreviaChatbot() {
    // Esta función se puede expandir para mostrar una vista previa
    console.log('🔄 Actualizando vista previa del chatbot...');
}

/**
 * Notificar al chatbot que debe actualizar su tema
 */
function notificarCambioDeTema() {
    console.log('📢 Notificando cambio de tema al chatbot...');
    
    // Enviar mensaje a todas las ventanas del chatbot abiertas
    const mensaje = {
        tipo: 'ACTUALIZAR_TEMA',
        timestamp: Date.now()
    };
    
    // Usar localStorage para comunicación entre pestañas
    localStorage.setItem('chatbot_tema_actualizado', JSON.stringify(mensaje));
    
    // Limpiar después de un momento
    setTimeout(() => {
        localStorage.removeItem('chatbot_tema_actualizado');
    }, 1000);
}

/**
 * Previsualizar fondo
 */
function previsualizarFondo(imagenUrl) {
    // Crear modal de previsualización
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); display: flex; align-items: center;
        justify-content: center; z-index: 10000; cursor: pointer;
    `;
    
    const img = document.createElement('img');
    img.src = imagenUrl;
    img.style.cssText = 'max-width: 90%; max-height: 90%; object-fit: contain;';
    
    modal.appendChild(img);
    modal.onclick = () => modal.remove();
    document.body.appendChild(modal);
}

/**
 * Eliminar fondo
 */
async function eliminarFondo(fondoId) {
    if (!confirm('¿Estás seguro de eliminar este fondo?')) return;
    
    try {
        const response = await fetch(`/api/chatbot/fondos/${fondoId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        mostrarNotificacion('Fondo eliminado correctamente', 'success');
        
        // Recargar galería
        if (window.dashboardManager && window.dashboardManager.currentSection === 'fondos') {
            await window.dashboardManager.cargarFondos();
        }
        
    } catch (error) {
        console.error('❌ Error eliminando fondo:', error);
        mostrarNotificacion(`Error eliminando fondo: ${error.message}`, 'error');
    }
}