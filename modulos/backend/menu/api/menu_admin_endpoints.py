# --- IMPORTS ESENCIALES ---
from flask import Blueprint, request, jsonify, render_template, send_from_directory, send_file, Response
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria
from modulos.backend.menu.database.models.ingrediente import Ingrediente
from modulos.backend.menu.excel.excel_manager import ExcelProductManager
from modulos.backend.menu.excel.plantillas_excel import generar_plantilla_basica, generar_plantilla_avanzada, generar_plantilla_ingredientes
from datetime import datetime

# --- FUNCIONES HELPER PARA SERIALIZACIÓN ---
def producto_to_dict(producto):
    """Convierte un objeto Producto a diccionario para JSON"""
    
    # Función helper para acceso seguro a relaciones
    def safe_get_relation_attr(obj, attr, default=None):
        try:
            if obj:
                return getattr(obj, attr, default)
            return default
        except:
            return default
    
    producto_dict = {
        'id': producto.id,
        'codigo': producto.codigo,
        'nombre': producto.nombre,
        'precio': float(producto.precio) if producto.precio else 0.0,
        'descripcion': producto.descripcion,
        'imagen_url': producto.imagen_url,
        'categoria_id': producto.categoria_id,
        'categoria_nombre': safe_get_relation_attr(producto.categoria, 'titulo'),
        'subcategoria_id': producto.subcategoria_id,
        'subcategoria_nombre': safe_get_relation_attr(producto.subcategoria, 'nombre'),
        'disponible': producto.disponible,
        'tiempo_preparacion': producto.tiempo_preparacion,
        'popularidad': producto.popularidad
    }
    
    # Obtener ingredientes asociados
    try:
        ingredientes = producto.ingredientes if producto.ingredientes else []
        producto_dict['ingredientes'] = [ingrediente.nombre for ingrediente in ingredientes]
    except:
        producto_dict['ingredientes'] = []
    
    return producto_dict

# --- FUNCIONES HELPER PARA SERIALIZACIÓN (Solo las que NO están en productos_endpoints) ---
# NOTA: producto_to_dict() se eliminó - ahora está en productos_endpoints.py

def categoria_to_dict(categoria):
    """Convierte un objeto Categoria a diccionario para JSON"""
    return {
        'id': categoria.id,
        'codigo': getattr(categoria, 'codigo', ''),
        'nombre': categoria.titulo,  # Usar titulo directamente del modelo
        'descripcion': getattr(categoria, 'descripcion', None),
        'activa': getattr(categoria, 'activa', True),
        'icono': getattr(categoria, 'icono', ''),
        'orden': getattr(categoria, 'orden', 0)
    }

def subcategoria_to_dict(subcategoria):
    """Convierte un objeto Subcategoria a diccionario para JSON"""
    return {
        'id': subcategoria.id,
        'codigo': getattr(subcategoria, 'codigo', ''),
        'nombre': subcategoria.nombre,
        'descripcion': getattr(subcategoria, 'descripcion', ''),
        'categoria_id': subcategoria.categoria_id,
        'tipo': getattr(subcategoria, 'tipo', ''),
        'activa': getattr(subcategoria, 'activa', True)
    }

def ingrediente_to_dict(ingrediente):
    """Convierte un objeto Ingrediente a diccionario para JSON"""
    return {
        'id': ingrediente.id,
        'codigo': getattr(ingrediente, 'codigo', ''),
        'producto_id': ingrediente.producto_id,
        'nombre': ingrediente.nombre,
        'cantidad': ingrediente.cantidad,
        'unidad': ingrediente.unidad,
        'costo': float(getattr(ingrediente, 'costo', 0.0)),
        'obligatorio': getattr(ingrediente, 'obligatorio', True),
        'activo': getattr(ingrediente, 'activo', True)
    }

# Crear engine y sessionmaker localmente para evitar importación circular
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
menu_admin_bp = Blueprint('menu_admin', __name__, 
                         template_folder='../templates',
                         static_folder='../static',
                         # Dejar static_url_path en '/static' para que, al registrar
                         # el blueprint con url_prefix='/menu-admin', las rutas
                         # queden en '/menu-admin/static/...'. Antes estaba
                         # causando '/menu-admin/menu-admin/static/...'.
                         static_url_path='/static')
excel_manager = ExcelProductManager()
Session = sessionmaker(bind=engine)

# 🔗 IMPORT DE BLUEPRINTS MODULARES DESHABILITADO TEMPORALMENTE
# from modulos.backend.menu.endpoints.productos_endpoints import productos_bp
# menu_admin_bp.register_blueprint(productos_bp, url_prefix='/productos')
# RAZÓN: Los endpoints modulares requieren verificación de imports

# Ruta para mostrar la interfaz de administración
@menu_admin_bp.route('/')
def admin_interface():
    """Mostrar la interfaz de administración del menú"""
    return render_template('admin_productos.html')

# Ruta principal - Usar admin_productos.html (arquitectura limpia)
@menu_admin_bp.route('/admin')
def admin_productos():
    """Administrador de productos con arquitectura modular"""
    return render_template('admin_productos.html')

# Ruta de prueba temporal
@menu_admin_bp.route('/test')
def admin_test():
    """Template de prueba sin CSS personalizado"""
    return render_template('admin_test_simple.html')

# Ruta específica para servir imágenes subidas
@menu_admin_bp.route('/static/uploads/productos/<filename>')
def servir_imagen_producto(filename):
    """Servir imágenes de productos subidas"""
    try:
        uploads_path = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'productos')
        return send_from_directory(uploads_path, filename)
    except Exception as e:
        print(f"Error sirviendo imagen {filename}: {e}")
        return "Imagen no encontrada", 404

