"""
📂 ENDPOINT ESPECÍFICO PARA GESTIÓN DE CATEGORÍAS
Responsabilidad única: CRUD completo de categorías y subcategorías + Sistema de iconos automático
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import re
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria

# Configuración de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '../database', 'menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

# Blueprint específico para categorías
categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

# 🎨 SISTEMA DE ICONOS AUTOMÁTICO
def detectar_icono_categoria(nombre_categoria):
    """
    🤖 DETECTA AUTOMÁTICAMENTE EL ICONO APROPIADO PARA UNA CATEGORÍA
    Usa inteligencia artificial por palabras clave y sinónimos
    """
    nombre = nombre_categoria.lower().strip()
    
    # Diccionario inteligente de iconos por categoría
    iconos_por_categoria = {
        # ENTRADAS Y APERITIVOS
        'entradas': '🍜', 'entrada': '🍜', 'aperitivos': '🍜', 'aperitivo': '🍜',
        'antipasto': '🍜', 'antipastos': '🍜', 'bocadillos': '🍜', 'bocadillo': '🍜',
        'tapas': '🍜', 'tapa': '🍜', 'picada': '🍜', 'picadas': '🍜',
        
        # PLATOS PRINCIPALES
        'platos principales': '🍽️', 'plato principal': '🍽️', 'principales': '🍽️',
        'almuerzo': '🍽️', 'almuerzos': '🍽️', 'cena': '🍽️', 'cenas': '🍽️',
        'comida': '🍽️', 'comidas': '🍽️', 'menu': '🍽️', 'menú': '🍽️',
        'fuerte': '🍽️', 'fuertes': '🍽️', 'ejecutivo': '🍽️',
        
        # POSTRES Y DULCES
        'postres': '🧁', 'postre': '🧁', 'dulces': '🧁', 'dulce': '🧁',
        'dessert': '🧁', 'desserts': '🧁', 'tortas': '🍰', 'torta': '🍰',
        'pasteles': '🍰', 'pastel': '🍰', 'helados': '🍦', 'helado': '🍦',
        'repostería': '🧁', 'reposteria': '🧁',
        
        # BEBIDAS
        'bebidas': '🍷', 'bebida': '🍷', 'drinks': '🍷', 'drink': '🍷',
        'líquidos': '🍷', 'liquidos': '🍷',
        
        # BEBIDAS ESPECÍFICAS
        'cervezas': '🍺', 'cerveza': '🍺', 'beer': '🍺', 'beers': '🍺',
        'vinos': '🍷', 'vino': '🍷', 'wine': '🍷', 'wines': '🍷',
        'cocteles': '🍸', 'coctel': '🍸', 'cocktail': '🍸', 'cocktails': '🍸',
        'jugos': '🧃', 'jugo': '🧃', 'juice': '🧃', 'juices': '🧃',
        'refrescos': '🥤', 'refresco': '🥤', 'gaseosas': '🥤', 'gaseosa': '🥤',
        'sodas': '🥤', 'soda': '🥤',
        
        # BEBIDAS CALIENTES
        'café': '☕', 'cafes': '☕', 'coffee': '☕',
        'té': '🍵', 'te': '🍵', 'tes': '🍵', 'tea': '🍵', 'teas': '🍵',
        'aromáticas': '🍵', 'aromaticas': '🍵', 'aromática': '🍵', 'aromatica': '🍵',
        'infusiones': '🍵', 'infusion': '🍵', 'chocolate caliente': '☕',
        
        # COMIDA ESPECÍFICA
        'pizza': '🍕', 'pizzas': '🍕', 'italiana': '🍕', 'italianas': '🍕',
        'hamburguesas': '🍔', 'hamburguesa': '🍔', 'burger': '🍔', 'burgers': '🍔',
        'sándwich': '🥪', 'sandwich': '🥪', 'sandwiches': '🥪',
        'tacos': '🌮', 'taco': '🌮', 'mexicana': '🌮', 'mexicanas': '🌮',
        'sushi': '🍣', 'japonesa': '🍣', 'japonesas': '🍣', 'asiática': '🍜', 'asiaticas': '🍜',
        
        # ENSALADAS Y SALUDABLES
        'ensaladas': '🥗', 'ensalada': '🥗', 'salad': '🥗', 'salads': '🥗',
        'saludables': '🥗', 'saludable': '🥗', 'healthy': '🥗', 'light': '🥗',
        'vegetariana': '🥗', 'vegetarianas': '🥗', 'vegana': '🌱', 'veganas': '🌱',
        
        # PANADERÍA Y DESAYUNO
        'panadería': '🥖', 'panaderia': '🥖', 'panes': '🍞', 'pan': '🍞',
        'desayuno': '🥐', 'desayunos': '🥐', 'breakfast': '🥐',
        'tostadas': '🍞', 'tostada': '🍞', 'croissant': '🥐', 'croissants': '🥐',
        
        # SNACKS Y APERITIVOS
        'snacks': '🍿', 'snack': '🍿', 'mecato': '🍿', 'mecatos': '🍿',
        'papas': '🍟', 'papa': '🍟', 'fritas': '🍟', 'frita': '🍟',
        'nachos': '🧀', 'nacho': '🧀', 'chips': '🍿',
        
        # CARNES Y PROTEÍNAS
        'carnes': '🥩', 'carne': '🥩', 'meat': '🥩', 'parrilla': '🥩',
        'pollo': '🍗', 'pollos': '🍗', 'chicken': '🍗', 'ave': '🍗', 'aves': '🍗',
        'pescado': '🐟', 'pescados': '🐟', 'fish': '🐟', 'mariscos': '🦐', 'marisco': '🦐',
        
        # ESPECIALES Y PROMOCIONES
        'promociones': '🎉', 'promocion': '🎉', 'promo': '🎉', 'promos': '🎉',
        'especiales': '⭐', 'especial': '⭐', 'del día': '⭐', 'del dia': '⭐',
        'combo': '🍽️', 'combos': '🍽️', 'menú del día': '⭐', 'menu del dia': '⭐'
    }
    
    # Buscar coincidencia exacta primero
    if nombre in iconos_por_categoria:
        return iconos_por_categoria[nombre]
    
    # Buscar coincidencias parciales (contiene la palabra)
    for palabra_clave, icono in iconos_por_categoria.items():
        if palabra_clave in nombre or nombre in palabra_clave:
            return icono
    
    # Buscar por palabras individuales
    palabras = re.split(r'\s+', nombre)
    for palabra in palabras:
        if palabra in iconos_por_categoria:
            return iconos_por_categoria[palabra]
    
    # Fallback: icono genérico por defecto
    return '🍽️'

def generar_codigo_categoria(nombre_categoria):
    """
    🏷️ GENERA CÓDIGO AUTOMÁTICO PARA CATEGORÍA
    Basado en las primeras letras del nombre
    """
    # Eliminar acentos y caracteres especiales
    import unicodedata
    nombre_limpio = unicodedata.normalize('NFD', nombre_categoria).encode('ascii', 'ignore').decode('ascii')
    
    # Tomar las primeras 3-4 letras y convertir a mayúsculas
    palabras = nombre_limpio.split()
    if len(palabras) >= 2:
        # Para nombres compuestos: primeras 2 letras de cada palabra
        codigo = ''.join([palabra[:2].upper() for palabra in palabras[:2]])
    else:
        # Para nombre simple: primeras 4 letras
        codigo = palabras[0][:4].upper()
    
    return codigo

# 🔧 FUNCIÓN HELPER PARA SERIALIZACIÓN
def categoria_to_dict(categoria):
    """Convierte un objeto Categoria a diccionario para JSON"""
    return {
        'id': categoria.id,
        'codigo': getattr(categoria, 'codigo', ''),
        'nombre': categoria.titulo,  # Usar titulo directamente del modelo
        'descripcion': getattr(categoria, 'descripcion', None),
        'activa': getattr(categoria, 'activa', True),
        'icono': getattr(categoria, 'icono', ''),
        'orden': getattr(categoria, 'orden', 0)
    }

def subcategoria_to_dict(subcategoria):
    """Convierte un objeto Subcategoria a diccionario para JSON"""
    return {
        'id': subcategoria.id,
        'codigo': getattr(subcategoria, 'codigo', ''),
        'nombre': subcategoria.nombre,
        'descripcion': getattr(subcategoria, 'descripcion', ''),
        'categoria_id': subcategoria.categoria_id,
        'tipo': getattr(subcategoria, 'tipo', ''),
        'activa': getattr(subcategoria, 'activa', True)
    }

@categorias_bp.route('/previsualizar-icono', methods=['GET', 'POST'])
def previsualizar_icono():
    """
    👁️ PREVISUALIZAR ICONO AUTOMÁTICO
    Permite ver qué icono se asignaría a una categoría sin crearla
    """
    try:
        # Obtener nombre del request (GET o POST)
        if request.method == 'GET':
            nombre = request.args.get('nombre', '').strip()
        else:  # POST
            if request.is_json:
                data = request.json
                nombre = data.get('nombre', '').strip()
            else:
                nombre = request.form.get('nombre', '').strip()
        
        if not nombre:
            return jsonify({'error': 'Nombre requerido'}), 400
        
        icono_detectado = detectar_icono_categoria(nombre)
        codigo_sugerido = generar_codigo_categoria(nombre)
        
        return jsonify({
            'nombre': nombre,
            'icono_sugerido': icono_detectado,
            'codigo_sugerido': codigo_sugerido,
            'preview': f"{nombre} → {icono_detectado}",
            'confianza': 0.95  # Simulado para ahora
        })
        
    except Exception as e:
        print(f"❌ Error previsualizando icono: {e}")
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/', methods=['GET', 'POST'])
def manejar_categorias():
    """
    📋 MANEJAR CATEGORÍAS - GET: Listar | POST: Crear
    """
    if request.method == 'GET':
        # 📋 LISTAR TODAS LAS CATEGORÍAS
        try:
            session = Session()
            
            categorias = session.query(Categoria).filter(Categoria.activa == True).all()
            categorias_dict = [categoria_to_dict(categoria) for categoria in categorias]
            session.close()
            
            return jsonify({
                'categorias': categorias_dict,
                'total': len(categorias_dict)
            })
            
        except Exception as e:
            print(f"❌ Error listando categorías: {e}")
            return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    elif request.method == 'POST':
        # ➕ CREAR NUEVA CATEGORÍA CON ICONO AUTOMÁTICO
        print("🚀 ENDPOINT POST /categorias/ EJECUTÁNDOSE")
        try:
            session = Session()
            
            # Obtener datos del request
            if request.is_json:
                data = request.json
            else:
                data = request.form.to_dict()
            
            print(f"📝 Datos recibidos: {data}")
            
            # Validaciones básicas
            if not data.get('nombre'):
                session.close()
                return jsonify({'error': 'El nombre es requerido'}), 400
            
            nombre_categoria = data.get('nombre').strip()
            print(f"🏷️ Categoría a crear: {nombre_categoria}")
            
            # 🎨 ASIGNACIÓN AUTOMÁTICA DE ICONO
            icono_auto = detectar_icono_categoria(nombre_categoria)
            icono_final = data.get('icono') or icono_auto  # Usar icono manual si se proporciona, sino automático
            print(f"🎨 Icono automático detectado: {icono_auto} → Final: {icono_final}")
            
            # 🏷️ GENERACIÓN AUTOMÁTICA DE CÓDIGO
            codigo_auto = generar_codigo_categoria(nombre_categoria)
            codigo_final = data.get('codigo') or codigo_auto
            
            # Verificar si código ya existe y generar uno único
            if session.query(Categoria).filter_by(codigo=codigo_final).first():
                contador = 1
                codigo_nuevo = f"{codigo_auto}{contador:02d}"
                while session.query(Categoria).filter_by(codigo=codigo_nuevo).first():
                    contador += 1
                    codigo_nuevo = f"{codigo_auto}{contador:02d}"
                codigo_final = codigo_nuevo
            
            # Crear nueva categoría
            nueva_categoria = Categoria(
                codigo=codigo_final,
                titulo=nombre_categoria,
                descripcion=data.get('descripcion', ''),
                icono=icono_final,  # 🎨 Icono automático asignado
                orden=int(data.get('orden', 0)) if data.get('orden') else 0,
                activa=data.get('activa') in [True, 'true', 'on', '1', 1] if 'activa' in data else True
            )
            
            session.add(nueva_categoria)
            session.commit()
            
            categoria_creada = {
                'id': nueva_categoria.id,
                'codigo': nueva_categoria.codigo,
                'nombre': nueva_categoria.titulo,
                'icono': nueva_categoria.icono,
                'descripcion': nueva_categoria.descripcion
            }
            
            session.close()
            
            print(f"✅ Categoría creada exitosamente: {categoria_creada}")
            return jsonify({
                'message': f'Categoría "{nombre_categoria}" creada exitosamente',
                'categoria': categoria_creada,
                'icono_detectado': icono_auto,
                'codigo_generado': codigo_final
            })
            
        except Exception as e:
            print(f"❌ Error creando categoría: {e}")
            return jsonify({'error': str(e)}), 500

@categorias_bp.route('/<int:id_categoria>')
def obtener_categoria(id_categoria):
    """
    🔍 OBTENER CATEGORÍA POR ID
    Devuelve los detalles de una categoría específica
    """
    try:
        session = Session()
        categoria = session.query(Categoria).filter_by(id=id_categoria).first()
        
        if not categoria:
            session.close()
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        categoria_dict = categoria_to_dict(categoria)
        session.close()
        
        return jsonify({
            'categoria': categoria_dict
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo categoría {id_categoria}: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@categorias_bp.route('/subcategorias/<int:categoria_id>')
def listar_subcategorias(categoria_id):
    """
    📋 LISTAR SUBCATEGORÍAS DE UNA CATEGORÍA
    Devuelve subcategorías específicas de una categoría
    """
    try:
        session = Session()
        
        subcategorias = session.query(Subcategoria)\
            .filter(Subcategoria.categoria_id == categoria_id)\
            .filter(Subcategoria.activa == True)\
            .all()
        
        subcategorias_dict = [subcategoria_to_dict(subcategoria) for subcategoria in subcategorias]
        session.close()
        
        return jsonify({
            'subcategorias': subcategorias_dict,
            'total': len(subcategorias_dict)
        })
        
    except Exception as e:
        print(f"❌ Error listando subcategorías de categoría {categoria_id}: {e}")
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['PUT'])
def actualizar_categoria(categoria_id):
    """
    ✏️ ACTUALIZAR CATEGORÍA EXISTENTE
    Actualiza campos de una categoría específica
    """
    try:
        session = Session()
        
        categoria = session.query(Categoria).filter(Categoria.id == categoria_id).first()
        
        if not categoria:
            session.close()
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        # Obtener datos del request
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        # Actualizar campos
        if 'nombre' in data:
            categoria.titulo = data['nombre']  # Usar titulo según el modelo
        if 'descripcion' in data:
            categoria.descripcion = data['descripcion']
        if 'icono' in data:
            categoria.icono = data['icono']
        if 'codigo' in data:
            categoria.codigo = data['codigo']
        if 'orden' in data:
            categoria.orden = int(data['orden']) if data['orden'] else 0
        if 'activa' in data:
            # Convertir correctamente el valor del checkbox
            categoria.activa = data['activa'] in [True, 'true', 'on', '1', 1]
        
        session.commit()
        session.close()
        
        return jsonify({
            'message': 'Categoría actualizada exitosamente'
        })
        
    except Exception as e:
        print(f"❌ Error actualizando categoría {categoria_id}: {e}")
        return jsonify({'error': str(e)}), 500

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
def eliminar_categoria(categoria_id):
    """
    🗑️ ELIMINAR CATEGORÍA
    Marca una categoría como inactiva
    """
    try:
        session = Session()
        
        categoria = session.query(Categoria).filter(Categoria.id == categoria_id).first()
        
        if not categoria:
            session.close()
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        # En lugar de eliminar, marcar como inactiva
        categoria.activa = False
        session.commit()
        session.close()
        
        return jsonify({
            'message': f'Categoría "{categoria.titulo}" desactivada exitosamente'
        })
        
    except Exception as e:
        print(f"❌ Error eliminando categoría {categoria_id}: {e}")
        return jsonify({'error': str(e)}), 500
