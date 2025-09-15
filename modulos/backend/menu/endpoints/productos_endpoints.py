"""
📦 ENDPOINT ESPECÍFICO PARA GESTIÓN DE PRODUCTOS
Responsabilidad única: CRUD completo de productos
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.categoria import Categoria  
from modulos.backend.menu.database.models.subcategoria import Subcategoria
from modulos.backend.menu.database.base import Base

# Configuración de base de datos
DATABASE_URL = 'sqlite:///modulos/backend/menu/database/menu.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Blueprint específico para productos
productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

# --- FUNCIONES HELPER ---
def to_bool(val):
    """Convierte un valor a boolean de forma segura"""
    if isinstance(val, bool):
        return val
    if val is None:
        return True
    s = str(val).strip().lower()
    if s in ('1', 'true', 't', 'yes', 'y'):
        return True
    if s in ('0', 'false', 'f', 'no', 'n'):
        return False
    # fallback: try interpret as int
    try:
        return bool(int(s))
    except:
        return True

def to_int_or_none(val):
    """Convierte un valor a entero o None de forma segura"""
    if val is None or val == '':
        return None
    try:
        return int(val)
    except:
        return None

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
    
    return {
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
        'instrucciones_preparacion': producto.instrucciones_preparacion,
        'notas_cocina': producto.notas_cocina,
        'tipo_producto': producto.tipo_producto
    }

@productos_bp.route('/', methods=['GET'])
@productos_bp.route('/api', methods=['GET'])
def listar_productos():
    """
    📋 LISTAR TODOS LOS PRODUCTOS
    Devuelve lista completa con información de categorías
    """
    try:
        session = Session()
        
        # Eager loading para evitar N+1 queries
        productos = session.query(Producto)\
            .options(joinedload(Producto.categoria))\
            .options(joinedload(Producto.subcategoria))\
            .all()
        
        productos_data = [producto_to_dict(producto) for producto in productos]
        
        session.close()
        
        return jsonify({
            'success': True,
            'productos': productos_data,
            'total': len(productos_data)
        })
        
    except Exception as e:
        print(f"❌ Error listando productos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@productos_bp.route('/<int:id_producto>', methods=['GET'])
@productos_bp.route('/api/<int:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    """
    🔍 OBTENER UN PRODUCTO ESPECÍFICO
    Devuelve información detallada de un producto
    """
    try:
        session = Session()
        
        producto = session.query(Producto)\
            .options(joinedload(Producto.categoria))\
            .options(joinedload(Producto.subcategoria))\
            .filter(Producto.id == id_producto)\
            .first()
        
        if not producto:
            session.close()
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        producto_data = producto_to_dict(producto)
        session.close()
        
        return jsonify({
            'success': True,
            'producto': producto_data
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo producto {id_producto}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@productos_bp.route('/', methods=['POST'])
@productos_bp.route('/api', methods=['POST'])
def crear_producto():
    """
    ➕ CREAR NUEVO PRODUCTO
    Crea un producto con validaciones completas anti-duplicados
    """
    try:
        # Manejar tanto JSON como FormData
        if request.content_type and 'application/json' in request.content_type:
            datos = request.get_json()
        else:
            # FormData desde formulario HTML
            datos = request.form.to_dict()
        
        if not datos or 'nombre' not in datos or 'precio' not in datos:
            return jsonify({'error': 'Faltan datos requeridos: nombre, precio'}), 400
        
        # No generar ID - dejar que SQLAlchemy lo auto-incremente
        if 'id' in datos:
            del datos['id']
            
        session = Session()
        
        # 🚨 VALIDACIÓN ANTI-DUPLICADOS
        nombre_producto = datos['nombre'].strip()
        
        # Verificar si ya existe un producto con el mismo nombre
        producto_existente = session.query(Producto).filter(
            Producto.nombre.ilike(f'%{nombre_producto}%')
        ).first()
        
        if producto_existente:
            session.close()
            return jsonify({
                'success': False,
                'error': f'Ya existe un producto con el nombre "{nombre_producto}". Los productos deben tener nombres únicos.',
                'producto_existente': {
                    'id': producto_existente.id,
                    'nombre': producto_existente.nombre,
                    'precio': float(producto_existente.precio)
                }
            }), 409  # 409 Conflict
        
        # Validar que el nombre no esté vacío después de strip
        if not nombre_producto:
            session.close()
            return jsonify({
                'success': False,
                'error': 'El nombre del producto no puede estar vacío'
            }), 400
        
        # Validar precio positivo
        try:
            precio = float(datos['precio'])
            if precio <= 0:
                session.close()
                return jsonify({
                    'success': False,
                    'error': 'El precio debe ser mayor a 0'
                }), 400
            datos['precio'] = precio
        except (ValueError, TypeError):
            session.close()
            return jsonify({
                'success': False,
                'error': 'El precio debe ser un número válido'
            }), 400
        
        # Actualizar el nombre limpio en los datos
        datos['nombre'] = nombre_producto
        
        # Aplicar normalizaciones seguras
        if 'disponible' in datos:
            datos['disponible'] = to_bool(datos.get('disponible'))
        else:
            datos['disponible'] = True

        if 'categoria_id' in datos:
            datos['categoria_id'] = to_int_or_none(datos.get('categoria_id'))
        if 'subcategoria_id' in datos:
            datos['subcategoria_id'] = to_int_or_none(datos.get('subcategoria_id'))

        # Asegurar tipo_producto presente
        if 'tipo_producto' not in datos or not datos.get('tipo_producto'):
            datos['tipo_producto'] = 'simple'

        # Crear producto con los datos validados
        producto = Producto(**datos)
        session.add(producto)
        session.commit()
        
        # Convertir a diccionario para respuesta
        producto_dict = producto_to_dict(producto)
        session.close()
        
        return jsonify({
            'success': True,
            'mensaje': 'Producto creado exitosamente',
            'producto': producto_dict,
            'producto_id': producto.id
        }), 201
        
    except Exception as e:
        print(f"❌ Error creando producto: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@productos_bp.route('/<int:id_producto>', methods=['PUT'])
@productos_bp.route('/api/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    """
    ✏️ ACTUALIZAR PRODUCTO EXISTENTE
    Actualiza campos con validación anti-duplicación
    """
    try:
        # Manejar tanto JSON como FormData
        if request.content_type and 'application/json' in request.content_type:
            datos = request.get_json()
        else:
            # FormData desde formulario HTML
            datos = request.form.to_dict()
            
        if not datos:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        session = Session()
        producto = session.query(Producto).filter_by(id=id_producto).first()
        if not producto:
            session.close()
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # ✅ VALIDACIÓN ANTI-DUPLICACIÓN: Verificar nombre único si se está cambiando
        if 'nombre' in datos:
            nombre_nuevo = datos['nombre'].strip()
            if not nombre_nuevo:
                session.close()
                return jsonify({'error': 'El nombre del producto no puede estar vacío'}), 400
            
            # Verificar que no exista otro producto con el mismo nombre (excluyendo el actual)
            producto_existente = session.query(Producto).filter(
                Producto.nombre.ilike(nombre_nuevo),
                Producto.id != id_producto
            ).first()
            
            if producto_existente:
                session.close()
                return jsonify({
                    'error': f'Ya existe un producto llamado "{nombre_nuevo}". Por favor elige un nombre diferente.',
                    'conflicto': 'nombre_duplicado',
                    'producto_existente': producto_existente.id
                }), 409
        
        # ✅ VALIDACIÓN DE PRECIO: Asegurar valores positivos
        if 'precio' in datos:
            try:
                precio = float(datos['precio'])
                if precio < 0:
                    session.close()
                    return jsonify({'error': 'El precio no puede ser negativo'}), 400
                datos['precio'] = precio
            except (ValueError, TypeError):
                session.close()
                return jsonify({'error': 'Precio inválido, debe ser un número'}), 400
        
        # ✅ NORMALIZAR DATOS: Aplicar conversiones de tipo antes de actualizar
        if 'disponible' in datos:
            datos['disponible'] = to_bool(datos.get('disponible'))
        if 'categoria_id' in datos:
            datos['categoria_id'] = to_int_or_none(datos.get('categoria_id'))
        if 'subcategoria_id' in datos:
            datos['subcategoria_id'] = to_int_or_none(datos.get('subcategoria_id'))

        # ✅ APLICAR CAMBIOS: Solo después de todas las validaciones
        for key, value in datos.items():
            if hasattr(producto, key):
                setattr(producto, key, value)
        
        session.commit()
        producto_dict = producto_to_dict(producto)
        session.close()
        
        return jsonify({
            'mensaje': 'Producto actualizado correctamente',
            'producto': producto_dict
        })
        
    except Exception as e:
        print(f"❌ Error actualizando producto {id_producto}: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@productos_bp.route('/<int:id_producto>', methods=['DELETE'])
@productos_bp.route('/api/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    """
    🗑️ ELIMINAR PRODUCTO
    Elimina producto con validaciones de integridad
    """
    try:
        session = Session()
        producto = session.query(Producto).filter_by(id=id_producto).first()
        
        if not producto:
            session.close()
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Guardar información del producto antes de eliminarlo
        producto_info = {
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo': producto.codigo
        }
        
        session.delete(producto)
        session.commit()
        session.close()
        
        return jsonify({
            'mensaje': f'Producto "{producto_info["nombre"]}" eliminado correctamente',
            'producto_eliminado': producto_info
        })
        
    except Exception as e:
        print(f"❌ Error eliminando producto {id_producto}: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

# 🎯 FUNCIONES ESPECIALIZADAS

@productos_bp.route('/categoria/<int:categoria_id>')
@productos_bp.route('/api/categoria/<int:categoria_id>')
def obtener_productos_categoria(categoria_id):
    """
    📂 OBTENER PRODUCTOS POR CATEGORÍA
    Devuelve productos filtrados por categoría específica
    """
    try:
        session = Session()
        productos = session.query(Producto).filter_by(categoria_id=categoria_id).all()
        productos_dict = [producto_to_dict(producto) for producto in productos]
        session.close()
        
        return jsonify({
            'productos': productos_dict,
            'total': len(productos_dict),
            'categoria_id': categoria_id
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo productos de categoría {categoria_id}: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@productos_bp.route('/stats')
@productos_bp.route('/api/stats') 
def obtener_estadisticas_productos():
    """
    📊 ESTADÍSTICAS DE PRODUCTOS
    Devuelve métricas generales de productos
    """
    try:
        from sqlalchemy import func
        session = Session()
        
        total = session.query(Producto).count()
        disponibles = session.query(Producto).filter_by(disponible=True).count()
        no_disponibles = session.query(Producto).filter_by(disponible=False).count()
        por_categoria = session.query(
            Categoria.titulo,
            func.count(Producto.id).label('cantidad')
        ).outerjoin(Producto).group_by(Categoria.id).all()
        
        session.close()
        
        return jsonify({
            'total': total,
            'disponibles': disponibles,
            'no_disponibles': no_disponibles,
            'por_categoria': [{'nombre': cat[0], 'cantidad': cat[1]} for cat in por_categoria]
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas de productos: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
