#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🏷️ ENDPOINTS PARA SUBCATEGORÍAS
Sistema completo de gestión de subcategorías con iconos automáticos
y relación con categorías padre
"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
import os
import re
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria

# Configuración de base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '../database', 'menu.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

# Blueprint específico para subcategorías
subcategorias_bp = Blueprint('subcategorias', __name__, url_prefix='/subcategorias')

# --- FUNCIONES HELPER ---

def subcategoria_to_dict(subcategoria):
    """Convierte un objeto Subcategoria a diccionario para JSON"""
    return {
        'id': subcategoria.id,
        'nombre': subcategoria.nombre,
        'descripcion': subcategoria.descripcion,
        'icono': subcategoria.icono or '🏷️',
        'codigo': subcategoria.codigo,
        'categoria_id': subcategoria.categoria_id,
        'categoria_nombre': subcategoria.categoria.titulo if subcategoria.categoria else None,
        'orden': subcategoria.orden,
        'activa': subcategoria.activa
    }

def detectar_icono_subcategoria(nombre_subcategoria):
    """
    🎨 SISTEMA DE DETECCIÓN AUTOMÁTICA DE ICONOS PARA SUBCATEGORÍAS
    Analiza el nombre y sugiere el icono más apropiado
    """
    nombre = nombre_subcategoria.lower().strip()
    
    # Mapeo específico para subcategorías (más granular que categorías)
    iconos_subcategorias = {
        # CARNES Y PROTEÍNAS
        'carne': '🥩', 'carnes': '🥩', 'res': '🥩', 'ternera': '🥩',
        'cerdo': '🥓', 'pork': '🥓', 'cochino': '🥓',
        'pollo': '🍗', 'aves': '🍗', 'gallina': '🍗', 'pavo': '🍗',
        'pescado': '🐟', 'salmon': '🍣', 'atun': '🍣', 'trucha': '🐟',
        'mariscos': '🦐', 'camaron': '🦐', 'langosta': '🦞', 'cangrejo': '🦀',
        
        # BEBIDAS ESPECÍFICAS
        'cerveza': '🍺', 'beer': '🍺', 'artesanal': '🍺', 'artesanales': '🍺',
        'vino': '🍷', 'wine': '🍷', 'tinto': '🍷', 'blanco': '🍷',
        'whisky': '🥃', 'ron': '🥃', 'vodka': '🥃', 'tequila': '🥃',
        'cafe': '☕', 'coffee': '☕', 'espresso': '☕', 'cappuccino': '☕',
        'te': '🍵', 'tea': '🍵', 'infusion': '🍵', 'herbal': '🍵',
        'jugo': '🧃', 'zumo': '🧃', 'natural': '🧃', 'fresco': '🧃',
        'soda': '🥤', 'gaseosa': '🥤', 'refresco': '🥤', 'cola': '🥤',
        
        # POSTRES ESPECÍFICOS
        'helado': '🍨', 'gelato': '🍨', 'sorbete': '🍨',
        'torta': '🍰', 'pastel': '🍰', 'cake': '🍰',
        'flan': '🍮', 'pudin': '🍮', 'creme': '🍮',
        'chocolate': '🍫', 'cacao': '🍫', 'brownie': '🍫',
        'fruta': '🍓', 'frutas': '🍓', 'fresa': '🍓', 'mango': '🥭',
        
        # PASTA Y GRANOS
        'pasta': '🍝', 'spaghetti': '🍝', 'fettuccine': '🍝', 'ravioli': '🍝',
        'arroz': '🍚', 'rice': '🍚', 'risotto': '🍚',
        'pizza': '🍕', 'pizzas': '🍕', 'margherita': '🍕', 'pepperoni': '🍕',
        
        # ENSALADAS Y VEGETALES
        'ensalada': '🥗', 'salad': '🥗', 'verde': '🥗', 'mixta': '🥗',
        'vegano': '🥬', 'vegetariano': '🥬', 'vegan': '🥬',
        'vegetal': '🥬', 'vegetales': '🥬',
        
        # PANADERÍA
        'pan': '🍞', 'bread': '🍞', 'integral': '🍞', 'artesano': '🍞',
        'sandwich': '🥪', 'bocadillo': '🥪', 'torta': '🥪',
        'empanada': '🥟', 'empanadas': '🥟', 'pastel': '🥟',
        
        # ESPECIALES REGIONALES
        'mexicana': '🌮', 'mexican': '🌮', 'taco': '🌮', 'burrito': '🌯',
        'italiana': '🍝', 'italian': '🍝', 'napolitana': '🍕',
        'asiática': '🍜', 'asian': '🍜', 'ramen': '🍜', 'sushi': '🍣',
        'mediterranea': '🫒', 'mediterranean': '🫒', 'griega': '🫒',
        
        # TEMPERATURA/PREPARACIÓN
        'caliente': '🔥', 'hot': '🔥', 'picante': '🌶️',
        'frio': '❄️', 'cold': '❄️', 'helado': '🧊',
        'frito': '🍤', 'asado': '🔥', 'grillado': '🔥',
        'horneado': '🔥', 'vapor': '♨️',
        
        # OCASIONES ESPECIALES
        'premium': '⭐', 'gourmet': '👨‍🍳', 'especial': '✨',
        'tradicional': '🏠', 'casero': '🏠', 'artesanal': '👨‍🍳',
        'infantil': '🧒', 'kids': '🧒', 'niños': '🧒',
        'ejecutivo': '💼', 'business': '💼'
    }
    
    # Buscar coincidencia exacta o parcial
    for clave, icono in iconos_subcategorias.items():
        if clave in nombre:
            print(f"🎨 Icono detectado para '{nombre_subcategoria}': {icono} (coincide con '{clave}')")
            return icono
    
    # Icono por defecto para subcategorías
    print(f"🎨 Icono por defecto para '{nombre_subcategoria}': 🏷️")
    return '🏷️'

