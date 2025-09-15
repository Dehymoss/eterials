"""
📊 ENDPOINT ESPECÍFICO PARA ESTADÍSTICAS
Responsabilidad única: Métricas, reportes y análisis del sistema de menú
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timedelta

# Blueprint específico para estadísticas
estadisticas_bp = Blueprint('estadisticas', __name__)

# Configuración de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

# Importar modelos
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria
from modulos.backend.menu.database.models.ingrediente import Ingrediente

@estadisticas_bp.route('/test', methods=['GET'])
def test_endpoint():
    """🧪 ENDPOINT DE PRUEBA"""
    return jsonify({
        'mensaje': 'Blueprint de estadísticas funcionando correctamente',
        'status': 'OK',
        'blueprint': 'estadisticas'
    })

@estadisticas_bp.route('/', methods=['GET'])
@estadisticas_bp.route('/general', methods=['GET'])
def obtener_estadisticas_generales():
    """
    📊 ESTADÍSTICAS GENERALES DEL SISTEMA
    Devuelve métricas principales del menú
    """
    try:
        session = Session()
        
        # Estadísticas básicas
        total_productos = session.query(Producto).count()
        total_categorias = session.query(Categoria).count()
        total_subcategorias = session.query(Subcategoria).count()
        total_ingredientes = session.query(Ingrediente).count()
        
        # Productos por estado
        productos_activos = session.query(Producto).filter(Producto.disponible == True).count()
        productos_inactivos = total_productos - productos_activos
        
        # Precios
        productos_con_precio = session.query(Producto).filter(
            Producto.precio.isnot(None), 
            Producto.precio > 0
        ).all()
        
        if productos_con_precio:
            precios = [float(p.precio) for p in productos_con_precio]
            precio_promedio = round(sum(precios) / len(precios), 2)
            precio_minimo = round(min(precios), 2)
            precio_maximo = round(max(precios), 2)
        else:
            precio_promedio = precio_minimo = precio_maximo = 0.0
        
        # Productos por categoría
        productos_por_categoria = []
        categorias = session.query(Categoria).all()
        for categoria in categorias:
            count = session.query(Producto).filter(Producto.categoria_id == categoria.id).count()
            productos_por_categoria.append({
                'categoria': categoria.titulo,
                'total': count
            })
        
        session.close()
        
        estadisticas = {
            'resumen': {
                'total_productos': total_productos,
                'total_categorias': total_categorias,
                'total_subcategorias': total_subcategorias,
                'total_ingredientes': total_ingredientes,
                'productos_activos': productos_activos,
                'productos_inactivos': productos_inactivos
            },
            'precios': {
                'promedio': precio_promedio,
                'minimo': precio_minimo,
                'maximo': precio_maximo,
                'productos_con_precio': len(productos_con_precio)
            },
            'distribucion': {
                'por_categoria': productos_por_categoria
            },
            'timestamp': datetime.now().isoformat(),
            'mensaje': f'Estadísticas generadas para {total_productos} productos'
        }
        
        return jsonify(estadisticas)
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas generales: {e}")
        return jsonify({'error': str(e)}), 500

@estadisticas_bp.route('/productos', methods=['GET'])
def obtener_estadisticas_productos():
    """
    🛒 ESTADÍSTICAS ESPECÍFICAS DE PRODUCTOS
    Análisis detallado por tipo, estado y características
    """
    try:
        session = Session()
        
        # Productos por tipo
        productos_simple = session.query(Producto).filter(
            Producto.tipo_producto == 'simple'
        ).count()
        productos_preparado = session.query(Producto).filter(
            Producto.tipo_producto == 'preparado'
        ).count()
        
        # Productos con imágenes
        productos_con_imagen = session.query(Producto).filter(
            Producto.imagen_url.isnot(None),
            Producto.imagen_url != ''
        ).count()
        productos_sin_imagen = session.query(Producto).filter(
            (Producto.imagen_url.is_(None)) | (Producto.imagen_url == '')
        ).count()
        
        # Productos con código
        productos_con_codigo = session.query(Producto).filter(
            Producto.codigo.isnot(None),
            Producto.codigo != ''
        ).count()
        
        # Top productos por precio
        productos_caros = session.query(Producto).filter(
            Producto.precio.isnot(None)
        ).order_by(Producto.precio.desc()).limit(5).all()
        
        top_caros = []
        for producto in productos_caros:
            top_caros.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio) if producto.precio else 0,
                'categoria': producto.categoria.titulo if producto.categoria else 'Sin categoría'
            })
        
        session.close()
        
        estadisticas = {
            'por_tipo': {
                'simple': productos_simple,
                'preparado': productos_preparado
            },
            'imagenes': {
                'con_imagen': productos_con_imagen,
                'sin_imagen': productos_sin_imagen,
                'porcentaje_con_imagen': round((productos_con_imagen / (productos_con_imagen + productos_sin_imagen)) * 100, 1) if (productos_con_imagen + productos_sin_imagen) > 0 else 0
            },
            'codificacion': {
                'con_codigo': productos_con_codigo,
                'porcentaje_codificado': round((productos_con_codigo / (productos_simple + productos_preparado)) * 100, 1) if (productos_simple + productos_preparado) > 0 else 0
            },
            'top_precios': top_caros,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(estadisticas)
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas de productos: {e}")
        return jsonify({'error': str(e)}), 500

@estadisticas_bp.route('/categorias', methods=['GET'])
def obtener_estadisticas_categorias():
    """
    📂 ESTADÍSTICAS DE CATEGORÍAS Y SUBCATEGORÍAS
    Análisis de la estructura jerárquica del menú
    """
    try:
        session = Session()
        
        # Estadísticas por categoría
        categorias_stats = []
        categorias = session.query(Categoria).all()
        
        for categoria in categorias:
            # Contar productos en esta categoría
            total_productos = session.query(Producto).filter(
                Producto.categoria_id == categoria.id
            ).count()
            
            # Contar productos activos
            productos_activos = session.query(Producto).filter(
                Producto.categoria_id == categoria.id,
                Producto.disponible == True
            ).count()
            
            # Contar subcategorías
            total_subcategorias = session.query(Subcategoria).filter(
                Subcategoria.categoria_id == categoria.id
            ).count()
            
            # Precio promedio en la categoría
            productos_con_precio = session.query(Producto).filter(
                Producto.categoria_id == categoria.id,
                Producto.precio.isnot(None),
                Producto.precio > 0
            ).all()
            
            precio_promedio = 0
            if productos_con_precio:
                precio_promedio = round(sum(float(p.precio) for p in productos_con_precio) / len(productos_con_precio), 2)
            
            categorias_stats.append({
                'id': categoria.id,
                'nombre': categoria.titulo,
                'total_productos': total_productos,
                'productos_activos': productos_activos,
                'total_subcategorias': total_subcategorias,
                'precio_promedio': precio_promedio,
                'activa': getattr(categoria, 'activa', True)
            })
        
        # Ordenar por total de productos
        categorias_stats.sort(key=lambda x: x['total_productos'], reverse=True)
        
        session.close()
        
        estadisticas = {
            'total_categorias': len(categorias_stats),
            'categorias': categorias_stats,
            'categoria_mas_productos': categorias_stats[0] if categorias_stats else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(estadisticas)
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas de categorías: {e}")
        return jsonify({'error': str(e)}), 500

@estadisticas_bp.route('/salud', methods=['GET'])
@estadisticas_bp.route('/health', methods=['GET'])
def verificar_salud_sistema():
    """
    🏥 VERIFICACIÓN DE SALUD DEL SISTEMA
    Diagnóstico de integridad de datos
    """
    try:
        session = Session()
        problemas = []
        
        # Verificar productos sin categoría
        productos_sin_categoria = session.query(Producto).filter(
            Producto.categoria_id.is_(None)
        ).count()
        if productos_sin_categoria > 0:
            problemas.append(f"{productos_sin_categoria} productos sin categoría asignada")
        
        # Verificar productos sin precio
        productos_sin_precio = session.query(Producto).filter(
            (Producto.precio.is_(None)) | (Producto.precio <= 0)
        ).count()
        if productos_sin_precio > 0:
            problemas.append(f"{productos_sin_precio} productos sin precio válido")
        
        # Verificar productos sin nombre
        productos_sin_nombre = session.query(Producto).filter(
            (Producto.nombre.is_(None)) | (Producto.nombre == '')
        ).count()
        if productos_sin_nombre > 0:
            problemas.append(f"{productos_sin_nombre} productos sin nombre")
        
        # Verificar categorías sin productos
        categorias_vacias = []
        categorias = session.query(Categoria).all()
        for categoria in categorias:
            count = session.query(Producto).filter(Producto.categoria_id == categoria.id).count()
            if count == 0:
                categorias_vacias.append(categoria.titulo)
        
        if categorias_vacias:
            problemas.append(f"{len(categorias_vacias)} categorías sin productos: {', '.join(categorias_vacias)}")
        
        # Verificar integridad de subcategorías
        subcategorias_huerfanas = session.query(Subcategoria).filter(
            Subcategoria.categoria_id.is_(None)
        ).count()
        if subcategorias_huerfanas > 0:
            problemas.append(f"{subcategorias_huerfanas} subcategorías sin categoría padre")
        
        session.close()
        
        # Determinar estado general
        if not problemas:
            estado = "EXCELENTE"
            mensaje = "Sistema en perfectas condiciones"
        elif len(problemas) <= 2:
            estado = "BUENO"
            mensaje = "Sistema estable con problemas menores"
        elif len(problemas) <= 5:
            estado = "REGULAR"
            mensaje = "Sistema funcional pero necesita atención"
        else:
            estado = "CRÍTICO"
            mensaje = "Sistema requiere mantenimiento urgente"
        
        diagnostico = {
            'estado': estado,
            'mensaje': mensaje,
            'total_problemas': len(problemas),
            'problemas_detectados': problemas,
            'timestamp': datetime.now().isoformat(),
            'recomendacion': "Revisar y corregir los problemas identificados" if problemas else "Sistema optimizado"
        }
        
        return jsonify(diagnostico)
        
    except Exception as e:
        print(f"❌ Error en verificación de salud: {e}")
        return jsonify({'error': str(e)}), 500

@estadisticas_bp.route('/resumen', methods=['GET'])
def obtener_resumen_completo():
    """
    📋 RESUMEN EJECUTIVO COMPLETO
    Dashboard principal con todas las métricas clave
    """
    try:
        session = Session()
        
        # Métricas básicas
        total_productos = session.query(Producto).count()
        total_categorias = session.query(Categoria).count()
        productos_activos = session.query(Producto).filter(Producto.disponible == True).count()
        
        # Precios
        productos_con_precio = session.query(Producto).filter(
            Producto.precio.isnot(None), Producto.precio > 0
        ).all()
        precio_promedio = 0
        if productos_con_precio:
            precio_promedio = round(sum(float(p.precio) for p in productos_con_precio) / len(productos_con_precio), 2)
        
        # Categoría más popular
        categoria_mas_productos = session.query(
            Categoria.titulo, func.count(Producto.id).label('total')
        ).join(Producto).group_by(Categoria.id).order_by(func.count(Producto.id).desc()).first()
        
        # Completitud de datos
        productos_con_imagen = session.query(Producto).filter(
            Producto.imagen_url.isnot(None), Producto.imagen_url != ''
        ).count()
        productos_con_codigo = session.query(Producto).filter(
            Producto.codigo.isnot(None), Producto.codigo != ''
        ).count()
        
        # Cálculos de porcentajes
        porcentaje_activos = round((productos_activos / total_productos) * 100, 1) if total_productos > 0 else 0
        porcentaje_con_imagen = round((productos_con_imagen / total_productos) * 100, 1) if total_productos > 0 else 0
        porcentaje_con_codigo = round((productos_con_codigo / total_productos) * 100, 1) if total_productos > 0 else 0
        
        session.close()
        
        resumen = {
            'metricas_principales': {
                'total_productos': total_productos,
                'total_categorias': total_categorias,
                'productos_activos': productos_activos,
                'porcentaje_activos': porcentaje_activos,
                'precio_promedio': precio_promedio
            },
            'completitud_datos': {
                'productos_con_imagen': productos_con_imagen,
                'porcentaje_con_imagen': porcentaje_con_imagen,
                'productos_con_codigo': productos_con_codigo,
                'porcentaje_con_codigo': porcentaje_con_codigo
            },
            'categoria_destacada': {
                'nombre': categoria_mas_productos[0] if categoria_mas_productos else 'N/A',
                'total_productos': categoria_mas_productos[1] if categoria_mas_productos else 0
            },
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        return jsonify(resumen)
        
    except Exception as e:
        print(f"❌ Error obteniendo resumen completo: {e}")
        return jsonify({'error': str(e)}), 500
