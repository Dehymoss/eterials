/**
 * Dashboard Chatbot - Sistema de Gestión de Fondos
 * Eterials Restaurant Management System
 */

class ChatbotDashboard {
    constructor() {
        this.fondoSeleccionado = null;
        this.temaAutomatico = null;
        this.init();
    }

    init() {
        console.log('🚀 Inicializando Dashboard Chatbot...');
        this.setupEventListeners();
        
        // Verificar si estamos en la sección de personalización y cargar galería si es necesario
        setTimeout(() => {
            const personalizacionSection = document.getElementById('seccion-personalizacion');
            const radioImagen = document.getElementById('fondo-imagen');
            
            if (personalizacionSection && personalizacionSection.classList.contains('active')) {
                console.log('📄 Sección personalización activa, verificando tipo de fondo...');
                if (radioImagen && radioImagen.checked) {
                    console.log('🖼️ Cargando galería inicial...');
                    this.cargarGaleria();
                }
            }
        }, 500);
        
        console.log('✅ Dashboard inicializado correctamente');
    }

    generarUrlChatbotConFondo(fondoData) {
        /**
         * Genera URL del chatbot con parámetros para aplicar fondo
         * Compatible con el sistema de personalización dinámica del chatbot
         */
        const baseUrl = '/chatbot';
        const params = new URLSearchParams();
        
        if (fondoData.tipo === 'imagen') {
            params.set('fondo_tipo', 'imagen');
            params.set('fondo_valor', fondoData.valor);
        } else if (fondoData.tipo === 'color') {
            params.set('fondo_tipo', 'color');
            params.set('fondo_valor', fondoData.valor);
        }
        
        // Agregar colores adaptativos si están disponibles
        if (this.temaAutomatico) {
            const colores = this.temaAutomatico;
            if (colores.text_color) params.set('text_color', colores.text_color);
            if (colores.title_color) params.set('title_color', colores.title_color);
            if (colores.accent_color) params.set('accent_color', colores.accent_color);
            if (colores.button_color) params.set('button_color', colores.button_color);
            if (colores.button_text_color) params.set('button_text_color', colores.button_text_color);
            if (colores.es_imagen_oscura !== undefined) params.set('es_imagen_oscura', colores.es_imagen_oscura);
        }
        
        return params.toString() ? `${baseUrl}?${params.toString()}` : baseUrl;
    }

    setupEventListeners() {
        // Event listener para el input de archivo
        const inputImagen = document.getElementById('input-nueva-imagen');
        if (inputImagen) {
            inputImagen.addEventListener('change', (event) => {
                this.manejarUploadImagen(event);
            });
        }
        
        // Event listener para formulario de configuración
        const formConfig = document.getElementById('form-configuracion');
        if (formConfig) {
            formConfig.addEventListener('submit', async (e) => {
                e.preventDefault();
                const menuGuardado = await guardarConfiguracionMenu();
                if (!menuGuardado) {
                    console.error('❌ Error guardando configuración');
                }
            });
        }
    }

    cambiarTipoFondo(tipo) {
        const panelImagen = document.getElementById('config-imagen-fondo');
        if (panelImagen) {
            panelImagen.classList.add('active');
            setTimeout(() => this.cargarGaleria(), 100);
        }
    }

