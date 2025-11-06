// Función de saludo simplificada
function obtenerSaludo() {
    let hora = new Date().getHours();
    if (hora >= 6 && hora < 12) return "Buenos días";
    if (hora >= 12 && hora < 18) return "Buenas tardes";
    return "Buenas noches";
}

async function mostrarSaludo() {
    let saludo = await obtenerSaludoPersonalizado();
    let numeroMesa = new URLSearchParams(window.location.search).get("mesa") || "Sin número";
    let nombreCliente = sessionStorage.getItem("nombreCliente") || "Invitado";
    let mensaje = `<span class="saludo-destacado">${saludo}</span><br>
    <span class="saludo-mensaje">
        ¡Bienvenido${nombreCliente !== "Invitado" ? `, <b>${nombreCliente}</b>` : ""}!<br>
        Es un placer atenderte en la mesa <b>${numeroMesa}</b>.
    </span>`;
    if (nombreCliente !== "Invitado") {
        document.getElementById("nombre-container").style.display = "none";
    } else {
        document.getElementById("nombre-container").style.display = "block";
    }
    document.getElementById("saludo").innerHTML = mensaje;
}

function actualizarEnlacesMenu() {
    const params = new URLSearchParams(window.location.search);
    const mesa = params.get("mesa") || sessionStorage.getItem("mesa") || 1;
    const nombreCliente = sessionStorage.getItem("nombreCliente") || "";
    
    // Construir parámetros de URL
    let parametros = `mesa=${mesa}`;
    if (nombreCliente && nombreCliente !== "Invitado") {
        parametros += `&nombre=${encodeURIComponent(nombreCliente)}`;
    }
    
    // Actualizar enlace del menú
    document.getElementById('btn-menu').href = `/menu/general?${parametros}`;
    
    // También actualizar otros enlaces que pueden necesitar el nombre
    const base = "/modulos";
    document.getElementById("btn-cancionero").href = `/modulos/cancionero/index.html?${parametros}`;
    document.getElementById("btn-mesero").href = `${base}/mesero/index.html?${parametros}`;
    document.getElementById("btn-karaoke").href = `${base}/karaoke/index.html?${parametros}`;
    document.getElementById("btn-opiniones").href = `${base}/opiniones/index.html?${parametros}`;
}

function guardarNombre() {
    let nombre = document.getElementById("nombre").value.trim();
    if (nombre !== "") {
        // Guardar en sessionStorage local
        sessionStorage.setItem("nombreCliente", nombre);
        
        // Enviar al backend
        const mesa = new URLSearchParams(window.location.search).get("mesa") || sessionStorage.getItem("mesa") || 1;
        crearSesionBackend(mesa, nombre);
        
        mostrarSaludo();
        actualizarEnlacesMenu(); // Actualizar enlaces cuando se guarda el nombre
        alert(`¡Gracias, ${nombre}! Ahora te llamaremos por tu nombre.`);
    } else {
        alert("Por favor, ingresa un nombre válido.");
    }
}

// Nueva función para crear sesión en backend
async function crearSesionBackend(mesa, nombre) {
    try {
        const datosNavegador = {
            userAgent: navigator.userAgent,
            pantalla: `${screen.width}x${screen.height}`,
            idioma: navigator.language
        };
        
        const response = await fetch('/api/chatbot/sesion/iniciar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mesa: mesa,
                nombre_cliente: nombre,
                dispositivo: datosNavegador.userAgent,
                ip_cliente: 'auto', // El backend detectará la IP
                metadatos: datosNavegador
            })
        });
        
        if (response.ok) {
            const sesion = await response.json();
            sessionStorage.setItem("sesionId", sesion.id);
            console.log('✅ Sesión creada en backend:', sesion);
        } else {
            console.error('❌ Error creando sesión:', response.status);
        }
    } catch (error) {
        console.error('❌ Error conectando con backend:', error);
    }
}

