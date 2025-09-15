from flask import Flask
from sqlalchemy import create_engine
import os

print("🚀 Iniciando aplicación Flask...")

# Crear la app Flask principal
app = Flask(__name__)

print("📦 Importando modelos...")
# Centralizar la creación de todas las tablas
from modulos.backend.menu.database.base import Base
# Importar todos los modelos para que se registren en Base
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria
from modulos.backend.menu.database.models.ingrediente import Ingrediente
print("✅ Modelos importados correctamente")

print("🗃️ Configurando base de datos...")
DB_PATH = os.path.join(os.path.dirname(__file__), 'modulos', 'backend', 'menu', 'database', 'menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
# Crear todas las tablas con una sola llamada
Base.metadata.create_all(engine)
print(f"✅ Base de datos configurada: {DB_PATH}")

print("🔌 Importando blueprints...")
# Importar y registrar blueprints con imports absolutos
from modulos.backend.menu.menu_admin_modular import menu_admin_bp  # Usar coordinador modular
# from modulos.backend.menu.endpoints import menu_general_api  # Comentado - archivo vacío
from modulos.panel_admin.admin_blueprint import admin_bp
from modulos.chatbot.chatbot_blueprint import chatbot_bp
from modulos.frontend.menu.routes import menu_bp
# Nuevos blueprints de cocina
from modulos.frontend.cocina.routes import cocina_bp
from modulos.backend.cocina.cocina_api import cocina_api_bp
# Blueprint de configuración de menú
# NOTA: configuracion_menu_endpoints.py fue migrado o removido - comentado temporalmente
# from configuracion_menu_endpoints import configuracion_menu_bp
print("✅ Blueprints importados correctamente")


# Registrar blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')  # Panel admin primero para que /admin apunte al dashboard
app.register_blueprint(menu_admin_bp, url_prefix='/menu-admin')  # Menú admin con prefijo correcto
# app.register_blueprint(menu_general_api)  # Comentado - no existe
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(menu_bp, url_prefix='/menu')
# Registrar blueprints de cocina
app.register_blueprint(cocina_bp, url_prefix='/cocina')  # Frontend cocina
app.register_blueprint(cocina_api_bp)  # API cocina (ya tiene prefix /api/cocina)
# Registrar blueprint de configuración de menú
# NOTA: configuracion_menu_bp comentado hasta localizar el archivo correcto
# app.register_blueprint(configuracion_menu_bp)  # Ya tiene url_prefix='/admin/configuracion-menu'

# Rutas de redirección para acceso más fácil
from flask import redirect, jsonify

@app.route('/')
def index():
    return "Servidor Eterials activo. Panel admin en /admin, menú en /menu, chatbot en /chatbot."

@app.route('/admin/menu')
def redirect_to_menu_admin():
    """Redirigir desde /admin/menu hacia la ruta correcta"""
    return redirect('/menu-admin/admin')

@app.route('/admin/menu/admin')
def redirect_to_menu_admin_specific():
    """Redirigir desde /admin/menu/admin hacia la ruta correcta"""
    return redirect('/menu-admin/admin')

# Rutas de redirección para APIs que pueden estar hardcodeadas en JavaScript
# @app.route('/admin/menu/api/productos', methods=['GET', 'POST', 'PUT', 'DELETE'])
# def redirect_productos_api():
#     """Redirigir API de productos a la ruta correcta"""
#     return redirect('/menu-admin/api/productos', code=307)  # 307 preserva el método HTTP

# @app.route('/admin/menu/api/categorias', methods=['GET', 'POST', 'PUT', 'DELETE'])
# def redirect_categorias_api():
#     """Redirigir API de categorías a la ruta correcta"""
#     return redirect('/menu-admin/api/categorias', code=307)  # 307 preserva el método HTTP

@app.route('/api/menu/menu-completo')
def redirect_menu_completo():
    """Redirigir API de menú completo a la ruta correcta"""
    return redirect('/menu-admin/api/productos')

if __name__ == "__main__":
    print("🚀 Iniciando servidor Eterials...")
    print("📊 Base de datos actualizada con modelos: Producto, Categoria, Subcategoria, Ingrediente")
    
    # Configuración para producción/desarrollo
    import os
    port = int(os.environ.get('PORT', 8080))  # Restaurado a puerto 8080
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print("🌐 URLs disponibles:")
    if debug_mode:
        print(f"   - http://127.0.0.1:{port}/ (Principal)")
        print(f"   - http://127.0.0.1:{port}/admin (Panel Admin)")
        print(f"   - http://127.0.0.1:{port}/admin/menu (Gestión Menú) → redirige a /menu-admin/admin")
        print(f"   - http://127.0.0.1:{port}/menu-admin/admin (Gestión Menú - Ruta directa)")
        print(f"   - http://127.0.0.1:{port}/cocina (🍳 Dashboard Cocina)")
        print(f"   - http://127.0.0.1:{port}/menu (Menú Público)")
        print(f"   - http://127.0.0.1:{port}/chatbot (Chatbot)")
        print(f"   - http://127.0.0.1:{port}/admin/configuracion-menu (🔧 Configuración de Menú)")
    else:
        print(f"   - Aplicación ejecutándose en modo producción en puerto {port}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