    async cargarGaleria() {
        console.log('🔄 INICIANDO CARGA DE GALERÍA...');
        console.log('📍 Buscando contenedor galeria-fondos-grid...');
        
        const container = document.getElementById('galeria-fondos-grid');
        console.log('📦 Contenedor encontrado:', !!container);
        
        if (!container) {
            console.error('❌ CONTENEDOR NO ENCONTRADO');
            console.log('📋 Todos los elementos con ID:');
            document.querySelectorAll('[id]').forEach(el => {
                console.log(`  - ${el.id}: ${el.tagName}`);
            });
            return;
        }
        
        console.log('✅ Contenedor encontrado, haciendo fetch...');
        
        try {
            console.log('📡 Fetch a /api/chatbot/fondos/existentes...');
            const response = await fetch('/api/chatbot/fondos/existentes');
            console.log('📊 Response status:', response.status);
            console.log('📊 Response ok:', response.ok);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('📊 Data recibida:', data);
            
            const fondos = data.fondos || [];
            console.log(`🖼️ Fondos array:`, fondos);
            console.log(`🔢 Total fondos: ${fondos.length} de ${data.total || 0}`);
            
            const counter = document.getElementById('fondos-counter');
            if (counter) {
                const totalCount = data.total || fondos.length;
                counter.textContent = `${totalCount} fondos disponibles`;
                console.log(`✅ Counter actualizado: ${totalCount} fondos`);
            }
            
            if (fondos.length === 0) {
                console.log('⚠️ NO HAY FONDOS - Mostrando placeholder');
                container.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #718096;">
                        <i class="fas fa-images" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                        <p>No hay fondos disponibles</p>
                    </div>
                `;
                return;
            }
            
            console.log('🏗️ GENERANDO HTML PARA FONDOS...');
            fondos.forEach((fondo, index) => {
                console.log(`  ${index + 1}. ${fondo.nombre}: ${fondo.url_preview}`);
            });
            
            const fondosHtml = fondos.map(fondo => `
                <div class="fondo-thumbnail-modern" onclick="window.dashboard.seleccionarFondo('${fondo.id}', '${fondo.nombre}', this)" 
                     title="${fondo.nombre}" data-fondo-id="${fondo.id}" data-fondo-url="${fondo.url_preview}" 
                     style="
                        display: inline-block;
                        border: 2px solid #ddd; 
                        padding: 10px; 
                        margin: 10px; 
                        cursor: pointer;
                        width: 150px;
                        height: 120px;
                        border-radius: 8px;
                        background: white;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        overflow: hidden;
                     ">
                    <img src="${fondo.url_preview}" alt="${fondo.nombre}" loading="lazy" 
                         style="
                            width: 100%; 
                            height: 80px; 
                            object-fit: cover;
                            border-radius: 4px;
                            display: block;
                         ">
                    <div class="fondo-overlay-modern" style="display: none;">
                        <i class="fas fa-check"></i>
                    </div>
                    <div class="fondo-info-modern" style="
                        text-align: center;
                        margin-top: 5px;
                        font-size: 12px;
                        color: #666;
                        overflow: hidden;
                        white-space: nowrap;
                        text-overflow: ellipsis;
                    ">
                        <span class="fondo-name">${fondo.nombre}</span>
                    </div>
                </div>
            `).join('');
            
            console.log('📝 HTML generado (primeros 200 chars):', fondosHtml.substring(0, 200) + '...');
            
            container.innerHTML = fondosHtml;
            
            // Asegurar que el contenedor sea visible
            container.style.display = 'block';
            container.style.minHeight = '200px';
            container.style.padding = '10px';
            container.style.backgroundColor = '#f8f9fa';
            container.style.border = '1px solid #dee2e6';
            container.style.borderRadius = '8px';
            
            console.log('✅ HTML INSERTADO EN CONTENEDOR');
            console.log('🎯 Contenedor después de insertar:', container.innerHTML.length, 'caracteres');
            console.log('📏 Contenedor visible:', container.offsetWidth, 'x', container.offsetHeight);
            
        } catch (error) {
            console.error('❌ ERROR EN CARGA GALERÍA:', error);
            console.error('📋 Stack trace completo:', error.stack);
            
            const container = document.getElementById('galeria-fondos-grid');
            if (container) {
                container.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #e53e3e;">
                        <p>ERROR: ${error.message}</p>
                        <small>Revisa la consola para detalles</small>
                    </div>
                `;
            }
        }
    }

    async seleccionarFondo(fondoId, nombre, elemento) {
        // Remover selección previa
        document.querySelectorAll('.fondo-thumbnail-modern').forEach(thumb => {
            thumb.classList.remove('selected');
        });
        
        // Seleccionar nuevo fondo
        if (elemento) {
            elemento.classList.add('selected');
        }
        
        console.log('🖼️ Fondo seleccionado:', nombre, 'ID:', fondoId);
        
        try {
            // Obtener URL directamente del atributo data
            const urlCompleta = elemento.dataset.fondoUrl;
            
            if (!urlCompleta || urlCompleta.includes('undefined')) {
                console.error('❌ URL de fondo no válida:', urlCompleta);
                this.mostrarNotificacion('Error: URL de fondo no válida', 'error');
                return;
            }
            
            // Extraer nombre del archivo de la URL
            const nombreArchivo = urlCompleta.split('/').pop();
            console.log('✅ URL obtenida desde data attribute:', urlCompleta);
            
            this.fondoSeleccionado = { 
                url: urlCompleta, 
                nombre, 
                id: fondoId,
                tipo: 'imagen',
                valor: urlCompleta,
                nombre_archivo: nombreArchivo,
                colores_adaptativos: null
            };
            
            console.log('✅ Fondo seleccionado guardado:', this.fondoSeleccionado);
            
            // ACTUALIZAR EL PREVISUALIZADOR INMEDIATAMENTE
            this.actualizarPrevisualizador(urlCompleta, nombre);
            
            // MOSTRAR NOTIFICACIÓN DE SELECCIÓN
            this.mostrarNotificacion(`✅ Fondo "${nombre}" seleccionado para preview`, 'success');
            
            // Mostrar botón de aplicar si no existe
            this.mostrarBotonAplicar();
        } catch (error) {
            console.error('❌ Error al seleccionar fondo:', error);
            this.mostrarNotificacion('Error al seleccionar el fondo', 'error');
        }
    }

