/**
 * 🍳 JAVASCRIPT COCINA - SISTEMA ETERIALS
 * Funcionalidad especializada para chef y auxiliares de cocina
 */

// ==========================================
//           VARIABLES GLOBALES
// ==========================================
let recetasCargadas = [];
let recetasFiltradas = [];
let categorias = new Set();

// URLs de la API
const API_BASE = '/api/cocina';
const ENDPOINTS = {
    recetas: `${API_BASE}/recetas`,
    detalle: `${API_BASE}/receta`,
    buscar: `${API_BASE}/buscar`,
    estadisticas: `${API_BASE}/estadisticas`
};

// ==========================================
//         INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    inicializarCocina();
    configurarEventos();
    iniciarReloj();
});

/**
 * Inicializa el módulo de cocina
 */
async function inicializarCocina() {
    mostrarCarga(true);
    
    try {
        // Cargar estadísticas y recetas en paralelo
        await Promise.all([
            cargarEstadisticas(),
            cargarRecetas()
        ]);
        
        // Configurar filtros
        configurarFiltros();
        
    } catch (error) {
        console.error('Error al inicializar cocina:', error);
        mostrarError('Error al cargar el dashboard de cocina');
    } finally {
        mostrarCarga(false);
    }
}

/**
 * Configurar todos los event listeners
 */
function configurarEventos() {
    // Búsqueda
    const inputBusqueda = document.getElementById('busqueda-recetas');
    const btnBuscar = document.getElementById('btn-buscar');
    
    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', debounce(buscarRecetas, 500));
        inputBusqueda.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                buscarRecetas();
            }
        });
    }
    
    if (btnBuscar) {
        btnBuscar.addEventListener('click', buscarRecetas);
    }
    
    // Filtros
    const filtroCategoria = document.getElementById('filtro-categoria');
    const filtroDisponibilidad = document.getElementById('filtro-disponibilidad');
    
    if (filtroCategoria) {
        filtroCategoria.addEventListener('change', aplicarFiltros);
    }
    
    if (filtroDisponibilidad) {
        filtroDisponibilidad.addEventListener('change', aplicarFiltros);
    }
    
    // Botón actualizar
    const btnActualizar = document.getElementById('btn-actualizar');
    if (btnActualizar) {
        btnActualizar.addEventListener('click', function() {
            inicializarCocina();
        });
    }
    
    // Botón reintentar
    const btnRetry = document.getElementById('btn-retry');
    if (btnRetry) {
        btnRetry.addEventListener('click', function() {
            inicializarCocina();
        });
    }
}

// ==========================================
//         CARGA DE DATOS
// ==========================================

/**
 * Cargar estadísticas del dashboard
 */
async function cargarEstadisticas() {
    try {
        const response = await fetch(ENDPOINTS.estadisticas);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            actualizarEstadisticas(data.estadisticas);
        } else {
            throw new Error(data.error || 'Error al cargar estadísticas');
        }
        
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        // No mostrar error crítico, las estadísticas son informativas
    }
}

/**
 * Cargar todas las recetas
 */
async function cargarRecetas() {
    try {
        const response = await fetch(ENDPOINTS.recetas);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            recetasCargadas = data.recetas || [];
            recetasFiltradas = [...recetasCargadas];
            
            // Extraer categorías únicas
            recetasCargadas.forEach(receta => {
                if (receta.categoria) {
                    categorias.add(receta.categoria);
                }
            });
            
            renderizarRecetas();
            
        } else {
            throw new Error(data.error || 'Error al cargar recetas');
        }
        
    } catch (error) {
        console.error('Error al cargar recetas:', error);
        throw error; // Re-lanzar para manejo en inicializarCocina
    }
}

// ==========================================
//         RENDERIZADO
// ==========================================

/**
 * Actualizar estadísticas en el dashboard
 */
function actualizarEstadisticas(stats) {
    const elementos = {
        'total-recetas': stats.total_recetas || 0,
        'recetas-disponibles': stats.recetas_disponibles || 0,
        'total-ingredientes': stats.total_ingredientes || 0,
        'categorias-activas': stats.categorias_activas || 0
    };
    
    Object.entries(elementos).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            animarContador(elemento, valor);
        }
    });
}

/**
 * Renderizar lista de recetas
 */
