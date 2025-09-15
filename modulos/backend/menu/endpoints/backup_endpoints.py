"""
💾 ENDPOINT ESPECÍFICO PARA BACKUP Y EXPORTACIÓN
Responsabilidad única: Respaldos, exportación y restauración de datos
"""

from flask import Blueprint, request, jsonify, render_template, send_file, make_response
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import os
import json
import tempfile
import zipfile
from datetime import datetime
from io import BytesIO

# Importar modelos (rutas correctas)
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria
from modulos.backend.menu.database.models.ingrediente import Ingrediente

backup_bp = Blueprint('backup', __name__)

# Configuración de base de datos (igual que estadísticas)
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

# Función helper para obtener sesión
def get_db_session():
    """
    🗃️ CONFIGURACIÓN DE SESIÓN DE BASE DE DATOS
    """
    return Session()

@backup_bp.route('/test', methods=['GET'])
def test_backup():
    """
    🧪 TEST DE ENDPOINT DE BACKUP
    """
    return jsonify({
        'status': 'OK',
        'mensaje': 'Blueprint de backup funcionando correctamente',
        'blueprint': 'backup'
    })

@backup_bp.route('/info', methods=['GET'])
def info_sistema():
    """
    ℹ️ INFORMACIÓN DEL SISTEMA PARA BACKUP
    Proporciona estadísticas básicas antes del backup
    """
    try:
        session = get_db_session()
        
        # Contar registros
        info = {
            'timestamp': datetime.now().isoformat(),
            'base_datos': {
                'total_productos': session.query(func.count(Producto.id)).scalar() or 0,
                'productos_activos': session.query(func.count(Producto.id)).filter(Producto.disponible == True).scalar() or 0,
                'total_categorias': session.query(func.count(Categoria.id)).scalar() or 0,
                'categorias_activas': session.query(func.count(Categoria.id)).filter(Categoria.activa == True).scalar() or 0,
                'total_subcategorias': session.query(func.count(Subcategoria.id)).scalar() or 0,
                'total_ingredientes': session.query(func.count(Ingrediente.id)).scalar() or 0
            },
            'archivos': {
                'ruta_base_datos': os.path.join(os.path.dirname(__file__), '..', 'database', 'menu.db'),
                'ruta_uploads': os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads'),
                'base_datos_existe': os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'database', 'menu.db')),
                'carpeta_uploads_existe': os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads'))
            },
            'estimacion_tamaños': {
                'productos_mb': round((session.query(func.count(Producto.id)).scalar() or 0) * 0.001, 2),
                'estimado_backup_mb': round((session.query(func.count(Producto.id)).scalar() or 0) * 0.005, 2)
            }
        }
        
        session.close()
        
        return jsonify(info)
        
    except Exception as e:
        return jsonify({
            'error': True,
            'mensaje': f'Error al obtener información del sistema: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@backup_bp.route('/exportar-json', methods=['GET'])
def exportar_json():
    """
    📄 EXPORTAR DATOS A JSON
    Genera un respaldo completo en formato JSON
    """
    try:
        session = get_db_session()
        
        # Recopilar todos los datos
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'productos': [],
            'categorias': [],
            'subcategorias': [],
            'ingredientes': []
        }
        
        # Productos
        productos = session.query(Producto).all()
        for producto in productos:
            backup_data['productos'].append({
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': float(producto.precio) if producto.precio else None,
                'categoria_id': producto.categoria_id,
                'subcategoria_id': producto.subcategoria_id,
                'imagen_url': producto.imagen_url,
                'disponible': producto.disponible,
                'tipo_producto': producto.tipo_producto,
                'tiempo_preparacion': producto.tiempo_preparacion,
                'instrucciones_preparacion': producto.instrucciones_preparacion,
                'notas_cocina': producto.notas_cocina,
                'codigo': producto.codigo
            })
        
        # Categorías
        categorias = session.query(Categoria).all()
        for categoria in categorias:
            backup_data['categorias'].append({
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion,
                'activa': categoria.activa
            })
        
        # Subcategorías
        subcategorias = session.query(Subcategoria).all()
        for subcategoria in subcategorias:
            backup_data['subcategorias'].append({
                'id': subcategoria.id,
                'nombre': subcategoria.nombre,
                'categoria_id': subcategoria.categoria_id
            })
        
        # Ingredientes
        ingredientes = session.query(Ingrediente).all()
        for ingrediente in ingredientes:
            backup_data['ingredientes'].append({
                'id': ingrediente.id,
                'producto_id': ingrediente.producto_id,
                'nombre': ingrediente.nombre,
                'cantidad': ingrediente.cantidad,
                'unidad': ingrediente.unidad
            })
        
        session.close()
        
        # Crear respuesta JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"menu_backup_{timestamp}.json"
        
        response = make_response(json.dumps(backup_data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': True,
            'mensaje': f'Error al generar exportación JSON: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500