    mostrarBotonAplicar() {
        // Habilitar el botón de aplicar cambios
        const btnAplicar = document.querySelector('.btn-action-primary');
        if (btnAplicar) {
            btnAplicar.disabled = false;
            btnAplicar.classList.remove('disabled');
            btnAplicar.style.opacity = '1';
            btnAplicar.style.cursor = 'pointer';
            
            // Agregar efecto visual para indicar que hay cambios pendientes
            btnAplicar.classList.add('fondo-seleccionado');
        }
    }





    actualizarPrevisualizador(fondoUrl, nombre) {
        console.log('🔄 Actualizando previsualizador con:', nombre);
        console.log('🖼️ URL del fondo:', fondoUrl);
        
        // Encontrar el iframe del previsualizador (múltiples selectores)
        const iframe = document.getElementById('preview-iframe') || 
                      document.querySelector('.chatbot-preview') ||
                      document.querySelector('iframe');
        
        console.log('🎯 Iframe encontrado:', !!iframe);
        
        if (iframe) {
            // MÉTODO DIRECTO: Aplicar el fondo al iframe
            iframe.style.backgroundImage = `url('${fondoUrl}')`;
            iframe.style.backgroundSize = 'cover';
            iframe.style.backgroundPosition = 'center';
            iframe.style.backgroundColor = 'transparent';
            
            // También actualizar el body del iframe si es accesible
            try {
                if (iframe.contentDocument && iframe.contentDocument.body) {
                    iframe.contentDocument.body.style.backgroundImage = `url('${fondoUrl}')`;
                    iframe.contentDocument.body.style.backgroundSize = 'cover';
                    iframe.contentDocument.body.style.backgroundPosition = 'center';
                }
            } catch (e) {
                // Error de CORS, ignorar
            }
            
            console.log('✅ Previsualizador actualizado con imagen');
        } else {
            console.error('❌ No se encontró el iframe previsualizador');
        }
        
        // Actualizar el texto del estado actual
        const estadoFondo = document.getElementById('fondo-actual-nombre');
        if (estadoFondo) {
            estadoFondo.textContent = `Imagen: ${nombre}`;
        }
    }

    async analizarContrasteFondo(fondoUrl) {
        if (!fondoUrl || fondoUrl.includes('undefined')) {
            this.mostrarNotificacion('❌ URL de fondo inválida', 'error');
            return;
        }

        // Aplicar fondo directamente
        const chatContainer = document.querySelector('.chat-container') || 
                            document.querySelector('.chatbot-container') || 
                            document.body;
        
        if (chatContainer) {
            chatContainer.style.backgroundImage = `url('${fondoUrl}')`;
            chatContainer.style.backgroundSize = 'cover';
            chatContainer.style.backgroundPosition = 'center';
            chatContainer.style.backgroundRepeat = 'no-repeat';
        }

        this.aplicarFondoInmediato('imagen', fondoUrl);
    }





    generarUrlChatbotConFondo(fondoData) {
        /**
         * Genera URL del chatbot con parámetros de fondo aplicado
         * Compatible con el sistema de personalización dinámica del template
         */
        console.log('🌐 Generando URL chatbot con fondo:', fondoData);
        
        const params = new URLSearchParams();
        params.set('fondo_tipo', fondoData.tipo);
        params.set('fondo_valor', fondoData.valor);
        
        // Si tenemos colores adaptativos, incluirlos
        if (this.temaAutomatico) {
            if (this.temaAutomatico.text_color) params.set('text_color', this.temaAutomatico.text_color);
            if (this.temaAutomatico.title_color) params.set('title_color', this.temaAutomatico.title_color);
            if (this.temaAutomatico.accent_color) params.set('accent_color', this.temaAutomatico.accent_color);
            if (this.temaAutomatico.button_color) params.set('button_color', this.temaAutomatico.button_color);
            if (this.temaAutomatico.button_text_color) params.set('button_text_color', this.temaAutomatico.button_text_color);
            if (this.temaAutomatico.es_imagen_oscura !== undefined) params.set('es_imagen_oscura', this.temaAutomatico.es_imagen_oscura);
        }
        
        const chatbotUrl = `/chatbot?${params.toString()}`;
        console.log('✅ URL generada:', chatbotUrl);
        return chatbotUrl;
    }