# --- SUGERENCIA DE IMÁGENES USANDO GOOGLE SEARCH ---
@menu_admin_bp.route('/productos/sugerir-imagenes', methods=['GET'])
def sugerir_imagenes():
    """Busca imágenes usando base de datos curada específica por producto"""
    nombre = request.args.get('nombre', '').strip()
    
    if not nombre:
        return jsonify({'success': False, 'error': 'Nombre del producto requerido'}), 400

    try:
        print(f"DEBUG: Buscando imágenes para: '{nombre}'")
        
        # BASE DE DATOS CURADA DE IMÁGENES POR CATEGORÍA
        imagenes_curadas = {
            'cerveza': [
                'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400&h=300&fit=crop',  # Budweiser
                'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=300&fit=crop',  # Cerveza dorada
                'https://images.unsplash.com/photo-1571613316887-6f8d5cbf7ef7?w=400&h=300&fit=crop',  # Corona
                'https://images.unsplash.com/photo-1583511655826-05700d52f4d9?w=400&h=300&fit=crop',  # Heineken
                'https://images.unsplash.com/photo-1594736797933-d0d39d634bdd?w=400&h=300&fit=crop'   # Stella Artois
            ],
            'budweiser': [
                'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400&h=300&fit=crop',  # Budweiser oficial
                'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=300&fit=crop',  # Lata cerveza
                'https://images.unsplash.com/photo-1569108627993-52fd2847eed9?w=400&h=300&fit=crop',  # Botella cerveza
                'https://images.unsplash.com/photo-1600298881974-6be191ceeda1?w=400&h=300&fit=crop',  # Six pack
                'https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=400&h=300&fit=crop'   # Cerveza fría
            ],
            'pizza': [
                'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',  # Pizza margherita
                'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop',  # Pizza pepperoni
                'https://images.unsplash.com/photo-1595708684082-a173bb3a06c5?w=400&h=300&fit=crop',  # Pizza artesanal
                'https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=400&h=300&fit=crop',  # Pizza hawaiana
                'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=400&h=300&fit=crop'   # Pizza italiana
            ],
            'hamburguesa': [
                'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop',  # Hamburguesa clásica
                'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400&h=300&fit=crop',  # Burger gourmet
                'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=400&h=300&fit=crop',  # Cheeseburger
                'https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=400&h=300&fit=crop',  # Double burger
                'https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=400&h=300&fit=crop'   # BBQ burger
            ],
            'bebida': [
                'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop',  # Cocktail colorido
                'https://images.unsplash.com/photo-1544966503-7cc5ac882d5e?w=400&h=300&fit=crop',  # Bebida tropical
                'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=300&fit=crop',  # Jugo fresco
                'https://images.unsplash.com/photo-1578849278619-e73505e9610f?w=400&h=300&fit=crop',  # Smoothie
                'https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=400&h=300&fit=crop'   # Refresco
            ],
            'postre': [
                'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=400&h=300&fit=crop',  # Tiramisu
                'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop',  # Cheesecake
                'https://images.unsplash.com/photo-1567206563064-6f60f40a2b57?w=400&h=300&fit=crop',  # Chocolate cake
                'https://images.unsplash.com/photo-1486427944299-d1955d23e34d?w=400&h=300&fit=crop',  # Brownies
                'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop'   # Ice cream
            ]
        }
        
        # Detectar categoría del producto
        nombre_lower = nombre.lower()
        categoria_detectada = None
        imagenes_seleccionadas = []
        
        # Buscar coincidencias exactas o parciales
        for categoria, urls in imagenes_curadas.items():
            if categoria in nombre_lower or any(word in nombre_lower for word in categoria.split()):
                categoria_detectada = categoria
                imagenes_seleccionadas = urls
                break
        
        # Si no hay coincidencia específica, usar imágenes de "bebida" como fallback
        if not imagenes_seleccionadas:
            categoria_detectada = 'bebida'
            imagenes_seleccionadas = imagenes_curadas['bebida']
        
        print(f"DEBUG: Categoría detectada: {categoria_detectada}")
        print(f"DEBUG: Imágenes encontradas: {len(imagenes_seleccionadas)}")
        
        return jsonify({
            'success': True, 
            'imagenes': imagenes_seleccionadas,
            'query': nombre,
            'producto': nombre,
            'categoria_detectada': categoria_detectada,
            'total_encontradas': len(imagenes_seleccionadas),
            'fuente': 'Base de datos curada'
        })
            
    except Exception as e:
        print(f"ERROR: Error buscando imágenes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'Error interno del servidor: {str(e)}',
            'query': nombre
        }), 500
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error buscando imágenes: {str(e)}'
        }), 500


# [LIMPIEZA DE CÓDIGO 09/09/2025]
# ✅ FUNCIONES OBSOLETAS DE BÚSQUEDA DE IMÁGENES ELIMINADAS (~280 líneas)
# Sistema migrado a: modulos/backend/menu/endpoints/imagenes_endpoints.py
# - buscar_imagenes_alternativo() → ELIMINADA
# - buscar_imagenes_unsplash() → ELIMINADA  
# - buscar_imagenes_pixabay() → ELIMINADA
# - buscar_imagenes_pexels() → ELIMINADA
# - buscar_imagenes_fallback() → ELIMINADA

# --- COMPATIBILIDAD CON ENDPOINTS DE PRODUCTOS ---
# Los endpoints principales de productos están en productos_endpoints.py


# ========================================
# ENDPOINTS DE PRODUCTOS ELIMINADOS 
# ========================================
# RAZÓN: Sistema migrado a arquitectura modular
# UBICACIÓN NUEVA: modulos/backend/menu/endpoints/productos_endpoints.py
# Los endpoints principales (GET, POST, PUT, DELETE) están en el módulo separado



