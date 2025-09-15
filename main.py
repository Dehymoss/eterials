#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETERIALS RESTAURANT - SISTEMA DE GESTIÓN COMPLETO
==================================================
Punto de entrada principal para el sistema de gestión de restaurante.

Módulos incluidos:
- 🤖 Chatbot con animaciones musicales
- ⚙️ Panel administrativo completo  
- 🍽️ Gestión de menús y productos
- 🍳 Dashboard de cocina especializado
- 📊 Sistema de estadísticas
- 🖼️ Gestión de imágenes

Autor: Sistema Eterials
Fecha: 14 de septiembre de 2025
Puerto: 8080 (configuración production-ready)
"""

print("🚀 Iniciando Sistema Eterials Restaurant...")
print("📂 Cargando módulos principales...")

# Importaciones principales de Flask
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
import os
import sys

# Agregar rutas de módulos al PATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'modulos'))

print("📦 Registrando blueprints...")

# Crear aplicación Flask principal
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eterials_restaurant_2025_secure_key'

# Configurar CORS para APIs
CORS(app)

# Importar y registrar blueprints principales
try:
    # 🤖 Módulo Chatbot con animaciones
    from modulos.chatbot.chatbot_blueprint import chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    print("✅ Chatbot registrado: /chatbot")
    
    # ⚙️ Panel administrativo
    from modulos.panel_admin.admin_blueprint import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    print("✅ Panel Admin registrado: /admin")
    
    # 🍽️ Sistema de gestión de menús (Backend)
    from modulos.backend.menu.menu_admin_endpoints import menu_admin_bp
    app.register_blueprint(menu_admin_bp, url_prefix='/menu-admin')
    print("✅ Gestión Menús registrado: /menu-admin")
    
    # 🌐 Frontend del menú para clientes
    from modulos.frontend.menu.routes import menu_frontend_bp
    app.register_blueprint(menu_frontend_bp, url_prefix='/menu')
    print("✅ Menú Cliente registrado: /menu")
    
    # 🍳 Dashboard de cocina
    from modulos.frontend.cocina.routes import cocina_bp
    app.register_blueprint(cocina_bp, url_prefix='/cocina')
    print("✅ Dashboard Cocina registrado: /cocina")
    
    print("🎉 Todos los módulos cargados exitosamente")
    
except ImportError as e:
    print(f"⚠️ Error cargando módulo: {e}")
    print("🔄 Continuando con módulos disponibles...")

# Ruta principal de bienvenida
@app.route('/')
def index():
    """Página principal del sistema con navegación completa"""
    return render_template('dashboard.html') if os.path.exists('templates/dashboard.html') else f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🏠 Eterials Restaurant - Sistema Principal</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; 
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; 
                         border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
            h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
            .nav-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                        gap: 20px; margin-top: 20px; }}
            .nav-card {{ background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%); 
                        color: white; padding: 20px; border-radius: 10px; text-decoration: none; 
                        transition: transform 0.3s; }}
            .nav-card:hover {{ transform: translateY(-5px); }}
            .nav-card h3 {{ margin: 0 0 10px 0; }}
            .nav-card p {{ margin: 0; opacity: 0.9; }}
            .status {{ text-align: center; margin: 20px 0; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 Sistema Eterials Restaurant</h1>
            <div class="status">✅ Sistema completamente operativo en puerto 8080</div>
            
            <div class="nav-grid">
                <a href="/chatbot" class="nav-card" style="background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);">
                    <h3>🤖 Chatbot</h3>
                    <p>Sistema de atención con efectos musicales y animaciones</p>
                </a>
                
                <a href="/admin" class="nav-card" style="background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);">
                    <h3>⚙️ Panel Admin</h3>
                    <p>Herramientas administrativas y configuración</p>
                </a>
                
                <a href="/menu-admin/admin" class="nav-card" style="background: linear-gradient(45deg, #a8edea 0%, #fed6e3 100%);">
                    <h3>🍽️ Gestión Menús</h3>
                    <p>CRUD completo de productos, categorías y recetas</p>
                </a>
                
                <a href="/menu/general" class="nav-card" style="background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%);">
                    <h3>📱 Menú Cliente</h3>
                    <p>Menú público optimizado para móviles</p>
                </a>
                
                <a href="/cocina" class="nav-card" style="background: linear-gradient(45deg, #89f7fe 0%, #66a6ff 100%);">
                    <h3>🍳 Dashboard Cocina</h3>
                    <p>Panel especializado para chef y auxiliares</p>
                </a>
                
                <a href="/admin/configuracion-menu" class="nav-card" style="background: linear-gradient(45deg, #fdbb2d 0%, #22c1c3 100%);">
                    <h3>🔧 Configuración</h3>
                    <p>Configuración avanzada del sistema</p>
                </a>
            </div>
            
            <div style="text-align: center; margin-top: 30px; color: #666;">
                <p>🌟 Sistema desarrollado para Eterials Restaurant</p>
                <p>🔗 Versión: 3.0.1 - Production Ready</p>
            </div>
        </div>
    </body>
    </html>
    """

# Redirección de compatibilidad
@app.route('/test')
def test():
    """Endpoint de testing para verificaciones"""
    return "✅ Sistema Eterials funcionando correctamente - Puerto 8080"

# Inicialización de base de datos
def initialize_database():
    """Inicializa la base de datos si no existe"""
    try:
        from modulos.backend.menu.models import init_db
        init_db()
        print("📊 Base de datos inicializada correctamente")
    except ImportError:
        print("⚠️ Modelos de base de datos no encontrados")
    except Exception as e:
        print(f"⚠️ Error inicializando base de datos: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando servidor Eterials Restaurant...")
    
    # Inicializar base de datos
    initialize_database()
    
    # Configuración para producción/desarrollo
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Servidor iniciando en puerto {port}")
    print(f"🔧 Modo debug: {'ON' if debug_mode else 'OFF'}")
    print("=" * 50)
    print("📍 URLs principales:")
    print(f"   🏠 Principal: http://127.0.0.1:{port}/")
    print(f"   🤖 Chatbot: http://127.0.0.1:{port}/chatbot")
    print(f"   ⚙️ Admin: http://127.0.0.1:{port}/admin")
    print(f"   🍽️ Gestión: http://127.0.0.1:{port}/menu-admin/admin")
    print(f"   📱 Menú: http://127.0.0.1:{port}/menu/general")
    print(f"   🍳 Cocina: http://127.0.0.1:{port}/cocina")
    print("=" * 50)
    
    # Iniciar servidor
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
