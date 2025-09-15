/**
 * SISTEMA DE CARGA MASIVA - IMPORTACIÓN EXCEL
 * Maneja importación masiva de productos desde archivos Excel
 */

class SistemaCargaMasiva {
    constructor() {
        this.baseURL = '/menu-admin';
        this.archivoActual = null;
        this.datosImportacion = [];
        this.resultadosImportacion = [];
        
        this.inicializar();
    }

    /**
     * Inicializar sistema de carga masiva
     */
    inicializar() {
        this.configurarEventos();
        console.log('✅ SistemaCargaMasiva inicializado correctamente');
    }

    /**
     * Configurar eventos
     */
    configurarEventos() {
        // Input de archivo Excel
        const inputExcel = document.getElementById('input-excel-archivo');
        if (inputExcel) {
            inputExcel.addEventListener('change', (e) => {
                this.manejarSeleccionExcel(e);
            });
        }

        // Botón seleccionar Excel
        const btnSeleccionar = document.getElementById('btn-seleccionar-excel');
        if (btnSeleccionar) {
            btnSeleccionar.addEventListener('click', () => {
                this.abrirSelectorExcel();
            });
        }

        // Botón procesar importación
        const btnProcesar = document.getElementById('btn-procesar-importacion');
        if (btnProcesar) {
            btnProcesar.addEventListener('click', () => {
                this.procesarImportacion();
            });
        }

        // Botón descargar plantilla
        const btnPlantilla = document.getElementById('btn-descargar-plantilla');
        if (btnPlantilla) {
            btnPlantilla.addEventListener('click', () => {
                this.descargarPlantilla();
            });
        }
    }

    /**
     * Abrir selector de archivos Excel
     */
    abrirSelectorExcel() {
        const input = document.getElementById('input-excel-archivo');
        if (input) {
            input.click();
        }
    }

    /**
     * Manejar selección de archivo Excel
     */
    async manejarSeleccionExcel(evento) {
        const archivo = evento.target.files[0];
        if (!archivo) return;

        try {
            this.validarArchivoExcel(archivo);
            this.archivoActual = archivo;
            
            // Mostrar información del archivo
            this.mostrarInfoArchivo(archivo);
            
            // Procesar archivo para preview
            await this.procesarArchivoExcel(archivo);
            
        } catch (error) {
            console.error('❌ Error procesando archivo Excel:', error);
            this.mostrarNotificacion(error.message, 'error');
        }
    }

    /**
     * Validar archivo Excel
     */
    validarArchivoExcel(archivo) {
        const tiposExcel = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            '.xlsx',
            '.xls'
        ];

        const esExcel = tiposExcel.some(tipo => 
            archivo.type === tipo || archivo.name.toLowerCase().endsWith(tipo)
        );

        if (!esExcel) {
            throw new Error('Archivo debe ser Excel (.xlsx o .xls)');
        }

        const maxTamano = 10 * 1024 * 1024; // 10MB
        if (archivo.size > maxTamano) {
            throw new Error('Archivo Excel muy grande (máximo 10MB)');
        }