def generar_codigo_subcategoria(nombre, categoria_nombre=None):
    """
    🏷️ GENERAR CÓDIGO ÚNICO PARA SUBCATEGORIA
    Formato: CATSUB (4 letras categoría + 3 letras subcategoría)
    """
    # Limpiar y obtener primeras letras del nombre
    nombre_limpio = re.sub(r'[^a-zA-Z\s]', '', nombre.upper())
    palabras = nombre_limpio.split()
    
    # Generar código de subcategoría
    if len(palabras) >= 2:
        codigo_sub = palabras[0][:2] + palabras[1][:1]
    else:
        codigo_sub = palabras[0][:3] if palabras else 'SUB'
    
    # Generar código de categoría si está disponible
    if categoria_nombre:
        categoria_limpia = re.sub(r'[^a-zA-Z\s]', '', categoria_nombre.upper())
        palabras_cat = categoria_limpia.split()
        if len(palabras_cat) >= 2:
            codigo_cat = palabras_cat[0][:2] + palabras_cat[1][:1]
        else:
            codigo_cat = palabras_cat[0][:3] if palabras_cat else 'CAT'
    else:
        codigo_cat = 'CAT'
    
    return f"{codigo_cat}{codigo_sub}"

# --- ENDPOINTS ---

@subcategorias_bp.route('/', methods=['GET', 'POST'])
def manejar_subcategorias():
    """
    🎯 ENDPOINT PRINCIPAL DE SUBCATEGORÍAS
    GET: Listar todas las subcategorías
    POST: Crear nueva subcategoría
    """
    session = Session()
    try:
        if request.method == 'GET':
            print("🚀 ENDPOINT GET /subcategorias/ EJECUTÁNDOSE")
            
            # Obtener subcategorías con información de categoría
            subcategorias = session.query(Subcategoria).options(
                joinedload(Subcategoria.categoria)
            ).order_by(Subcategoria.orden, Subcategoria.nombre).all()
            
            subcategorias_data = [subcategoria_to_dict(sub) for sub in subcategorias]
            
            print(f"✅ {len(subcategorias_data)} subcategorías encontradas")
            return jsonify({
                'success': True,
                'subcategorias': subcategorias_data,
                'total': len(subcategorias_data)
            })
        
        elif request.method == 'POST':
            print("🚀 ENDPOINT POST /subcategorias/ EJECUTÁNDOSE")
            
            # Obtener datos del request
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            print(f"📝 Datos recibidos: {data}")
            
            # Validar datos requeridos
            if not data.get('nombre'):
                return jsonify({
                    'success': False,
                    'message': 'El nombre de la subcategoría es obligatorio'
                }), 400
            
            if not data.get('categoria_id'):
                return jsonify({
                    'success': False,
                    'message': 'Debe seleccionar una categoría padre'
                }), 400
            
            # Verificar que la categoría existe
            categoria = session.query(Categoria).filter_by(
                id=int(data['categoria_id'])
            ).first()
            
            if not categoria:
                return jsonify({
                    'success': False,
                    'message': 'La categoría seleccionada no existe'
                }), 400
            
            # Generar código e icono automáticos
            codigo = generar_codigo_subcategoria(data['nombre'], categoria.titulo)
            icono = detectar_icono_subcategoria(data['nombre'])
            
            print(f"🏷️ Subcategoría a crear: {data['nombre']}")
            print(f"📂 Categoría padre: {categoria.titulo}")
            print(f"🎨 Icono automático detectado: {icono}")
            print(f"🏷️ Código generado: {codigo}")
            
            # Crear nueva subcategoría
            nueva_subcategoria = Subcategoria(
                nombre=data['nombre'],
                descripcion=data.get('descripcion', ''),
                codigo=codigo,
                icono=icono,
                categoria_id=int(data['categoria_id']),
                activa=data.get('activa', True),
                orden=data.get('orden', 0)
            )
            
            session.add(nueva_subcategoria)
            session.commit()
            
            # Recargar con información de categoría
            session.refresh(nueva_subcategoria)
            nueva_subcategoria = session.query(Subcategoria).options(
                joinedload(Subcategoria.categoria)
            ).filter_by(id=nueva_subcategoria.id).first()
            
            resultado = subcategoria_to_dict(nueva_subcategoria)
            
            print(f"✅ Subcategoría creada exitosamente: {resultado}")
            return jsonify({
                'success': True,
                'message': 'Subcategoría creada correctamente',
                'subcategoria': resultado
            })
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error en manejar_subcategorias: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500
    finally:
        session.close()

