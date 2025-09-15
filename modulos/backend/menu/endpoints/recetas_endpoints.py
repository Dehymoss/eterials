"""
ENDPOINTS PARA GESTIÓN DE RECETAS
Módulo separado para todas las funciones relacionadas con recetas
Conecta con guardar_receta() del sistema principal
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
import os
import traceback

# Importar modelos necesarios
from ..database.models.producto import Producto
from ..database.models.categoria import Categoria
from ..database.models.ingrediente import Ingrediente

# Configuración de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

# Crear blueprint para recetas
recetas_bp = Blueprint('recetas', __name__)

def receta_to_dict(producto):
    """Convierte un producto-receta a diccionario optimizado para el frontend de recetas"""
    
    # Función helper para acceso seguro a relaciones
    def safe_get_relation_attr(obj, attr, default=None):
        try:
            if obj:
                return getattr(obj, attr, default)
            return default
        except:
            return default
    
    receta_dict = {
        # Información básica
        'id': producto.id,
        'codigo': producto.codigo,
        'nombre': producto.nombre,
        'descripcion': producto.descripcion or '',
        'precio': float(producto.precio) if producto.precio else 0.0,
        'imagen_url': producto.imagen_url or '',
        
        # Categorización
        'categoria_id': producto.categoria_id,
        'categoria_nombre': safe_get_relation_attr(producto.categoria, 'titulo', 'Sin categoría'),
        'subcategoria_id': producto.subcategoria_id,
        'subcategoria_nombre': safe_get_relation_attr(producto.subcategoria, 'nombre', ''),
        
        # Información de preparación
        'tiempo_preparacion': producto.tiempo_preparacion or '',
        'instrucciones_preparacion': getattr(producto, 'instrucciones_preparacion', '') or '',
        'notas_cocina': getattr(producto, 'notas_cocina', '') or '',
        
        # Estado
        'disponible': producto.disponible,
        'tipo_producto': getattr(producto, 'tipo_producto', 'preparado'),
        'es_especial': getattr(producto, 'es_especial', False),
        'popularidad': producto.popularidad or 0,
        
        # Metadatos
        'fecha_creacion': getattr(producto, 'fecha_creacion', None),
        'fecha_actualizacion': getattr(producto, 'fecha_actualizacion', None)
    }
    
    # Obtener ingredientes asociados con detalles completos
    try:
        ingredientes = producto.ingredientes if producto.ingredientes else []
        receta_dict['ingredientes'] = []
        receta_dict['total_ingredientes'] = len(ingredientes)
        
        for ingrediente in ingredientes:
            receta_dict['ingredientes'].append({
                'id': ingrediente.id,
                'nombre': ingrediente.nombre,
                'cantidad': ingrediente.cantidad or '',
                'unidad': ingrediente.unidad or 'ud',
                'notas': getattr(ingrediente, 'notas', '') or '',
                'obligatorio': getattr(ingrediente, 'obligatorio', True),
                'costo': float(getattr(ingrediente, 'costo', 0.0))
            })
    except Exception as e:
        print(f"Error obteniendo ingredientes: {e}")
        receta_dict['ingredientes'] = []
        receta_dict['total_ingredientes'] = 0
    
    return receta_dict

@recetas_bp.route('/', methods=['GET'])
@recetas_bp.route('/api/recetas', methods=['GET'])
def obtener_recetas():
    """Obtener todas las recetas (productos de tipo 'preparado')"""
    session = Session()
    try:
        # Filtrar solo productos de tipo 'preparado' que son recetas
        recetas = session.query(Producto)\
                        .options(joinedload(Producto.categoria))\
                        .options(joinedload(Producto.subcategoria))\
                        .options(joinedload(Producto.ingredientes))\
                        .filter(Producto.tipo_producto == 'preparado')\
                        .all()
        
        recetas_data = [receta_to_dict(r) for r in recetas]
        
        return jsonify({
            'success': True,
            'recetas': recetas_data,
            'total': len(recetas_data),
            'mensaje': f'Se encontraron {len(recetas_data)} recetas'
        })
        
    except Exception as e:
        session.rollback()
        print(f"Error obteniendo recetas: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error obteniendo recetas: {str(e)}'
        }), 500
    finally:
        session.close()

@recetas_bp.route('/<int:receta_id>', methods=['GET'])
@recetas_bp.route('/api/recetas/<int:receta_id>', methods=['GET'])
def obtener_receta(receta_id):
    """Obtener una receta específica con todos sus detalles"""
    session = Session()
    try:
        receta = session.query(Producto)\
                       .options(joinedload(Producto.categoria))\
                       .options(joinedload(Producto.subcategoria))\
                       .options(joinedload(Producto.ingredientes))\
                       .filter(Producto.id == receta_id)\
                       .filter(Producto.tipo_producto == 'preparado')\
                       .first()
        
        if not receta:
            return jsonify({
                'success': False,
                'error': 'Receta no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'receta': receta_to_dict(receta)
        })
        
    except Exception as e:
        session.rollback()
        print(f"Error obteniendo receta {receta_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error obteniendo receta: {str(e)}'
        }), 500
    finally:
        session.close()

@recetas_bp.route('/', methods=['POST'])
@recetas_bp.route('/api/recetas', methods=['POST'])
def crear_receta():
    """Crear una nueva receta completa con ingredientes"""
    session = Session()
    try:
        # Obtener datos del request
        if request.content_type and 'application/json' in request.content_type:
            datos = request.get_json()
        else:
            return jsonify({
                'success': False,
                'error': 'Se requiere Content-Type: application/json'
            }), 400
        
        if not datos:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400
        
        # Validaciones básicas
        campos_requeridos = ['nombre', 'precio']
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {campo}'
                }), 400
        
        # Validar que el nombre no existe
        nombre_receta = datos['nombre'].strip()
        receta_existente = session.query(Producto)\
                                 .filter(Producto.nombre.ilike(f'%{nombre_receta}%'))\
                                 .filter(Producto.tipo_producto == 'preparado')\
                                 .first()
        
        if receta_existente:
            return jsonify({
                'success': False,
                'error': f'Ya existe una receta con el nombre "{nombre_receta}"'
            }), 409
        
        # Validar precio
        try:
            precio = float(datos['precio'])
            if precio <= 0:
                return jsonify({
                    'success': False,
                    'error': 'El precio debe ser mayor a 0'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Precio inválido'
            }), 400
        
        # Preparar datos del producto-receta
        datos_producto = {
            'nombre': nombre_receta,
            'descripcion': datos.get('descripcion', ''),
            'precio': precio,
            'categoria_id': datos.get('categoria_id'),
            'subcategoria_id': datos.get('subcategoria_id'),
            'imagen_url': datos.get('imagen_url', ''),
            'tiempo_preparacion': datos.get('tiempo_preparacion', ''),
            'instrucciones_preparacion': datos.get('instrucciones_preparacion', ''),
            'notas_cocina': datos.get('notas_cocina', ''),
            'disponible': datos.get('disponible', True),
            'es_especial': datos.get('es_especial', False),
            'tipo_producto': 'preparado'  # Siempre preparado para recetas
        }
        
        # Crear el producto-receta
        nueva_receta = Producto(**datos_producto)
        session.add(nueva_receta)
        session.flush()  # Para obtener el ID sin hacer commit completo
        
        # Procesar ingredientes si existen
        ingredientes_data = datos.get('ingredientes', [])
        ingredientes_creados = []
        
        for ing_data in ingredientes_data:
            if ing_data.get('nombre'):  # Solo crear si tiene nombre
                ingrediente = Ingrediente(
                    producto_id=nueva_receta.id,
                    nombre=ing_data['nombre'].strip(),
                    cantidad=ing_data.get('cantidad', ''),
                    unidad=ing_data.get('unidad', 'ud'),
                    notas=ing_data.get('notas', ''),
                    obligatorio=ing_data.get('obligatorio', True),
                    costo=float(ing_data.get('costo', 0.0)),
                    activo=True
                )
                session.add(ingrediente)
                ingredientes_creados.append(ingrediente)
        
        # Confirmar todos los cambios
        session.commit()
        
        # Recargar la receta con todas las relaciones
        receta_completa = session.query(Producto)\
                               .options(joinedload(Producto.categoria))\
                               .options(joinedload(Producto.subcategoria))\
                               .options(joinedload(Producto.ingredientes))\
                               .filter(Producto.id == nueva_receta.id)\
                               .first()
        
        return jsonify({
            'success': True,
            'mensaje': 'Receta creada exitosamente',
            'receta': receta_to_dict(receta_completa),
            'ingredientes_agregados': len(ingredientes_creados)
        }), 201
        
    except Exception as e:
        session.rollback()
        print(f"Error creando receta: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
    finally:
        session.close()

@recetas_bp.route('/<int:receta_id>', methods=['PUT'])
@recetas_bp.route('/api/recetas/<int:receta_id>', methods=['PUT'])
def actualizar_receta(receta_id):
    """Actualizar una receta existente"""
    session = Session()
    try:
        # Obtener datos del request
        if request.content_type and 'application/json' in request.content_type:
            datos = request.get_json()
        else:
            return jsonify({
                'success': False,
                'error': 'Se requiere Content-Type: application/json'
            }), 400
        
        # Buscar la receta
        receta = session.query(Producto)\
                       .filter(Producto.id == receta_id)\
                       .filter(Producto.tipo_producto == 'preparado')\
                       .first()
        
        if not receta:
            return jsonify({
                'success': False,
                'error': 'Receta no encontrada'
            }), 404
        
        # Validar nombre único si se está cambiando
        if 'nombre' in datos and datos['nombre'].strip() != receta.nombre:
            nombre_nuevo = datos['nombre'].strip()
            receta_existente = session.query(Producto)\
                                    .filter(Producto.nombre.ilike(f'%{nombre_nuevo}%'))\
                                    .filter(Producto.tipo_producto == 'preparado')\
                                    .filter(Producto.id != receta_id)\
                                    .first()
            
            if receta_existente:
                return jsonify({
                    'success': False,
                    'error': f'Ya existe otra receta con el nombre "{nombre_nuevo}"'
                }), 409
        
        # Validar precio si se está cambiando
        if 'precio' in datos:
            try:
                precio = float(datos['precio'])
                if precio <= 0:
                    return jsonify({
                        'success': False,
                        'error': 'El precio debe ser mayor a 0'
                    }), 400
                datos['precio'] = precio
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Precio inválido'
                }), 400
        
        # Actualizar campos del producto-receta
        campos_actualizables = [
            'nombre', 'descripcion', 'precio', 'categoria_id', 'subcategoria_id',
            'imagen_url', 'tiempo_preparacion', 'instrucciones_preparacion',
            'notas_cocina', 'disponible', 'es_especial'
        ]
        
        for campo in campos_actualizables:
            if campo in datos:
                setattr(receta, campo, datos[campo])
        
        # Actualizar ingredientes si se proporcionan
        if 'ingredientes' in datos:
            # Eliminar ingredientes existentes
            session.query(Ingrediente)\
                   .filter(Ingrediente.producto_id == receta_id)\
                   .delete()
            
            # Agregar nuevos ingredientes
            for ing_data in datos['ingredientes']:
                if ing_data.get('nombre'):
                    ingrediente = Ingrediente(
                        producto_id=receta_id,
                        nombre=ing_data['nombre'].strip(),
                        cantidad=ing_data.get('cantidad', ''),
                        unidad=ing_data.get('unidad', 'ud'),
                        notas=ing_data.get('notas', ''),
                        obligatorio=ing_data.get('obligatorio', True),
                        costo=float(ing_data.get('costo', 0.0)),
                        activo=True
                    )
                    session.add(ingrediente)
        
        session.commit()
        
        # Recargar con relaciones
        receta_actualizada = session.query(Producto)\
                                   .options(joinedload(Producto.categoria))\
                                   .options(joinedload(Producto.subcategoria))\
                                   .options(joinedload(Producto.ingredientes))\
                                   .filter(Producto.id == receta_id)\
                                   .first()
        
        return jsonify({
            'success': True,
            'mensaje': 'Receta actualizada exitosamente',
            'receta': receta_to_dict(receta_actualizada)
        })
        
    except Exception as e:
        session.rollback()
        print(f"Error actualizando receta {receta_id}: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
    finally:
        session.close()

@recetas_bp.route('/<int:receta_id>', methods=['DELETE'])
@recetas_bp.route('/api/recetas/<int:receta_id>', methods=['DELETE'])
def eliminar_receta(receta_id):
    """Eliminar una receta y todos sus ingredientes"""
    session = Session()
    try:
        receta = session.query(Producto)\
                       .filter(Producto.id == receta_id)\
                       .filter(Producto.tipo_producto == 'preparado')\
                       .first()
        
        if not receta:
            return jsonify({
                'success': False,
                'error': 'Receta no encontrada'
            }), 404
        
        nombre_receta = receta.nombre
        
        # Eliminar ingredientes asociados primero
        ingredientes_eliminados = session.query(Ingrediente)\
                                        .filter(Ingrediente.producto_id == receta_id)\
                                        .count()
        
        session.query(Ingrediente)\
               .filter(Ingrediente.producto_id == receta_id)\
               .delete()
        
        # Eliminar la receta
        session.delete(receta)
        session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': f'Receta "{nombre_receta}" eliminada exitosamente',
            'ingredientes_eliminados': ingredientes_eliminados
        })
        
    except Exception as e:
        session.rollback()
        print(f"Error eliminando receta {receta_id}: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
    finally:
        session.close()

@recetas_bp.route('/buscar', methods=['GET'])
@recetas_bp.route('/api/recetas/buscar', methods=['GET'])
def buscar_recetas():
    """Buscar recetas por nombre, categoría o ingredientes"""
    session = Session()
    try:
        termino = request.args.get('q', '').strip()
        categoria_id = request.args.get('categoria_id')
        
        if not termino and not categoria_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere un término de búsqueda o categoría'
            }), 400
        
        query = session.query(Producto)\
                      .options(joinedload(Producto.categoria))\
                      .options(joinedload(Producto.subcategoria))\
                      .options(joinedload(Producto.ingredientes))\
                      .filter(Producto.tipo_producto == 'preparado')
        
        # Filtrar por término de búsqueda
        if termino:
            query = query.filter(
                Producto.nombre.ilike(f'%{termino}%') |
                Producto.descripcion.ilike(f'%{termino}%') |
                Producto.instrucciones_preparacion.ilike(f'%{termino}%')
            )
        
        # Filtrar por categoría
        if categoria_id:
            try:
                categoria_id = int(categoria_id)
                query = query.filter(Producto.categoria_id == categoria_id)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'ID de categoría inválido'
                }), 400
        
        recetas = query.all()
        recetas_data = [receta_to_dict(r) for r in recetas]
        
        return jsonify({
            'success': True,
            'recetas': recetas_data,
            'total': len(recetas_data),
            'termino_busqueda': termino,
            'categoria_id': categoria_id
        })
        
    except Exception as e:
        session.rollback()
        print(f"Error buscando recetas: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
    finally:
        session.close()

# Endpoint de compatibilidad con el sistema anterior
@recetas_bp.route('/guardar-receta', methods=['POST'])
def guardar_receta_legacy():
    """Endpoint de compatibilidad con el sistema anterior"""
    # Redirigir al endpoint nuevo
    return crear_receta()
