/**
 * SISTEMA DE GESTIÓN DE RECETAS
 * Conecta el modal de recetas con el backend menu_admin_endpoints.py
 * Funciones: guardar_receta(), actualizar_receta(), eliminar_receta()
 */

// Prevenir declaraciones múltiples
if (!window.GestorRecetas) {

class GestorRecetas {
    constructor() {
        this.baseURL = '/menu-admin/api'; // Base URL del blueprint
        this.recetas = [];
        this.categorias = [];
        this.recetaActual = null;
        this.ingredientes = [];
        
        this.inicializar();
    }

    /**
     * Inicializar el sistema de recetas
     */
    async inicializar() {
        try {
            // Cargar datos iniciales
            await this.cargarCategorias();
            
            // Configurar eventos
            this.configurarEventos();
            
            console.log('✅ GestorRecetas inicializado correctamente');
        } catch (error) {
            console.error('❌ Error inicializando GestorRecetas:', error);
            this.mostrarNotificacion('Error al inicializar sistema de recetas', 'error');
        }
    }

    /**
     * MODAL - Abrir para nueva receta
     */
    abrirModalNuevaReceta() {
        console.log('📖 Abriendo modal nueva receta...');
        
        this.recetaActual = null;
        this.ingredientes = [];
        this.limpiarFormulario();
        
        document.getElementById('modal-receta-titulo').textContent = 'Nueva Receta';
        document.getElementById('receta-id').value = '';
        
        const modalElement = document.getElementById('modal-receta');
        if (!modalElement) {
            console.error('❌ No se encontró el modal con ID "modal-receta"');
            return;
        }
        
        try {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            console.log('✅ Modal de receta mostrado correctamente');
        } catch (error) {
            console.error('❌ Error abriendo modal:', error);
        }
        
        // Enfocar primer campo
        setTimeout(() => {
            document.getElementById('receta-nombre')?.focus();
        }, 500);
    }

    /**
     * CONEXIÓN A BD - Guardar receta (crear o actualizar)
     */
    async guardarReceta() {
        console.log('💾 Guardando receta...');
        
        const formData = this.recopilarDatosFormulario();
        const recetaId = document.getElementById('receta-id').value;
        
        try {
            // Usar el endpoint guardar_receta() que ya existe en menu_admin_endpoints.py
            const response = await fetch('/menu-admin/guardar-receta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const resultado = await response.json();
            console.log('✅ Receta guardada:', resultado);
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modal-receta'));
            modal.hide();
            
            // Notificar éxito
            const accion = recetaId ? 'actualizada' : 'creada';
            this.mostrarNotificacion(`Receta ${accion} exitosamente`, 'success');
            
            // Recargar lista de productos para mostrar la nueva receta
            if (window.gestorProductos) {
                await window.gestorProductos.cargarProductos();
            }
            
        } catch (error) {
            console.error('❌ Error guardando receta:', error);
            this.mostrarNotificacion(`Error al guardar: ${error.message}`, 'error');
        }
    }

    /**
     * UTILIDADES - Recopilar datos del formulario
     */
    recopilarDatosFormulario() {
        const formData = {
            // Información básica
            nombre: document.getElementById('receta-nombre').value.trim(),
            descripcion: document.getElementById('receta-descripcion').value.trim(),
            precio: parseFloat(document.getElementById('receta-precio').value) || 0,
            categoria_id: parseInt(document.getElementById('receta-categoria').value) || null,
            tiempo_preparacion: document.getElementById('receta-tiempo').value.trim(),
            imagen_url: document.getElementById('receta-imagen-url').value.trim(),
            
            // Preparación
            instrucciones_preparacion: document.getElementById('receta-instrucciones').value.trim(),
            notas_cocina: document.getElementById('receta-notas').value.trim(),
            
            // Estado
            disponible: document.getElementById('receta-disponible').checked,
            es_especial: document.getElementById('receta-especial').checked,
            
            // Ingredientes
            ingredientes: this.ingredientes,
            
            // Tipo de producto
            tipo_producto: 'preparado' // Las recetas siempre son productos preparados
        };
        
        console.log('📊 Datos del formulario recopilados:', formData);
        return formData;
    }

    /**
     * INGREDIENTES - Agregar ingrediente
     */
    agregarIngrediente() {
        const ingrediente = {
            id: Date.now(), // ID temporal para el frontend
            nombre: '',
            cantidad: '',
            unidad: '',
            notas: ''
        };
        
        this.ingredientes.push(ingrediente);
        this.renderizarIngredientes();
        
        // Enfocar el campo nombre del nuevo ingrediente
        setTimeout(() => {
            const nuevoInput = document.querySelector(`#ingrediente-${ingrediente.id}-nombre`);
            nuevoInput?.focus();
        }, 100);
    }

    /**
     * INGREDIENTES - Eliminar ingrediente
     */
    eliminarIngrediente(ingredienteId) {
        this.ingredientes = this.ingredientes.filter(ing => ing.id !== ingredienteId);
        this.renderizarIngredientes();
        this.mostrarNotificacion('Ingrediente eliminado', 'info');
    }

    /**
     * INGREDIENTES - Renderizar lista
     */
    renderizarIngredientes() {
        const container = document.getElementById('lista-ingredientes');
        const mensajeSin = document.getElementById('sin-ingredientes-mensaje');
        
        if (this.ingredientes.length === 0) {
            mensajeSin.style.display = 'block';
            container.innerHTML = mensajeSin.outerHTML;
            return;
        }
        
        const ingredientesHTML = this.ingredientes.map(ingrediente => `
            <div class="card mb-2" id="ingrediente-card-${ingrediente.id}">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-md-4">
                            <input type="text" class="form-control form-control-sm" 
                                   id="ingrediente-${ingrediente.id}-nombre"
                                   placeholder="Nombre del ingrediente" 
                                   value="${ingrediente.nombre}"
                                   onchange="gestorRecetas.actualizarIngrediente(${ingrediente.id}, 'nombre', this.value)">
                        </div>
                        <div class="col-md-2">
                            <input type="text" class="form-control form-control-sm" 
                                   id="ingrediente-${ingrediente.id}-cantidad"
                                   placeholder="Cantidad" 
                                   value="${ingrediente.cantidad}"
                                   onchange="gestorRecetas.actualizarIngrediente(${ingrediente.id}, 'cantidad', this.value)">
                        </div>
                        <div class="col-md-2">
                            <select class="form-select form-select-sm" 
                                    id="ingrediente-${ingrediente.id}-unidad"
                                    onchange="gestorRecetas.actualizarIngrediente(${ingrediente.id}, 'unidad', this.value)">
                                <option value="">Unidad</option>
                                <option value="kg" ${ingrediente.unidad === 'kg' ? 'selected' : ''}>Kg</option>
                                <option value="g" ${ingrediente.unidad === 'g' ? 'selected' : ''}>Gramos</option>
                                <option value="l" ${ingrediente.unidad === 'l' ? 'selected' : ''}>Litros</option>
                                <option value="ml" ${ingrediente.unidad === 'ml' ? 'selected' : ''}>ML</option>
                                <option value="ud" ${ingrediente.unidad === 'ud' ? 'selected' : ''}>Unidades</option>
                                <option value="taza" ${ingrediente.unidad === 'taza' ? 'selected' : ''}>Taza</option>
                                <option value="cdta" ${ingrediente.unidad === 'cdta' ? 'selected' : ''}>Cucharadita</option>
                                <option value="cda" ${ingrediente.unidad === 'cda' ? 'selected' : ''}>Cucharada</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <input type="text" class="form-control form-control-sm" 
                                   id="ingrediente-${ingrediente.id}-notas"
                                   placeholder="Notas opcionales" 
                                   value="${ingrediente.notas}"
                                   onchange="gestorRecetas.actualizarIngrediente(${ingrediente.id}, 'notas', this.value)">
                        </div>
                        <div class="col-md-1">
                            <button type="button" class="btn btn-outline-danger btn-sm" 
                                    onclick="gestorRecetas.eliminarIngrediente(${ingrediente.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = ingredientesHTML;
    }

    /**
     * INGREDIENTES - Actualizar ingrediente
     */
    actualizarIngrediente(ingredienteId, campo, valor) {
        const ingrediente = this.ingredientes.find(ing => ing.id === ingredienteId);
        if (ingrediente) {
            ingrediente[campo] = valor;
            console.log(`✅ Ingrediente ${ingredienteId} actualizado: ${campo} = ${valor}`);
        }
    }

    /**
     * UTILIDADES - Búsqueda de imágenes web para recetas
     */
    async buscarImagenesReceta() {
        console.log('🔍 Buscando imágenes para receta...');
        
        const nombreReceta = document.getElementById('receta-nombre').value.trim();
        if (!nombreReceta) {
            alert('Por favor, escribe el nombre de la receta primero');
            return;
        }
        
        try {
            const response = await fetch(`/menu-admin/api/imagenes/buscar/?nombre=${encodeURIComponent(nombreReceta)}&limite=6`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 Imágenes encontradas:', data);
            
            if (data.imagenes && data.imagenes.length > 0) {
                this.mostrarGaleriaImagenesReceta(data.imagenes);
            } else {
                alert(`No se encontraron imágenes para "${nombreReceta}"`);
            }
        } catch (error) {
            console.error('❌ Error buscando imágenes:', error);
            alert(`Error al buscar imágenes: ${error.message}`);
        }
    }

    /**
     * UTILIDADES - Mostrar galería de imágenes para receta
     */
    mostrarGaleriaImagenesReceta(imagenes) {
        // Reutilizar la lógica del gestor de productos pero para recetas
        const modalBody = document.querySelector('#modal-receta .modal-body');
        
        let galeriaContainer = document.getElementById('galeria-imagenes-receta');
        
        if (!galeriaContainer) {
            galeriaContainer = document.createElement('div');
            galeriaContainer.id = 'galeria-imagenes-receta';
            galeriaContainer.innerHTML = `
                <div class="mt-3 p-3 border rounded" style="max-height: 400px; overflow-y: auto;">
                    <h6><i class="fas fa-images"></i> Selecciona una imagen (${imagenes.length} encontradas):</h6>
                    <div id="galeria-grid-receta" class="row"></div>
                    <div class="text-center mt-3">
                        <button type="button" class="btn btn-sm btn-secondary" onclick="document.getElementById('galeria-imagenes-receta').style.display='none'">
                            <i class="fas fa-times"></i> Cerrar Galería
                        </button>
                    </div>
                </div>
            `;
            modalBody.appendChild(galeriaContainer);
        }
        
        const galeriaGrid = document.getElementById('galeria-grid-receta');
        galeriaGrid.innerHTML = '';
        
        imagenes.forEach((imagen, index) => {
            const imgUrl = imagen.url || imagen;
            const thumbnailUrl = imagen.thumbnail || imagen.url || imagen;
            const descripcion = imagen.descripcion || `Opción ${index + 1}`;
            
            const imgContainer = document.createElement('div');
            imgContainer.className = 'col-lg-2 col-md-3 col-sm-4 col-6 mb-2';
            imgContainer.innerHTML = `
                <div class="card imagen-seleccionable-receta" style="cursor: pointer;" data-url="${imgUrl}">
                    <img src="${thumbnailUrl}" class="card-img-top" style="height: 80px; object-fit: cover;" alt="${descripcion}">
                    <div class="card-body p-1">
                        <small class="text-muted">${descripcion}</small>
                    </div>
                </div>
            `;
            
            const card = imgContainer.querySelector('.imagen-seleccionable-receta');
            card.addEventListener('click', () => {
                this.seleccionarImagenReceta(imgUrl);
            });
            
            galeriaGrid.appendChild(imgContainer);
        });
        
        galeriaContainer.style.display = 'block';
    }

    /**
     * UTILIDADES - Seleccionar imagen para receta
     */
    seleccionarImagenReceta(url) {
        console.log('✅ Imagen seleccionada para receta:', url);
        
        // Asignar URL al campo
        const campoUrl = document.getElementById('receta-imagen-url');
        if (campoUrl) {
            campoUrl.value = url;
        }
        
        // Mostrar preview
        this.mostrarPreviewImagenReceta(url);
        
        // Notificación
        this.mostrarNotificacion('✅ Imagen seleccionada correctamente', 'success');
        
        // Ocultar galería
        setTimeout(() => {
            const galeria = document.getElementById('galeria-imagenes-receta');
            if (galeria) {
                galeria.style.display = 'none';
            }
        }, 1000);
    }

    /**
     * UTILIDADES - Mostrar preview de imagen de receta
     */
    mostrarPreviewImagenReceta(url) {
        const previewContainer = document.getElementById('preview-imagen-receta');
        const previewImg = document.getElementById('preview-img-receta');
        
        if (!previewContainer || !previewImg) return;
        
        if (!url || url.trim() === '') {
            previewContainer.style.display = 'none';
            return;
        }
        
        previewImg.src = url;
        previewContainer.style.display = 'block';
        
        previewImg.onload = () => console.log('✅ Preview de receta cargado');
        previewImg.onerror = () => previewContainer.style.display = 'none';
    }

    /**
     * CONEXIÓN A BD - Cargar categorías
     */
    async cargarCategorias() {
        try {
            const response = await fetch(`${this.baseURL}/categorias`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.categorias = data.categorias || data;
            this.poblarSelectCategorias();
            
            console.log(`✅ ${this.categorias.length} categorías cargadas para recetas`);
        } catch (error) {
            console.error('❌ Error cargando categorías:', error);
        }
    }

    /**
     * INTERFAZ - Poblar select de categorías
     */
    poblarSelectCategorias() {
        const select = document.getElementById('receta-categoria');
        if (!select) return;
        
        select.innerHTML = '<option value="">Seleccionar categoría...</option>';
        
        this.categorias.forEach(categoria => {
            const option = document.createElement('option');
            option.value = categoria.id;
            option.textContent = categoria.titulo || categoria.nombre;
            select.appendChild(option);
        });
    }

    /**
     * EVENTOS - Configurar todos los event listeners
     */
    configurarEventos() {
        // Botón nueva receta
        document.getElementById('btn-nueva-receta')?.addEventListener('click', () => {
            this.abrirModalNuevaReceta();
        });
        
        // Botón guardar receta
        document.getElementById('btn-guardar-receta')?.addEventListener('click', () => {
            this.guardarReceta();
        });
        
        // Botón agregar ingrediente
        document.getElementById('btn-agregar-ingrediente')?.addEventListener('click', () => {
            this.agregarIngrediente();
        });
        
        // Botón buscar imágenes para recetas
        document.getElementById('btn-buscar-imagenes-receta')?.addEventListener('click', () => {
            this.buscarImagenesReceta();
        });
        
        // Monitor de cambios en URL de imagen para preview
        document.getElementById('receta-imagen-url')?.addEventListener('input', (e) => {
            this.mostrarPreviewImagenReceta(e.target.value);
        });
        
        // Formulario de receta
        document.getElementById('form-receta')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.guardarReceta();
        });
    }

    /**
     * UTILIDADES - Limpiar formulario
     */
    limpiarFormulario() {
        document.getElementById('form-receta').reset();
        this.ingredientes = [];
        this.renderizarIngredientes();
        
        // Ocultar preview de imagen
        const previewContainer = document.getElementById('preview-imagen-receta');
        if (previewContainer) {
            previewContainer.style.display = 'none';
        }
    }

    /**
     * UTILIDADES - Sistema de notificaciones
     */
    mostrarNotificacion(mensaje, tipo = 'info') {
        if (window.notificaciones) {
            window.notificaciones.mostrar(mensaje, tipo);
        } else {
            console.log(`${tipo.toUpperCase()}: ${mensaje}`);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.gestorRecetas = new GestorRecetas();
});

// Exponer funciones globales
window.abrirModalNuevaReceta = () => window.gestorRecetas?.abrirModalNuevaReceta();

// Marcar como cargado
window.GestorRecetas = GestorRecetas;

} // Fin de la protección contra declaraciones múltiples
