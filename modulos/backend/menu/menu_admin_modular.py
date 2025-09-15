"""
🎯 COORDINADOR PRINCIPAL - MENU ADMIN
Conecta todos los endpoints modulares de forma organizada
"""

from flask import Blueprint, render_template

# Importar endpoints específicos (todos los migrados)
from .endpoints.productos_endpoints import productos_bp
from .endpoints.categorias_endpoints import categorias_bp
from .endpoints.subcategorias_endpoints import subcategorias_bp
from .endpoints.imagenes_endpoints import imagenes_bp
from .endpoints.estadisticas_endpoints import estadisticas_bp
from .endpoints.backup_endpoints import backup_bp
from .endpoints.recetas_endpoints import recetas_bp

# Blueprint principal que coordina todo
menu_admin_bp = Blueprint('menu_admin', __name__, 
                          url_prefix='/menu-admin',
                          template_folder='templates',
                          static_folder='static')

# Registrar sub-blueprints con prefijos específicos (todos migrados)
menu_admin_bp.register_blueprint(productos_bp, url_prefix='/api/productos')
menu_admin_bp.register_blueprint(categorias_bp, url_prefix='/api/categorias') 
menu_admin_bp.register_blueprint(subcategorias_bp, url_prefix='/api/subcategorias')
menu_admin_bp.register_blueprint(imagenes_bp, url_prefix='/api/imagenes')
menu_admin_bp.register_blueprint(estadisticas_bp, url_prefix='/api/estadisticas')
menu_admin_bp.register_blueprint(backup_bp, url_prefix='/api/backup')
menu_admin_bp.register_blueprint(recetas_bp, url_prefix='/api/recetas')

# Ruta principal del admin
@menu_admin_bp.route('/')
@menu_admin_bp.route('/admin')
def admin_dashboard():
    """
    🏠 PÁGINA PRINCIPAL DE ADMINISTRACIÓN
    Sirve el template HTML del panel de control
    """
    return render_template('admin_productos.html')

# Ruta de diagnóstico
@menu_admin_bp.route('/debug/routes')
def debug_routes():
    """
    🔍 DIAGNÓSTICO DE RUTAS
    Muestra todas las rutas registradas en este blueprint
    """
    from flask import current_app
    rules = []
    for rule in current_app.url_map.iter_rules():
        if 'menu_admin' in str(rule.endpoint):
            rules.append({
                'endpoint': str(rule.endpoint),
                'methods': list(rule.methods),
                'rule': str(rule)
            })
    
    return {
        'blueprint': 'menu_admin_modular',
        'total_rutas': len(rules),
        'rutas': rules,
        'mensaje': 'Sistema modular funcionando'
    }

# Compatibilidad con URLs antiguas (para migración gradual)
@menu_admin_bp.route('/productos/sugerir-imagenes', methods=['GET'])
def buscar_imagenes_compatibilidad():
    """
    🔄 COMPATIBILIDAD CON URL ANTIGUA
    Redirige al nuevo endpoint modular de imágenes
    """
    from flask import redirect, url_for, request
    return redirect(url_for('menu_admin.imagenes.buscar_imagenes_web', **request.args))

@menu_admin_bp.route('/backup', methods=['GET'])
def admin_backup_compatibilidad():
    """
    💾 PÁGINA DE BACKUP Y RESTAURACIÓN
    Sirve el template de gestión de backups (compatibilidad)
    """
    from flask import render_template
    return render_template('backup.html')



@menu_admin_bp.route('/api/productos', methods=['GET', 'POST'])
@menu_admin_bp.route('/api/productos/<int:id_producto>', methods=['GET', 'PUT', 'DELETE'])
def productos_compatibilidad(**kwargs):
    """
    🔄 COMPATIBILIDAD CON URLs ANTIGUAS DE PRODUCTOS
    Redirige a los nuevos endpoints modulares
    """
    from flask import redirect, url_for, request
    
    if 'id_producto' in kwargs:
        if request.method == 'GET':
            return redirect(url_for('menu_admin.productos.obtener_producto', id_producto=kwargs['id_producto']))
        elif request.method == 'PUT':
            return redirect(url_for('menu_admin.productos.actualizar_producto', id_producto=kwargs['id_producto']))
        elif request.method == 'DELETE':
            return redirect(url_for('menu_admin.productos.eliminar_producto', id_producto=kwargs['id_producto']))
    else:
        if request.method == 'GET':
            return redirect(url_for('menu_admin.productos.listar_productos'))
        elif request.method == 'POST':
            return redirect(url_for('menu_admin.productos.crear_producto'))

# COMPATIBILIDAD CATEGORÍAS DESHABILITADA - USAR ENDPOINTS MODULARES DIRECTOS
# @menu_admin_bp.route('/api/categorias', methods=['GET', 'POST'])
# @menu_admin_bp.route('/api/categorias/<int:categoria_id>', methods=['GET', 'PUT', 'DELETE'])
# @menu_admin_bp.route('/api/subcategorias/categoria/<int:categoria_id>', methods=['GET'])
# def categorias_compatibilidad(**kwargs):
#     """
#     🔄 COMPATIBILIDAD CON URLs ANTIGUAS DE CATEGORÍAS
#     Redirige a los nuevos endpoints modulares
#     """
#     from flask import redirect, url_for, request
#     
#     if 'categoria_id' in kwargs and '/subcategorias/' in request.path:
#         return redirect(url_for('menu_admin.categorias.listar_subcategorias', categoria_id=kwargs['categoria_id']))
#     elif 'categoria_id' in kwargs:
#         if request.method == 'GET':
#             return redirect(url_for('menu_admin.categorias.listar_categorias'))  # Ajustar según necesidad
#         elif request.method == 'PUT':
#             return redirect(url_for('menu_admin.categorias.actualizar_categoria', categoria_id=kwargs['categoria_id']))
#         elif request.method == 'DELETE':
#             return redirect(url_for('menu_admin.categorias.eliminar_categoria', categoria_id=kwargs['categoria_id']))
#     else:
#         if request.method == 'GET':
#             return redirect(url_for('menu_admin.categorias.manejar_categorias'))
#         elif request.method == 'POST':
#             return redirect(url_for('menu_admin.categorias.manejar_categorias'))

# Compatibilidad para estadísticas (URLs antiguas)
@menu_admin_bp.route('/api/stats', methods=['GET'])
@menu_admin_bp.route('/api/estadisticas', methods=['GET'])
def estadisticas_compatibilidad():
    """
    🔄 COMPATIBILIDAD CON URLs ANTIGUAS DE ESTADÍSTICAS
    Redirige al nuevo endpoint modular de estadísticas
    """
    from flask import redirect, url_for, request
    return redirect(url_for('menu_admin.estadisticas.obtener_resumen_completo', **request.args))

# Compatibilidad para recetas (URLs antiguas)
@menu_admin_bp.route('/guardar-receta', methods=['POST'])
def recetas_compatibilidad():
    """
    🔄 COMPATIBILIDAD CON URL ANTIGUA DE RECETAS
    Redirige al nuevo endpoint modular de recetas
    """
    from flask import redirect, url_for, request
    return redirect(url_for('menu_admin.recetas.crear_receta'), code=307)  # 307 preserva POST
