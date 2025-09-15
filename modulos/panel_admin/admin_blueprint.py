#!/usr/bin/env python3
"""
🎛️ DASHBOARD ADMINISTRATIVO - BLUEPRINT INTELIGENTE
=================================================
Convierte el admin_server.py existente en bl              # Verificar estado de servicios
        servicios = {
            'cliente': verificar_servicio('http://127.0.0.1:8080/'),
            'admin_menu': verificar_servicio('http://127.0.0.1:8080/menu-admin/admin'),
            'chatbot': verificar_servicio('http://127.0.0.1:8080/chatbot'),
            'menu_api': verificar_servicio('http://127.0.0.1:8080/menu-admin/api/productos')
        }ificar estado de servicios
        servicios = {
            'cliente': verificar_servicio('http://127.0.0.1:8080/'),
            'admin_menu': verificar_servicio('http://127.0.0.1:8080/menu-admin/admin'),
            'chatbot': verificar_servicio('http://127.0.0.1:8080/chatbot'),
            'menu_api': verificar_servicio('http://127.0.0.1:8080/menu-admin/api/productos')
        } para app.py
Sin duplicar código ni archivos
"""

from flask import Blueprint, render_template, jsonify, request, send_from_directory, send_file
import os
import sys
import json
import requests
from datetime import datetime
import qrcode
import socket

