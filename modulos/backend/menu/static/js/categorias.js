/**
 * SISTEMA DE GESTIÓN DE CATEGORÍAS - CONEXIÓN BD ↔ MODALES
 * Maneja CRUD completo para categorías y subcategorías
 */

// Prevenir declaraciones múltiples
if (!window.GestorCategorias) {

class GestorCategorias {
    constructor() {
        this.baseURL = '/menu-admin/api';
        this.categorias = [];
        this.subcategorias = [];
        this.categoriaActual = null;
        
        this.inicializar();
    }

    /**
     * Inicializar el sistema de categorías
     */
    async inicializar() {
        try {
            await this.cargarCategorias();
            this.configurarEventos();
            console.log('✅ GestorCategorias inicializado correctamente');
        } catch (error) {
            console.error('❌ Error inicializando GestorCategorias:', error);
        }
    }

    /**
     * CONEXIÓN BD - Cargar todas las categorías
     */
    async cargarCategorias() {
        try {
            const response = await fetch(`${this.baseURL}/categorias`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.categorias = data.categorias || data; // Maneja tanto {categorias: []} como [] directamente
            this.renderizarTablaCategorias();
            
            console.log(`✅ ${this.categorias.length} categorías cargadas desde BD`);
        } catch (error) {
            console.error('❌ Error cargando categorías:', error);
            this.mostrarNotificacion('Error al cargar categorías desde la base de datos', 'error');
        }
    }

    /**
     * MODAL - Abrir para nueva categoría
     */
    abrirModalNuevaCategoria() {
        this.categoriaActual = null;
        this.limpiarFormularioCategoria();
        
        document.getElementById('modal-categoria-titulo').textContent = 'Nueva Categoría';
        document.getElementById('categoria-id').value = '';
        
        // SIEMPRE mostrar pestaña subcategorías, incluso para nueva categoría
        console.log('🔧 DEBUG: Forzando mostrar pestaña subcategorías en nueva categoría');
        const tabContainer = document.getElementById('subcategorias-tab-container');
        if (tabContainer) {
            tabContainer.style.display = 'block';
            console.log('✅ Pestaña subcategorías mostrada forzadamente');
        }
        
        const modal = new bootstrap.Modal(document.getElementById('modal-categoria'));
        modal.show();
        
        setTimeout(() => {
            document.getElementById('categoria-titulo').focus();
        }, 500);
    }

    /**
     * MODAL - Abrir para editar categoría
     */
    async abrirModalEditarCategoria(categoriaId) {
        try {
            console.log('🔧 DEBUG abrirModalEditarCategoria:', categoriaId);
            
            const categoria = this.categorias.find(c => c.id == categoriaId);
            if (!categoria) {
                throw new Error('Categoría no encontrada');
            }
            
            this.categoriaActual = categoria;
            this.cargarDatosEnFormularioCategoria(categoria);
            
            document.getElementById('modal-categoria-titulo').textContent = 'Editar Categoría';
            
            console.log('🔧 DEBUG: Llamando configurarTabSubcategorias con:', categoria.id, categoria.nombre);
            // Configurar tab de subcategorías para categoría existente
            await this.configurarTabSubcategorias(categoria.id, categoria.nombre);
            
            const modal = new bootstrap.Modal(document.getElementById('modal-categoria'));
            modal.show();
            
        } catch (error) {
            console.error('❌ Error cargando categoría para editar:', error);
            this.mostrarNotificacion('Error al cargar datos de la categoría', 'error');
        }
    }

    /**
     * CONEXIÓN BD - Guardar categoría
     */
    async guardarCategoria() {
        const formData = new FormData(document.getElementById('form-categoria'));
        const categoriaId = document.getElementById('categoria-id').value;
        
        try {
            const url = categoriaId ? 
                `${this.baseURL}/categorias/${categoriaId}` : 
                `${this.baseURL}/categorias`;
                
            const method = categoriaId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modal-categoria'));
            modal.hide();
            
            // Recargar tabla
            await this.cargarCategorias();
            
            const accion = categoriaId ? 'actualizada' : 'creada';
            this.mostrarNotificacion(`Categoría ${accion} exitosamente`, 'success');
            
        } catch (error) {
            console.error('❌ Error guardando categoría:', error);
            this.mostrarNotificacion(`Error al guardar: ${error.message}`, 'error');
        }
    }

    /**
     * CONEXIÓN BD - Eliminar categoría
     */
    async eliminarCategoria(categoriaId, nombreCategoria) {
        const confirmar = confirm(`¿Está seguro de eliminar la categoría "${nombreCategoria}"?`);
        if (!confirmar) return;
        
        try {
            const response = await fetch(`${this.baseURL}/categorias/${categoriaId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            await this.cargarCategorias();
            this.mostrarNotificacion('Categoría eliminada exitosamente', 'success');
            
        } catch (error) {
            console.error('❌ Error eliminando categoría:', error);
            this.mostrarNotificacion(`Error al eliminar: ${error.message}`, 'error');
        }
    }

    /**
     * INTERFAZ - Renderizar tabla de categorías
     */
    renderizarTablaCategorias() {
        const tbody = document.getElementById('categorias-tbody');
        if (!tbody) {
            console.error('❌ No se encontró el elemento categorias-tbody');
            return;
        }
        
        if (this.categorias.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">
                        <i class="fas fa-info-circle"></i>
                        No hay categorías registradas. Haga clic en "Nueva Categoría" para agregar.
                    </td>
                </tr>
            `;
            return;
        }
        
        const categoriasHTML = this.categorias.map(categoria => `
            <tr>
                <td>${categoria.id}</td>
                <td>
                    ${categoria.icono || ''} ${categoria.titulo || categoria.nombre}
                </td>
                <td>
                    <small class="text-muted">${categoria.descripcion || 'Sin descripción'}</small>
                </td>
                <td class="text-center">${categoria.orden || '-'}</td>
                <td class="text-center">
                    <span class="badge ${categoria.activa ? 'bg-success' : 'bg-secondary'}">
                        ${categoria.activa ? 'Activa' : 'Inactiva'}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="gestorCategorias.abrirModalEditarCategoria(${categoria.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="gestorCategorias.eliminarCategoria(${categoria.id}, '${categoria.titulo || categoria.nombre}')" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
        
        tbody.innerHTML = categoriasHTML;
    }

    /**
     * EVENTOS - Configurar event listeners
     */
    configurarEventos() {
        // Botón nueva categoría
        document.getElementById('btn-nueva-categoria')?.addEventListener('click', () => {
            this.abrirModalNuevaCategoria();
        });
        
        // Formulario de categoría
        document.getElementById('form-categoria')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.guardarCategoria();
        });
        
        // Botón guardar en modal
        document.getElementById('btn-guardar-categoria')?.addEventListener('click', () => {
            this.guardarCategoria();
        });
        
        // 🎨 PREVISUALIZACIÓN AUTOMÁTICA DE ICONO
        document.getElementById('categoria-titulo')?.addEventListener('input', (e) => {
            this.previsualizarIcono(e.target.value);
        });
        
        // Botón sugerir icono
        document.getElementById('btn-sugerir-icono')?.addEventListener('click', () => {
            const nombre = document.getElementById('categoria-titulo').value;
            if (nombre.trim()) {
                this.previsualizarIcono(nombre);
            } else {

        // --- EVENT LISTENERS PARA SUBCATEGORÍAS ---
        
        // Botones para nueva subcategoría
        document.getElementById('btn-nueva-subcategoria-modal')?.addEventListener('click', () => {
            this.mostrarFormularioNuevaSubcategoria();
        });
        
        document.getElementById('btn-primera-subcategoria')?.addEventListener('click', () => {
            this.mostrarFormularioNuevaSubcategoria();
        });
        
        // Botones cancelar subcategoría
        document.getElementById('btn-cancelar-subcategoria')?.addEventListener('click', () => {
            this.cancelarFormularioSubcategoria();
        });
        
        document.getElementById('btn-cancelar-subcategoria-form')?.addEventListener('click', () => {
            this.cancelarFormularioSubcategoria();
        });
        
        // Formulario de subcategoría rápida
        document.getElementById('form-subcategoria-rapida')?.addEventListener('submit', (e) => {
            this.crearSubcategoriaRapida(e);
        });
        
        // Preview icono subcategoría en tiempo real
        document.getElementById('subcategoria-nombre-rapida')?.addEventListener('input', () => {
            this.actualizarPreviewIconoSubcategoria();
        });
                this.mostrarNotificacion('Escriba el nombre de la categoría primero', 'warning');
            }
        });
    }

    /**
     * 🎨 PREVISUALIZACIÓN AUTOMÁTICA DE ICONO
     * Muestra el icono que se asignará automáticamente
     */
    async previsualizarIcono(nombreCategoria) {
        if (!nombreCategoria || nombreCategoria.trim().length < 2) {
            this.limpiarPreviewIcono();
            return;
        }
        
        try {
            const response = await fetch(`/menu-admin/api/categorias/previsualizar-icono?nombre=${encodeURIComponent(nombreCategoria.trim())}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.mostrarPreviewIcono(data);
            
        } catch (error) {
            console.error('❌ Error previsualizando icono:', error);
            this.limpiarPreviewIcono();
        }
    }
    
    /**
     * 🖼️ MOSTRAR PREVIEW DEL ICONO
     */
    mostrarPreviewIcono(data) {
        // Crear o actualizar el preview
        let previewContainer = document.getElementById('preview-icono');
        
        if (!previewContainer) {
            // Crear contenedor de preview después del campo título
            const tituloInput = document.getElementById('categoria-titulo');
            previewContainer = document.createElement('div');
            previewContainer.id = 'preview-icono';
            previewContainer.className = 'mt-2 p-2 border rounded bg-light';
            tituloInput.parentNode.appendChild(previewContainer);
        }
        
        previewContainer.innerHTML = `
            <div class="d-flex align-items-center">
                <span style="font-size: 1.5rem; margin-right: 10px;">${data.icono_sugerido}</span>
                <div class="flex-grow-1">
                    <small class="text-muted d-block">Icono sugerido automáticamente:</small>
                    <strong>${data.preview}</strong>
                    <small class="text-muted d-block">Código: ${data.codigo_sugerido}</small>
                </div>
                <button type="button" class="btn btn-sm btn-success" onclick="gestorCategorias.aplicarIconoSugerido('${data.icono_sugerido}', '${data.codigo_sugerido}')">
                    <i class="fas fa-check"></i> Usar
                </button>
            </div>
        `;
        
        previewContainer.style.display = 'block';
    }
    
    /**
     * 🎯 APLICAR ICONO SUGERIDO
     */
    aplicarIconoSugerido(icono, codigo) {
        const iconoInput = document.getElementById('categoria-icono');
        const codigoInput = document.getElementById('categoria-codigo');
        
        if (iconoInput) {
            iconoInput.value = icono;
        }
        
        if (codigoInput) {
            codigoInput.value = codigo;
        }
        
        this.mostrarNotificacion(`✅ Icono ${icono} aplicado correctamente`, 'success');
    }
    
    /**
     * 🧹 LIMPIAR PREVIEW DEL ICONO
     */
    limpiarPreviewIcono() {
        const previewContainer = document.getElementById('preview-icono');
        if (previewContainer) {
            previewContainer.style.display = 'none';
        }
    }

    /**
     * UTILIDADES - Limpiar formulario
     */
    limpiarFormularioCategoria() {
        document.getElementById('form-categoria').reset();
        document.getElementById('categoria-activa').checked = true;
        this.limpiarPreviewIcono(); // 🧹 Limpiar preview del icono
    }

    /**
     * UTILIDADES - Cargar datos en formulario
     */
    cargarDatosEnFormularioCategoria(categoria) {
        document.getElementById('categoria-id').value = categoria.id || '';
        document.getElementById('categoria-titulo').value = categoria.titulo || categoria.nombre || '';
        document.getElementById('categoria-descripcion').value = categoria.descripcion || '';
        document.getElementById('categoria-icono').value = categoria.icono || '';
        document.getElementById('categoria-orden').value = categoria.orden || '';
        document.getElementById('categoria-activa').checked = categoria.activa !== false;
    }

    /**
     * 🏷️ CARGAR SUBCATEGORÍAS DE UNA CATEGORÍA ESPECÍFICA
     */
    async cargarSubcategorias(categoriaId) {
        try {
            const response = await fetch(`${this.baseURL}/subcategorias/categoria/${categoriaId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.subcategorias = data.subcategorias || [];
            
            console.log(`✅ ${this.subcategorias.length} subcategorías cargadas para categoría ${categoriaId}`);
            return this.subcategorias;
        } catch (error) {
            console.error('❌ Error cargando subcategorías:', error);
            return [];
        }
    }

    /**
     * 🎨 CONFIGURAR TAB DE SUBCATEGORÍAS CUANDO SE EDITA UNA CATEGORÍA
     */
    async configurarTabSubcategorias(categoriaId, categoriaNombre) {
        const tabContainer = document.getElementById('subcategorias-tab-container');
        const nombreCategoriaActual = document.getElementById('nombre-categoria-actual');
        const contadorSubcategorias = document.getElementById('contador-subcategorias');
        
        console.log('🔧 DEBUG configurarTabSubcategorias:', { categoriaId, categoriaNombre, tabContainer });
        
        if (categoriaId && tabContainer) {
            // Mostrar la pestaña de subcategorías
            tabContainer.style.display = 'block';
            console.log('✅ Pestaña subcategorías mostrada');
            
            // Actualizar nombre de categoría actual
            if (nombreCategoriaActual) {
                nombreCategoriaActual.textContent = categoriaNombre || 'esta categoría';
            }
            
            // Cargar subcategorías
            console.log('🔧 DEBUG: Cargando subcategorías...');
            const subcategorias = await this.cargarSubcategorias(categoriaId);
            console.log('🔧 DEBUG: Subcategorías cargadas:', subcategorias);
            
            // Actualizar contador
            if (contadorSubcategorias) {
                contadorSubcategorias.textContent = subcategorias.length;
                contadorSubcategorias.className = subcategorias.length > 0 ? 'badge bg-primary' : 'badge bg-secondary';
                console.log('🔧 DEBUG: Contador actualizado:', subcategorias.length);
            }
            
            // Renderizar lista
            this.renderizarSubcategoriasEnModal(subcategorias);
            console.log('🔧 DEBUG: Subcategorías renderizadas en modal');
            
        } else if (tabContainer) {
            // Ocultar la pestaña si es nueva categoría
            console.log('🔧 DEBUG: Ocultando pestaña (nueva categoría)');
            tabContainer.style.display = 'none';
        } else {
            console.log('🔧 DEBUG: No se encontró tabContainer');
        }
    }

    /**
     * 📋 RENDERIZAR SUBCATEGORÍAS EN EL MODAL
     */
    renderizarSubcategoriasEnModal(subcategorias) {
        const container = document.getElementById('lista-subcategorias-categoria');
        const mensajeSin = document.getElementById('sin-subcategorias-mensaje');
        
        if (!container) return;

        if (subcategorias.length === 0) {
            // Mostrar mensaje sin subcategorías
            if (mensajeSin) {
                mensajeSin.style.display = 'block';
            }
            container.innerHTML = '';
        } else {
            // Ocultar mensaje y mostrar lista
            if (mensajeSin) {
                mensajeSin.style.display = 'none';
            }
            
            container.innerHTML = subcategorias.map(sub => `
                <div class="card mb-2" data-subcategoria-id="${sub.id}">
                    <div class="card-body py-2">
                        <div class="row align-items-center">
                            <div class="col-1 text-center">
                                <span style="font-size: 1.5em;">${sub.icono || '🏷️'}</span>
                            </div>
                            <div class="col-6">
                                <strong>${sub.nombre}</strong>
                                <br><small class="text-muted">${sub.descripcion || 'Sin descripción'}</small>
                            </div>
                            <div class="col-2">
                                <span class="badge ${sub.activa ? 'bg-success' : 'bg-secondary'} badge-sm">
                                    ${sub.activa ? 'Activa' : 'Inactiva'}
                                </span>
                            </div>
                            <div class="col-3 text-end">
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary btn-sm" 
                                            onclick="gestorCategorias.editarSubcategoriaModal(${sub.id})" title="Editar">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-outline-danger btn-sm" 
                                            onclick="gestorCategorias.eliminarSubcategoriaModal(${sub.id}, '${sub.nombre}')" title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    /**
     * 🆕 MOSTRAR FORMULARIO PARA NUEVA SUBCATEGORÍA
     */
    mostrarFormularioNuevaSubcategoria() {
        const container = document.getElementById('form-nueva-subcategoria-container');
        const input = document.getElementById('subcategoria-nombre-rapida');
        
        if (container) {
            container.style.display = 'block';
            
            // Focus en el campo de nombre
            setTimeout(() => {
                if (input) input.focus();
            }, 100);
        }
    }

    /**
     * 🚫 CANCELAR FORMULARIO NUEVA SUBCATEGORÍA
     */
    cancelarFormularioSubcategoria() {
        const container = document.getElementById('form-nueva-subcategoria-container');
        const form = document.getElementById('form-subcategoria-rapida');
        
        if (container) {
            container.style.display = 'none';
        }
        
        if (form) {
            form.reset();
        }
        
        // Reset preview icono
        const preview = document.getElementById('preview-icono-subcategoria-rapida');
        if (preview) {
            preview.textContent = '🏷️';
        }
    }

    /**
     * 🎨 ACTUALIZAR PREVIEW ICONO SUBCATEGORÍA EN TIEMPO REAL
     */
    async actualizarPreviewIconoSubcategoria() {
        const input = document.getElementById('subcategoria-nombre-rapida');
        const preview = document.getElementById('preview-icono-subcategoria-rapida');
        
        if (!input || !preview || !input.value.trim()) {
            if (preview) preview.textContent = '🏷️';
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/subcategorias/previsualizar-icono?nombre=${encodeURIComponent(input.value.trim())}`);
            const data = await response.json();
            
            if (data.success && data.icono) {
                preview.textContent = data.icono;
            }
        } catch (error) {
            console.error('❌ Error obteniendo preview de icono:', error);
            preview.textContent = '🏷️';
        }
    }

    /**
     * 💾 CREAR NUEVA SUBCATEGORÍA
     */
    async crearSubcategoriaRapida(event) {
        event.preventDefault();
        
        const categoriaId = this.categoriaActual ? this.categoriaActual.id : null;
        if (!categoriaId) {
            this.mostrarNotificacion('Error: No se ha seleccionado una categoría', 'error');
            return;
        }

        const formData = {
            nombre: document.getElementById('subcategoria-nombre-rapida').value.trim(),
            descripcion: document.getElementById('subcategoria-descripcion-rapida').value.trim(),
            categoria_id: categoriaId,
            activa: true
        };

        if (!formData.nombre) {
            this.mostrarNotificacion('El nombre es obligatorio', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/subcategorias/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarNotificacion(`Subcategoría "${formData.nombre}" creada correctamente`, 'success');
                
                // Cancelar formulario y recargar subcategorías
                this.cancelarFormularioSubcategoria();
                await this.configurarTabSubcategorias(categoriaId, this.categoriaActual.nombre);
                
            } else {
                this.mostrarNotificacion(data.message || 'Error al crear subcategoría', 'error');
            }
        } catch (error) {
            console.error('❌ Error creando subcategoría:', error);
            this.mostrarNotificacion('Error de conexión al crear subcategoría', 'error');
        }
    }

    /**
     * ✏️ EDITAR SUBCATEGORÍA EN MODAL
     */
    editarSubcategoriaModal(subcategoriaId) {
        // Para simplicidad, mostrar alert por ahora
        // En el futuro se puede implementar un modal inline o expandir el formulario
        alert(`Función de edición de subcategoría ${subcategoriaId} será implementada próximamente`);
    }

    /**
     * 🗑️ ELIMINAR SUBCATEGORÍA EN MODAL
     */
    async eliminarSubcategoriaModal(subcategoriaId, nombre) {
        if (!confirm(`¿Estás seguro de que deseas eliminar la subcategoría "${nombre}"?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/subcategorias/${subcategoriaId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarNotificacion(`Subcategoría "${nombre}" eliminada correctamente`, 'success');
                
                // Recargar subcategorías
                const categoriaId = this.categoriaActual ? this.categoriaActual.id : null;
                if (categoriaId) {
                    await this.configurarTabSubcategorias(categoriaId, this.categoriaActual.nombre);
                }
                
            } else {
                this.mostrarNotificacion(data.message || 'Error al eliminar subcategoría', 'error');
            }
        } catch (error) {
            console.error('❌ Error eliminando subcategoría:', error);
            this.mostrarNotificacion('Error de conexión al eliminar subcategoría', 'error');
        }
    }

    /**
     * UTILIDADES - Mostrar notificación
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
    // Solo inicializar si estamos en la pestaña de categorías
    if (document.getElementById('categorias-tbody')) {
        console.log('🎯 Inicializando GestorCategorias...');
        window.gestorCategorias = new GestorCategorias();
    } else {
        console.log('⚠️ No se encontró el elemento categorias-tbody, no se inicializa GestorCategorias');
    }
});

// Exponer funciones globales
window.abrirModalNuevaCategoria = () => window.gestorCategorias?.abrirModalNuevaCategoria();
window.editarCategoria = (id) => window.gestorCategorias?.abrirModalEditarCategoria(id);
window.eliminarCategoria = (id, nombre) => window.gestorCategorias?.eliminarCategoria(id, nombre);

// Marcar como cargado
window.GestorCategorias = GestorCategorias;

} // Fin de la protección contra declaraciones múltiples