        return true;
    }

    /**
     * Mostrar información del archivo seleccionado
     */
    mostrarInfoArchivo(archivo) {
        const info = document.getElementById('info-archivo-excel');
        if (!info) return;

        const tamanoMB = (archivo.size / 1024 / 1024).toFixed(2);
        
        info.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-file-excel"></i>
                <strong>Archivo seleccionado:</strong> ${archivo.name}<br>
                <small>Tamaño: ${tamanoMB} MB | Última modificación: ${new Date(archivo.lastModified).toLocaleDateString()}</small>
            </div>
        `;
        info.style.display = 'block';
    }

    /**
     * Procesar archivo Excel para preview
     */
    async procesarArchivoExcel(archivo) {
        this.mostrarCargando(true, 'Procesando archivo Excel...');

        try {
            // Leer archivo usando FileReader
            const datosArchivo = await this.leerArchivo(archivo);
            
            // Simular procesamiento (en implementación real usaríamos SheetJS)
            await this.simularProcesamiento();
            
            // Mostrar preview de datos
            this.mostrarPreviewDatos();
            
        } catch (error) {
            console.error('❌ Error procesando Excel:', error);
            this.mostrarNotificacion(`Error procesando archivo: ${error.message}`, 'error');
        } finally {
            this.mostrarCargando(false);
        }
    }

    /**
     * Leer archivo como ArrayBuffer
     */
    leerArchivo(archivo) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = () => reject(new Error('Error leyendo archivo'));
            
            reader.readAsArrayBuffer(archivo);
        });
    }

    /**
     * Simular procesamiento de datos Excel
     */
    async simularProcesamiento() {
        // Simular datos de ejemplo para demo
        this.datosImportacion = [
            {
                nombre: 'Pizza Margherita',
                descripcion: 'Pizza clásica con tomate y mozzarella',
                precio: 15000,
                categoria: 'Pizza',
                disponible: true,
                estado: 'válido'
            },
            {
                nombre: 'Hamburguesa BBQ',
                descripcion: 'Hamburguesa con salsa BBQ',
                precio: 18000,
                categoria: 'Hamburguesas',
                disponible: true,
                estado: 'válido'
            },
            {
                nombre: 'Producto Incompleto',
                descripcion: '',
                precio: null,
                categoria: '',
                disponible: true,
                estado: 'error - precio requerido'
            }
        ];

        // Simular tiempo de procesamiento
        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    /**
     * Mostrar preview de datos procesados
     */
    mostrarPreviewDatos() {
        const container = document.getElementById('preview-datos-importacion');
        if (!container) return;

        const validosCount = this.datosImportacion.filter(item => item.estado === 'válido').length;
        const erroresCount = this.datosImportacion.length - validosCount;

        const tabla = `
            <div class="alert ${erroresCount > 0 ? 'alert-warning' : 'alert-success'}">
                <h6><i class="fas fa-chart-bar"></i> Resumen de importación:</h6>
                <div class="row">
                    <div class="col-md-4">
                        <strong>Total productos:</strong> ${this.datosImportacion.length}
                    </div>
                    <div class="col-md-4 text-success">
                        <strong>Válidos:</strong> ${validosCount}
                    </div>
                    <div class="col-md-4 ${erroresCount > 0 ? 'text-danger' : 'text-muted'}">
                        <strong>Con errores:</strong> ${erroresCount}
                    </div>
                </div>
            </div>

            <div class="table-responsive">
                <table class="table table-sm table-bordered">
                    <thead class="table-dark">
                        <tr>
                            <th>Estado</th>
                            <th>Nombre</th>
                            <th>Descripción</th>
                            <th>Precio</th>
                            <th>Categoría</th>
                            <th>Observaciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.datosImportacion.map(item => `
                            <tr class="${item.estado === 'válido' ? 'table-success' : 'table-danger'}">
                                <td>
                                    <i class="fas ${item.estado === 'válido' ? 'fa-check text-success' : 'fa-times text-danger'}"></i>
                                </td>
                                <td>${item.nombre || '-'}</td>
                                <td>
                                    <small>${item.descripcion ? item.descripcion.substring(0, 50) + '...' : '-'}</small>
                                </td>
                                <td>${item.precio ? '$' + item.precio.toLocaleString() : '-'}</td>
                                <td>${item.categoria || '-'}</td>
                                <td>
                                    <small class="${item.estado === 'válido' ? 'text-success' : 'text-danger'}">
                                        ${item.estado}
                                    </small>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <div class="mt-3">
                <button id="btn-procesar-importacion" class="btn btn-success" ${erroresCount > 0 ? 'disabled' : ''}>
                    <i class="fas fa-upload"></i> 
                    Importar ${validosCount} productos válidos
                </button>
                <button class="btn btn-secondary ms-2" onclick="sistemaCargaMasiva.cancelarImportacion()">
                    <i class="fas fa-times"></i> Cancelar
                </button>
            </div>
        `;

        container.innerHTML = tabla;
        container.style.display = 'block';

        // Reconfigurar evento del botón procesar
        const btnProcesar = document.getElementById('btn-procesar-importacion');
        if (btnProcesar && !btnProcesar.disabled) {
            btnProcesar.onclick = () => this.procesarImportacion();
        }
    }

    /**
     * Procesar importación masiva
     */
    async procesarImportacion() {
        const productosValidos = this.datosImportacion.filter(item => item.estado === 'válido');
        
        if (productosValidos.length === 0) {
            this.mostrarNotificacion('No hay productos válidos para importar', 'warning');
            return;
        }

        this.mostrarCargando(true, `Importando ${productosValidos.length} productos...`);

        try {
            const resultados = [];
            
            // Procesar productos uno por uno
            for (let i = 0; i < productosValidos.length; i++) {
                const producto = productosValidos[i];
                
                try {
                    const resultado = await this.crearProducto(producto);
                    resultados.push({
                        ...producto,
                        importado: true,
                        id: resultado.id
                    });
                    
                    // Actualizar progreso
                    this.actualizarProgreso(i + 1, productosValidos.length);
                    
                } catch (error) {
                    console.error('❌ Error importando producto:', producto.nombre, error);
                    resultados.push({
                        ...producto,
                        importado: false,
                        error: error.message
                    });
                }
            }

            this.resultadosImportacion = resultados;
            this.mostrarResultadosImportacion(resultados);
            
            // Notificar éxito
            const exitosos = resultados.filter(r => r.importado).length;
            this.mostrarNotificacion(`${exitosos} productos importados exitosamente`, 'success');

        } catch (error) {
            console.error('❌ Error en importación masiva:', error);
            this.mostrarNotificacion(`Error en importación: ${error.message}`, 'error');
        } finally {
            this.mostrarCargando(false);
        }
    }

    /**
     * Crear producto individual
     */
    async crearProducto(datosProducto) {
        const formData = new FormData();
        formData.append('nombre', datosProducto.nombre);
        formData.append('descripcion', datosProducto.descripcion);
        formData.append('precio', datosProducto.precio);
        formData.append('categoria', datosProducto.categoria);
        formData.append('disponible', datosProducto.disponible ? 'on' : '');

        const response = await fetch(`${this.baseURL}/api/productos`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Actualizar progreso de importación
     */
    actualizarProgreso(actual, total) {
        const progreso = document.getElementById('progreso-importacion');
        if (progreso) {
            const porcentaje = Math.round((actual / total) * 100);
            progreso.innerHTML = `
                <div class="progress mb-2">
                    <div class="progress-bar" style="width: ${porcentaje}%" 
                         aria-valuenow="${porcentaje}" aria-valuemin="0" aria-valuemax="100">
                        ${porcentaje}%
                    </div>
                </div>
                <small>Procesando ${actual} de ${total} productos...</small>
            `;
        }
    }

    /**
     * Mostrar resultados finales
     */
    mostrarResultadosImportacion(resultados) {
        const container = document.getElementById('resultados-importacion');
        if (!container) return;

        const exitosos = resultados.filter(r => r.importado).length;
        const fallidos = resultados.length - exitosos;

        container.innerHTML = `
            <div class="alert alert-info">
                <h5><i class="fas fa-check-circle"></i> Importación completada</h5>
                <div class="row">
                    <div class="col-md-6 text-success">
                        <strong>Exitosos:</strong> ${exitosos}
                    </div>
                    <div class="col-md-6 text-danger">
                        <strong>Fallidos:</strong> ${fallidos}
                    </div>
                </div>
            </div>
            
            <button class="btn btn-primary" onclick="window.location.reload()">
                <i class="fas fa-sync"></i> Ver productos importados
            </button>
        `;

        container.style.display = 'block';
    }

    /**
     * Descargar plantilla Excel
     */
    async descargarPlantilla() {
        try {
            this.mostrarCargando(true, 'Generando plantilla...');
            
            const response = await fetch(`${this.baseURL}/api/plantilla-excel`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = 'plantilla_productos.xlsx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            window.URL.revokeObjectURL(url);
            
            this.mostrarNotificacion('Plantilla descargada exitosamente', 'success');
            
        } catch (error) {
            console.error('❌ Error descargando plantilla:', error);
            this.mostrarNotificacion('Error descargando plantilla', 'error');
        } finally {
            this.mostrarCargando(false);
        }
    }

    /**
     * Cancelar importación
     */
    cancelarImportacion() {
        this.limpiarImportacion();
        this.mostrarNotificacion('Importación cancelada', 'info');
    }

    /**
     * Limpiar datos de importación
     */
    limpiarImportacion() {
        this.archivoActual = null;
        this.datosImportacion = [];
        this.resultadosImportacion = [];
        
        const elementos = [
            'info-archivo-excel',
            'preview-datos-importacion', 
            'resultados-importacion',
            'progreso-importacion'
        ];
        
        elementos.forEach(id => {
            const elemento = document.getElementById(id);
            if (elemento) {
                elemento.style.display = 'none';
                elemento.innerHTML = '';
            }
        });
        
        const input = document.getElementById('input-excel-archivo');
        if (input) {
            input.value = '';
        }
    }

    /**
     * Mostrar/ocultar indicador de carga
     */
    mostrarCargando(mostrar, mensaje = 'Procesando...') {
        const indicador = document.getElementById('carga-masiva-loading');
        if (indicador) {
            if (mostrar) {
                indicador.innerHTML = `
                    <div class="text-center p-3">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <div class="mt-2">${mensaje}</div>
                    </div>
                `;
                indicador.style.display = 'block';
            } else {
                indicador.style.display = 'none';
            }
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
if (!window.sistemaCargaMasiva) {
    document.addEventListener('DOMContentLoaded', () => {
        window.sistemaCargaMasiva = new SistemaCargaMasiva();
    });
}

console.log('✅ SistemaCargaMasiva cargado correctamente');