@menu_admin_bp.route('/debug/api-status', methods=['GET'])
def debug_api_status():
    """Endpoint de debug para verificar estado de APIs"""
    session = Session()
    try:
        # Verificar categorías
        categorias = session.query(Categoria).all()
        categorias_count = len(categorias)
        categorias_sample = [categoria_to_dict(c) for c in categorias[:2]]  # Solo 2 ejemplos
        
        # Verificar productos
        from sqlalchemy.orm import joinedload
        productos = session.query(Producto)\
                          .options(joinedload(Producto.categoria))\
                          .options(joinedload(Producto.subcategoria))\
                          .all()
        productos_count = len(productos)
        productos_sample = [producto_to_dict(p) for p in productos[:2]]  # Solo 2 ejemplos
        
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'database_status': 'connected',
            'categorias': {
                'count': categorias_count,
                'sample': categorias_sample,
                'api_endpoint': '/menu-admin/api/categorias'
            },
            'productos': {
                'count': productos_count,
                'sample': productos_sample,
                'api_endpoint': '/menu-admin/api/productos'
            },
            'expected_format': {
                'categorias': {'success': True, 'categorias': '[]'},
                'productos': {'success': True, 'productos': '[]'}
            }
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': f'Debug error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500
    finally:
        session.close()


# Endpoints para categorías

@menu_admin_bp.route('/categorias', methods=['GET'])
@menu_admin_bp.route('/api/categorias', methods=['GET'])
def obtener_categorias():
    """Obtener todas las categorías desde la base de datos"""
    session = Session()
    try:
        categorias = session.query(Categoria).all()
        categorias_dict = [categoria_to_dict(c) for c in categorias]
        return jsonify({
            'success': True,
            'categorias': categorias_dict
        })
    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        return jsonify({'error': 'Error obteniendo categorías'}), 500
    finally:
        session.close()


@menu_admin_bp.route('/categorias/<id_categoria>', methods=['GET'])
@menu_admin_bp.route('/api/categorias/<id_categoria>', methods=['GET'])
def obtener_categoria(id_categoria):
    """Obtener una categoría específica desde la base de datos"""
    session = Session()
    categoria = session.query(Categoria).filter_by(id=id_categoria).first()
    session.close()
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    return jsonify(categoria_to_dict(categoria))


