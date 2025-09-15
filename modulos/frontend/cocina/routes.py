"""
Blueprint Frontend Cocina - Sistema de Gestión de Restaurante
Rutas especializadas para chef y auxiliares de cocina
"""

from flask import Blueprint, render_template, request, jsonify
import requests

# Crear blueprint para el módulo cocina
cocina_bp = Blueprint('cocina', __name__, 
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/cocina/static',
                     url_prefix='/cocina')

@cocina_bp.route('/')
def dashboard_cocina():
    """Dashboard principal para la cocina"""
    return render_template('dashboard_cocina.html')

@cocina_bp.route('/recetas')
def lista_recetas():
    """Lista todas las recetas de productos preparados"""
    try:
        # Llamar a la API backend para obtener recetas
        response = requests.get('http://localhost:8080/api/cocina/recetas')
        if response.status_code == 200:
            recetas = response.json()
            return render_template('dashboard_cocina.html', recetas=recetas)
        else:
            return render_template('dashboard_cocina.html', error="Error al cargar recetas")
    except Exception as e:
        return render_template('dashboard_cocina.html', error=f"Error de conexión: {str(e)}")

@cocina_bp.route('/receta/<int:producto_id>')
def detalle_receta(producto_id):
    """Muestra el detalle completo de una receta específica"""
    try:
        # Llamar a la API backend para obtener detalle de receta
        response = requests.get(f'http://localhost:8080/api/cocina/receta/{producto_id}')
        if response.status_code == 200:
            receta = response.json()
            return render_template('detalle_receta.html', receta=receta)
        else:
            return render_template('detalle_receta.html', error="Receta no encontrada")
    except Exception as e:
        return render_template('detalle_receta.html', error=f"Error de conexión: {str(e)}")

@cocina_bp.route('/buscar')
def buscar_recetas():
    """Busca recetas por nombre o categoría"""
    termino = request.args.get('q', '')
    try:
        response = requests.get(f'http://localhost:8080/api/cocina/buscar?q={termino}')
        if response.status_code == 200:
            recetas = response.json()
            return jsonify(recetas)
        else:
            return jsonify({'error': 'Error en búsqueda'})
    except Exception as e:
        return jsonify({'error': f'Error de conexión: {str(e)}'})
