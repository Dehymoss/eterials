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

# Importar y registrar blueprints principales uno por uno
blueprints_cargados = 0

# 🤖 Módulo Chatbot con animaciones
try:
    from modulos.chatbot.chatbot_blueprint import chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    print("✅ Chatbot registrado: /chatbot")
    blueprints_cargados += 1
except ImportError as e:
    print(f"❌ Error cargando Chatbot: {e}")

# ⚙️ Panel administrativo
try:
    from modulos.panel_admin.admin_blueprint import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    print("✅ Panel Admin registrado: /admin")
    blueprints_cargados += 1
except ImportError as e:
    print(f"❌ Error cargando Admin: {e}")

# 🍽️ Sistema de gestión de menús (Backend)
try:
    from modulos.backend.menu.menu_admin_endpoints import menu_admin_bp
    app.register_blueprint(menu_admin_bp, url_prefix='/menu-admin')
    print("✅ Gestión Menús registrado: /menu-admin")
    blueprints_cargados += 1
except ImportError as e:
    print(f"❌ Error cargando Gestión Menús: {e}")

# 🌐 Frontend del menú para clientes (CORREGIDO: se llama menu_bp, no menu_frontend_bp)
try:
    from modulos.frontend.menu.routes import menu_bp
    app.register_blueprint(menu_bp, url_prefix='/menu')
    print("✅ Menú Cliente registrado: /menu")
    blueprints_cargados += 1
except ImportError as e:
    print(f"❌ Error cargando Menú Cliente: {e}")

# 🍳 Dashboard de cocina
try:
    from modulos.frontend.cocina.routes import cocina_bp
    app.register_blueprint(cocina_bp, url_prefix='/cocina')
    print("✅ Dashboard Cocina registrado: /cocina")
    blueprints_cargados += 1
except ImportError as e:
    print(f"❌ Error cargando Dashboard Cocina: {e}")

print(f"🎉 {blueprints_cargados}/5 módulos cargados exitosamente")

# Ruta principal de bienvenida
@app.route('/')
def index():
    """Página principal del sistema con navegación completa"""
    # Redirigir al panel admin que tiene el dashboard original
    return redirect(url_for('admin.dashboard'))

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