@menu_admin_bp.route('/categorias', methods=['POST'])
@menu_admin_bp.route('/api/categorias', methods=['POST'])
def crear_categoria():
    """Crear una nueva categoría en la base de datos"""
    datos = request.get_json()
    if not datos or 'nombre' not in datos:
        return jsonify({'error': 'Faltan datos requeridos: nombre'}), 400
    
    session = Session()
    try:
        # Usar 'titulo' que es el campo real en la base de datos
        categoria = Categoria(
            titulo=datos['nombre'],  # Mapear nombre -> titulo
            descripcion=datos.get('descripcion', ''),
            activa=datos.get('activa', True),
            icono=datos.get('icono', ''),
            orden=datos.get('orden', 0)
        )
        session.add(categoria)
        session.commit()
        categoria_dict = categoria_to_dict(categoria)
        return jsonify({'success': True, 'categoria': categoria_dict}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': f'Error al crear categoría: {str(e)}'}), 500
    finally:
        session.close()


@menu_admin_bp.route('/categorias/<id_categoria>', methods=['PUT'])
@menu_admin_bp.route('/api/categorias/<id_categoria>', methods=['PUT'])
def actualizar_categoria(id_categoria):
    """Actualizar una categoría existente en la base de datos"""
    datos = request.get_json()
    print(f"🔍 DEBUG: Actualizando categoría {id_categoria}")
    print(f"🔍 DEBUG: Datos recibidos: {datos}")
    
    if not datos:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    session = Session()
    try:
        categoria = session.query(Categoria).filter_by(id=id_categoria).first()
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        print(f"🔍 DEBUG: Categoría antes del cambio - activa: {categoria.activa}")
        
        # Mapear campos frontend -> backend (igual que en crear_categoria)
        if 'nombre' in datos:
            categoria.titulo = datos['nombre']  # Mapear nombre -> titulo
        if 'descripcion' in datos:
            categoria.descripcion = datos['descripcion']
        if 'activa' in datos:
            print(f"🔍 DEBUG: Cambiando activa de {categoria.activa} a {datos['activa']}")
            categoria.activa = datos['activa']
        if 'icono' in datos:
            categoria.icono = datos['icono']
        if 'orden' in datos:
            categoria.orden = datos['orden']
            
        print(f"🔍 DEBUG: Categoría después del cambio - activa: {categoria.activa}")
        
        session.commit()
        print(f"🔍 DEBUG: Commit realizado")
        
        categoria_dict = categoria_to_dict(categoria)
        print(f"🔍 DEBUG: Diccionario respuesta: {categoria_dict}")
        
        return jsonify({'success': True, 'categoria': categoria_dict}), 200
    except Exception as e:
        session.rollback()
        print(f"🔍 DEBUG: Error en actualización: {str(e)}")
        return jsonify({'success': False, 'error': f'Error al actualizar categoría: {str(e)}'}), 500
    finally:
        session.close()


@menu_admin_bp.route('/categorias/<id_categoria>', methods=['DELETE'])
@menu_admin_bp.route('/api/categorias/<id_categoria>', methods=['DELETE'])
def eliminar_categoria(id_categoria):
    """Eliminar una categoría de la base de datos"""
    session = Session()
    try:
        categoria = session.query(Categoria).filter_by(id=id_categoria).first()
        if not categoria:
            session.close()
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        # Verificar si hay productos asociados a esta categoría
        productos_asociados = session.query(Producto).filter_by(categoria_id=id_categoria).count()
        
        # Verificar si hay subcategorías asociadas a esta categoría
        subcategorias_asociadas = session.query(Subcategoria).filter_by(categoria_id=id_categoria).count()
        
        # Obtener parámetro para forzar eliminación
        forzar = request.args.get('forzar', 'false').lower() == 'true'
        
        if not forzar and (productos_asociados > 0 or subcategorias_asociadas > 0):
            # Informar sobre las relaciones existentes
            mensaje_error = []
            if productos_asociados > 0:
                mensaje_error.append(f'{productos_asociados} producto(s)')
            if subcategorias_asociadas > 0:
                mensaje_error.append(f'{subcategorias_asociadas} subcategoría(s)')
            
            session.close()
            return jsonify({
                'error': f'La categoría "{categoria.nombre}" tiene {" y ".join(mensaje_error)} asociada(s).',
                'detalles': {
                    'productos': productos_asociados,
                    'subcategorias': subcategorias_asociadas
                },
                'sugerencia': 'Puedes: 1) Reasignar estos elementos a otra categoría, 2) Eliminarlos primero, o 3) Usar eliminación forzada (eliminará todo automáticamente)'
            }), 400
        
        if forzar:
            # Eliminación forzada: eliminar subcategorías y reasignar productos
            if subcategorias_asociadas > 0:
                subcategorias = session.query(Subcategoria).filter_by(categoria_id=id_categoria).all()
                for subcategoria in subcategorias:
                    session.delete(subcategoria)
            
            if productos_asociados > 0:
                productos = session.query(Producto).filter_by(categoria_id=id_categoria).all()
                for producto in productos:
                    producto.categoria_id = None  # Dejar sin categoría
                    producto.subcategoria_id = None  # Limpiar subcategoría también
        
        # Eliminar la categoría
        session.delete(categoria)
        session.commit()
        session.close()
        
        mensaje = 'Categoría eliminada correctamente'
        if forzar:
            mensaje += f' (eliminadas {subcategorias_asociadas} subcategorías y {productos_asociados} productos reasignados)'
        
        return jsonify({'mensaje': mensaje})
        
    except Exception as e:
        session.rollback()
        session.close()
        print(f"ERROR: Error al eliminar categoría: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al eliminar categoría: {str(e)}'}), 500


# Endpoint para obtener el menú completo organizado por categorías desde la base de datos
@menu_admin_bp.route('/menu-completo', methods=['GET'])
def obtener_menu_completo():
    """Obtener el menú completo organizado por categorías desde la base de datos"""
    session = Session()
    categorias = session.query(Categoria).all()
    productos = session.query(Producto).all()
    session.close()
    menu = {}
    for cat in categorias:
        menu[cat.id] = {
            'categoria': categoria_to_dict(cat),
            'productos': [producto_to_dict(p) for p in productos if p.categoria == cat.id]
        }
    return jsonify(menu)

# Endpoint para obtener productos por categoría desde la base de datos
@menu_admin_bp.route('/categorias/<id_categoria>/productos', methods=['GET'])
def obtener_productos_categoria(id_categoria):
    """Obtener productos de una categoría específica desde la base de datos"""
    session = Session()
    productos = session.query(Producto).filter_by(categoria=id_categoria).all()
    session.close()
    return jsonify([producto_to_dict(p) for p in productos])

# Endpoints para Excel
@menu_admin_bp.route('/excel/plantilla', methods=['GET'])
def generar_plantilla_excel():
    """Generar y descargar una plantilla Excel para cargar productos (actualizada 28/07/2025)"""
    try:
        tipo = request.args.get('tipo', 'basica')  # 'basica' o 'avanzada'
        nombre_archivo = request.args.get('nombre', 'plantilla_productos.xlsx')
        
        # Crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            archivo_plantilla = os.path.join(temp_dir, nombre_archivo)
            
            if tipo == 'avanzada':
                generar_plantilla_avanzada(archivo_plantilla)
                download_name = 'plantilla_productos_recetas.xlsx'
            else:
                generar_plantilla_basica(archivo_plantilla)
                download_name = 'plantilla_productos_basica.xlsx'
            
            return send_file(
                archivo_plantilla,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
    except Exception as e:
        return jsonify({'error': f'Error al generar plantilla: {str(e)}'}), 500

@menu_admin_bp.route('/excel/plantilla-ingredientes', methods=['GET'])
def generar_plantilla_ingredientes_endpoint():
    """Generar y descargar una plantilla Excel para ingredientes (nuevo 28/07/2025)"""
    try:
        nombre_archivo = request.args.get('nombre', 'plantilla_ingredientes.xlsx')
        
        # Crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            archivo_plantilla = os.path.join(temp_dir, nombre_archivo)
            generar_plantilla_ingredientes(archivo_plantilla)
            
            return send_file(
                archivo_plantilla,
                as_attachment=True,
                download_name='plantilla_ingredientes.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
    except Exception as e:
        return jsonify({'error': f'Error al generar plantilla de ingredientes: {str(e)}'}), 500

@menu_admin_bp.route('/excel/plantilla-categorias', methods=['GET'])
def generar_plantilla_categorias_endpoint():
    """Generar y descargar una plantilla Excel para cargar categorías"""
    try:
        nombre_archivo = request.args.get('nombre', 'plantilla_categorias.xlsx')
        
        # Generar plantilla en directorio temporal
        temp_dir = tempfile.gettempdir()
        archivo_plantilla = os.path.join(temp_dir, nombre_archivo)
        
        # Usar la función del módulo de plantillas
        generar_plantilla_categorias(archivo_plantilla)
        
        return send_file(
            archivo_plantilla,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': f'Error al generar plantilla de categorías: {str(e)}'}), 500


@menu_admin_bp.route('/excel/cargar', methods=['POST'])
def cargar_productos_excel():
    """Cargar productos desde un archivo Excel a la base de datos"""
    try:
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        archivo = request.files['archivo']
        if archivo.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        if not archivo.filename.endswith('.xlsx'):
            return jsonify({'error': 'El archivo debe ser un Excel (.xlsx)'}), 400
        temp_path = os.path.join(tempfile.gettempdir(), archivo.filename)
        archivo.save(temp_path)
        resultado_procesamiento = excel_manager.procesar_archivo_excel(temp_path)
        if resultado_procesamiento['productos']:
            session = Session()
            for datos in resultado_procesamiento['productos']:
                if 'id' not in datos:
                    datos['id'] = str(uuid.uuid4())
                producto = Producto(**datos)
                session.add(producto)
            session.commit()
            session.close()
            os.remove(temp_path)
            return jsonify({
                'mensaje': 'Archivo procesado exitosamente',
                'productos_procesados': resultado_procesamiento['total_procesados'],
                'productos_cargados': len(resultado_procesamiento['productos']),
                'productos_fallidos': 0,
                'errores_procesamiento': resultado_procesamiento['errores'],
                'errores_carga': []
            })
        else:
            os.remove(temp_path)
            return jsonify({
                'error': 'No se pudieron procesar productos del archivo',
                'errores': resultado_procesamiento['errores']
            }), 400
    except Exception as e:
        return jsonify({'error': f'Error al procesar archivo: {str(e)}'}), 500

@menu_admin_bp.route('/test-excel', methods=['GET'])
def test_excel():
    """Endpoint de prueba para verificar el blueprint"""
    return jsonify({'mensaje': 'Endpoint Excel funcional'})

@menu_admin_bp.route('/excel/plantilla-preparacion', methods=['GET'])
def generar_plantilla_preparacion():
    """Generar y descargar una plantilla Excel específica para ingredientes y preparación"""
    try:
        print("=== DEBUG: Iniciando generación de plantilla de preparación ===")
        
        # Nombre descriptivo con fecha
        fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"eterials_ingredientes_preparacion_{fecha_actual}.xlsx"
        print(f"DEBUG: Generando archivo: {nombre_archivo}")
        
        # Generar plantilla en directorio temporal
        temp_dir = tempfile.gettempdir()
        archivo_plantilla = os.path.join(temp_dir, nombre_archivo)
        
        # Crear un DataFrame con las columnas necesarias para ingredientes y preparación
        session = Session()
        productos = session.query(Producto).all()
        session.close()
        
        # Convertir productos a formato para Excel
        datos = []
        for p in productos:
            datos.append({
                'ID': p.id,
                'Nombre': p.nombre,
                'Categoría': p.categoria,
                'Precio': p.precio,
                'Ingrediente 1': '',
                'Ingrediente 2': '',
                'Ingrediente 3': '',
                'Ingrediente 4': '',
                'Ingrediente 5': '',
                'Cantidad 1': '',
                'Cantidad 2': '',
                'Cantidad 3': '',
                'Cantidad 4': '',
                'Cantidad 5': '',
                'Preparación': '',
                'Tiempo Preparación': ''
            })
        
        # Crear DataFrame y guardar a Excel
        df = pd.DataFrame(datos)
        
        # Aplicar estilos y formatos
        with pd.ExcelWriter(archivo_plantilla, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Ingredientes y Preparación', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Ingredientes y Preparación']
            
            # Formato para títulos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FFD966',
                'border': 1
            })
            
            # Aplicar formato a cabeceras
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Ajustar anchos de columna
            worksheet.set_column('A:A', 36)  # ID
            worksheet.set_column('B:B', 25)  # Nombre
            worksheet.set_column('C:C', 15)  # Categoría
            worksheet.set_column('D:D', 10)  # Precio
            worksheet.set_column('E:I', 15)  # Ingredientes
            worksheet.set_column('J:N', 10)  # Cantidades
            worksheet.set_column('O:O', 30)  # Preparación
            worksheet.set_column('P:P', 15)  # Tiempo
            
            # Agregar instrucciones
            worksheet.merge_range('A20:P20', 'INSTRUCCIONES PARA COMPLETAR LA PLANTILLA', workbook.add_format({
                'bold': True, 'bg_color': '#DDEBF7', 'border': 1, 'align': 'center'
            }))
            worksheet.merge_range('A21:P25', 
                '1. Complete los ingredientes para cada producto (máximo 5 por producto)\n'
                '2. Ingrese las cantidades correspondientes a cada ingrediente\n'
                '3. Describa el proceso de preparación paso a paso\n'
                '4. Indique el tiempo estimado de preparación (ej: 15 min, 1 hora)\n'
                '5. No modifique el ID, Nombre, Categoría ni Precio de los productos existentes', 
                workbook.add_format({'bg_color': '#DDEBF7', 'border': 1, 'text_wrap': True}))
        
        # Enviar archivo con headers optimizados para forzar diálogo "Guardar como"
        return send_file(
            archivo_plantilla,
            as_attachment=True,
            download_name=nombre_archivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"ERROR: Error en generación de plantilla de preparación: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al generar plantilla: {str(e)}'}), 500


# ===== ENDPOINT DE ESTADÍSTICAS =====
@menu_admin_bp.route('/api/stats', methods=['GET'])
@menu_admin_bp.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas del menú para el dashboard"""
    try:
        engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Contar productos totales
        total_productos = session.query(Producto).count()
        
        # Contar categorías totales
        total_categorias = session.query(Categoria).count()
        
        # Contar productos activos/disponibles
        productos_activos = session.query(Producto).filter(Producto.disponible == True).count()
        
        # Calcular precio promedio
        productos_con_precio = session.query(Producto).filter(Producto.precio.isnot(None), Producto.precio > 0).all()
        if productos_con_precio:
            precio_promedio = sum(float(p.precio) for p in productos_con_precio) / len(productos_con_precio)
            precio_promedio = round(precio_promedio, 2)
        else:
            precio_promedio = 0.0
            
        session.close()
        
        estadisticas = {
            'total_productos': total_productos,
            'total_categorias': total_categorias,
            'productos_activos': productos_activos,
            'precio_promedio': precio_promedio
        }
        
        return jsonify(estadisticas)
        
    except Exception as e:
        print(f"ERROR: Error al obtener estadísticas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

# ===== ENDPOINTS DE SUBCATEGORÍAS =====
@menu_admin_bp.route('/subcategorias', methods=['GET'])
@menu_admin_bp.route('/api/subcategorias', methods=['GET'])
def obtener_subcategorias():
    """Obtener todas las subcategorías"""
    try:
        session = Session()
        subcategorias = session.query(Subcategoria).all()
        
        resultado = []
        for subcategoria in subcategorias:
            resultado.append({
                'id': subcategoria.id,
                'nombre': subcategoria.nombre,
                'descripcion': subcategoria.descripcion,
                'categoria_id': subcategoria.categoria_id,
                'activa': subcategoria.activa
            })
        
        session.close()
        return jsonify(resultado)
        
    except Exception as e:
        print(f"ERROR: Error al obtener subcategorías: {str(e)}")
        return jsonify({'error': f'Error al obtener subcategorías: {str(e)}'}), 500

@menu_admin_bp.route('/api/subcategorias/categoria/<int:categoria_id>', methods=['GET'])
def obtener_subcategorias_por_categoria(categoria_id):
    """Obtener subcategorías filtradas por categoría"""
    try:
        session = Session()
        
        # En el contexto de administración, mostrar TODAS las subcategorías (activas e inactivas)
        # Para el menú público, se puede crear otro endpoint específico que filtre solo activas
        subcategorias = session.query(Subcategoria).filter_by(categoria_id=categoria_id).all()
        
        resultado = []
        for subcategoria in subcategorias:
            resultado.append({
                'id': subcategoria.id,
                'nombre': subcategoria.nombre,
                'descripcion': subcategoria.descripcion,
                'categoria_id': subcategoria.categoria_id,
                'activa': subcategoria.activa
            })
        
        session.close()
        return jsonify({'success': True, 'subcategorias': resultado})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
        print(f"ERROR: Error al obtener subcategorías por categoría: {str(e)}")
        return jsonify({'error': f'Error al obtener subcategorías por categoría: {str(e)}'}), 500

@menu_admin_bp.route('/api/subcategorias', methods=['POST'])
def crear_subcategoria():
    """Crear nueva subcategoría"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return jsonify({'error': 'El nombre es obligatorio'}), 400
        if not data.get('categoria_id'):
            return jsonify({'error': 'La categoría es obligatoria'}), 400
        
        session = Session()
        
        # Verificar que la categoría existe
        categoria_existe = session.query(Categoria).filter_by(id=data['categoria_id']).first()
        if not categoria_existe:
            session.close()
            return jsonify({'error': 'La categoría especificada no existe'}), 400
        
        # Crear nueva subcategoría
        nueva_subcategoria = Subcategoria(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            categoria_id=data['categoria_id'],
            activa=data.get('activa', True)
        )
        
        session.add(nueva_subcategoria)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Subcategoría creada correctamente'}), 201
        
    except Exception as e:
        print(f"ERROR: Error al crear subcategoría: {str(e)}")
        return jsonify({'error': f'Error al crear subcategoría: {str(e)}'}), 500

@menu_admin_bp.route('/api/subcategorias/<int:subcategoria_id>', methods=['GET'])
def obtener_subcategoria_por_id(subcategoria_id):
    """Obtener una subcategoría específica por ID"""
    try:
        session = Session()
        
        subcategoria = session.query(Subcategoria).filter_by(id=subcategoria_id).first()
        if not subcategoria:
            session.close()
            return jsonify({'error': 'Subcategoría no encontrada'}), 404
        
        resultado = {
            'id': subcategoria.id,
            'nombre': subcategoria.nombre,
            'descripcion': subcategoria.descripcion,
            'categoria_id': subcategoria.categoria_id,
            'activa': subcategoria.activa
        }
        
        session.close()
        return jsonify({'success': True, 'subcategoria': resultado})
        
    except Exception as e:
        print(f"ERROR: Error al obtener subcategoría: {str(e)}")
        return jsonify({'error': f'Error al obtener subcategoría: {str(e)}'}), 500

@menu_admin_bp.route('/api/subcategorias/<int:subcategoria_id>', methods=['PUT'])
def actualizar_subcategoria(subcategoria_id):
    """Actualizar subcategoría existente"""
    try:
        data = request.get_json()
        session = Session()
        
        subcategoria = session.query(Subcategoria).filter_by(id=subcategoria_id).first()
        if not subcategoria:
            session.close()
            return jsonify({'error': 'Subcategoría no encontrada'}), 404
        
        # Actualizar campos
        if 'nombre' in data:
            subcategoria.nombre = data['nombre']
        if 'descripcion' in data:
            subcategoria.descripcion = data['descripcion']
        if 'categoria_id' in data:
            subcategoria.categoria_id = data['categoria_id']
        if 'activa' in data:
            subcategoria.activa = data['activa']
        
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Subcategoría actualizada correctamente'})
        
    except Exception as e:
        print(f"ERROR: Error al actualizar subcategoría: {str(e)}")
        return jsonify({'error': f'Error al actualizar subcategoría: {str(e)}'}), 500

@menu_admin_bp.route('/api/subcategorias/<int:subcategoria_id>', methods=['DELETE'])
def eliminar_subcategoria(subcategoria_id):
    """Eliminar subcategoría"""
    try:
        session = Session()
        
        # Verificar si hay productos usando esta subcategoría
        productos_dependientes = session.query(Producto).filter_by(subcategoria_id=subcategoria_id).count()
        if productos_dependientes > 0:
            session.close()
            return jsonify({
                'error': f'No se puede eliminar la subcategoría porque {productos_dependientes} producto(s) la están usando. Elimina o reasigna los productos primero.'
            }), 400
        
        subcategoria = session.query(Subcategoria).filter_by(id=subcategoria_id).first()
        if not subcategoria:
            session.close()
            return jsonify({'error': 'Subcategoría no encontrada'}), 404
        
        session.delete(subcategoria)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Subcategoría eliminada correctamente'})
        
    except Exception as e:
        print(f"ERROR: Error al eliminar subcategoría: {str(e)}")
        return jsonify({'error': f'Error al eliminar subcategoría: {str(e)}'}), 500


# ===== ENDPOINT PARA SUBIR IMÁGENES =====
@menu_admin_bp.route('/subir-imagen', methods=['POST'])
def subir_imagen():
    """Endpoint para subir imágenes de productos al servidor"""
    try:
        # Verificar que se envió un archivo. Aceptar varios nombres comunes por compatibilidad.
        file_keys = ['imagen', 'file', 'image', 'foto', 'archivo', 'file0']
        archivo = None
        used_key = None
        for key in file_keys:
            if key in request.files:
                archivo = request.files[key]
                used_key = key
                break
        if archivo is None:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        # Log breve para debugging
        print(f"DEBUG: recibir archivo usando clave '{used_key}' y filename='{getattr(archivo, 'filename', None)}'")
        
        # Verificar que el archivo no esté vacío
        if not getattr(archivo, 'filename', ''):
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        # Verificar que sea una imagen
        extensiones_permitidas = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        extension = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
        
        if extension not in extensiones_permitidas:
            return jsonify({'error': 'Tipo de archivo no permitido. Usa: PNG, JPG, JPEG, GIF, WEBP'}), 400
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_unico = f"{timestamp}_{uuid.uuid4().hex[:8]}.{extension}"
        
        # Ruta donde guardar el archivo
        carpeta_uploads = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'productos')
        ruta_archivo = os.path.join(carpeta_uploads, nombre_unico)
        
        # Crear carpeta si no existe
        os.makedirs(carpeta_uploads, exist_ok=True)
        
        # Guardar el archivo
        archivo.save(ruta_archivo)
        
        # Generar URL absoluta para acceder a la imagen
        # Usar request.host_url para generar URL completa
        url_imagen = f"{request.host_url}menu-admin/static/uploads/productos/{nombre_unico}"
        
        return jsonify({
            'success': True,
            'url': url_imagen,
            'filename': nombre_unico,
            'message': 'Imagen subida correctamente'
        })
        
    except Exception as e:
        print(f"ERROR: Error al subir imagen: {str(e)}")
        return jsonify({'error': f'Error al subir imagen: {str(e)}'}), 500


# ===== ENDPOINTS PARA PLANTILLAS EXCEL Y CARGA MASIVA =====

@menu_admin_bp.route('/api/plantillas/productos')
def descargar_plantilla_productos():
    """Genera y descarga plantilla Excel para productos"""
    try:
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_path = temp_file.name
        temp_file.close()
        
        # Generar plantilla de productos
        from modulos.backend.menu.excel.plantillas_excel import generar_plantilla_productos
        generar_plantilla_productos(temp_path)
        
        # Enviar archivo como descarga
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'plantilla_productos_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"ERROR: Error generando plantilla de productos: {str(e)}")
        return jsonify({'error': f'Error generando plantilla: {str(e)}'}), 500

@menu_admin_bp.route('/api/plantillas/categorias')
def descargar_plantilla_categorias():
    """Genera y descarga plantilla Excel para categorías"""
    try:
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_path = temp_file.name
        temp_file.close()
        
        # Generar plantilla de categorías
        from modulos.backend.menu.excel.plantillas_excel import generar_plantilla_categorias
        generar_plantilla_categorias(temp_path)
        
        # Enviar archivo como descarga
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'plantilla_categorias_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"ERROR: Error generando plantilla de categorías: {str(e)}")
        return jsonify({'error': f'Error generando plantilla: {str(e)}'}), 500

@menu_admin_bp.route('/api/plantillas/subcategorias')
def descargar_plantilla_subcategorias():
    """Genera y descarga plantilla Excel para subcategorías"""
    try:
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_path = temp_file.name
        temp_file.close()
        
        # Generar plantilla de subcategorías
        from modulos.backend.menu.excel.plantillas_excel import generar_plantilla_subcategorias
        generar_plantilla_subcategorias(temp_path)
        
        # Enviar archivo como descarga
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'plantilla_subcategorias_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"ERROR: Error generando plantilla de subcategorías: {str(e)}")
        return jsonify({'error': f'Error generando plantilla: {str(e)}'}), 500

@menu_admin_bp.route('/api/plantillas/ingredientes')
def descargar_plantilla_ingredientes():
    """Genera y descarga plantilla Excel para ingredientes"""
    try:
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_path = temp_file.name
        temp_file.close()
        
        # Generar plantilla de ingredientes
        from modulos.backend.menu.excel.plantillas_excel import generar_plantilla_ingredientes
        generar_plantilla_ingredientes(temp_path)
        
        # Enviar archivo como descarga
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'plantilla_ingredientes_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"ERROR: Error generando plantilla de ingredientes: {str(e)}")
        return jsonify({'error': f'Error generando plantilla: {str(e)}'}), 500

@menu_admin_bp.route('/api/cargar-excel', methods=['POST'])
def cargar_excel():
    """Carga masiva de productos desde archivo Excel"""
    session = Session()
    try:
        # Verificar que se envió un archivo
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        archivo = request.files['archivo']
        
        if archivo.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        # Verificar que sea un archivo Excel
        if not archivo.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Solo se permiten archivos Excel (.xlsx, .xls)'}), 400
        
        # Leer archivo Excel
        df = pd.read_excel(archivo)
        
        # Validar columnas mínimas requeridas
        columnas_requeridas = ['nombre', 'precio', 'categoria']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            return jsonify({
                'error': f'Columnas faltantes: {", ".join(columnas_faltantes)}'
            }), 400
        
        # Procesar cada fila
        productos_creados = 0
        errores = []
        
        for index, row in df.iterrows():
            try:
                # Buscar o crear categoría
                categoria_nombre = str(row['categoria']).strip()
                categoria = session.query(Categoria).filter_by(titulo=categoria_nombre).first()
                
                if not categoria:
                    # Crear categoría nueva
                    categoria = Categoria(
                        titulo=categoria_nombre,
                        descripcion=f"Categoría creada automáticamente para {categoria_nombre}",
                        activa=True
                    )
                    session.add(categoria)
                    session.flush()  # Para obtener el ID
                
                # Crear producto
                producto = Producto(
                    nombre=str(row['nombre']).strip(),
                    precio=float(row['precio']) if pd.notna(row['precio']) else 0.0,
                    descripcion=str(row.get('descripcion', '')).strip() if pd.notna(row.get('descripcion')) else '',
                    categoria_id=categoria.id,
                    disponible=bool(row.get('disponible', True)),
                    tipo_producto=str(row.get('tipo_producto', 'simple')).strip(),
                    imagen_url=str(row.get('imagen_url', '')).strip() if pd.notna(row.get('imagen_url')) else '',
                    tiempo_preparacion=str(row.get('tiempo_preparacion', '')).strip() if pd.notna(row.get('tiempo_preparacion')) else '',
                    instrucciones_preparacion=str(row.get('instrucciones_preparacion', '')).strip() if pd.notna(row.get('instrucciones_preparacion')) else '',
                    notas_cocina=str(row.get('notas_cocina', '')).strip() if pd.notna(row.get('notas_cocina')) else ''
                )
                
                session.add(producto)
                productos_creados += 1
                
            except Exception as e:
                errores.append(f"Fila {index + 2}: {str(e)}")
                continue
        
        # Confirmar cambios
        session.commit()
        
        resultado = {
            'success': True,
            'message': f'Carga masiva completada',
            'procesados': productos_creados,
            'errores': len(errores)
        }
        
        if errores:
            resultado['detalles_errores'] = errores[:10]  # Solo primeros 10 errores
        
        return jsonify(resultado)
        
    except Exception as e:
        session.rollback()
        print(f"ERROR: Error en carga masiva: {str(e)}")
        return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500
    finally:
        session.close()

@menu_admin_bp.route('/api/backup/crear', methods=['POST'])
def crear_backup():
    """Crea backup completo del sistema"""
    db_session = Session()
    try:
        # Obtener todos los datos
        productos = db_session.query(Producto).all()
        categorias = db_session.query(Categoria).all()
        subcategorias = db_session.query(Subcategoria).all()
        ingredientes = db_session.query(Ingrediente).all()
        
        # Crear estructura de backup
        backup_data = {
            'version': '1.0',
            'fecha_backup': datetime.now().isoformat(),
            'productos': [producto_to_dict(p) for p in productos],
            'categorias': [categoria_to_dict(c) for c in categorias],
            'subcategorias': [subcategoria_to_dict(s) for s in subcategorias],
            'ingredientes': [ingrediente_to_dict(i) for i in ingredientes]
        }
        
        # Crear archivo temporal
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f'backup_eterials_{timestamp}.json'
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        import json
        json.dump(backup_data, temp_file, indent=2, ensure_ascii=False)
        temp_file.close()
        
        return jsonify({
            'success': True,
            'message': 'Backup creado exitosamente',
            'archivo': nombre_archivo,
            'registros': {
                'productos': len(productos),
                'categorias': len(categorias),
                'subcategorias': len(subcategorias),
                'ingredientes': len(ingredientes)
            }
        })
        
    except Exception as e:
        print(f"ERROR: Error creando backup: {str(e)}")
        return jsonify({'error': f'Error creando backup: {str(e)}'}), 500
    finally:
        db_session.close()

@menu_admin_bp.route('/api/backup/restaurar', methods=['POST'])
def restaurar_backup():
    """Restaura backup del sistema"""
    db_session = Session()
    try:
        if 'backup' not in request.files:
            return jsonify({'error': 'No se envió archivo de backup'}), 400
        
        archivo = request.files['backup']
        
        if archivo.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        # Leer archivo JSON
        import json
        backup_data = json.load(archivo)
        
        # Validar estructura del backup
        if 'productos' not in backup_data:
            return jsonify({'error': 'Archivo de backup inválido'}), 400
        
        # CUIDADO: Esto borra todos los datos actuales
        if not request.form.get('confirmar_borrado'):
            return jsonify({
                'error': 'Operación peligrosa. Agregue confirmar_borrado=true'
            }), 400
        
        # Limpiar base de datos
        db_session.query(Ingrediente).delete()
        db_session.query(Producto).delete()
        db_session.query(Subcategoria).delete()
        db_session.query(Categoria).delete()
        
        # Restaurar categorías
        for cat_data in backup_data.get('categorias', []):
            categoria = Categoria(**{k: v for k, v in cat_data.items() if k != 'id'})
            db_session.add(categoria)
        
        # Restaurar productos (simplificado)
        for prod_data in backup_data.get('productos', []):
            producto_dict = {k: v for k, v in prod_data.items() 
                           if k not in ['id', 'categoria_nombre', 'subcategoria_nombre', 'ingredientes']}
            producto = Producto(**producto_dict)
            db_session.add(producto)
        
        db_session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Backup restaurado exitosamente'
        })
        
    except Exception as e:
        db_session.rollback()
        print(f"ERROR: Error restaurando backup: {str(e)}")
        return jsonify({'error': f'Error restaurando backup: {str(e)}'}), 500
    finally:
        db_session.close()