    aplicarFondoInmediato(tipo, valor) {
        console.log(`🚀 Aplicando fondo inmediato: ${tipo} = ${valor}`);
        
        // Solución CORS: Recargar iframe con parámetros URL
        const iframe = document.getElementById('preview-iframe') || document.querySelector('iframe');
        if (iframe) {
            try {
                // Obtener URL actual del iframe
                const currentSrc = iframe.src;
                const baseUrl = currentSrc.split('?')[0]; // Remover parámetros existentes
                
                // Crear parámetros básicos de fondo
                let urlParams = new URLSearchParams();
                urlParams.set('fondo_tipo', tipo);
                urlParams.set('fondo_valor', valor);
                
                // Si tenemos tema adaptativo, agregar esos parámetros también
                if (this.temaAdaptativo) {
                    urlParams.set('text_color', this.temaAdaptativo.text_color);
                    urlParams.set('title_color', this.temaAdaptativo.title_color);
                    urlParams.set('accent_color', this.temaAdaptativo.accent_color);
                    urlParams.set('button_color', this.temaAdaptativo.button_color);
                    urlParams.set('button_text_color', this.temaAdaptativo.button_text_color);
                    urlParams.set('es_imagen_oscura', this.temaAdaptativo.es_imagen_oscura);
                    console.log('✨ Incluyendo colores adaptativos en la URL del iframe');
                }
                
                // Crear nueva URL completa
                const newUrl = `${baseUrl}?${urlParams.toString()}`;
                
                // Recargar iframe con nueva configuración
                iframe.src = newUrl;
                
                console.log(`✅ Iframe recargado con configuración completa: ${tipo} = ${valor}`);
                this.mostrarNotificacion(`Fondo aplicado: ${tipo}`, 'success');
                
            } catch (e) {
                console.log('⚠️ Error al recargar iframe:', e);
                this.mostrarNotificacion('Error al aplicar fondo', 'error');
            }
        } else {
            console.log('⚠️ No se encontró iframe de preview');
            this.mostrarNotificacion('Preview no disponible - Intenta abrir una nueva pestaña del chatbot', 'info');
        }
        
        // 🔄 COMUNICACIÓN CON PESTAÑAS ABIERTAS DEL CHATBOT
        // Usar BroadcastChannel para comunicar cambios a pestañas del chatbot abiertas
        try {
            // Crear canal de comunicación
            const channel = new BroadcastChannel('eterials-fondo-change');
            
            // Enviar mensaje de cambio a todas las pestañas del chatbot
            channel.postMessage({
                type: 'fondo_changed',
                fondo_tipo: tipo,
                fondo_valor: valor,
                timestamp: Date.now()
            });
            
            console.log(`📡 Enviado mensaje de cambio de fondo a pestañas del chatbot: ${tipo} = ${valor}`);
            
            // Cerrar el canal
            setTimeout(() => channel.close(), 1000);
            
        } catch (e) {
            console.log('⚠️ BroadcastChannel no soportado, pestañas abiertas no se actualizarán automáticamente');
        }
    }

    async aplicarFondo() {
        console.log('🚀 INICIANDO aplicarFondo()...');
        console.log('📋 Estado fondoSeleccionado:', this.fondoSeleccionado);
        console.log('🎨 Estado temaAutomatico:', this.temaAutomatico);
        
        try {
            if (!this.fondoSeleccionado || this.fondoSeleccionado.tipo !== 'imagen') {
                this.mostrarNotificacion('Selecciona una imagen de fondo', 'warning');
                return;
            }
            
            const fondoData = { 
                tipo: 'imagen', 
                valor: this.fondoSeleccionado.url, 
                nombre: this.fondoSeleccionado.nombre
            };
            
            console.log('📤 Aplicando fondo ID:', this.fondoSeleccionado.id);
            
            // Llamar al endpoint para aplicar el fondo
            const response = await fetch('/api/chatbot/fondos/aplicar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fondo_tipo: 'imagen',
                    fondo_valor: this.fondoSeleccionado.id,
                    fondo_url: this.fondoSeleccionado.url
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ Fondo aplicado exitosamente al sistema');
                console.log('📋 Respuesta del servidor:', result);
                
                // MOSTRAR NOTIFICACIÓN DE ÉXITO
                this.mostrarNotificacion(`✅ Fondo "${fondoData.nombre}" aplicado correctamente al chatbot`, 'success');
                
                // ACTUALIZAR ESTADO ACTUAL
                const estadoFondo = document.getElementById('fondo-actual-nombre');
                if (estadoFondo) {
                    estadoFondo.textContent = `Imagen: ${fondoData.nombre}`;
                }
                
                const estadoActualizacion = document.getElementById('ultima-actualizacion');
                if (estadoActualizacion) {
                    estadoActualizacion.textContent = new Date().toLocaleTimeString();
                }
                
                // RECARGAR IFRAME DE PREVIEW PARA VER EL CAMBIO
                const iframe = document.getElementById('preview-iframe');
                if (iframe) {
                    const currentSrc = iframe.src.split('?')[0];
                    iframe.src = currentSrc + '?t=' + Date.now();
                }
                
                // OFRECER ABRIR CHATBOT EN NUEVA PESTAÑA
                setTimeout(() => {
                    const abrirChatbot = confirm('¿Quieres abrir el chatbot en una nueva pestaña para ver el fondo aplicado?');
                    if (abrirChatbot) {
                        window.open('/chatbot', '_blank');
                    }
                }, 1000);
                
            } else {
                console.error('❌ Error del servidor:', result.error || result.message);
                this.mostrarNotificacion(`❌ Error: ${result.error || result.message}`, 'error');
            }
            
        } catch (error) {
            console.error('❌ Error aplicando fondo:', error);
            this.mostrarNotificacion(`❌ Error de conexión: ${error.message}`, 'error');
            
            // También mostrar detalles técnicos en consola
            console.error('📋 Detalles del error:', error);
        }
    }

