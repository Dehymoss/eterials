"""
🎯 MENU ADMIN ENDPOINTS - ARCHIVO COORDINADOR LIMPIO
Responsabilidad: Servir plantillas HTML y coordinar blueprints modulares
NOTA: Todo el código CRUD se migró a archivos específicos modulares

📋 ESTADO DE MIGRACIÓN MODULAR:
✅ PRODUCTOS -> endpoints/productos_endpoints.py (COMPLETO)
✅ CATEGORÍAS -> endpoints/categorias_endpoints.py (COMPLETO)  
✅ IMÁGENES -> endpoints/imagenes_endpoints.py (COMPLETO)
🔄 ESTADÍSTICAS -> Por migrar
🔄 BACKUP -> Por migrar

🌐 COORDINADOR: menu_admin_modular.py gestiona todos los módulos
"""

from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Configuración de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

# Importar modelos para compatibilidad
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria
from modulos.backend.menu.database.models.ingrediente import Ingrediente
from datetime import datetime

# 🔗 IMPORT BLUEPRINTS MODULARES
from modulos.backend.menu.endpoints.productos_endpoints import productos_bp
from modulos.backend.menu.endpoints.categorias_endpoints import categorias_bp
from modulos.backend.menu.endpoints.imagenes_endpoints import imagenes_bp

# --- FUNCIONES HELPER PARA SERIALIZACIÓN (COMPATIBILIDAD) ---
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

# Blueprint principal
menu_admin_bp = Blueprint(
    'menu_admin',
    __name__,
    url_prefix='/menu-admin',
    template_folder='templates',
    static_folder='static'
)

# Registrar sub-blueprints después de definir el blueprint principal (evitar imports circulares)
menu_admin_bp.register_blueprint(productos_bp, url_prefix='/api/productos')
menu_admin_bp.register_blueprint(categorias_bp, url_prefix='/api/categorias')

# ===== RUTAS PRINCIPALES DE TEMPLATES =====

@menu_admin_bp.route('/')
@menu_admin_bp.route('/admin')
def admin_dashboard():
    """
    🏠 PÁGINA PRINCIPAL DE ADMINISTRACIÓN
    Sirve el template HTML del panel de control
    """
    return render_template('admin_productos.html')

@menu_admin_bp.route('/estadisticas')
def admin_estadisticas():
    """
    📊 PÁGINA DE ESTADÍSTICAS
    Sirve el template de análisis y reportes
    """
    return render_template('estadisticas.html')

@menu_admin_bp.route('/backup')
def admin_backup():
    """
    💾 PÁGINA DE BACKUP Y RESTAURACIÓN
    Sirve el template de gestión de backups
    """
    return render_template('backup.html')

# ===== SISTEMA DE INTERCAMBIO DE MENÚS =====

# Archivo de configuración para estado del menú
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config_menu.json')

def obtener_estado_menu():
    """Obtiene el estado actual del menú (proyecto o treinta)"""
    try:
        import json
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('menu_activo', 'proyecto')  # Default: proyecto
        return 'proyecto'  # Si no existe archivo, usar proyecto por defecto
    except:
        return 'proyecto'

def guardar_estado_menu(nuevo_estado):
    """Guarda el nuevo estado del menú"""
    try:
        import json
        config = {
            'menu_activo': nuevo_estado,
            'fecha_cambio': datetime.now().isoformat(),
            'descripcion': 'proyecto' if nuevo_estado == 'proyecto' else 'treinta'
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando estado del menú: {e}")
        return False

@menu_admin_bp.route('/api/menu/estado', methods=['GET'])
def obtener_estado_menu_api():
    """API para obtener el estado actual del menú"""
    estado = obtener_estado_menu()
    return jsonify({
        'success': True,
        'menu_activo': estado,
        'descripcion': 'Menú del Proyecto' if estado == 'proyecto' else 'Menú de Treinta (Externo)'
    })

@menu_admin_bp.route('/api/menu/cambiar', methods=['POST'])
def cambiar_menu_api():
    """API para cambiar entre menú proyecto y menú treinta"""
    try:
        data = request.get_json()
        nuevo_estado = data.get('menu_activo')
        
        if nuevo_estado not in ['proyecto', 'treinta']:
            return jsonify({
                'success': False,
                'error': 'Estado inválido. Debe ser "proyecto" o "treinta"'
            }), 400
        
        if guardar_estado_menu(nuevo_estado):
            descripcion = 'Menú del Proyecto activado' if nuevo_estado == 'proyecto' else 'Menú de Treinta activado'
            return jsonify({
                'success': True,
                'menu_activo': nuevo_estado,
                'mensaje': descripcion
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error al guardar la configuración'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en el servidor: {str(e)}'
        }), 500

# ===== FUNCIONES HELPER DE UTILIDAD =====

def buscar_imagenes_fallback(query):
    """
    🖼️ FUNCIÓN HELPER PARA BÚSQUEDA DE IMÁGENES FALLBACK
    Genera URLs de Picsum cuando la búsqueda web falla
    """
    imagenes = []
    
    # Usar Picsum con diferentes parámetros
    for i in range(10):
        seed = abs(hash(f"{query}_{i}")) % 1000
        url = f"https://picsum.photos/400/300?random={seed}"
        imagenes.append(url)
    
    return imagenes

# 🏁 FIN DEL ARCHIVO COORDINADOR
# ✅ Endpoints modulares registrados:
# - productos_endpoints.py → /api/productos/* - CRUD completo de productos migrado ✅
# - categorias_endpoints.py → /api/categorias/* - CRUD completo de categorías migrado ✅
# - imagenes_endpoints.py → /api/imagenes/* - Búsqueda de imágenes MIGRADO ✅
# ⏳ Próximos endpoints por migrar:
# - estadisticas_endpoints.py → /api/estadisticas/* - Reportes y analytics
# - backup_endpoints.py → /api/backup/* - Gestión de backups