function renderizarRecetas() {
    const container = document.getElementById('recipes-grid');
    const noResults = document.getElementById('no-results');
    
    if (!container) return;
    
    // Limpiar contenedor
    container.innerHTML = '';
    
    if (recetasFiltradas.length === 0) {
        container.style.display = 'none';
        if (noResults) noResults.style.display = 'block';
        return;
    }
    
    container.style.display = 'grid';
    if (noResults) noResults.style.display = 'none';
    
    // Crear cards de recetas
    recetasFiltradas.forEach(receta => {
        const card = crearCardReceta(receta);
        container.appendChild(card);
    });
}

/**
 * Crear card individual de receta
 */
function crearCardReceta(receta) {
    const card = document.createElement('div');
    card.className = 'recipe-card';
    card.setAttribute('data-receta-id', receta.id);
    
    // Imagen
    const imagenHtml = receta.imagen_url 
        ? `<img src="${receta.imagen_url}" alt="${receta.nombre}" loading="lazy">`
        : `<div class="recipe-placeholder">
             <i class="fas fa-utensils"></i>
             <span>Sin imagen</span>
           </div>`;
    
    // Metadatos
    const metadatos = [];
    if (receta.categoria) {
        metadatos.push(`<span class="metadata-tag">
            <i class="fas fa-tag"></i> ${receta.categoria}
        </span>`);
    }
    if (receta.tiempo_preparacion) {
        metadatos.push(`<span class="metadata-tag">
            <i class="fas fa-clock"></i> ${receta.tiempo_preparacion}
        </span>`);
    }
    
    // Estado disponibilidad
    const estadoClass = receta.disponible ? 'available' : 'unavailable';
    const estadoTexto = receta.disponible ? '✅ Disponible' : '❌ No Disponible';
    
    card.innerHTML = `
        <div class="recipe-image">
            ${imagenHtml}
        </div>
        <div class="recipe-content">
            <h3 class="recipe-name">${receta.nombre}</h3>
            <p class="recipe-description">${receta.descripcion || 'Sin descripción disponible'}</p>
            
            <div class="recipe-metadata">
                ${metadatos.join('')}
            </div>
            
            <div class="recipe-status">
                <span class="status-badge ${estadoClass}">${estadoTexto}</span>
                <span class="ingredients-count">
                    <i class="fas fa-leaf"></i>
                    ${receta.total_ingredientes} ingredientes
                </span>
            </div>
        </div>
    `;
    
    // Event listener para ir al detalle
    card.addEventListener('click', function() {
        abrirDetalleReceta(receta.id);
    });
    
    // Efecto hover mejorado
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
    
    return card;
}

/**
 * Configurar opciones de filtros
 */
function configurarFiltros() {
    const selectCategoria = document.getElementById('filtro-categoria');
    
    if (selectCategoria && categorias.size > 0) {
        // Limpiar opciones existentes (excepto "Todas")
        const opcionTodas = selectCategoria.querySelector('option[value=""]');
        selectCategoria.innerHTML = '';
        selectCategoria.appendChild(opcionTodas);
        
        // Agregar categorías
        Array.from(categorias).sort().forEach(categoria => {
            const option = document.createElement('option');
            option.value = categoria;
            option.textContent = categoria;
            selectCategoria.appendChild(option);
        });
    }
}

// ==========================================
//         BÚSQUEDA Y FILTROS
// ==========================================

/**
 * Buscar recetas por término
 */