// Nueva función para actualizar actividad de sesión
async function actualizarActividadSesion() {
    const sesionId = sessionStorage.getItem("sesionId");
    if (!sesionId) return;
    
    try {
        await fetch(`/api/chatbot/sesion/${sesionId}/actividad`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('❌ Error actualizando actividad:', error);
    }
}

// --- Inactividad: configuración dinámica desde backend ---
let inactividadTimeout;
let timeoutConfiguracion = 600000; // Default: 10 minutos

// Cargar configuración de timeout desde backend
async function cargarTimeoutConfiguracion() {
    try {
        const response = await fetch('/api/chatbot/configuracion/timeout');
        if (response.ok) {
            const config = await response.json();
            timeoutConfiguracion = config.timeout_milisegundos;
            console.log(`⏰ Timeout configurado: ${config.timeout_minutos} minutos`);
        }
    } catch (error) {
        console.warn('⚠️ Usando timeout por defecto:', error);
    }
}

function resetInactividad() {
    clearTimeout(inactividadTimeout);
    
    // Actualizar actividad en backend
    actualizarActividadSesion();
    
    inactividadTimeout = setTimeout(async () => {
        // Validar sesión en backend antes de cerrar
        const sesionId = sessionStorage.getItem("sesionId");
        if (sesionId) {
            try {
                const response = await fetch(`/api/chatbot/sesion/${sesionId}/validar`);
                if (response.ok) {
                    const validacion = await response.json();
                    if (!validacion.valida) {
                        console.log('🔒 Sesión invalidada por servidor:', validacion.razon);
                    }
                }
            } catch (error) {
                console.warn('⚠️ Error validando sesión:', error);
            }
        }
        
        // Cerrar sesión en backend antes de limpiar local
        cerrarSesionBackend();
        sessionStorage.clear();
        location.reload();
    }, timeoutConfiguracion);
}

// Nueva función para cerrar sesión en backend
async function cerrarSesionBackend() {
    const sesionId = sessionStorage.getItem("sesionId");
    if (!sesionId) return;
    
    try {
        await fetch(`/api/chatbot/sesion/${sesionId}/cerrar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log('✅ Sesión cerrada en backend');
    } catch (error) {
        console.error('❌ Error cerrando sesión:', error);
    }
}
["click", "mousemove", "keydown", "scroll", "touchstart"].forEach(evt =>
    document.addEventListener(evt, resetInactividad)
);

// Estrellas de calificación
document.addEventListener('DOMContentLoaded', function () {
    mostrarSaludo();
    resetInactividad();
    actualizarEnlacesMenu(); // Actualizar enlaces al cargar la página

    const estrellas = document.querySelectorAll('.estrella');
    let calificacionSeleccionada = 0;

    estrellas.forEach(estrella => {
        estrella.addEventListener('mouseenter', function () {
            pintarEstrellas(this.dataset.valor);
        });
        estrella.addEventListener('mouseleave', function () {
            pintarEstrellas(calificacionSeleccionada);
        });
        estrella.addEventListener('click', function () {
            calificacionSeleccionada = this.dataset.valor;
            pintarEstrellas(calificacionSeleccionada);
        });
    });

    function pintarEstrellas(valor) {
        estrellas.forEach(estrella => {
            if (estrella.dataset.valor <= valor) {
                estrella.classList.add('seleccionada');
            } else {
                estrella.classList.remove('seleccionada');
            }
        });
    }

    window.enviarCalificacion = function () {
        if (calificacionSeleccionada > 0) {
            // Enviar al backend
            enviarCalificacionBackend(calificacionSeleccionada);
            alert(`¡Gracias por tu calificación de ${calificacionSeleccionada} estrella(s)!`);
        } else {
            alert('Por favor, selecciona una calificación.');
        }
    }
    
    // Nueva función para enviar calificación al backend
    async function enviarCalificacionBackend(estrellas) {
        const sesionId = sessionStorage.getItem("sesionId");
        if (!sesionId) {
            console.warn('⚠️ No hay sesión activa para guardar calificación');
            return;
        }
        
        try {
            const response = await fetch('/api/chatbot/calificacion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sesion_id: sesionId,
                    estrellas: estrellas,
                    categoria: 'servicio' // Categoría por defecto
                })
            });
            
            if (response.ok) {
                const calificacion = await response.json();
                console.log('✅ Calificación guardada:', calificacion);
            } else {
                console.error('❌ Error guardando calificación:', response.status);
            }
        } catch (error) {
            console.error('❌ Error enviando calificación:', error);
        }
    }
});

function actualizarSaludo() {
    const h2Saludo = document.querySelector('.texto-iluminable:nth-of-type(2)');
    const hora = new Date().getHours();
    let saludo = "Buenas noches";
    if (hora >= 6 && hora < 12) {
        saludo = "Buenos días";
    } else if (hora >= 12 && hora < 20) {
        saludo = "Buenas tardes";
    }
    if (h2Saludo) {
        h2Saludo.textContent = saludo;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Chatbot cargado correctamente');
    
    // Cargar configuraciones del backend
    cargarConfiguracionesBackend();
    
    // Cargar saludo y actualizar UI
    actualizarSaludo();
    mostrarSaludo();
    actualizarEnlacesMenu();
    
    // Intentar restaurar sesión existente
    restaurarSesionExistente();
    
    // Cargar configuración de timeout
    cargarTimeoutConfiguracion();
    
    // Escuchar cambios de tema desde el dashboard
    escucharCambiosDeTema();
});

// Nueva función para escuchar cambios de tema
function escucharCambiosDeTema() {
    // Escuchar cambios en localStorage
    window.addEventListener('storage', function(e) {
        if (e.key === 'chatbot_tema_actualizado') {
            console.log('🔄 Tema actualizado detectado, recargando...');
            // Recargar configuraciones del backend
            cargarConfiguracionesBackend();
        }
    });
    
    // También verificar periódicamente por si no se detecta el evento
    setInterval(() => {
        const mensaje = localStorage.getItem('chatbot_tema_actualizado');
        if (mensaje) {
            const datos = JSON.parse(mensaje);
            if (Date.now() - datos.timestamp < 2000) { // Mensaje reciente
                console.log('🔄 Tema actualizado detectado (polling), recargando...');
                cargarConfiguracionesBackend();
            }
        }
    }, 1000);
}

// SISTEMA DE TEMAS ELIMINADO - Solo personalización por URL parámetros disponible

// Nueva función para restaurar sesión existente
async function restaurarSesionExistente() {
    const sesionId = sessionStorage.getItem("sesionId");
    if (!sesionId) return;
    
    try {
        const response = await fetch(`/api/chatbot/sesion/${sesionId}`);
        if (response.ok) {
            const sesion = await response.json();
            if (sesion.activa) {
                console.log('✅ Sesión restaurada:', sesion);
                // Actualizar actividad
                actualizarActividadSesion();
            } else {
                // Sesión inactiva, limpiar
                sessionStorage.removeItem("sesionId");
            }
        }
    } catch (error) {
        console.warn('⚠️ Error restaurando sesión:', error);
        sessionStorage.removeItem("sesionId");
    }
}

// Guardar mesa en sessionStorage
document.addEventListener('DOMContentLoaded', function () {
    const params = new URLSearchParams(window.location.search);
    let mesa = params.get("mesa");
    if (mesa) {
        sessionStorage.setItem("mesa", mesa);
    }
});

/* ======================================================
   🎨 SISTEMA DE GESTIÓN DE TEMAS PERSONALIZADOS
   ====================================================== */

// Variables globales para el sistema de temas
let temasDisponibles = [];
let temaPersonalizacionActual = {};

// Inicializar sistema de temas al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('admin')) {
        cargarTemasPredefinidos();
        inicializarPersonalizacion();
    }
});

// Cargar y mostrar temas predefinidos
async function cargarTemasPredefinidos() {
    try {
        const response = await fetch('/api/chatbot/temas');
        if (response.ok) {
            temasDisponibles = await response.json();
            mostrarTemasPredefinidos();
        } else {
            console.error('❌ Error cargando temas:', response.statusText);
            document.getElementById('grid-temas-predefinidos').innerHTML = 
                '<div class="error-message">❌ Error cargando temas</div>';
        }
    } catch (error) {
        console.error('❌ Error:', error);
        document.getElementById('grid-temas-predefinidos').innerHTML = 
            '<div class="error-message">❌ Error de conexión</div>';
    }
}

// Mostrar tarjetas de temas predefinidos
function mostrarTemasPredefinidos() {
    const container = document.getElementById('grid-temas-predefinidos');
    
    if (temasDisponibles.length === 0) {
        container.innerHTML = '<div class="loading-message">⚠️ No hay temas disponibles</div>';
        return;
    }
    
    container.innerHTML = temasDisponibles.map(tema => {
        const colores = extraerColoresTema(tema.propiedades);
        const preview = generarPreviewTema(tema);
        
        return `
            <div class="theme-card ${tema.activo ? 'active' : ''}" data-tema-id="${tema.id}">
                <div class="theme-preview" style="background: ${preview}"></div>
                <div class="theme-info">
                    <h4>${tema.nombre}</h4>
                    <p>${tema.descripcion}</p>
                    <div class="theme-colors">
                        ${colores.map(color => `<div class="color-dot" style="background-color: ${color}"></div>`).join('')}
                    </div>
                </div>
                <div class="theme-actions">
                    <button class="btn-theme btn-apply-theme" onclick="aplicarTema(${tema.id})">
                        ${tema.activo ? '✓ Activo' : 'Aplicar'}
                    </button>
                    <button class="btn-theme btn-edit-theme" onclick="editarTema(${tema.id})">
                        Editar
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Extraer colores principales de un tema
function extraerColoresTema(propiedades) {
    const colores = [];
    propiedades.forEach(prop => {
        if (prop.categoria === 'colores' && prop.valor.includes('#')) {
            colores.push(prop.valor);
        }
    });
    return colores.slice(0, 4); // Máximo 4 colores
}

// Generar preview visual del tema
function generarPreviewTema(tema) {
    const colores = extraerColoresTema(tema.propiedades);
    if (colores.length >= 2) {
        return `linear-gradient(135deg, ${colores[0]} 0%, ${colores[1]} 100%)`;
    } else if (colores.length === 1) {
        return colores[0];
    }
    return 'linear-gradient(135deg, #d4af37 0%, #2c1810 100%)';
}

// Aplicar tema seleccionado
async function aplicarTema(temaId) {
    try {
        const response = await fetch(`/api/chatbot/temas/${temaId}/activar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const resultado = await response.json();
            console.log('✅ Tema aplicado:', resultado);
            
            // Actualizar interfaz
            cargarTemasPredefinidos();
            
            // Notificación visual
            mostrarNotificacion('✅ Tema aplicado correctamente', 'success');
            
            // Aplicar tema inmediatamente (opcional)
            // window.location.reload();
        } else {
            console.error('❌ Error aplicando tema');
            mostrarNotificacion('❌ Error aplicando tema', 'error');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarNotificacion('❌ Error de conexión', 'error');
    }
}

// Editar tema existente
function editarTema(temaId) {
    const tema = temasDisponibles.find(t => t.id === temaId);
    if (!tema) return;
    
    // Cargar propiedades del tema en los controles de personalización
    cargarTemaEnPersonalizacion(tema);
    
    // Cambiar a la pestaña de personalización manual
    cambiarSeccionDashboard('seccion-temas');
    
    mostrarNotificacion(`📝 Editando tema: ${tema.nombre}`, 'info');
}

// Cargar tema en controles de personalización
function cargarTemaEnPersonalizacion(tema) {
    temaPersonalizacionActual = { ...tema };
    
    tema.propiedades.forEach(prop => {
        const elemento = document.getElementById(mapearPropiedadAControl(prop.nombre));
        if (elemento) {
            elemento.value = prop.valor;
            
            // Si es color, actualizar también el texto
            if (prop.categoria === 'colores') {
                const textoElemento = document.getElementById(elemento.id + '-text');
                if (textoElemento) {
                    textoElemento.value = prop.valor;
                }
            }
        }
    });
}

// Mapear nombres de propiedades a controles HTML
function mapearPropiedadAControl(nombrePropiedad) {
    const mapeo = {
        'color_primario': 'color-primary',
        'color_secundario': 'color-secondary',
        'color_acento': 'color-accent',
        'texto_claro': 'color-text-light',
        'texto_oscuro': 'color-text-dark',
        'fuente_principal': 'font-primary',
        'fuente_secundaria': 'font-secondary',
        'fuente_acento': 'font-accent',
        'estilo_botones': 'button-style',
        'color_fondo': 'bg-color'
    };
    
    return mapeo[nombrePropiedad] || nombrePropiedad;
}

// Cambiar pestaña de personalización
function cambiarTabPersonalizacion(tabName) {
    // Ocultar todos los paneles
    document.querySelectorAll('.config-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Desactivar todas las pestañas
    document.querySelectorAll('.config-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Activar panel y pestaña seleccionada
    document.getElementById(`panel-${tabName}`).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// Aplicar color individual
function aplicarColor(tipoColor) {
    const colorInput = document.getElementById(`color-${tipoColor}`);
    const textInput = document.getElementById(`color-${tipoColor}-text`);
    
    if (colorInput && textInput) {
        const color = colorInput.value;
        textInput.value = color;
        
        // Aplicar inmediatamente como preview
        aplicarColorEnVivo(tipoColor, color);
        
        mostrarNotificacion(`🎨 Color ${tipoColor} actualizado`, 'success');
    }
}

// Aplicar color en tiempo real
function aplicarColorEnVivo(tipoColor, color) {
    const root = document.documentElement;
    
    const mapeoColores = {
        'primary': '--color-primary',
        'secondary': '--color-secondary',
        'accent': '--color-accent',
        'text-light': '--color-text-light',
        'text-dark': '--color-text-dark'
    };
    
    if (mapeoColores[tipoColor]) {
        root.style.setProperty(mapeoColores[tipoColor], color);
    }
}

// Aplicar tipografía
function aplicarTipografia(tipoFuente) {
    const selectElement = document.getElementById(`font-${tipoFuente}`);
    if (!selectElement) return;
    
    const fuenteSeleccionada = selectElement.value;
    
    // Aplicar en preview
    const preview = document.getElementById('typography-preview');
    if (tipoFuente === 'primary') {
        preview.querySelector('.preview-primary').style.fontFamily = fuenteSeleccionada;
    } else if (tipoFuente === 'secondary') {
        preview.querySelector('.preview-secondary').style.fontFamily = fuenteSeleccionada;
    } else if (tipoFuente === 'accent') {
        preview.querySelector('.preview-accent').style.fontFamily = fuenteSeleccionada;
    }
    
    mostrarNotificacion(`📝 Tipografía ${tipoFuente} actualizada`, 'success');
}

// Vista previa de cambios
function previsualizarCambios() {
    // Abrir ventana de preview del chatbot
    const mesaParam = new URLSearchParams(window.location.search).get('mesa') || '1';
    const urlPreview = `/chatbot?mesa=${mesaParam}&preview=true`;
    
    window.open(urlPreview, 'preview', 'width=800,height=600,scrollbars=yes,resizable=yes');
    
    mostrarNotificacion('👁️ Abriendo vista previa...', 'info');
}

// Guardar tema personalizado
async function guardarTemaPersonalizado(categoria) {
    try {
        const propiedades = recopilarPropiedadesPersonalizacion(categoria);
        
        const datos = {
            nombre: temaPersonalizacionActual.nombre || `Tema Personalizado ${Date.now()}`,
            descripcion: `Tema personalizado - ${categoria}`,
            propiedades: propiedades
        };
        
        const response = await fetch('/api/chatbot/temas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        if (response.ok) {
            const resultado = await response.json();
            console.log('✅ Tema personalizado guardado:', resultado);
            
            // Recargar temas
            cargarTemasPredefinidos();
            
            mostrarNotificacion('💾 Tema personalizado guardado', 'success');
        } else {
            console.error('❌ Error guardando tema personalizado');
            mostrarNotificacion('❌ Error guardando tema', 'error');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarNotificacion('❌ Error de conexión', 'error');
    }
}

// Recopilar propiedades de personalización
function recopilarPropiedadesPersonalizacion(categoria) {
    const propiedades = {};
    
    if (categoria === 'colores') {
        propiedades.colores = {};
        const colores = ['primary', 'secondary', 'accent', 'text-light', 'text-dark'];
        colores.forEach(color => {
            const elemento = document.getElementById(`color-${color}`);
            if (elemento) {
                propiedades.colores[`--color-${color.replace('_', '-')}`] = elemento.value;
            }
        });
    } else if (categoria === 'tipografia') {
        propiedades.tipografia = {};
        const fuentes = ['primary', 'secondary', 'accent'];
        fuentes.forEach(fuente => {
            const elemento = document.getElementById(`font-${fuente}`);
            if (elemento) {
                propiedades.tipografia[`--font-${fuente}`] = elemento.value;
            }
        });
    }
    // Agregar más categorías según necesidad
    
    return propiedades;
}

// Crear nuevo tema desde personalización
async function crearTemaDesdePersonalizacion() {
    const nombre = prompt('Nombre del nuevo tema:', 'Mi Tema Personalizado');
    if (!nombre) return;
    
    try {
        const todasLasPropiedades = [
            ...recopilarPropiedadesPersonalizacion('colores'),
            ...recopilarPropiedadesPersonalizacion('tipografia'),
            ...recopilarPropiedadesPersonalizacion('botones'),
            ...recopilarPropiedadesPersonalizacion('efectos'),
            ...recopilarPropiedadesPersonalizacion('fondos')
        ];
        
        const datos = {
            nombre: nombre,
            descripcion: 'Tema creado desde personalización manual',
            propiedades: todasLasPropiedades
        };
        
        const response = await fetch('/api/chatbot/temas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        if (response.ok) {
            const resultado = await response.json();
            console.log('✅ Nuevo tema creado:', resultado);
            
            cargarTemasPredefinidos();
            mostrarNotificacion(`✨ Tema "${nombre}" creado exitosamente`, 'success');
        } else {
            console.error('❌ Error creando tema');
            mostrarNotificacion('❌ Error creando tema', 'error');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarNotificacion('❌ Error de conexión', 'error');
    }
}

// Resetear temas a valores por defecto
async function resetearTemas() {
    if (!confirm('¿Estás seguro de que quieres restaurar todos los temas por defecto? Esto eliminará todos los temas personalizados.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/chatbot/temas/resetear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            console.log('✅ Temas restaurados por defecto');
            cargarTemasPredefinidos();
            mostrarNotificacion('🔄 Temas restaurados por defecto', 'success');
        } else {
            console.error('❌ Error restaurando temas');
            mostrarNotificacion('❌ Error restaurando temas', 'error');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarNotificacion('❌ Error de conexión', 'error');
    }
}

// Función auxiliar para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion ${tipo}`;
    notificacion.innerHTML = mensaje;
    
    // Estilos básicos
    Object.assign(notificacion.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '8px',
        zIndex: '10000',
        fontFamily: 'Patrick Hand, cursive',
        fontWeight: 'bold',
        backgroundColor: tipo === 'success' ? '#28a745' : 
                         tipo === 'error' ? '#dc3545' : 
                         tipo === 'warning' ? '#ffc107' : '#17a2b8',
        color: tipo === 'warning' ? '#212529' : 'white',
        boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });
    
    document.body.appendChild(notificacion);
    
    // Animar entrada
    setTimeout(() => {
        notificacion.style.transform = 'translateX(0)';
    }, 100);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notificacion.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notificacion);
        }, 300);
    }, 3000);
}

