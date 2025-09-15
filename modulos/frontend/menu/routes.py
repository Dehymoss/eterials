"""
FRONTEND MENÚ - RUTAS LIMPIAS Y OPTIMIZADAS
Solo funcionalidades esenciales para el menú público
Incluye verificación de configuración de menú (propio vs externo)
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

# Blueprint del menú público
menu_bp = Blueprint('menu', __name__, 
                   template_folder='templates',
                   static_folder='static',
                   static_url_path='/static',
                   url_prefix='/menu')

# ===== UTILIDADES DE CONFIGURACIÓN =====

def verificar_configuracion_menu():
    """Verificar configuración actual del sistema de menú"""
    try:
        DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'modulos', 'backend', 'menu', 'database', 'menu.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM configuracion_sistema")
        rows = cursor.fetchall()
        
        config = {}
        for row in rows:
            config[row['clave']] = row['valor']
        
        conn.close()
        
        return {
            'menu_activo': config.get('menu_activo', 'propio'),
            'menu_externo_url': config.get('menu_externo_url', ''),
            'redirect_automatico': config.get('redirect_automatico', 'false').lower() == 'true',
            'mensaje_mantenimiento': config.get('mensaje_mantenimiento', 'Redirigiendo al menú...')
        }
    except Exception as e:
        print(f"Error verificando configuración: {e}")
        return {
            'menu_activo': 'propio',
            'menu_externo_url': '',
            'redirect_automatico': False,
            'mensaje_mantenimiento': 'Error de configuración'
        }

# ===== RUTAS PRINCIPALES =====

@menu_bp.route('/')
@menu_bp.route('/general')
def menu_general():
    """Página principal del menú público con verificación de configuración"""
    # Verificar si se fuerza el menú interno
    force_internal = request.args.get('force_internal', 'false').lower() == 'true'
    
    # Si no se fuerza interno, verificar configuración de menú
    if not force_internal:
        config = verificar_configuracion_menu()
        
        # Si está configurado para menú externo y redirección automática
        if config['menu_activo'] == 'externo' and config['redirect_automatico']:
            if config['menu_externo_url']:
                return redirect(config['menu_externo_url'])
        
    # Si está configurado para menú externo pero sin redirección automática
    if config['menu_activo'] == 'externo' and not config['redirect_automatico']:
        # Mostrar página de transición con botón manual
        return render_template('menu_transicion.html', 
                             config=config,
                             nombre=request.args.get('nombre', ''),
                             mesa=request.args.get('mesa', ''))    # Menú propio (comportamiento normal o forzado)
    nombre = request.args.get('nombre', '')
    mesa = request.args.get('mesa', '')
    return render_template('menu_general.html', nombre=nombre, mesa=mesa)

@menu_bp.route('/dia')
def menu_dia():
    """Compatibilidad - redirige al menú general"""
    return redirect(url_for('menu.menu_general', **request.args))



@menu_bp.route('/debug')
def debug():
    """Página de debug simple para el menú"""
    try:
        import requests
        # Test rápido de conectividad
        productos_response = requests.get("http://localhost:8080/menu-admin/api/productos", timeout=2)
        productos_ok = productos_response.status_code == 200
        
        return f"""
        <html>
        <head><title>Menu Debug</title></head>
        <body style="background: #333; color: white; font-family: Arial; padding: 20px;">
            <h1>🔍 Menu Debug</h1>
            <p><strong>Backend Status:</strong> {'✅ OK' if productos_ok else '❌ Error'}</p>
            <p><strong>Cliente:</strong> {request.args.get('nombre', 'Invitado')} | Mesa: {request.args.get('mesa', 'N/A')}</p>
            <p><a href="/menu/general" style="color: yellow;">← Volver al Menú</a></p>
        </body>
        </html>
        """
    except:
        return "<h1>Debug Error</h1><p><a href='/menu/general'>Volver al Menu</a></p>"

@menu_bp.route('/error')
def error():
    """Página de error"""
    return render_template('error.html')

# --- API PRINCIPAL DEL MENÚ ---

# ===== API SIMPLE DEL MENÚ =====

@menu_bp.route('/api/menu-completo')
def api_menu_completo():
    """API optimizada para obtener menú completo desde backend"""
    try:
        import requests
        
        # Obtener categorías
        categorias_response = requests.get("http://localhost:8080/menu-admin/api/categorias/", timeout=3)
        if categorias_response.status_code == 200:
            categorias_data = categorias_response.json()
            categorias = categorias_data.get('categorias', [])
        else:
            categorias = []
        
        # Obtener productos
        productos_response = requests.get("http://localhost:8080/menu-admin/api/productos/", timeout=3)
        if productos_response.status_code == 200:
            productos_data = productos_response.json()
            productos_raw = productos_data.get('productos', [])
            # Filtrar productos disponibles
            productos = [p for p in productos_raw if p.get('disponible', True)]
        else:
            productos = []
        
        return jsonify({
            'success': True,
            'categorias': categorias,
            'productos': productos,
            'total': len(productos)
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error en api_menu_completo: {error_details}")
        return jsonify({
            'success': False,
            'error': f'Error cargando menú: {str(e)}',
            'debug': error_details
        }), 500

# ===== MANEJADORES DE ERROR =====

@menu_bp.errorhandler(404)
def not_found(error):
    return redirect(url_for('menu.menu_general'))

@menu_bp.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, 
                         error_message="Error del servidor"), 500
