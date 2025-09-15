"""
API Backend Cocina - Sistema de Gestión de Restaurante
API especializada para obtener datos de recetas desde el libro de recetas
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from modulos.backend.menu.database.base import Base
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.ingrediente import Ingrediente
from modulos.backend.menu.database.models.categoria import Categoria
import os

# Crear engine de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'menu', 'database', 'menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear blueprint para API de cocina
cocina_api_bp = Blueprint('cocina_api', __name__, url_prefix='/api/cocina')

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Se cierra en cada endpoint

@cocina_api_bp.route('/dashboard', methods=['GET'])
def dashboard_cocina():
    """Dashboard con estadísticas de cocina"""
    db = get_db()
    try:
        # Estadísticas básicas
        total_productos = db.query(Producto).count()
        productos_preparados = db.query(Producto).filter(Producto.tipo_producto == 'preparado').count()
        productos_simples = db.query(Producto).filter(Producto.tipo_producto == 'simple').count()
        total_categorias = db.query(Categoria).count()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'total_productos': total_productos,
                'productos_preparados': productos_preparados,
                'productos_simples': productos_simples,
                'total_categorias': total_categorias
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error obteniendo dashboard: {str(e)}'}), 500
    finally:
        db.close()

@cocina_api_bp.route('/recetas', methods=['GET'])
def obtener_recetas():
    """Obtiene todas las recetas de productos preparados"""
    db = get_db()
    try:
        # Obtener solo productos preparados que tienen recetas
        productos_preparados = db.query(Producto).filter(
            Producto.tipo_producto == 'preparado'
        ).all()
        
        recetas = []
        for producto in productos_preparados:
            # Obtener categoría
            categoria = db.query(Categoria).filter(Categoria.id == producto.categoria_id).first()
            categoria_nombre = categoria.nombre if categoria else "Sin categoría"
            
            receta = {
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'imagen_url': producto.imagen_url,
                'categoria': categoria_nombre,
                'tiempo_preparacion': producto.tiempo_preparacion,
                'precio': float(producto.precio) if producto.precio else 0,
                'disponible': producto.disponible,
                'tiene_ingredientes': len(producto.ingredientes) > 0,
                'total_ingredientes': len(producto.ingredientes)
            }
            recetas.append(receta)
        
        return jsonify({
            'success': True,
            'recetas': recetas,
            'total': len(recetas)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener recetas: {str(e)}'
        }), 500
    finally:
        db.close()

@cocina_api_bp.route('/receta/<int:producto_id>', methods=['GET'])
def obtener_detalle_receta(producto_id):
    """Obtiene el detalle completo de una receta específica"""
    db = get_db()
    try:
        # Obtener producto preparado
        producto = db.query(Producto).filter(
            Producto.id == producto_id,
            Producto.tipo_producto == 'preparado'
        ).first()
        
        if not producto:
            return jsonify({
                'success': False,
                'error': 'Receta no encontrada'
            }), 404
        
        # Obtener categoría
        categoria = db.query(Categoria).filter(Categoria.id == producto.categoria_id).first()
        categoria_nombre = categoria.nombre if categoria else "Sin categoría"
        
        # Obtener ingredientes
        ingredientes = []
        for ingrediente in producto.ingredientes:
            ingredientes.append({
                'id': ingrediente.id,
                'nombre': ingrediente.nombre,
                'cantidad': ingrediente.cantidad,
                'unidad': ingrediente.unidad,
                'notas': ingrediente.notas
            })
        
        # Preparar datos completos de la receta
        receta_completa = {
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'imagen_url': producto.imagen_url,
            'categoria': categoria_nombre,
            'precio': float(producto.precio) if producto.precio else 0,
            'tiempo_preparacion': producto.tiempo_preparacion,
            'instrucciones_preparacion': producto.instrucciones_preparacion,
            'notas_cocina': producto.notas_cocina,
            'ingredientes': ingredientes,
            'total_ingredientes': len(ingredientes),
            'disponible': producto.disponible
        }
        
        return jsonify({
            'success': True,
            'receta': receta_completa
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener detalle de receta: {str(e)}'
        }), 500
    finally:
        db.close()

@cocina_api_bp.route('/buscar', methods=['GET'])
def buscar_recetas():
    """Busca recetas por nombre o categoría"""
    db = get_db()
    try:
        termino = request.args.get('q', '').strip()
        
        if not termino:
            return jsonify({
                'success': True,
                'recetas': [],
                'mensaje': 'Proporciona un término de búsqueda'
            })
        
        # Buscar en productos preparados
        productos = db.query(Producto).filter(
            Producto.tipo_producto == 'preparado',
            Producto.nombre.ilike(f'%{termino}%')
        ).all()
        
        # También buscar por categoría
        categorias = db.query(Categoria).filter(
            Categoria.nombre.ilike(f'%{termino}%')
        ).all()
        
        productos_por_categoria = []
        for categoria in categorias:
            productos_cat = db.query(Producto).filter(
                Producto.categoria_id == categoria.id,
                Producto.tipo_producto == 'preparado'
            ).all()
            productos_por_categoria.extend(productos_cat)
        
        # Combinar resultados sin duplicados
        todos_productos = list(set(productos + productos_por_categoria))
        
        recetas = []
        for producto in todos_productos:
            categoria = db.query(Categoria).filter(Categoria.id == producto.categoria_id).first()
            categoria_nombre = categoria.nombre if categoria else "Sin categoría"
            
            receta = {
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'imagen_url': producto.imagen_url,
                'categoria': categoria_nombre,
                'tiempo_preparacion': producto.tiempo_preparacion,
                'total_ingredientes': len(producto.ingredientes)
            }
            recetas.append(receta)
        
        return jsonify({
            'success': True,
            'recetas': recetas,
            'total': len(recetas),
            'termino_busqueda': termino
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en búsqueda: {str(e)}'
        }), 500
    finally:
        db.close()

@cocina_api_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas básicas para el dashboard"""
    db = get_db()
    try:
        total_recetas = db.query(Producto).filter(Producto.tipo_producto == 'preparado').count()
        recetas_disponibles = db.query(Producto).filter(
            Producto.tipo_producto == 'preparado',
            Producto.disponible == True
        ).count()
        
        total_ingredientes = db.query(Ingrediente).count()
        
        categorias_con_recetas = db.query(Categoria).join(Producto).filter(
            Producto.tipo_producto == 'preparado'
        ).distinct().count()
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'total_recetas': total_recetas,
                'recetas_disponibles': recetas_disponibles,
                'total_ingredientes': total_ingredientes,
                'categorias_activas': categorias_con_recetas
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener estadísticas: {str(e)}'
        }), 500
    finally:
        db.close()