async function buscarRecetas() {
    const input = document.getElementById('busqueda-recetas');
    if (!input) return;
    
    const termino = input.value.trim();
    
    if (!termino) {
        // Si no hay término, mostrar todas las recetas
        recetasFiltradas = [...recetasCargadas];
        aplicarFiltros();
        return;
    }
    
    try {
        mostrarCarga(true, 'Buscando recetas...');
        
        const response = await fetch(`${ENDPOINTS.buscar}?q=${encodeURIComponent(termino)}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            recetasFiltradas = data.recetas || [];
            aplicarFiltros();
        } else {
            throw new Error(data.error || 'Error en búsqueda');
        }
        
    } catch (error) {
        console.error('Error en búsqueda:', error);
        mostrarError('Error al buscar recetas');
    } finally {
        mostrarCarga(false);
    }
}

/**
 * Aplicar filtros a las recetas
 */
function aplicarFiltros() {
    const filtroCategoria = document.getElementById('filtro-categoria');
    const filtroDisponibilidad = document.getElementById('filtro-disponibilidad');
    
    let recetasTemp = [...recetasFiltradas];
    
    // Filtro por categoría
    if (filtroCategoria && filtroCategoria.value) {
        recetasTemp = recetasTemp.filter(receta => 
            receta.categoria === filtroCategoria.value
        );
    }
    
    // Filtro por disponibilidad
    if (filtroDisponibilidad && filtroDisponibilidad.value) {
        const disponible = filtroDisponibilidad.value === 'true';
        recetasTemp = recetasTemp.filter(receta => 
            receta.disponible === disponible
        );
    }
    
    // Actualizar lista filtrada y renderizar
    recetasFiltradas = recetasTemp;
    renderizarRecetas();
}

// ==========================================
//         NAVEGACIÓN
// ==========================================

/**
 * Abrir detalle de receta
 */
function abrirDetalleReceta(recetaId) {
    if (!recetaId) return;
    
    // Navegar a la página de detalle
    window.location.href = `/cocina/receta/${recetaId}`;
}

// ==========================================
//         UTILIDADES
// ==========================================

/**
 * Mostrar/ocultar indicador de carga
 */
function mostrarCarga(mostrar, mensaje = 'Cargando...') {
    const spinner = document.getElementById('loading-spinner');
    const modal = document.getElementById('modal-carga');
    
    if (spinner) {
        spinner.style.display = mostrar ? 'block' : 'none';
    }
    
    if (modal) {
        modal.style.display = mostrar ? 'flex' : 'none';
        if (mostrar && mensaje) {
            const textoModal = modal.querySelector('p');
            if (textoModal) textoModal.textContent = mensaje;
        }
    }
}

/**
 * Mostrar mensaje de error
 */
function mostrarError(mensaje) {
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    
    if (errorContainer && errorMessage) {
        errorMessage.textContent = mensaje;
        errorContainer.style.display = 'block';
    }
    
    // Ocultar otros elementos
    const recipesGrid = document.getElementById('recipes-grid');
    const noResults = document.getElementById('no-results');
    
    if (recipesGrid) recipesGrid.style.display = 'none';
    if (noResults) noResults.style.display = 'none';
}

/**
 * Animar contador numérico
 */
function animarContador(elemento, valorFinal) {
    const valorInicial = 0;
    const duracion = 1000; // 1 segundo
    const incremento = valorFinal / (duracion / 16); // 60 FPS
    let valorActual = valorInicial;
    
    const timer = setInterval(() => {
        valorActual += incremento;
        
        if (valorActual >= valorFinal) {
            elemento.textContent = valorFinal;
            clearInterval(timer);
        } else {
            elemento.textContent = Math.floor(valorActual);
        }
    }, 16);
}

/**
 * Debounce para búsqueda
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Reloj en tiempo real
 */
function iniciarReloj() {
    const reloj = document.getElementById('reloj-cocina');
    if (!reloj) return;
    
    function actualizarReloj() {
        const ahora = new Date();
        const hora = ahora.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        reloj.textContent = hora;
    }
    
    // Actualizar inmediatamente y luego cada segundo
    actualizarReloj();
    setInterval(actualizarReloj, 1000);
}

/**
 * Formatear tiempo de preparación
 */
function formatearTiempo(tiempo) {
    if (!tiempo) return 'No especificado';
    
    // Si ya tiene formato legible, devolverlo tal como está
    if (tiempo.includes('min') || tiempo.includes('hora')) {
        return tiempo;
    }
    
    // Si es solo un número, asumimos que son minutos
    const numero = parseInt(tiempo);
    if (!isNaN(numero)) {
        if (numero < 60) {
            return `${numero} min`;
        } else {
            const horas = Math.floor(numero / 60);
            const minutos = numero % 60;
            return minutos > 0 ? `${horas}h ${minutos}min` : `${horas}h`;
        }
    }
    
    return tiempo;
}

/**
 * Limpiar búsqueda y filtros
 */
function limpiarFiltros() {
    const inputBusqueda = document.getElementById('busqueda-recetas');
    const filtroCategoria = document.getElementById('filtro-categoria');
    const filtroDisponibilidad = document.getElementById('filtro-disponibilidad');
    
    if (inputBusqueda) inputBusqueda.value = '';
    if (filtroCategoria) filtroCategoria.value = '';
    if (filtroDisponibilidad) filtroDisponibilidad.value = '';
    
    recetasFiltradas = [...recetasCargadas];
    renderizarRecetas();
}

// ==========================================
//         EXPORT PARA TESTING
// ==========================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        inicializarCocina,
        cargarRecetas,
        buscarRecetas,
        aplicarFiltros,
        formatearTiempo
    };
}
