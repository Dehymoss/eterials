/**
 * MENU TRANSICIÓN - JAVASCRIPT MODULAR
 * Archivo: menu-transicion.js
 * Módulo: Frontend Menu
 * 
 * Maneja la lógica de transición entre menú propio y menú externo
 */

// Clase principal para manejo de transición de menú
class MenuTransicion {
    constructor() {
        this.loadConfigFromHTML();
        this.init();
    }

    loadConfigFromHTML() {
        const configElement = document.getElementById('menu-config');
        
        if (configElement) {
            this.config = {
                menu_activo: configElement.dataset.menuActivo || 'propio',
                menu_externo_url: configElement.dataset.menuExternoUrl || '',
                redirect_automatico: configElement.dataset.redirectAutomatico === 'true',
                mensaje_mantenimiento: configElement.dataset.mensajeMantenimiento || ''
            };
            
            this.clienteInfo = {
                nombre: configElement.dataset.clienteNombre || '',
                mesa: configElement.dataset.clienteMesa || ''
            };
        } else {
            // Fallback si no encuentra el elemento
            this.config = window.CONFIG_MENU || {};
            this.clienteInfo = window.CLIENTE_INFO || {};
        }
    }

    init() {
        console.log('🔄 MenuTransicion iniciado:', {
            menu_activo: this.config.menu_activo,
            redirect_automatico: this.config.redirect_automatico,
            cliente: this.clienteInfo.nombre,
            mesa: this.clienteInfo.mesa
        });

        // Configurar auto-redirección si está habilitada
        if (this.config.redirect_automatico && this.config.menu_externo_url) {
            this.startAutoRedirect();
        }

        // Configurar eventos
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Evento para el botón de menú externo
        const btnMenuExterno = document.getElementById('btnMenuExterno');
        if (btnMenuExterno) {
            btnMenuExterno.addEventListener('click', (e) => {
                e.preventDefault();
                this.redirectToExternal();
            });
        }
    }

    redirectToExternal() {
        if (!this.config.menu_externo_url) {
            console.error('❌ URL del menú externo no configurada');
            return;
        }

        // Construir URL con parámetros de cliente
        let url = this.config.menu_externo_url;
        const params = new URLSearchParams();
        
        if (this.clienteInfo.nombre) {
            params.append('nombre', this.clienteInfo.nombre);
        }
        if (this.clienteInfo.mesa) {
            params.append('mesa', this.clienteInfo.mesa);
        }
        
        if (params.toString()) {
            url += (url.includes('?') ? '&' : '?') + params.toString();
        }
        
        console.log('🔗 Redirigiendo a menú externo:', url);
        window.location.href = url;
    }

    goToInternalMenu() {
        // Esta función es llamada por el onclick del div
        // La lógica real está en forceInternalMenu()
        console.log('🏠 Solicitado acceso a menú interno');
    }

    forceInternalMenu() {
        // Construir URL del menú interno con parámetros
        let url = '/menu/general?force_internal=true';
        
        if (this.clienteInfo.nombre) {
            url += '&nombre=' + encodeURIComponent(this.clienteInfo.nombre);
        }
        if (this.clienteInfo.mesa) {
            url += '&mesa=' + encodeURIComponent(this.clienteInfo.mesa);
        }
        
        console.log('🏠 Forzando menú interno:', url);
        window.location.href = url;
    }

    startAutoRedirect() {
        if (!this.config.menu_externo_url) {
            console.error('❌ No se puede auto-redirigir: URL no configurada');
            return;
        }

        let countdown = 5;
        const countdownElement = this.createCountdownElement(countdown);
        
        // Agregar el countdown al mensaje de transición
        const transitionMessage = document.querySelector('.transition-message');
        if (transitionMessage) {
            transitionMessage.appendChild(countdownElement);
        }
        
        const timer = setInterval(() => {
            countdown--;
            const countdownSpan = document.getElementById('countdown');
            if (countdownSpan) {
                countdownSpan.textContent = countdown;
            }
            
            if (countdown <= 0) {
                clearInterval(timer);
                this.redirectToExternal();
            }
        }, 1000);

        console.log('⏰ Auto-redirección iniciada: 5 segundos');
    }

    createCountdownElement(initialCount) {
        const countdownElement = document.createElement('div');
        countdownElement.className = 'countdown';
        countdownElement.innerHTML = `
            <i class="fas fa-clock me-2"></i>
            Redirigiendo automáticamente en 
            <span id="countdown">${initialCount}</span> 
            segundos...
        `;
        return countdownElement;
    }

    // Método estático para acceso global
    static redirectToExternal() {
        if (window.menuTransicionInstance) {
            window.menuTransicionInstance.redirectToExternal();
        }
    }

    static goToInternalMenu() {
        if (window.menuTransicionInstance) {
            window.menuTransicionInstance.goToInternalMenu();
        }
    }

    static forceInternalMenu() {
        if (window.menuTransicionInstance) {
            window.menuTransicionInstance.forceInternalMenu();
        }
    }
}

// Protección anti-redeclaración
if (!window.MenuTransicion) {
    window.MenuTransicion = MenuTransicion;
    
    // Inicializar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        window.menuTransicionInstance = new MenuTransicion();
        
        // Exposer métodos globalmente para onclick en HTML
        window.MenuTransicion.redirectToExternal = MenuTransicion.redirectToExternal;
        window.MenuTransicion.goToInternalMenu = MenuTransicion.goToInternalMenu;
        window.MenuTransicion.forceInternalMenu = MenuTransicion.forceInternalMenu;
    });
}

// Debug/Analytics logging
window.addEventListener('load', function() {
    if (window.menuTransicionInstance) {
        const instance = window.menuTransicionInstance;
        console.log('📊 Menu Transition Analytics:', {
            timestamp: new Date().toISOString(),
            menu_activo: instance.config.menu_activo,
            redirect_automatico: instance.config.redirect_automatico,
            url_externa: instance.config.menu_externo_url ? 'configurada' : 'no configurada',
            cliente: instance.clienteInfo.nombre || 'anónimo',
            mesa: instance.clienteInfo.mesa || 'n/a'
        });
    }
});