# Crear blueprint basado en admin_server.py existente
admin_bp = Blueprint('admin', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/admin')

# Ruta avanzada del generador QR
@admin_bp.route('/generador-qr')
def generador_qr_avanzado():
    """Vista avanzada del generador de QR"""
    return render_template('generador-qr.html')
import io
import base64
from PIL import Image

# Crear blueprint basado en admin_server.py existente
admin_bp = Blueprint('admin', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/admin')

# Ruta avanzada del generador QR
@admin_bp.route('/generador-qr')
def generador_qr_avanzado():
    """Vista avanzada del generador de QR"""
    return render_template('generador-qr.html')

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# ===============================
# FUNCIONES AUXILIARES (del admin_server.py original)
# ===============================

def obtener_ip_local():
    """Obtener la IP local de la red automáticamente"""
    try:
        # Crear un socket para conectar temporalmente y obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conectar a un servidor externo
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except:
        # Fallback a IP fija si falla la detección automática
        return "192.168.1.23"

def verificar_servicio(url):
    """Verificar si un servicio está disponible"""
    try:
        response = requests.get(url, timeout=3, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def obtener_estadisticas():
    """Obtener estadísticas del sistema"""
    try:
        # Importar los modelos SQLAlchemy directamente
        from modulos.backend.menu.database.models.producto import Producto
        from modulos.backend.menu.database.models.categoria import Categoria
        from modulos.backend.menu.database.base import Base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        
        # Configurar la sesión de base de datos (usar ruta relativa desde main.py)
        db_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'menu', 'database', 'menu.db')
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        session = Session()

        stats = {
            'total_productos': 0,
            'total_categorias': 0,
            'uptime': '0 min'
        }
        
        # Obtener estadísticas de productos
        total_productos = session.query(Producto).count()
        stats['total_productos'] = total_productos
        
        # Obtener estadísticas de categorías
        try:
            total_categorias = session.query(Categoria).count()
            stats['total_categorias'] = total_categorias
        except Exception:
            stats['total_categorias'] = 0
        
        session.close()
        return stats
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {'total_productos': 0, 'total_categorias': 0, 'uptime': '0 min'}

# ===============================
# RUTAS PRINCIPALES (del admin_server.py original)
# ===============================

@admin_bp.route('/')
def dashboard():
    """Dashboard principal del administrador"""
    return render_template('dashboard.html')

@admin_bp.route('/menu')
def gestionar_menu():
    """Dashboard Admin Productos - Independiente del CRUD"""
    return render_template('dashboard_productos.html')

@admin_bp.route('/menu-debug')
def menu_debug():
    """Debug simple"""
    return "<h1 style='color:red; font-size:50px;'>HOLA MUNDO - FLASK FUNCIONA</h1><p>Fecha: 3 de septiembre 2025</p>"

@admin_bp.route('/chatbot')
def gestionar_chatbot():
    """Gestión del módulo de chatbot"""
    return render_template('chatbot_admin.html')

@admin_bp.route('/qr')
def gestionar_qr():
    """Gestión del generador de códigos QR"""
    return render_template('qr_admin_simple.html')

@admin_bp.route('/qr-test')
def gestionar_qr_test():
    """Versión de prueba del generador QR"""
    return render_template('qr_admin_simple.html')

@admin_bp.route('/api/download-qr/<int:table_number>')
def download_qr(table_number):
    """Descargar QR como archivo PNG"""
    try:
        # Generar QR (IP automática para móviles)
        ip_local = obtener_ip_local()
        qr_url = f"http://{ip_local}:8080/chatbot?mesa={table_number}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar en buffer
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return send_file(
            img_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'QR_Mesa_{table_number}.png'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# RUTAS DEL DASHBOARD
# ===============================

@admin_bp.route('/estadisticas')
def ver_estadisticas():
    """Estadísticas del sistema"""
    return render_template('estadisticas.html')

# ===============================
# API ENDPOINTS (del admin_server.py original)
# ===============================

@admin_bp.route('/api/status')
def api_status():
    """Estado de todos los módulos del sistema"""
    try:
        # Verificar estado de servicios
        servicios = {
            'cliente': verificar_servicio('http://127.0.0.1:8080/'),
            'admin_menu': verificar_servicio('http://127.0.0.1:8080/menu-admin/admin'),
            'chatbot': verificar_servicio('http://127.0.0.1:8080/chatbot'),
            'menu_api': verificar_servicio('http://127.0.0.1:8080/menu-admin/api/productos')
        }
        
        # Estadísticas básicas
        stats = obtener_estadisticas()
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'servicios': servicios,
            'estadisticas': stats,
            'estado_general': all(servicios.values())
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/menu/stats')
def api_menu_stats():
    """Estadísticas del módulo de menú"""
    try:
        # Intentar obtener datos del menú
        response = requests.get('http://127.0.0.1:8080/menu-admin/api/productos', timeout=3)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'estadisticas': data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Fallback a archivos JSON
            stats = obtener_estadisticas()
            return jsonify({
                'success': True,
                'estadisticas': stats,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/chatbot/config', methods=['GET', 'POST'])
def api_chatbot_config():
    """Configuración del chatbot"""
    if request.method == 'GET':
        return jsonify({
            'mensaje_bienvenida': '¡Hola! Soy tu asistente virtual de Eterials Gastro-Café',
            'respuestas_automaticas': True,
            'identificacion_mesa': True
        })
    else:
        # POST - Actualizar configuración
        config = request.json
        return jsonify({
            'success': True,
            'message': 'Configuración actualizada',
            'config': config
        })

@admin_bp.route('/api/get-local-ip', methods=['GET'])
def get_local_ip():
    """Endpoint para obtener la IP local automáticamente"""
    try:
        ip_local = obtener_ip_local()
        return jsonify({
            'success': True,
            'ip_local': ip_local,
            'base_url': f"http://{ip_local}:8080"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'ip_local': '192.168.1.23',  # Fallback
            'base_url': 'http://192.168.1.23:8080'
        })

@admin_bp.route('/api/generate-qr', methods=['POST'])
def generate_qr_api():
    """Endpoint para generar QR codes usando Python"""
    try:
        data = request.get_json()
        table_number = data.get('table_number', 1)
        
        # URL que redirige al chatbot con el número de mesa (IP automática para móviles)
        ip_local = obtener_ip_local()
        url = f"http://{ip_local}:8080/chatbot?mesa={table_number}"
        
        # Crear el QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64 para enviar al frontend
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Convertir a base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'qr_base64': img_base64,
            'url': url,
            'table_number': table_number
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===============================
# GENERADOR QR (del admin_server.py original)
# ===============================

@admin_bp.route('/qr-generator')
def qr_generator():
    """Servir el generador de QR integrado mejorado"""
    qr_file = os.path.join(BASE_DIR, 'templates', 'generador-qr.html')
    try:
        with open(qr_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Generador QR no encontrado", 404

@admin_bp.route('/api/obtener-ip')
def obtener_ip_actual():
    """API para obtener IP dinámica para generación de QR"""
    ip = obtener_ip_local()
    return jsonify({'ip': ip})

@admin_bp.route('/qr-assets/<path:filename>')
def qr_assets(filename):
    """Servir assets del generador QR"""
    qr_dir = os.path.join(BASE_DIR, 'templates')
    return send_from_directory(qr_dir, filename)
