/**
 * SISTEMA PRINCIPAL DE PRODUCTOS - CONEXIÓN BD ↔ MODALES
 * Maneja toda la lógica de CRUD para productos
 * Conecta interfaz con endpoints de menu_admin_endpoints.py
 */

// Prevenir declaraciones múltiples
if (!window.GestorProductos) {

class GestorProductos {
    constructor() {
        this.baseURL = '/menu-admin/api'; // Base URL corregida para el blueprint modular
        this.productos = [];
        this.categorias = [];
        this.subcategorias = [];
        this.productoActual = null;
        
        this.inicializar();
    }

    /**
     * Inicializar el sistema completo
     */
    async inicializar() {
        try {
            // Cargar datos iniciales
            await this.cargarCategorias();
            await this.cargarProductos();
            
            // Configurar eventos
            this.configurarEventos();
            
            console.log('✅ GestorProductos inicializado correctamente');
        } catch (error) {
            console.error('❌ Error inicializando GestorProductos:', error);
            this.mostrarNotificacion('Error al inicializar el sistema', 'error');
        }
    }

    /**
     * CONEXIÓN A BASE DE DATOS - Cargar productos
     */
    async cargarProductos() {
        try {
            const response = await fetch(`${this.baseURL}/productos/`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.productos = data.productos || data; // Maneja tanto {productos: []} como [] directamente
            this.renderizarProductos();
            this.actualizarEstadisticas();
            
            console.log(`✅ ${this.productos.length} productos cargados desde BD`);
        } catch (error) {
            console.error('❌ Error cargando productos:', error);
            this.mostrarNotificacion('Error al cargar productos desde la base de datos', 'error');
            
            // Mostrar estado offline
            const contenedorProductos = document.getElementById('productos-container');
            if (contenedorProductos) {
                contenedorProductos.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-warning">
                            <i class="fas fa-database"></i>
                            <strong>Conexión de Base de Datos</strong><br>
                            No se pudieron cargar los productos. Verifique que el servidor esté corriendo.
                            <br><small>Error: ${error.message}</small>
                        </div>
                    </div>
                `;
            }
        }
    }

    /**
     * CONEXIÓN A BASE DE DATOS - Cargar categorías
     */
    async cargarCategorias() {
        try {
            const response = await fetch(`${this.baseURL}/categorias/`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.categorias = data.categorias || data; // Maneja tanto {categorias: []} como [] directamente
            this.poblarSelectCategorias();
            
            console.log(`✅ ${this.categorias.length} categorías cargadas desde BD`);
        } catch (error) {
            console.error('❌ Error cargando categorías:', error);
            this.mostrarNotificacion('Error al cargar categorías', 'warning');
        }
    }

    /**
     * CONEXIÓN A BASE DE DATOS - Cargar subcategorías por categoría
     */
    async cargarSubcategorias(categoriaId) {
        if (!categoriaId) {
            this.subcategorias = [];
            this.poblarSelectSubcategorias();
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/subcategorias/categoria/${categoriaId}/`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.subcategorias = await response.json();
            this.poblarSelectSubcategorias();
            
            console.log(`✅ ${this.subcategorias.length} subcategorías cargadas para categoría ${categoriaId}`);
        } catch (error) {
            console.error('❌ Error cargando subcategorías:', error);
            this.subcategorias = [];
            this.poblarSelectSubcategorias();
        }
    }

    /**
     * MODAL - Abrir para nuevo producto
     */
    abrirModalNuevoProducto() {
        console.log('🎯 Intentando abrir modal nuevo producto...');
        
        this.productoActual = null;
        this.limpiarFormulario();
        
        document.getElementById('modal-titulo').textContent = 'Nuevo Producto';
        document.getElementById('producto-id').value = '';
        
        const modalElement = document.getElementById('modal-producto');
        console.log('🔍 Modal element encontrado:', !!modalElement);
        
        if (!modalElement) {
            console.error('❌ No se encontró el modal con ID "modal-producto"');
            return;
        }
        
        try {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            console.log('✅ Modal mostrado correctamente');
        } catch (error) {
            console.error('❌ Error abriendo modal:', error);
        }
        
        // Enfocar primer campo
        setTimeout(() => {
            document.getElementById('producto-nombre')?.focus();
        }, 500);
    }

    /**
     * MODAL - Abrir para editar producto existente
     */
    async abrirModalEditarProducto(productoId) {
        console.log('🔄 Cargando producto para editar, ID:', productoId);
        
        try {
            // La URL correcta es /menu-admin/api/productos/<id> según el blueprint modular
            const response = await fetch(`${this.baseURL}/productos/${productoId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 Datos del producto recibidos:', data);
            
            // El endpoint devuelve {success: true, producto: {...}}
            this.productoActual = data.producto || data;
            this.cargarDatosEnFormulario(this.productoActual);
            
            document.getElementById('modal-titulo').textContent = 'Editar Producto';
            document.getElementById('producto-id').value = productoId;
            
            const modal = new bootstrap.Modal(document.getElementById('modal-producto'));
            modal.show();
            
            console.log('✅ Modal de edición abierto correctamente');
            
        } catch (error) {
            console.error('❌ Error cargando producto para editar:', error);
            this.mostrarNotificacion('Error al cargar datos del producto', 'error');
        }
    }

    /**
     * CONEXIÓN A BASE DE DATOS - Guardar producto (crear o actualizar)
     */
    async guardarProducto() {
        const formData = new FormData(document.getElementById('form-producto'));
        const productoId = document.getElementById('producto-id').value;
        
        try {
            const url = productoId ? 
                `${this.baseURL}/productos/${productoId}/` : 
                `${this.baseURL}/productos/`;
                
            const method = productoId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            const producto = await response.json();
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modal-producto'));
            modal.hide();
            
            // Recargar lista
            await this.cargarProductos();
            
            // Notificar éxito
            const accion = productoId ? 'actualizado' : 'creado';
            this.mostrarNotificacion(`Producto ${accion} exitosamente`, 'success');
            
        } catch (error) {
            console.error('❌ Error guardando producto:', error);
            this.mostrarNotificacion(`Error al guardar: ${error.message}`, 'error');
        }
    }

    /**
     * CONEXIÓN A BASE DE DATOS - Eliminar producto
     */
    async eliminarProducto(productoId, nombreProducto) {
        const confirmar = confirm(`¿Está seguro de eliminar "${nombreProducto}"?`);
        if (!confirmar) return;
        
        try {
            const response = await fetch(`${this.baseURL}/productos/${productoId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            
            // Recargar lista
            await this.cargarProductos();
            
            this.mostrarNotificacion('Producto eliminado exitosamente', 'success');
            
        } catch (error) {
            console.error('❌ Error eliminando producto:', error);
            this.mostrarNotificacion(`Error al eliminar: ${error.message}`, 'error');
        }
    }

    /**
     * INTERFAZ - Renderizar lista de productos
     */
    renderizarProductos() {
        const contenedor = document.getElementById('productos-container');
        if (!contenedor) return;
        
        if (this.productos.length === 0) {
            contenedor.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <i class="fas fa-info-circle"></i>
                        <strong>No hay productos registrados</strong><br>
                        Haga clic en "Nuevo Producto" para agregar el primer producto.
                    </div>
                </div>
            `;
            return;
        }
        
        const productosHTML = this.productos.map(producto => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card producto-card h-100">
                    ${producto.imagen_url ? `
                        <img src="${producto.imagen_url}" class="card-img-top producto-imagen" alt="${producto.nombre}">
                    ` : `
                        <div class="card-img-top producto-imagen-placeholder">
                            <i class="fas fa-image"></i>
                        </div>
                    `}
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title producto-nombre">${producto.nombre}</h5>
                        <p class="card-text producto-descripcion flex-grow-1">${producto.descripcion || 'Sin descripción'}</p>
                        <div class="producto-info">
                            <div class="producto-precio">$${parseFloat(producto.precio || 0).toLocaleString()}</div>
                            <div class="producto-categoria">${producto.categoria_nombre || 'Sin categoría'}</div>
                        </div>
                        <div class="producto-acciones mt-3">
                            <button class="btn btn-sm btn-primary" onclick="gestorProductos.abrirModalEditarProducto(${producto.id})">
                                <i class="fas fa-edit"></i> Editar
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="gestorProductos.eliminarProducto(${producto.id}, '${producto.nombre}')">
                                <i class="fas fa-trash"></i> Eliminar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        contenedor.innerHTML = productosHTML;
    }

    /**
     * INTERFAZ - Poblar select de categorías
     */
    poblarSelectCategorias() {
        const select = document.getElementById('producto-categoria');
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
     * INTERFAZ - Poblar select de subcategorías
     */
    poblarSelectSubcategorias() {
        const select = document.getElementById('producto-subcategoria');
        if (!select) return;
        
        select.innerHTML = '<option value="">Seleccionar subcategoría...</option>';
        
        this.subcategorias.forEach(subcategoria => {
            const option = document.createElement('option');
            option.value = subcategoria.id;
            option.textContent = subcategoria.nombre;
            select.appendChild(option);
        });
    }

    /**
     * EVENTOS - Configurar todos los event listeners
     */
    configurarEventos() {
        // Botón nuevo producto
        const btnNuevoProducto = document.getElementById('btn-nuevo-producto');
        console.log('🔍 Botón nuevo producto encontrado:', !!btnNuevoProducto);
        
        btnNuevoProducto?.addEventListener('click', () => {
            console.log('🖱️ Click en botón nuevo producto detectado');
            this.abrirModalNuevoProducto();
        });
        
        // Formulario de producto
        document.getElementById('form-producto')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.guardarProducto();
        });
        
        // Cambio de categoría
        document.getElementById('producto-categoria')?.addEventListener('change', (e) => {
            this.cargarSubcategorias(e.target.value);
        });
        
        // Monitor de cambios en URL de imagen para preview
        document.getElementById('producto-imagen-url')?.addEventListener('input', (e) => {
            this.mostrarPreviewImagen(e.target.value);
        });
        
        // Botón guardar en modal
        document.getElementById('btn-guardar-producto')?.addEventListener('click', () => {
            this.guardarProducto();
        });
        
        // Botón buscar imágenes web
        document.getElementById('btn-buscar-imagenes')?.addEventListener('click', () => {
            this.buscarImagenesWeb();
        });
    }

    /**
     * UTILIDADES - Limpiar formulario
     */
    limpiarFormulario() {
        document.getElementById('form-producto').reset();
        document.getElementById('producto-subcategoria').innerHTML = '<option value="">Seleccionar subcategoría...</option>';
    }

    /**
     * UTILIDADES - Cargar datos en formulario para edición
     */
    cargarDatosEnFormulario(producto) {
        console.log('📝 Poblando formulario con producto:', producto);
        
        // Validar existencia de elementos antes de asignar valores
        const campos = [
            {id: 'producto-id', valor: producto.id || ''},
            {id: 'producto-nombre', valor: producto.nombre || ''},
            {id: 'producto-descripcion', valor: producto.descripcion || ''},
            {id: 'producto-precio', valor: producto.precio || ''},
            {id: 'producto-categoria', valor: producto.categoria_id || ''},
            {id: 'producto-imagen-url', valor: producto.imagen_url || ''}
        ];
        
        campos.forEach(campo => {
            const elemento = document.getElementById(campo.id);
            if (elemento) {
                elemento.value = campo.valor;
                console.log(`✅ ${campo.id} asignado:`, campo.valor);
            } else {
                console.error(`❌ Elemento no encontrado: ${campo.id}`);
            }
        });
        
        // Mostrar preview de imagen si existe URL
        if (producto.imagen_url) {
            this.mostrarPreviewImagen(producto.imagen_url);
        }
        
        // Cargar subcategorías si hay categoría seleccionada
        if (producto.categoria_id) {
            this.cargarSubcategorias(producto.categoria_id).then(() => {
                const subcategoriaElement = document.getElementById('producto-subcategoria');
                if (subcategoriaElement) {
                    subcategoriaElement.value = producto.subcategoria_id || '';
                    console.log('✅ producto-subcategoria asignado:', producto.subcategoria_id);
                } else {
                    console.error('❌ Elemento no encontrado: producto-subcategoria');
                }
            });
        }
    }

    /**
     * UTILIDADES - Buscar imágenes en web
     */
    async buscarImagenesWeb() {
        console.log('🔍 Buscando imágenes en web...');
        
        const nombreProducto = document.getElementById('producto-nombre').value.trim();
        if (!nombreProducto) {
            alert('Por favor, escribe el nombre del producto primero');
            return;
        }
        
        try {
            // NUEVA URL DE LA API LIBRE DE BÚSQUEDA DE IMÁGENES
            const response = await fetch(`/menu-admin/api/imagenes/buscar?nombre=${encodeURIComponent(nombreProducto)}&limite=6`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 Respuesta de búsqueda:', data);
            
            if (data.imagenes && data.imagenes.length > 0) {
                this.mostrarGaleriaImagenes(data.imagenes);
            } else {
                alert(`No se encontraron imágenes para "${nombreProducto}". Mensaje: ${data.mensaje || 'Sin mensaje'}`);
            }
        } catch (error) {
            console.error('❌ Error buscando imágenes:', error);
            alert(`Error al buscar imágenes: ${error.message}`);
        }
    }

    /**
     * UTILIDADES - Mostrar galería de imágenes
     */
    mostrarGaleriaImagenes(imagenes) {
        console.log('🖼️ Mostrando galería con:', imagenes.length, 'imágenes');
        console.log('📊 Datos de imágenes recibidas:', imagenes);
        
        // Crear contenedor de galería
        const modalBody = document.querySelector('#modal-producto .modal-body');
        console.log('📍 Modal body encontrado:', !!modalBody);
        
        let galeriaContainer = document.getElementById('galeria-imagenes');
        
        if (!galeriaContainer) {
            galeriaContainer = document.createElement('div');
            galeriaContainer.id = 'galeria-imagenes';
            galeriaContainer.innerHTML = `
                <div class="mt-3 p-3 border rounded" style="max-height: 400px; overflow-y: auto;">
                    <h6><i class="fas fa-images"></i> Selecciona una imagen (${imagenes.length} encontradas):</h6>
                    <div id="galeria-grid" class="row"></div>
                    <div class="text-center mt-3">
                        <button type="button" class="btn btn-sm btn-secondary" onclick="document.getElementById('galeria-imagenes').style.display='none'">
                            <i class="fas fa-times"></i> Cerrar Galería
                        </button>
                    </div>
                </div>
            `;
            modalBody.appendChild(galeriaContainer);
        } else {
            // Actualizar contador de imágenes
            const titulo = galeriaContainer.querySelector('h6');
            titulo.innerHTML = `<i class="fas fa-images"></i> Selecciona una imagen (${imagenes.length} encontradas):`;
        }
        
        // Limpiar galería anterior
        const galeriaGrid = document.getElementById('galeria-grid');
        console.log('📍 Galería grid encontrada:', !!galeriaGrid);
        galeriaGrid.innerHTML = '';
        
        // Crear miniaturas con formato mejorado
        console.log('🔄 Procesando', imagenes.length, 'imágenes...');
        imagenes.forEach((imagen, index) => {
            console.log(`📷 Procesando imagen ${index + 1}:`, imagen);
            // La API ahora retorna objetos con {url, thumbnail, descripcion, fuente}
            const imgUrl = imagen.url || imagen; // Fallback para compatibilidad
            const thumbnailUrl = imagen.thumbnail || imagen.url || imagen;
            const descripcion = imagen.descripcion || `Opción ${index + 1}`;
            const fuente = imagen.fuente || 'web';
            
            const imgContainer = document.createElement('div');
            imgContainer.className = 'col-lg-2 col-md-3 col-sm-4 col-6 mb-2';
            imgContainer.innerHTML = `
                <div class="card imagen-seleccionable" style="cursor: pointer;" data-url="${imgUrl}">
                    <img src="${thumbnailUrl}" class="card-img-top" style="height: 80px; object-fit: cover;" 
                         alt="${descripcion}" onerror="console.error('❌ Error cargando imagen:', this.src); this.parentElement.innerHTML='<div class=text-danger>Error cargando imagen</div>';">
                    <div class="card-body p-1">
                        <small class="text-muted">${fuente}</small>
                    </div>
                </div>
            `;
            
            // Agregar event listener para la selección
            const card = imgContainer.querySelector('.imagen-seleccionable');
            card.addEventListener('click', () => {
                this.seleccionarImagen(imgUrl);
            });
            
            console.log(`✅ Imagen ${index + 1} agregada al grid:`, {imgUrl, thumbnailUrl, descripcion, fuente});
            galeriaGrid.appendChild(imgContainer);
        });
        
        // Mostrar galería
        galeriaContainer.style.display = 'block';
    }
    
    /**
     * UTILIDADES - Seleccionar imagen de la galería
     */
    seleccionarImagen(url) {
        console.log('✅ Imagen seleccionada:', url);
        
        // Feedback visual: marcar imagen seleccionada
        document.querySelectorAll('.imagen-seleccionable').forEach(card => {
            card.classList.remove('border-success', 'border-3');
        });
        
        const imagenSeleccionada = document.querySelector(`[data-url="${url}"]`);
        if (imagenSeleccionada) {
            imagenSeleccionada.classList.add('border-success', 'border-3');
        }
        
        // Asignar URL al campo
        const campoUrl = document.getElementById('producto-imagen-url');
        if (campoUrl) {
            campoUrl.value = url;
            console.log('✅ URL asignada al campo');
        }
        
        // Mostrar preview
        this.mostrarPreviewImagen(url);
        
        // Notificación
        this.mostrarNotificacion('✅ Imagen seleccionada correctamente', 'success');
        
        // Ocultar galería después de 1 segundo
        setTimeout(() => {
            const galeria = document.getElementById('galeria-imagenes');
            if (galeria) {
                galeria.style.display = 'none';
            }
        }, 1000);
    }

    /**
     * UTILIDADES - Mostrar notificación
     */
    mostrarNotificacion(mensaje, tipo = 'info') {
        // Crear notificación temporal
        const notificacion = document.createElement('div');
        notificacion.className = `alert alert-${tipo === 'success' ? 'success' : 'info'} position-fixed`;
        notificacion.style.cssText = 'top: 20px; right: 20px; z-index: 10000; max-width: 300px;';
        notificacion.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notificacion);
        
        // Auto-remover después de 3 segundos
        setTimeout(() => {
            if (notificacion.parentElement) {
                notificacion.remove();
            }
        }, 3000);
    }

    /**
     * UTILIDADES - Mostrar preview de imagen
     */
    mostrarPreviewImagen(url) {
        console.log('🖼️ Intentando mostrar preview de:', url);
        
        const previewContainer = document.getElementById('preview-imagen');
        const previewImg = document.getElementById('preview-img');
        
        if (!previewContainer || !previewImg) {
            console.error('❌ Elementos de preview no encontrados');
            return;
        }
        
        if (!url || url.trim() === '') {
            previewContainer.style.display = 'none';
            console.log('🚫 URL vacía, ocultando preview');
            return;
        }
        
        console.log('✅ Mostrando preview de imagen');
        previewImg.src = url;
        previewContainer.style.display = 'block';
        
        // Manejar errores de carga de imagen
        previewImg.onload = () => {
            console.log('✅ Imagen cargada correctamente');
        };
        
        previewImg.onerror = () => {
            console.log('❌ Error cargando imagen, ocultando preview');
            previewContainer.style.display = 'none';
        };
    }

    /**
     * UTILIDADES - Actualizar estadísticas del dashboard
     */
    actualizarEstadisticas() {
        const totalProductos = this.productos.length;
        const productosActivos = this.productos.filter(p => p.disponible).length;
        const categorias = [...new Set(this.productos.map(p => p.categoria_id))].length;
        
        // Actualizar solo si los elementos existen
        const elementoTotal = document.getElementById('stat-productos-total');
        const elementoActivos = document.getElementById('stat-productos-activos');
        const elementoCategorias = document.getElementById('stat-categorias');
        
        if (elementoTotal) elementoTotal.textContent = totalProductos;
        if (elementoActivos) elementoActivos.textContent = productosActivos;
        if (elementoCategorias) elementoCategorias.textContent = this.categorias.length;
        
        console.log(`📊 Estadísticas: ${totalProductos} productos, ${productosActivos} activos, ${this.categorias.length} categorías`);
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
    window.gestorProductos = new GestorProductos();
});

// Exponer funciones globales para uso en HTML
window.abrirModalNuevoProducto = () => window.gestorProductos?.abrirModalNuevoProducto();
window.editarProducto = (id) => window.gestorProductos?.abrirModalEditarProducto(id);
window.eliminarProducto = (id, nombre) => window.gestorProductos?.eliminarProducto(id, nombre);

// Marcar como cargado
window.GestorProductos = GestorProductos;

} // Fin de la protección contra declaraciones múltiples