@subcategorias_bp.route('/<int:subcategoria_id>', methods=['GET', 'PUT', 'DELETE'])
def manejar_subcategoria_especifica(subcategoria_id):
    """
    🎯 ENDPOINT PARA SUBCATEGORÍA ESPECÍFICA
    GET: Obtener detalles de una subcategoría
    PUT: Actualizar subcategoría
    DELETE: Eliminar subcategoría
    """
    session = Session()
    try:
        subcategoria = session.query(Subcategoria).options(
            joinedload(Subcategoria.categoria)
        ).filter_by(id=subcategoria_id).first()
        
        if not subcategoria:
            return jsonify({
                'success': False,
                'message': 'Subcategoría no encontrada'
            }), 404
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'subcategoria': subcategoria_to_dict(subcategoria)
            })
        
        elif request.method == 'PUT':
            # Obtener datos de actualización
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            print(f"🔄 Actualizando subcategoría {subcategoria_id}: {data}")
            
            # Actualizar campos
            if 'nombre' in data:
                subcategoria.nombre = data['nombre']
                # Regenerar icono si cambió el nombre
                subcategoria.icono = detectar_icono_subcategoria(data['nombre'])
            
            if 'descripcion' in data:
                subcategoria.descripcion = data['descripcion']
                
            if 'categoria_id' in data:
                # Verificar que la nueva categoría existe
                nueva_categoria = session.query(Categoria).filter_by(
                    id=int(data['categoria_id'])
                ).first()
                if nueva_categoria:
                    subcategoria.categoria_id = int(data['categoria_id'])
                    # Regenerar código con nueva categoría
                    subcategoria.codigo = generar_codigo_subcategoria(
                        subcategoria.nombre, 
                        nueva_categoria.titulo
                    )
                    
            if 'activa' in data:
                subcategoria.activa = bool(data['activa'])
                
            if 'orden' in data:
                subcategoria.orden = int(data['orden'])
            
            session.commit()
            session.refresh(subcategoria)
            
            # Recargar con información actualizada
            subcategoria = session.query(Subcategoria).options(
                joinedload(Subcategoria.categoria)
            ).filter_by(id=subcategoria_id).first()
            
            return jsonify({
                'success': True,
                'message': 'Subcategoría actualizada correctamente',
                'subcategoria': subcategoria_to_dict(subcategoria)
            })
        
        elif request.method == 'DELETE':
            print(f"🗑️ Eliminando subcategoría: {subcategoria.nombre}")
            
            session.delete(subcategoria)
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Subcategoría eliminada correctamente'
            })
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error en subcategoría específica: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500
    finally:
        session.close()

@subcategorias_bp.route('/categoria/<int:categoria_id>', methods=['GET'])
def listar_subcategorias_por_categoria(categoria_id):
    """
    📂 OBTENER SUBCATEGORÍAS DE UNA CATEGORÍA ESPECÍFICA
    """
    session = Session()
    try:
        # Verificar que la categoría existe
        categoria = session.query(Categoria).filter_by(id=categoria_id).first()
        if not categoria:
            return jsonify({
                'success': False,
                'message': 'Categoría no encontrada'
            }), 404
        
        # Obtener subcategorías
        subcategorias = session.query(Subcategoria).options(
            joinedload(Subcategoria.categoria)
        ).filter_by(categoria_id=categoria_id).order_by(
            Subcategoria.orden, Subcategoria.nombre
        ).all()
        
        subcategorias_data = [subcategoria_to_dict(sub) for sub in subcategorias]
        
        return jsonify({
            'success': True,
            'categoria': {
                'id': categoria.id,
                'nombre': categoria.titulo,
                'icono': categoria.icono
            },
            'subcategorias': subcategorias_data,
            'total': len(subcategorias_data)
        })
        
    except Exception as e:
        print(f"❌ Error listando subcategorías por categoría: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500
    finally:
        session.close()

@subcategorias_bp.route('/previsualizar-icono', methods=['GET'])
def previsualizar_icono():
    """
    🎨 PREVISUALIZAR ICONO BASADO EN NOMBRE
    Utilizado por el frontend para mostrar iconos en tiempo real
    """
    nombre = request.args.get('nombre', '').strip()
    
    if not nombre:
        return jsonify({
            'success': False,
            'message': 'Parámetro nombre es requerido'
        }), 400
    
    icono = detectar_icono_subcategoria(nombre)
    
    return jsonify({
        'success': True,
        'icono': icono,
        'nombre': nombre
    })

if __name__ == '__main__':
    print("🏷️ Sistema de subcategorías listo")