/* ======================================================
   🌫️🎶 HUMAREDA MUSICAL DINÁMICA
   ====================================================== */
document.addEventListener("DOMContentLoaded", () => {
    const humareda = document.querySelector(".humareda");

    function crearParticula() {
        if (!humareda) return;

        const particula = document.createElement("div");
        particula.className = "particula";

        // Notas y colores posibles
        const notas = ["♪", "♫", "♬", "♩", "♭", "♯"];
        const colores = ["nota-amarilla", "nota-rosa", "nota-verde", "nota-morada", "nota-azul"];

        // Aleatorios
        const nota = notas[Math.floor(Math.random() * notas.length)];
        const color = colores[Math.floor(Math.random() * colores.length)];

        particula.textContent = nota;
        particula.classList.add(color);

        // Posición horizontal aleatoria
        const offsetX = (Math.random() * 60) - 30;
        particula.style.left = `${50 + offsetX}%`;

        // Tamaño y duración aleatorios
        const size = 30 + Math.random() * 30;
        particula.style.setProperty("--humo-size", `${size}px`);
        const duracion = 6 + Math.random() * 6;
        particula.style.animationDuration = `${duracion}s`;

        humareda.appendChild(particula);

        setTimeout(() => particula.remove(), duracion * 1000);
    }

    // Generar nuevas partículas periódicamente
    setInterval(crearParticula, 1200);
});
