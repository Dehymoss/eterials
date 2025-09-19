from flask import Blueprint, jsonify, render_template
import socket
from datetime import datetime

admin_bp = Blueprint('admin', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    """Dashboard principal administrativo."""
    return render_template('dashboard.html')

@admin_bp.route('/admin')
def dashboard_admin():
    """Dashboard principal administrativo via /admin/admin."""
    return render_template('dashboard.html')

@admin_bp.route('/debug-dashboard')
def debug_dashboard():
    """Dashboard simplificado para debugging"""
    import os
    try:
        debug_file_path = os.path.join(os.getcwd(), 'debug_dashboard.html')
        with open(debug_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>Debug Dashboard - Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #1e3c72; color: white;">
            <h1>❌ Debug Dashboard No Disponible</h1>
            <p>El archivo debug_dashboard.html no se encontró.</p>
            <div style="margin: 20px;">
                <a href="/admin" style="display: inline-block; margin: 10px; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">🔙 Volver al Admin</a>
                <a href="/admin/chatbot" style="display: inline-block; margin: 10px; padding: 15px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">🤖 Dashboard Chatbot</a>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Debug Dashboard - Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #dc3545; color: white;">
            <h1>❌ Error en Debug Dashboard</h1>
            <p>Error: {str(e)}</p>
            <div style="margin: 20px;">
                <a href="/admin" style="display: inline-block; margin: 10px; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">🔙 Volver al Admin</a>
            </div>
        </body>
        </html>
        '''

@admin_bp.route('/generador-qr')
def generador_qr():
    """Generador de códigos QR para mesas y barra"""
    return render_template('generador-qr.html')

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@admin_bp.route('/api/obtener-ip')
@admin_bp.route('/api/get-local-ip')  # Alias para compatibilidad
def obtener_ip_actual():
    """Obtiene la URL base correcta para generar QR codes"""
    import os
    
    # Detectar si estamos en Render.com
    if 'RENDER' in os.environ or 'onrender.com' in os.environ.get('RENDER_EXTERNAL_URL', ''):
        # Estamos en producción en Render.com
        render_url = os.environ.get('RENDER_EXTERNAL_URL', '')
        if render_url:
            base_url = render_url.rstrip('/')
        else:
            # Fallback si no está definida la variable
            base_url = "https://eterials-restaurant.onrender.com"
    else:
        # Desarrollo local
        ip = obtener_ip_local()
        base_url = f"http://{ip}:8080"
    
    return jsonify({
        'success': True,
        'base_url': base_url,
        'ip': obtener_ip_local(),
        'environment': 'production' if 'RENDER' in os.environ else 'development',
        'timestamp': datetime.now().isoformat()
    })

@admin_bp.route('/api/status')
def api_status():
    """API para el dashboard - estado de servicios y estadísticas"""
    try:
        # Verificar estado de servicios (simulado por ahora)
        servicios = {
            'chatbot': True,  # Siempre true si el servidor está funcionando
            'menu_admin': True,
            'menu_cliente': True,
            'cocina': True
        }
        
        # Estadísticas básicas (simuladas por ahora)
        estadisticas = {
            'total_productos': 0,  # Se puede conectar con la BD más adelante
            'total_categorias': 0,
            'uptime': '< 1 hora'
        }
        
        return jsonify({
            'status': 'ok',
            'servicios': servicios,
            'estadisticas': estadisticas,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'servicios': {},
            'estadisticas': {},
            'timestamp': datetime.now().isoformat()
        }), 500