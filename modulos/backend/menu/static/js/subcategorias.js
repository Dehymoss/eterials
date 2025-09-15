/**
 * 🏷️ GESTOR DE SUBCATEGORÍAS
 * Sistema para gestión de subcategorías con iconos automáticos
 * y relación con categorías padre
 */

// Protección anti-redeclaración
if (!window.GestorSubcategorias) {
    
    class GestorSubcategorias {
        constructor() {
            console.log('🏷️ Inicializando Gestor de Subcategorías...');
            this.configurarEventListeners();
            this.cargarCategorias();
            this.cargarSubcategorias();
        }

        /**
         * 🔗 CONFIGURAR EVENT LISTENERS
         */
        configurarEventListeners() {
            // Eventos del modal
            const btnGuardar = document.getElementById('btn-guardar-subcategoria');
            if (btnGuardar) {
                btnGuardar.addEventListener('click', () => this.guardarSubcategoria());
            }

            // Evento para sugerir icono automático
            const btnSugerirIcono = document.getElementById('btn-sugerir-icono-subcategoria');
            if (btnSugerirIcono) {
                btnSugerirIcono.addEventListener('click', () => this.sugerirIconoAutomatico());
            }

            // Evento para actualizar icono al escribir nombre
            const inputNombre = document.getElementById('subcategoria-nombre');
            if (inputNombre) {
                inputNombre.addEventListener('input', () => this.actualizarIconoEnTiempoReal());
                inputNombre.addEventListener('blur', () => this.actualizarCodigoEnTiempoReal());
            }

            // Evento para filtrar por categoría
            const filtroCategoria = document.getElementById('filtro-categoria-subcategorias');
            if (filtroCategoria) {
                filtroCategoria.addEventListener('change', () => this.filtrarSubcategorias());
            }
        }

        /**
         * 📂 CARGAR CATEGORÍAS PARA SELECTOR
         */
        async cargarCategorias() {
            try {
                const response = await fetch('/menu-admin/api/categorias/');
                const data = await response.json();
                
                const selectorCategoria = document.getElementById('subcategoria-categoria-id');
                const filtroCategoria = document.getElementById('filtro-categoria-subcategorias');
                
                if (data.categorias && selectorCategoria) {
                    selectorCategoria.innerHTML = '<option value="">Seleccionar categoría...</option>';
                    filtroCategoria.innerHTML = '<option value="">Todas las categorías</option>';
                    
                    data.categorias.forEach(categoria => {
                        const option = `<option value="${categoria.id}">${categoria.icono} ${categoria.nombre}</option>`;
                        selectorCategoria.innerHTML += option;
                        filtroCategoria.innerHTML += option;
                    });
                }
            } catch (error) {
                console.error('❌ Error cargando categorías:', error);
            }
        }

        /**
         * 📋 CARGAR SUBCATEGORÍAS
         */
        async cargarSubcategorias() {
            try {
                const response = await fetch('/menu-admin/api/subcategorias/');
                const data = await response.json();
                
                this.renderizarSubcategorias(data.subcategorias || []);
            } catch (error) {
                console.error('❌ Error cargando subcategorías:', error);
                this.renderizarSubcategorias([]);
            }
        }

        /**
         * 🖼️ RENDERIZAR TABLA DE SUBCATEGORÍAS
         */
        renderizarSubcategorias(subcategorias) {
            const tbody = document.getElementById('subcategorias-tbody');
            if (!tbody) return;

            if (subcategorias.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">
                            <i class="fas fa-layer-group fa-2x mb-2"></i><br>
                            No hay subcategorías registradas
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = subcategorias.map(subcategoria => `
                <tr>
                    <td><span class="badge bg-secondary">#${subcategoria.id}</span></td>
                    <td class="text-center">
                        <span class="icono-categoria">${subcategoria.icono || '🏷️'}</span>
                    </td>
                    <td><strong>${subcategoria.nombre}</strong></td>
                    <td>
                        <span class="badge bg-info">
                            ${subcategoria.categoria_nombre || 'Sin categoría'}
                        </span>
                    </td>
                    <td>${subcategoria.descripcion || '<em>Sin descripción</em>'}</td>
                    <td>
                        <span class="badge ${subcategoria.activa ? 'bg-success' : 'bg-danger'}">
                            ${subcategoria.activa ? 'Activa' : 'Inactiva'}
                        </span>
                    </td>
                    <td><span class="badge bg-primary">${subcategoria.productos_count || 0}</span></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-sm" onclick="editarSubcategoria(${subcategoria.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="eliminarSubcategoria(${subcategoria.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        /**
         * ➕ CREAR NUEVA SUBCATEGORÍA
         */
        crearSubcategoria() {
            // Limpiar formulario
            document.getElementById('form-subcategoria').reset();
            document.getElementById('subcategoria-id').value = '';
            document.getElementById('modalSubcategoriaLabel').textContent = '➕ Nueva Subcategoría';
            
            // Reset preview icono
            const preview = document.getElementById('preview-icono-subcategoria');
            if (preview) preview.textContent = '🏷️';
            
            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modal-subcategoria'));
            modal.show();
        }

        /**
         * 💾 GUARDAR SUBCATEGORÍA
         */
        async guardarSubcategoria() {
            const form = document.getElementById('form-subcategoria');
            const formData = new FormData(form);
            
            try {
                // Convertir FormData a objeto JSON
                const data = {};
                formData.forEach((value, key) => {
                    if (key === 'activa') {
                        data[key] = true; // Checkbox marcado
                    } else if (value) {
                        data[key] = value;
                    }
                });

                console.log('📝 Datos de subcategoría a enviar:', data);

                const subcategoriaId = document.getElementById('subcategoria-id').value;
                const url = subcategoriaId ? 
                    `/menu-admin/api/subcategorias/${subcategoriaId}` : 
                    '/menu-admin/api/subcategorias/';
                
                const method = subcategoriaId ? 'PUT' : 'POST';

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    // Mostrar notificación de éxito
                    mostrarNotificacion('✅ Subcategoría guardada exitosamente', 'success');
                    
                    // Cerrar modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modal-subcategoria'));
                    modal.hide();
                    
                    // Recargar tabla
                    this.cargarSubcategorias();
                } else {
                    mostrarNotificacion(`❌ Error: ${result.error}`, 'error');
                }
            } catch (error) {
                console.error('❌ Error guardando subcategoría:', error);
                mostrarNotificacion('❌ Error de conexión al guardar subcategoría', 'error');
            }
        }

        /**
         * 🎨 SUGERIR ICONO AUTOMÁTICO
         */
        async sugerirIconoAutomatico() {
            const nombre = document.getElementById('subcategoria-nombre').value.trim();
            if (!nombre) {
                mostrarNotificacion('⚠️ Ingrese el nombre de la subcategoría primero', 'warning');
                return;
            }

            try {
                const response = await fetch('/menu-admin/api/categorias/previsualizar-icono', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ nombre: nombre })
                });

                const data = await response.json();
                
                if (data.icono_sugerido) {
                    document.getElementById('subcategoria-icono').value = data.icono_sugerido;
                    this.actualizarPreviewIcono(data.icono_sugerido);
                    mostrarNotificacion(`🎨 Icono sugerido: ${data.icono_sugerido}`, 'success');
                } else {
                    mostrarNotificacion('🤖 No se pudo detectar un icono específico', 'info');
                }
            } catch (error) {
                console.error('❌ Error sugiriendo icono:', error);
            }
        }

        /**
         * ⚡ ACTUALIZAR ICONO EN TIEMPO REAL
         */
        async actualizarIconoEnTiempoReal() {
            const nombre = document.getElementById('subcategoria-nombre').value.trim();
            if (!nombre) return;

            // Llamada para obtener sugerencia de icono
            try {
                const response = await fetch('/menu-admin/api/categorias/previsualizar-icono', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ nombre: nombre })
                });

                const data = await response.json();
                
                if (data.icono_sugerido) {
                    document.getElementById('subcategoria-icono').value = data.icono_sugerido;
                    this.actualizarPreviewIcono(data.icono_sugerido);
                }
            } catch (error) {
                console.log('Sin sugerencia de icono disponible');
            }
        }

        /**
         * 📝 ACTUALIZAR CÓDIGO EN TIEMPO REAL
         */
        actualizarCodigoEnTiempoReal() {
            const nombre = document.getElementById('subcategoria-nombre').value.trim();
            if (!nombre) return;

            // Generar código basado en el nombre (similar al de categorías)
            const codigo = nombre.toUpperCase()
                .replace(/[ÁÀÄÂ]/g, 'A')
                .replace(/[ÉÈËÊ]/g, 'E')
                .replace(/[ÍÌÏÎ]/g, 'I')
                .replace(/[ÓÒÖÔ]/g, 'O')
                .replace(/[ÚÙÜÛ]/g, 'U')
                .replace(/Ñ/g, 'N')
                .replace(/[^A-Z0-9]/g, '')
                .substring(0, 4);

            document.getElementById('subcategoria-codigo').value = codigo;
        }

        /**
         * 🔄 ACTUALIZAR PREVIEW DE ICONO
         */
        actualizarPreviewIcono(icono) {
            const preview = document.getElementById('preview-icono-subcategoria');
            if (preview && icono) {
                preview.textContent = icono;
                preview.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    preview.style.transform = 'scale(1)';
                }, 200);
            }
        }

        /**
         * 🔍 FILTRAR SUBCATEGORÍAS POR CATEGORÍA
         */
        async filtrarSubcategorias() {
            const categoriaId = document.getElementById('filtro-categoria-subcategorias').value;
            
            try {
                const url = categoriaId ? 
                    `/menu-admin/api/subcategorias/categoria/${categoriaId}` : 
                    '/menu-admin/api/subcategorias/';
                    
                const response = await fetch(url);
                const data = await response.json();
                
                this.renderizarSubcategorias(data.subcategorias || []);
            } catch (error) {
                console.error('❌ Error filtrando subcategorías:', error);
            }
        }
    }

    // Crear instancia global
    window.GestorSubcategorias = GestorSubcategorias;
    
    // Funciones globales para llamadas desde HTML
    window.crearSubcategoria = function() {
        if (window.gestorSubcategorias) {
            window.gestorSubcategorias.crearSubcategoria();
        }
    };
    
    window.editarSubcategoria = function(id) {
        console.log(`✏️ Editar subcategoría ${id}`);
        // TODO: Implementar edición
    };
    
    window.eliminarSubcategoria = function(id) {
        console.log(`🗑️ Eliminar subcategoría ${id}`);
        // TODO: Implementar eliminación
    };

    // Inicializar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        window.gestorSubcategorias = new GestorSubcategorias();
    });
}
