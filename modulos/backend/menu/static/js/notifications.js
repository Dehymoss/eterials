/* =====================================================
   NOTIFICATIONS JS - SISTEMA INDEPENDIENTE NOTIFICACIONES
   ===================================================== */

// Prevenir declaraciones múltiples
if (!window.SistemaNotificaciones) {
    
class SistemaNotificaciones {
    constructor() {
        this.contenedor = null;
        this.notificaciones = [];
        this.autoIncrementoId = 1;
        this.maxNotificaciones = 5;
        this.duracionDefault = 5000; // 5 segundos
        this.init();
    }

    // Inicializar el sistema
    init() {
        this.crearContenedor();
        this.configurarEventos();
    }

    // Crear contenedor de notificaciones
    crearContenedor() {
        if (document.querySelector('.notificaciones-container')) return;
        
        this.contenedor = document.createElement('div');
        this.contenedor.className = 'notificaciones-container';
        document.body.appendChild(this.contenedor);
    }

    // Configurar eventos globales
    configurarEventos() {
        // Cerrar notificaciones con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.cerrarTodas();
            }
        });

        // Pausar auto-cierre al hacer hover
        this.contenedor.addEventListener('mouseenter', () => {
            this.pausarTodas();
        });

        this.contenedor.addEventListener('mouseleave', () => {
            this.reanudarTodas();
        });
    }

    // Mostrar notificación
    mostrar(mensaje, tipo = 'info', opciones = {}) {
        const config = {
            titulo: opciones.titulo || this.getTituloDefault(tipo),
            duracion: opciones.duracion || this.duracionDefault,
            persistente: opciones.persistente || false,
            acciones: opciones.acciones || [],
            icono: opciones.icono || this.getIconoDefault(tipo),
            animacion: opciones.animacion || '',
            imagen: opciones.imagen || null,
            id: opciones.id || this.autoIncrementoId++
        };

        const notificacion = this.crearNotificacion(mensaje, tipo, config);
        this.agregarNotificacion(notificacion, config);
        
        return notificacion;
    }

    // Métodos de conveniencia
    exito(mensaje, opciones = {}) {
        return this.mostrar(mensaje, 'exito', opciones);
    }

    error(mensaje, opciones = {}) {
        return this.mostrar(mensaje, 'error', { 
            duracion: 8000, // Los errores duran más
            ...opciones 
        });
    }

    warning(mensaje, opciones = {}) {
        return this.mostrar(mensaje, 'warning', opciones);
    }

    info(mensaje, opciones = {}) {
        return this.mostrar(mensaje, 'info', opciones);
    }

    // Crear elemento de notificación
    crearNotificacion(mensaje, tipo, config) {
        const notif = document.createElement('div');
        notif.className = `notificacion ${tipo}`;
        notif.dataset.id = config.id;

        // Aplicar animación especial si se especifica
        if (config.animacion) {
            notif.classList.add(config.animacion);
        }

        const html = `
            <div class="notificacion-header">
                <div class="notificacion-icono">
                    <i class="${config.icono}"></i>
                </div>
                <h6 class="notificacion-titulo">${config.titulo}</h6>
                <button class="notificacion-cerrar" onclick="notificaciones.cerrar(${config.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notificacion-cuerpo">
                <p class="notificacion-mensaje">${mensaje}</p>
                ${config.imagen ? `<img src="${config.imagen}" class="notificacion-imagen" alt="Imagen">` : ''}
                ${this.crearAcciones(config.acciones, config.id)}
            </div>
            ${!config.persistente ? `<div class="notificacion-progress">
                <div class="notificacion-progress-bar" style="animation-duration: ${config.duracion}ms;"></div>
            </div>` : ''}
        `;

        notif.innerHTML = html;
        return notif;
    }

    // Crear botones de acción
    crearAcciones(acciones, id) {
        if (!acciones || acciones.length === 0) return '';

        const botonesHtml = acciones.map(accion => `
            <button class="btn-notificacion ${accion.tipo || ''}" 
                    onclick="notificaciones.ejecutarAccion(${id}, '${accion.callback}', '${accion.parametros || ''}')">
                ${accion.icono ? `<i class="${accion.icono}"></i> ` : ''}${accion.texto}
            </button>
        `).join('');

        return `<div class="notificacion-acciones">${botonesHtml}</div>`;
    }

    // Agregar notificación al contenedor
    agregarNotificacion(notificacion, config) {
        // Limitar número de notificaciones
        if (this.notificaciones.length >= this.maxNotificaciones) {
            this.cerrar(this.notificaciones[0].dataset.id);
        }

        this.contenedor.appendChild(notificacion);
        this.notificaciones.push(notificacion);

        // Mostrar con animación
        setTimeout(() => {
            notificacion.classList.add('mostrar');
        }, 50);

        // Auto-cerrar si no es persistente
        if (!config.persistente) {
            setTimeout(() => {
                this.cerrar(config.id);
            }, config.duracion);
        }

        // Reproducir sonido si está habilitado
        this.reproducirSonido(config.tipo || 'info');
    }

    // Cerrar notificación específica
    cerrar(id) {
        const notificacion = document.querySelector(`.notificacion[data-id="${id}"]`);
        if (!notificacion) return;

        notificacion.classList.add('ocultar');
        
        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.parentNode.removeChild(notificacion);
            }
            this.notificaciones = this.notificaciones.filter(n => n.dataset.id !== id.toString());
        }, 400);
    }

    // Cerrar todas las notificaciones
    cerrarTodas() {
        this.notificaciones.forEach(notif => {
            this.cerrar(notif.dataset.id);
        });
    }

    // Pausar auto-cierre de todas las notificaciones
    pausarTodas() {
        this.notificaciones.forEach(notif => {
            const progressBar = notif.querySelector('.notificacion-progress-bar');
            if (progressBar) {
                progressBar.style.animationPlayState = 'paused';
            }
        });
    }

    // Reanudar auto-cierre de todas las notificaciones
    reanudarTodas() {
        this.notificaciones.forEach(notif => {
            const progressBar = notif.querySelector('.notificacion-progress-bar');
            if (progressBar) {
                progressBar.style.animationPlayState = 'running';
            }
        });
    }

    // Ejecutar acción de botón
    ejecutarAccion(id, callback, parametros) {
        try {
            // Cerrar la notificación
            this.cerrar(id);
            
            // Ejecutar callback si existe
            if (callback && typeof window[callback] === 'function') {
                if (parametros) {
                    window[callback](JSON.parse(parametros));
                } else {
                    window[callback]();
                }
            }
        } catch (error) {
            console.error('Error ejecutando acción de notificación:', error);
        }
    }

    // Obtener título por defecto según el tipo
    getTituloDefault(tipo) {
        const titulos = {
            'exito': '¡Éxito!',
            'error': 'Error',
            'warning': 'Advertencia',
            'info': 'Información'
        };
        return titulos[tipo] || 'Notificación';
    }

    // Obtener icono por defecto según el tipo
    getIconoDefault(tipo) {
        const iconos = {
            'exito': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle', 
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return iconos[tipo] || 'fas fa-bell';
    }

    // Reproducir sonido de notificación
    reproducirSonido(tipo) {
        // Solo si el usuario ha interactuado con la página
        if (!document.body.dataset.userInteracted) return;

        try {
            const audio = new Audio();
            const sonidos = {
                'exito': 'data:audio/wav;base64,UklGRvIBAABXQVZFZm10IBAAAAABA...',
                'error': 'data:audio/wav;base64,UklGRvIBAABXQVZFZm10IBAAAAABA...',
                'warning': 'data:audio/wav;base64,UklGRvIBAABXQVZFZm10IBAAAAABA...',
                'info': 'data:audio/wav;base64,UklGRvIBAABXQVZFZm10IBAAAAABA...'
            };
            
            if (sonidos[tipo]) {
                audio.src = sonidos[tipo];
                audio.volume = 0.3;
                audio.play().catch(() => {}); // Ignorar errores de autoplay
            }
        } catch (error) {
            // Ignorar errores de audio
        }
    }

    // Configurar máximo de notificaciones
    setMaxNotificaciones(max) {
        this.maxNotificaciones = Math.max(1, max);
    }

    // Configurar duración por defecto
    setDuracionDefault(duracion) {
        this.duracionDefault = Math.max(1000, duracion);
    }

    // Obtener estadísticas
    getEstadisticas() {
        return {
            total: this.notificaciones.length,
            tipos: this.notificaciones.reduce((acc, notif) => {
                const tipo = [...notif.classList].find(c => 
                    ['exito', 'error', 'warning', 'info'].includes(c)
                ) || 'info';
                acc[tipo] = (acc[tipo] || 0) + 1;
                return acc;
            }, {}),
            persistentes: this.notificaciones.filter(n => 
                !n.querySelector('.notificacion-progress')
            ).length
        };
    }
}

// Crear instancia global
const notificaciones = new SistemaNotificaciones();

// Marcar interacción del usuario para permitir sonidos
document.addEventListener('click', () => {
    document.body.dataset.userInteracted = 'true';
}, { once: true });

// Funciones de conveniencia globales
window.mostrarNotificacion = (mensaje, tipo, opciones) => {
    return notificaciones.mostrar(mensaje, tipo, opciones);
};

window.notificacionExito = (mensaje, opciones) => {
    return notificaciones.exito(mensaje, opciones);
};

window.notificacionError = (mensaje, opciones) => {
    return notificaciones.error(mensaje, opciones);
};

window.notificacionWarning = (mensaje, opciones) => {
    return notificaciones.warning(mensaje, opciones);
};

window.notificacionInfo = (mensaje, opciones) => {
    return notificaciones.info(mensaje, opciones);
};

// Exponer la instancia globalmente
window.notificaciones = notificaciones;

// Marcar como cargado
window.SistemaNotificaciones = SistemaNotificaciones;

console.log('✅ Sistema de Notificaciones cargado correctamente');

} // Fin de la protección contra declaraciones múltiples
