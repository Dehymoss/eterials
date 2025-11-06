/**
 * SISTEMA DE UPLOAD DE IMÁGENES - GESTIÓN DE ARCHIVOS
 * Maneja carga de imágenes y preview
 */

class SistemaUploadImagen {
    constructor() {
        this.baseURL = '/menu-admin';
        this.imagenActual = null;
        this.maxTamano = 20 * 1024 * 1024; // 20MB
        this.tiposPermitidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        
        this.inicializar();
    }

    /**
     * Inicializar el sistema de upload
     */
    inicializar() {
        this.configurarEventos();
        console.log('✅ SistemaUploadImagen inicializado correctamente');
    }

    /**
     * Configurar eventos del sistema
     */
    configurarEventos() {
        // Input de archivo
        const inputArchivo = document.getElementById('input-imagen-archivo');
        if (inputArchivo) {
            inputArchivo.addEventListener('change', (e) => {
                this.manejarSeleccionArchivo(e);
            });
        }

        // Botón para abrir selector
        const btnSeleccionar = document.getElementById('btn-seleccionar-imagen');
        if (btnSeleccionar) {
            btnSeleccionar.addEventListener('click', () => {
                this.abrirSelectorArchivos();
            });
        }

        // Área de arrastrar y soltar
        const dropZone = document.getElementById('upload-drop-zone');
        if (dropZone) {
            this.configurarDropZone(dropZone);
        }
    }

    /**
     * Abrir selector de archivos
     */
    abrirSelectorArchivos() {
        const input = document.getElementById('input-imagen-archivo');
        if (input) {
            input.click();
        }
    }

    /**
     * Manejar selección de archivo
     */
    async manejarSeleccionArchivo(evento) {
        const archivo = evento.target.files[0];
        if (!archivo) return;

        try {
            // Validar archivo
            this.validarArchivo(archivo);
            
            // Mostrar preview
            await this.mostrarPreview(archivo);
            
            // Subir archivo
            await this.subirArchivo(archivo);
            
        } catch (error) {
            console.error('❌ Error procesando archivo:', error);
            this.mostrarNotificacion(error.message, 'error');
        }
    }

    /**
     * Validar archivo seleccionado
     */
    validarArchivo(archivo) {
        // Validar tipo
        if (!this.tiposPermitidos.includes(archivo.type)) {
            throw new Error('Tipo de archivo no permitido. Use: JPG, PNG, GIF, WEBP');
        }

        // Validar tamaño
        if (archivo.size > this.maxTamano) {
            throw new Error(`Archivo muy grande. Máximo: ${this.maxTamano / 1024 / 1024}MB`);
        }

        return true;
    }

    /**
     * Mostrar preview de la imagen
     */
    async mostrarPreview(archivo) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const preview = document.getElementById('imagen-preview');
                if (preview) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    preview.classList.add('preview-activo');
                }
                
                // Ocultar placeholder
                const placeholder = document.getElementById('imagen-placeholder');
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
                
                resolve();
            };
            
            reader.onerror = () => reject(new Error('Error leyendo archivo'));
            reader.readAsDataURL(archivo);
        });
    }

    /**
     * Subir archivo al servidor
     */
    async subirArchivo(archivo) {
        const formData = new FormData();
        formData.append('imagen', archivo);

        // Mostrar indicador de carga
        this.mostrarCargando(true);

        try {
            const response = await fetch(`${this.baseURL}/api/imagenes/subir-imagen`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const resultado = await response.json();
            
            // Guardar URL de la imagen
            this.imagenActual = resultado.url;
            
            // Actualizar campo de URL si existe
            const campoUrl = document.getElementById('producto-imagen');
            if (campoUrl) {
                campoUrl.value = resultado.url;
            }

            this.mostrarNotificacion('Imagen subida exitosamente', 'success');
            
            return resultado;

        } catch (error) {
            console.error('❌ Error subiendo archivo:', error);
            this.mostrarNotificacion(`Error subiendo imagen: ${error.message}`, 'error');
            throw error;
        } finally {
            this.mostrarCargando(false);
        }
    }

    /**
     * Configurar zona de arrastrar y soltar
     */
    configurarDropZone(dropZone) {
        // Prevenir comportamiento por defecto
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Efectos visuales
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            });
        });

        // Manejar drop
        dropZone.addEventListener('drop', (e) => {
            const archivos = e.dataTransfer.files;
            if (archivos.length > 0) {
                this.procesarArchivosDrop(archivos[0]);
            }
        });
    }

    /**
     * Procesar archivos desde drag & drop
     */
    async procesarArchivosDrop(archivo) {
        try {
            this.validarArchivo(archivo);
            await this.mostrarPreview(archivo);
            await this.subirArchivo(archivo);
        } catch (error) {
            console.error('❌ Error procesando archivo drop:', error);
            this.mostrarNotificacion(error.message, 'error');
        }
    }

    /**
     * Mostrar/ocultar indicador de carga
     */
    mostrarCargando(mostrar) {
        const indicador = document.getElementById('upload-loading');
        const boton = document.getElementById('btn-seleccionar-imagen');
        
        if (indicador) {
            indicador.style.display = mostrar ? 'block' : 'none';
        }
        
        if (boton) {
            boton.disabled = mostrar;
            boton.innerHTML = mostrar ? 
                '<i class="fas fa-spinner fa-spin"></i> Subiendo...' : 
                '<i class="fas fa-upload"></i> Seleccionar Imagen';
        }
    }

    /**
     * Limpiar preview y datos
     */
    limpiarUpload() {
        this.imagenActual = null;
        
        const preview = document.getElementById('imagen-preview');
        const placeholder = document.getElementById('imagen-placeholder');
        const campoUrl = document.getElementById('producto-imagen');
        const input = document.getElementById('input-imagen-archivo');
        
        if (preview) {
            preview.src = '';
            preview.style.display = 'none';
            preview.classList.remove('preview-activo');
        }
        
        if (placeholder) {
            placeholder.style.display = 'block';
        }
        
        if (campoUrl) {
            campoUrl.value = '';
        }
        
        if (input) {
            input.value = '';
        }
    }

    /**
     * Obtener URL de imagen actual
     */
    obtenerUrlActual() {
        return this.imagenActual;
    }

    /**
     * Cargar imagen desde URL existente
     */
    async cargarImagenDesdeUrl(url) {
        if (!url) return;
        
        try {
            const preview = document.getElementById('imagen-preview');
            const placeholder = document.getElementById('imagen-placeholder');
            
            if (preview && placeholder) {
                preview.src = url;
                preview.style.display = 'block';
                preview.classList.add('preview-activo');
                placeholder.style.display = 'none';
                
                this.imagenActual = url;
            }
        } catch (error) {
            console.error('❌ Error cargando imagen desde URL:', error);
        }
    }

    /**
     * Mostrar notificación
     */
    mostrarNotificacion(mensaje, tipo = 'info') {
        if (window.notificaciones) {
            window.notificaciones.mostrar(mensaje, tipo);
        } else {
            console.log(`${tipo.toUpperCase()}: ${mensaje}`);
        }
    }
}

// Inicializar solo si no existe ya
if (!window.sistemaUploadImagen) {
    document.addEventListener('DOMContentLoaded', () => {
        window.sistemaUploadImagen = new SistemaUploadImagen();
    });
}

console.log('✅ SistemaUploadImagen cargado correctamente');