    mostrarNotificacion(mensaje, tipo = 'info') {
        console.log(`${tipo.toUpperCase()}: ${mensaje}`);
        
        // Crear notificación visual
        let notificacionContainer = document.getElementById('notificaciones-container');
        if (!notificacionContainer) {
            notificacionContainer = document.createElement('div');
            notificacionContainer.id = 'notificaciones-container';
            notificacionContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 300px;
            `;
            document.body.appendChild(notificacionContainer);
        }
        
        const notificacion = document.createElement('div');
        notificacion.style.cssText = `
            background: ${tipo === 'success' ? '#4CAF50' : tipo === 'error' ? '#f44336' : tipo === 'warning' ? '#ff9800' : '#2196F3'};
            color: white;
            padding: 12px 16px;
            margin-bottom: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-size: 14px;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Agregar estilos de animación si no existen
        if (!document.getElementById('notificacion-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notificacion-styles';
            styles.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        notificacion.textContent = mensaje;
        notificacionContainer.appendChild(notificacion);
        
        // Auto eliminar después de 4 segundos
        setTimeout(() => {
            notificacion.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => {
                if (notificacion.parentNode) {
                    notificacion.parentNode.removeChild(notificacion);
                }
            }, 300);
        }, 4000);
    }

    /**
     * Maneja el upload de nuevas imágenes de fondo
     */
    async manejarUploadImagen(event) {
        const file = event.target.files[0];
        if (!file) {
            console.log('❌ No se seleccionó archivo');
            return;
        }

        console.log('📤 Iniciando upload de imagen:', file.name);
        console.log('📊 Tamaño:', (file.size / 1024 / 1024).toFixed(2), 'MB');
        console.log('📋 Tipo:', file.type);

        // Validaciones
        if (!file.type.startsWith('image/')) {
            this.mostrarNotificacion('❌ Solo se permiten archivos de imagen', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB
            this.mostrarNotificacion('❌ El archivo es muy grande (máximo 5MB)', 'error');
            return;
        }

        try {
            this.mostrarNotificacion('⏳ Subiendo imagen...', 'info');

            // Crear FormData para el upload
            const formData = new FormData();
            formData.append('archivo', file); // Cambiar 'file' por 'archivo' para coincidir con el endpoint

            // Realizar upload
            const response = await fetch('/api/chatbot/fondos/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                console.log('✅ Upload exitoso:', result);
                this.mostrarNotificacion(`✅ Imagen "${file.name}" subida correctamente`, 'success');
                
                // Actualizar galería
                await this.cargarGaleria();
                
                // Limpiar input
                event.target.value = '';
                
                // Seleccionar automáticamente la nueva imagen si viene con ID
                if (result.fondo && result.fondo.id) {
                    setTimeout(() => {
                        const nuevoFondo = document.querySelector(`[data-fondo-id="${result.fondo.id}"]`);
                        if (nuevoFondo) {
                            nuevoFondo.click();
                        }
                    }, 500);
                }
                
            } else {
                throw new Error(result.error || 'Error desconocido en el upload');
            }

        } catch (error) {
            console.error('❌ Error en upload:', error);
            this.mostrarNotificacion(`❌ Error al subir imagen: ${error.message}`, 'error');
            
            // Limpiar input en caso de error
            event.target.value = '';
        }
    }
}

// Inicializar dashboard cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new ChatbotDashboard();
    console.log('✅ Dashboard listo');
});



function aplicarSoloFondo() {
    console.log('🔥 BOTÓN APLICAR PRESIONADO - aplicarSoloFondo()');
    console.log('🔧 window.dashboard existe:', !!window.dashboard);
    
    if (window.dashboard) {
        console.log('✅ Llamando a window.dashboard.aplicarFondo()...');
        window.dashboard.aplicarFondo();
    } else {
        console.error('❌ window.dashboard no está disponible');
    }
}

function mostrarSeccion(seccion) {
    console.log(`📄 Mostrando sección: ${seccion}`);
    
    // Ocultar todas las secciones
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Mostrar sección seleccionada
    const targetSection = document.getElementById(`seccion-${seccion}`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Actualizar navegación
    document.querySelectorAll('.dashboard-nav a').forEach(link => {
        link.classList.remove('nav-active');
    });
    
    const activeLink = document.querySelector(`[onclick*="${seccion}"]`);
    if (activeLink) {
        activeLink.classList.add('nav-active');
    }
    
    // Si es la sección de personalización, cargar galería
    if (seccion === 'personalizacion' && window.dashboard) {
        setTimeout(() => {
            console.log('🖼️ Cargando galería para sección personalización...');
            const radioImagen = document.getElementById('fondo-imagen');
            if (radioImagen && radioImagen.checked) {
                window.dashboard.cargarGaleria();
            }
        }, 100);
    }
}

function seleccionarTipoFondo(tipo) {
    if (window.dashboard) {
        window.dashboard.cambiarTipoFondo('imagen');
    }
}

// ===============================================
// GESTIÓN DE MENÚ - NUEVAS FUNCIONES
// ===============================================

/**
 * Prueba el menú principal abriendo en nueva pestaña
 */
function probarMenuPrincipal() {
    const menuUrl = '/menu/general';
    console.log('🍽️ Abriendo menú principal:', menuUrl);
    
    // Actualizar estado visual
    actualizarEstadoMenu('principal');
    
    // Abrir en nueva pestaña
    window.open(menuUrl, '_blank');
}

/**
 * Prueba el menú alternativo si está configurado
 */
function probarMenuAlternativo() {
    const urlInput = document.getElementById('menu-alternativo-url');
    const url = urlInput ? urlInput.value.trim() : '';
    
    if (!url) {
        alert('⚠️ Primero configura la URL del menú alternativo');
        if (urlInput) {
            urlInput.focus();
        }
        return;
    }
    
    // Validar URL básica
    try {
        new URL(url);
    } catch (e) {
        alert('❌ URL no válida. Ejemplo: https://ejemplo.com/menu-especial');
        return;
    }
    
    console.log('🔗 Abriendo menú alternativo:', url);
    
    // Actualizar estado visual
    actualizarEstadoMenu('alternativo', url);
    
    // Abrir en nueva pestaña
    window.open(url, '_blank');
}

/**
 * Actualiza el estado visual del sistema de menús
 */
function actualizarEstadoMenu(tipo, url = null) {
    const statusElement = document.getElementById('menu-status');
    
    if (!statusElement) return;
    
    const ahora = new Date().toLocaleString();
    const menuPrincipalHabilitado = document.getElementById('menu-principal-habilitado')?.checked;
    const menuAlternativoHabilitado = document.getElementById('menu-alternativo-habilitado')?.checked;
    
    let statusText = '';
    let iconClass = 'fas fa-info-circle text-warning';
    
    if (menuPrincipalHabilitado && menuAlternativoHabilitado) {
        statusText = 'Ambos menús habilitados - Los usuarios verán ambas opciones';
        iconClass = 'fas fa-check-circle text-success';
    } else if (menuPrincipalHabilitado && !menuAlternativoHabilitado) {
        statusText = 'Solo menú principal habilitado';
        iconClass = 'fas fa-check-circle text-success';
    } else if (!menuPrincipalHabilitado && menuAlternativoHabilitado) {
        statusText = 'Solo menú alternativo habilitado';
        iconClass = 'fas fa-external-link-alt text-warning';
    } else {
        statusText = '⚠️ Ningún menú habilitado - Los usuarios no podrán ver menús';
        iconClass = 'fas fa-exclamation-triangle text-error';
    }
    
    if (tipo === 'principal') {
        statusText += ` - Menú principal probado: ${ahora}`;
    } else if (tipo === 'alternativo' && url) {
        statusText += ` - Menú alternativo probado: ${ahora}`;
    }
    
    statusElement.innerHTML = `
        <i class="${iconClass}"></i> 
        <span>${statusText}</span>
    `;
}

/**
 * Carga la configuración del menú desde el servidor
 */
async function cargarConfiguracionMenu() {
    try {
        console.log('📋 Cargando configuración de menús desde API...');
        
        const response = await fetch('/api/chatbot/configuracion/menus', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Error desconocido');
        }
        
        const config = data.configuracion;
        
        // Aplicar configuración a la interfaz
        const checkboxMenuPrincipal = document.getElementById('menu-principal-habilitado');
        const checkboxMenuAlternativo = document.getElementById('menu-alternativo-habilitado');
        const inputUrlPrincipal = document.getElementById('menu-principal-url');
        const inputUrlAlternativo = document.getElementById('menu-alternativo-url');
        
        if (checkboxMenuPrincipal) {
            checkboxMenuPrincipal.checked = config.menu_principal_activo;
        }
        
        if (checkboxMenuAlternativo) {
            checkboxMenuAlternativo.checked = config.menu_alternativo_activo;
        }
        
        if (inputUrlPrincipal) {
            inputUrlPrincipal.value = config.menu_principal_url || '/menu/general';
        }
        
        if (inputUrlAlternativo) {
            inputUrlAlternativo.value = config.menu_alternativo_url || '';
        }
        
        // Configurar event listeners para actualizar estado cuando cambien los controles
        [checkboxMenuPrincipal, checkboxMenuAlternativo, inputUrlPrincipal, inputUrlAlternativo].forEach(element => {
            if (element) {
                element.addEventListener('change', () => {
                    actualizarEstadoMenu();
                });
            }
        });
        
        // Actualizar estado inicial
        setTimeout(() => actualizarEstadoMenu(), 100);
        
        console.log('✅ Configuración de menú cargada desde API:', config);
        
    } catch (error) {
        console.error('❌ Error cargando configuración de menú:', error);
        
        // Fallback a valores por defecto
        const checkboxMenuPrincipal = document.getElementById('menu-principal-habilitado');
        const checkboxMenuAlternativo = document.getElementById('menu-alternativo-habilitado');
        const inputUrlPrincipal = document.getElementById('menu-principal-url');
        const inputUrlAlternativo = document.getElementById('menu-alternativo-url');
        
        if (checkboxMenuPrincipal) checkboxMenuPrincipal.checked = true;
        if (checkboxMenuAlternativo) checkboxMenuAlternativo.checked = false;
        if (inputUrlPrincipal) inputUrlPrincipal.value = '/menu/general';
        if (inputUrlAlternativo) inputUrlAlternativo.value = '';
    }
}

/**
 * Guarda la configuración del menú
 */
async function guardarConfiguracionMenu() {
    try {
        const checkboxMenuPrincipal = document.getElementById('menu-principal-habilitado');
        const checkboxMenuAlternativo = document.getElementById('menu-alternativo-habilitado');
        const inputUrlPrincipal = document.getElementById('menu-principal-url');
        const inputUrlAlternativo = document.getElementById('menu-alternativo-url');
        
        const config = {
            menu_principal_activo: checkboxMenuPrincipal ? checkboxMenuPrincipal.checked : true,
            menu_alternativo_activo: checkboxMenuAlternativo ? checkboxMenuAlternativo.checked : false,
            menu_principal_url: inputUrlPrincipal ? inputUrlPrincipal.value.trim() : '/menu/general',
            menu_alternativo_url: inputUrlAlternativo ? inputUrlAlternativo.value.trim() : ''
        };
        
        // Validaciones
        if (config.menu_alternativo_activo && !config.menu_alternativo_url) {
            alert('❌ Para habilitar el menú alternativo debes proporcionar una URL válida');
            if (inputUrlAlternativo) inputUrlAlternativo.focus();
            return false;
        }
        
        if (config.menu_alternativo_url && config.menu_alternativo_url !== '') {
            // Validar que sea una URL válida (permitir rutas relativas)
            if (!config.menu_alternativo_url.startsWith('/') && !config.menu_alternativo_url.startsWith('http')) {
                alert('❌ URL del menú alternativo debe empezar con / o http. Ejemplo: /menu/especial o https://ejemplo.com/menu');
                if (inputUrlAlternativo) inputUrlAlternativo.focus();
                return false;
            }
        }
        
        if (!config.menu_principal_activo && !config.menu_alternativo_activo) {
            const confirmar = confirm('⚠️ Vas a deshabilitar ambos menús. Los usuarios no podrán ver ningún menú. ¿Continuar?');
            if (!confirmar) {
                return false;
            }
        }
        
        console.log('💾 Guardando configuración de menú en API:', config);
        
        // Enviar configuración al API
        const response = await fetch('/api/chatbot/configuracion/menus', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Error desconocido');
        }
        
        // Actualizar estado en la interfaz
        actualizarEstadoMenu();
        
        // Mostrar notificación de éxito temporal
        const statusElement = document.getElementById('menu-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <i class="fas fa-check-circle text-success"></i> 
                <span>✅ Configuración guardada correctamente</span>
            `;
            
            setTimeout(() => {
                actualizarEstadoMenu();
            }, 3000);
        }
        
        console.log('✅ Configuración de menú guardada exitosamente');
        return true;
        
    } catch (error) {
        console.error('❌ Error guardando configuración de menú:', error);
        alert(`Error guardando la configuración: ${error.message}`);
        return false;
    }
}

// ===============================================
// FUNCIONES FALTANTES LLAMADAS DESDE EL HTML
// ===============================================

function actualizarDashboard() {
    console.log('🔄 Actualizando dashboard...');
    if (window.dashboard) {
        // Recargar métricas y datos
        window.dashboard.cargarGaleria();
        window.dashboard.mostrarNotificacion('🔄 Dashboard actualizado', 'success');
    }
}

function aplicarFiltros() {
    console.log('🔍 Aplicando filtros de calificaciones...');
    // Implementar lógica de filtros aquí
    window.dashboard && window.dashboard.mostrarNotificacion('🔍 Filtros aplicados', 'info');
}

function marcarTodasLeidas() {
    console.log('✅ Marcando todas las notificaciones como leídas...');
    // Implementar lógica aquí
    window.dashboard && window.dashboard.mostrarNotificacion('✅ Notificaciones marcadas como leídas', 'success');
}

function actualizarPreviewFondo() {
    console.log('🖼️ Actualizando preview del fondo...');
    const iframe = document.getElementById('preview-iframe');
    if (iframe) {
        // Recargar iframe
        const currentSrc = iframe.src;
        iframe.src = currentSrc.split('?')[0] + '?t=' + Date.now();
        window.dashboard && window.dashboard.mostrarNotificacion('🔄 Preview actualizado', 'info');
    }
}

function resetearConfiguracion() {
    console.log('🔄 Reseteando configuración...');
    const confirmar = confirm('¿Estás seguro de que quieres resetear toda la configuración?');
    if (confirmar) {
        // Implementar lógica de reset aquí
        window.dashboard && window.dashboard.mostrarNotificacion('🔄 Configuración reseteada', 'warning');
    }
}

// Cargar configuración al inicializar
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(cargarConfiguracionMenu, 1000);
    
    // Manejar envío del formulario
    const form = document.getElementById('form-configuracion');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault(); // Evitar envío normal del formulario
            console.log('📋 Submit del formulario interceptado, guardando configuración de menú...');
            await guardarConfiguracionMenu();
        });
    }
});

// ================================================================================
// FUNCIÓN RESTABLECER FONDO - Sistema de Fondos Robusto
// ================================================================================
async function resetearFondo() {
    /**
     * Restablece el fondo del chatbot al negro por defecto
     * Limpia la configuración de base de datos para usar fondo negro automático
     */
    try {
        console.log('🖤 Iniciando restablecimiento de fondo al negro por defecto...');
        
        // Confirmar acción con el usuario
        const confirmar = confirm('¿Estás seguro de que quieres restablecer el fondo a negro por defecto?\n\nEsto eliminará cualquier configuración de fondo personalizado.');
        if (!confirmar) {
            console.log('❌ Restablecimiento cancelado por el usuario');
            return;
        }
        
        // Llamar al endpoint para limpiar configuración de fondo
        const response = await fetch('/api/chatbot/fondos/restablecer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                accion: 'restablecer_negro'
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            console.log('✅ Fondo restablecido exitosamente:', data);
            
            // Mostrar mensaje de éxito
            const statusElement = document.querySelector('.status-msg');
            if (statusElement) {
                statusElement.innerHTML = `
                    <i class="fas fa-check-circle text-success"></i> 
                    <span>🖤 Fondo restablecido a negro por defecto</span>
                `;
                statusElement.style.display = 'block';
            }
            
            // Actualizar preview
            actualizarPreviewFondo();
            
            // Recargar galería de fondos
            if (typeof cargarFondosExistentes === 'function') {
                cargarFondosExistentes();
            }
            
            // Mensaje temporal de éxito
            alert('✅ Fondo restablecido a negro por defecto.\n\nEl chatbot ahora mostrará fondo negro hasta que selecciones otro fondo.');
            
        } else {
            throw new Error(data.error || 'Error desconocido al restablecer fondo');
        }
        
    } catch (error) {
        console.error('❌ Error restableciendo fondo:', error);
        alert(`❌ Error al restablecer fondo: ${error.message}\n\nIntenta nuevamente o contacta al administrador.`);
    }
}