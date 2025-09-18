#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Endpoints para el Backend del Chatbot
=========================================
Define todas las rutas y endpoints para el sistema del chatbot.
"""

from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
import json
import os

# Importar modelos
from .models import (
    Sesion, Calificacion, Comentario, NotificacionMesero, 
    Analytics, ConfiguracionChatbot, TemaPersonalizacion, PropiedadTema
)

# Crear blueprint para las APIs del chatbot
chatbot_api_bp = Blueprint('chatbot_api', __name__, url_prefix='/api/chatbot')

# Configuración de base de datos (usar la misma que el sistema principal)
def get_db_session():
    """Obtener sesión de base de datos"""
    # TODO: Conectar con la configuración principal de la BD
    engine = create_engine('sqlite:///modulos/backend/menu/menu.db')
    Session = sessionmaker(bind=engine)
    return Session()

# Crear SessionLocal para compatibilidad con nuevos endpoints
SessionLocal = get_db_session

# ==================== ENDPOINTS DE SESIONES ====================

@chatbot_api_bp.route('/sesion/iniciar', methods=['POST'])
def iniciar_sesion():
    """
    Inicia una nueva sesión de chatbot para una mesa
    
    POST /api/chatbot/sesion/iniciar
    Body: {
        "mesa": "1" | "barra",
        "nombre_cliente": "Juan" (opcional),
        "dispositivo": "user-agent string",
        "ip_cliente": "192.168.1.x"
    }
    """
    try:
        data = request.get_json()
        mesa = data.get('mesa', '1')
        nombre_cliente = data.get('nombre_cliente', '')
        dispositivo = data.get('dispositivo', request.headers.get('User-Agent', ''))
        ip_cliente = data.get('ip_cliente', request.remote_addr)
        
        db = get_db_session()
        
        # Verificar si ya existe una sesión activa para esta mesa
        sesion_existente = db.query(Sesion).filter(
            Sesion.mesa == mesa,
            Sesion.activa == True
        ).first()
        
        if sesion_existente:
            # Actualizar sesión existente
            sesion_existente.fecha_ultimo_acceso = datetime.utcnow()
            if nombre_cliente:
                sesion_existente.nombre_cliente = nombre_cliente
            db.commit()
            sesion_id = sesion_existente.id
        else:
            # Crear nueva sesión
            nueva_sesion = Sesion(
                mesa=mesa,
                nombre_cliente=nombre_cliente,
                dispositivo=dispositivo,
                ip_cliente=ip_cliente
            )
            db.add(nueva_sesion)
            db.commit()
            sesion_id = nueva_sesion.id
        
        # Registrar analytics
        analytics = Analytics(
            mesa=mesa,
            evento='acceso',
            valor_texto=f'Sesión iniciada - Cliente: {nombre_cliente or "Anónimo"}',
            metadatos=json.dumps({'dispositivo': dispositivo, 'ip': ip_cliente})
        )
        db.add(analytics)
        db.commit()
        
        db.close()
        
        return jsonify({
            'success': True,
            'sesion_id': sesion_id,
            'mensaje': f'Sesión iniciada para mesa {mesa}',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@chatbot_api_bp.route('/sesion/<int:sesion_id>/actualizar', methods=['PUT'])
def actualizar_sesion(sesion_id):
    """
    Actualiza datos de la sesión (principalmente el nombre del cliente)
    
    PUT /api/chatbot/sesion/<id>/actualizar
    Body: {
        "nombre_cliente": "Juan Pérez",
        "actualizar_ultimo_acceso": true
    }
    """
    try:
        data = request.get_json()
        
        db = get_db_session()
        sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
        
        if not sesion:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        if 'nombre_cliente' in data:
            sesion.nombre_cliente = data['nombre_cliente']
        
        if data.get('actualizar_ultimo_acceso', True):
            sesion.fecha_ultimo_acceso = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'mensaje': 'Sesión actualizada correctamente',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_api_bp.route('/sesion/<int:sesion_id>/actividad', methods=['POST'])
def actualizar_actividad_sesion(sesion_id):
    """
    Actualiza la actividad de una sesión (última vez activa)
    
    POST /api/chatbot/sesion/<id>/actividad
    """
    try:
        session = get_db_session()
        
        # Buscar la sesión
        sesion = session.query(Sesion).filter_by(id=sesion_id).first()
        if not sesion:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        # Actualizar última actividad
        sesion.fecha_ultimo_acceso = datetime.utcnow()
        session.commit()
        
        return jsonify({
            'success': True,
            'sesion_id': sesion_id,
            'ultima_actividad': sesion.fecha_ultimo_acceso.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()

@chatbot_api_bp.route('/sesion/<int:sesion_id>/cerrar', methods=['POST'])
def cerrar_sesion(sesion_id):
    """
    Cierra una sesión específica
    
    POST /api/chatbot/sesion/<id>/cerrar
    """
    try:
        session = get_db_session()
        
        # Buscar la sesión
        sesion = session.query(Sesion).filter_by(id=sesion_id).first()
        if not sesion:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        # Marcar como inactiva
        sesion.activa = False
        sesion.fecha_ultimo_acceso = datetime.utcnow()
        session.commit()
        
        return jsonify({
            'success': True,
            'sesion_id': sesion_id,
            'mensaje': 'Sesión cerrada correctamente',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()

@chatbot_api_bp.route('/sesion/<int:sesion_id>', methods=['GET'])
def obtener_sesion(sesion_id):
    """
    Obtiene los datos de una sesión específica
    
    GET /api/chatbot/sesion/<id>
    """
    try:
        session = get_db_session()
        
        # Buscar la sesión
        sesion = session.query(Sesion).filter_by(id=sesion_id).first()
        if not sesion:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'id': sesion.id,
            'mesa': sesion.mesa,
            'nombre_cliente': sesion.nombre_cliente,
            'fecha_inicio': sesion.fecha_inicio.isoformat() if sesion.fecha_inicio else None,
            'fecha_ultimo_acceso': sesion.fecha_ultimo_acceso.isoformat() if sesion.fecha_ultimo_acceso else None,
            'dispositivo': sesion.dispositivo,
            'ip_cliente': sesion.ip_cliente,
            'activa': sesion.activa,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()

@chatbot_api_bp.route('/sesion/<int:sesion_id>/validar', methods=['GET'])
def validar_sesion(sesion_id):
    """
    Valida si una sesión sigue siendo válida según configuraciones de timeout
    
    GET /api/chatbot/sesion/<id>/validar
    """
    try:
        session = get_db_session()
        
        # Buscar la sesión
        sesion = session.query(Sesion).filter_by(id=sesion_id).first()
        if not sesion:
            return jsonify({
                'success': False,
                'valida': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        # Verificar si está activa
        if not sesion.activa:
            return jsonify({
                'success': True,
                'valida': False,
                'razon': 'Sesión marcada como inactiva'
            })
        
        # Obtener configuración de timeout (en minutos)
        config_timeout = session.query(ConfiguracionChatbot).filter_by(
            clave='sesion_timeout'
        ).first()
        
        timeout_minutos = 10  # Default
        if config_timeout and config_timeout.valor.isdigit():
            timeout_minutos = int(config_timeout.valor)
        
        # Verificar tiempo de inactividad
        if sesion.fecha_ultimo_acceso:
            tiempo_inactivo = datetime.utcnow() - sesion.fecha_ultimo_acceso
            if tiempo_inactivo.total_seconds() > (timeout_minutos * 60):
                # Marcar sesión como inactiva automáticamente
                sesion.activa = False
                session.commit()
                
                return jsonify({
                    'success': True,
                    'valida': False,
                    'razon': f'Timeout: {tiempo_inactivo.total_seconds()/60:.1f} minutos de inactividad',
                    'timeout_aplicado': True
                })
        
        return jsonify({
            'success': True,
            'valida': True,
            'timeout_restante_minutos': timeout_minutos - (
                (datetime.utcnow() - sesion.fecha_ultimo_acceso).total_seconds() / 60
                if sesion.fecha_ultimo_acceso else 0
            )
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()

@chatbot_api_bp.route('/sesiones/activas', methods=['GET'])
def obtener_sesiones_activas():
    """
    Obtiene todas las sesiones activas para el dashboard administrativo
    
    GET /api/chatbot/sesiones/activas
    """
    try:
        db = SessionLocal()
        
        # Obtener sesiones activas con información de cliente
        sesiones_activas = db.query(Sesion).filter_by(activa=True).order_by(
            Sesion.fecha_inicio.desc()
        ).all()
        
        # Formatear datos para el dashboard
        sesiones_data = []
        for sesion in sesiones_activas:
            tiempo_activo = datetime.utcnow() - sesion.fecha_inicio
            ultimo_acceso = sesion.fecha_ultimo_acceso or sesion.fecha_inicio
            tiempo_inactivo = datetime.utcnow() - ultimo_acceso
            
            sesiones_data.append({
                'id': sesion.id,
                'mesa': sesion.mesa,
                'cliente': sesion.nombre_cliente or 'Anónimo',
                'inicio': sesion.fecha_inicio.strftime('%H:%M:%S'),
                'ultimo_acceso': ultimo_acceso.strftime('%H:%M:%S'),
                'tiempo_activo': f"{int(tiempo_activo.total_seconds() // 60)}min",
                'estado': 'Activa',
                'dispositivo': sesion.dispositivo or 'Desktop'
            })
        
        return jsonify({
            'success': True,
            'sesiones': sesiones_data,
            'total': len(sesiones_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener sesiones activas: {str(e)}'
        }), 500
    finally:
        db.close()

@chatbot_api_bp.route('/configuracion/timeout', methods=['GET'])
def obtener_timeout_configurado():
    """
    Obtiene el timeout configurado para sesiones en milisegundos (para JavaScript)
    
    GET /api/chatbot/configuracion/timeout
    """
    try:
        session = get_db_session()
        
        # Obtener configuración de timeout
        config_timeout = session.query(ConfiguracionChatbot).filter_by(
            clave='sesion_timeout'
        ).first()
        
        timeout_minutos = 10  # Default
        if config_timeout and config_timeout.valor.isdigit():
            timeout_minutos = int(config_timeout.valor)
        
        return jsonify({
            'success': True,
            'timeout_minutos': timeout_minutos,
            'timeout_milisegundos': timeout_minutos * 60 * 1000,
            'mensaje': f'Sesiones se cierran automáticamente después de {timeout_minutos} minutos de inactividad'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()

# ==================== ENDPOINTS DE CALIFICACIONES ====================

@chatbot_api_bp.route('/calificacion', methods=['POST'])
def guardar_calificacion():
    """
    Guarda una calificación del cliente
    
    POST /api/chatbot/calificacion
    Body: {
        "sesion_id": 123,
        "estrellas": 5,
        "categoria": "servicio" | "comida" | "ambiente" | "general"
    }
    """
    try:
        data = request.get_json()
        sesion_id = data.get('sesion_id')
        estrellas = data.get('estrellas')
        categoria = data.get('categoria', 'general')
        
        if not sesion_id or not estrellas or estrellas < 1 or estrellas > 5:
            return jsonify({
                'success': False,
                'error': 'Datos inválidos. Se requiere sesion_id y estrellas (1-5)'
            }), 400
        
        db = get_db_session()
        
        # Verificar que la sesión existe y está activa
        sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
        if not sesion:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        if not sesion.activa:
            return jsonify({
                'success': False,
                'error': 'No se puede calificar una sesión inactiva'
            }), 400
        
        # Verificar si ya existe una calificación para esta sesión y categoría
        calificacion_existente = db.query(Calificacion).filter(
            Calificacion.sesion_id == sesion_id,
            Calificacion.categoria == categoria
        ).first()
        
        if calificacion_existente:
            # Actualizar calificación existente
            calificacion_existente.estrellas = estrellas
            calificacion_existente.fecha_calificacion = datetime.utcnow()
            db.commit()
            
            return jsonify({
                'success': True,
                'accion': 'actualizada',
                'calificacion_id': calificacion_existente.id,
                'sesion_id': sesion_id,
                'estrellas': estrellas,
                'categoria': categoria,
                'mensaje': 'Calificación actualizada correctamente'
            })
        
        # Crear nueva calificación
        calificacion = Calificacion(
            sesion_id=sesion_id,
            estrellas=estrellas,
            categoria=categoria
        )
        db.add(calificacion)
        
        # Registrar analytics
        analytics = Analytics(
            mesa=sesion.mesa,
            evento='calificacion',
            valor_numerico=estrellas,
            valor_texto=f'Calificación {categoria}: {estrellas} estrellas',
            metadatos=json.dumps({'categoria': categoria, 'cliente': sesion.nombre_cliente})
        )
        db.add(analytics)
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'mensaje': f'Calificación de {estrellas} estrellas guardada',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_api_bp.route('/calificaciones', methods=['GET'])
def obtener_calificaciones():
    """
    Obtiene todas las calificaciones para el dashboard administrativo
    
    GET /api/chatbot/calificaciones
    """
    try:
        db = SessionLocal()
        
        # Obtener calificaciones recientes con información de sesión
        calificaciones = db.query(Calificacion).join(Sesion).order_by(
            Calificacion.fecha_calificacion.desc()
        ).limit(50).all()
        
        # Formatear datos para el dashboard
        calificaciones_data = []
        for cal in calificaciones:
            calificaciones_data.append({
                'id': cal.id,
                'mesa': cal.sesion.mesa,
                'cliente': cal.sesion.nombre_cliente or 'Anónimo',
                'estrellas': cal.estrellas,
                'categoria': cal.categoria,
                'fecha': cal.fecha_calificacion.strftime('%d/%m/%Y %H:%M'),
                'sesion_id': cal.sesion_id
            })
        
        # Calcular estadísticas
        total_calificaciones = len(calificaciones_data)
        promedio = sum(c['estrellas'] for c in calificaciones_data) / total_calificaciones if total_calificaciones > 0 else 0
        
        return jsonify({
            'success': True,
            'calificaciones': calificaciones_data,
            'estadisticas': {
                'total': total_calificaciones,
                'promedio': round(promedio, 1),
                'excelentes': len([c for c in calificaciones_data if c['estrellas'] >= 4]),
                'necesitan_atencion': len([c for c in calificaciones_data if c['estrellas'] <= 2])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener calificaciones: {str(e)}'
        }), 500
    finally:
        db.close()

# ==================== ENDPOINTS DE COMENTARIOS ====================

@chatbot_api_bp.route('/comentario', methods=['POST'])
def guardar_comentario():
    """
    Guarda un comentario del cliente
    
    POST /api/chatbot/comentario
    Body: {
        "sesion_id": 123,
        "texto_comentario": "Excelente servicio!",
        "tipo": "felicitacion" | "sugerencia" | "queja" | "general"
    }
    """
    try:
        data = request.get_json()
        sesion_id = data.get('sesion_id')
        texto_comentario = data.get('texto_comentario', '').strip()
        tipo = data.get('tipo', 'general')
        
        if not sesion_id or not texto_comentario:
            return jsonify({
                'success': False,
                'error': 'Se requiere sesion_id y texto_comentario'
            }), 400
        
        db = get_db_session()
        
        # Verificar que la sesión existe
        sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
        if not sesion:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        # Crear comentario
        comentario = Comentario(
            sesion_id=sesion_id,
            texto_comentario=texto_comentario,
            tipo=tipo
        )
        db.add(comentario)
        
        # Registrar analytics
        analytics = Analytics(
            mesa=sesion.mesa,
            evento='comentario',
            valor_texto=f'Comentario {tipo}: {texto_comentario[:50]}...',
            metadatos=json.dumps({
                'tipo': tipo, 
                'longitud': len(texto_comentario),
                'cliente': sesion.nombre_cliente
            })
        )
        db.add(analytics)
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'mensaje': 'Comentario guardado correctamente',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ENDPOINTS DE NOTIFICACIONES ====================

@chatbot_api_bp.route('/notificacion/mesero', methods=['POST'])
def llamar_mesero():
    """
    Crea una notificación para llamar al mesero
    
    POST /api/chatbot/notificacion/mesero
    Body: {
        "sesion_id": 123,
        "tipo_notificacion": "llamar_mesero" | "pedido_especial" | "emergencia",
        "mensaje": "Necesito ayuda con el menú" (opcional),
        "prioridad": "normal" | "alta" | "urgente"
    }
    """
    try:
        data = request.get_json()
        sesion_id = data.get('sesion_id')
        tipo_notificacion = data.get('tipo_notificacion', 'llamar_mesero')
        mensaje = data.get('mensaje', '')
        prioridad = data.get('prioridad', 'normal')
        
        if not sesion_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere sesion_id'
            }), 400
        
        db = get_db_session()
        
        # Verificar que la sesión existe
        sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
        if not sesion:
            return jsonify({
                'success': False,
                'error': 'Sesión no encontrada'
            }), 404
        
        # Crear notificación
        notificacion = NotificacionMesero(
            sesion_id=sesion_id,
            tipo_notificacion=tipo_notificacion,
            mensaje=mensaje,
            prioridad=prioridad
        )
        db.add(notificacion)
        
        # Registrar analytics
        analytics = Analytics(
            mesa=sesion.mesa,
            evento='notificacion',
            valor_texto=f'{tipo_notificacion} - Prioridad: {prioridad}',
            metadatos=json.dumps({
                'tipo': tipo_notificacion,
                'prioridad': prioridad,
                'mensaje': mensaje,
                'cliente': sesion.nombre_cliente
            })
        )
        db.add(analytics)
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'mensaje': f'Notificación enviada - Mesa {sesion.mesa}',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_api_bp.route('/notificaciones/pendientes', methods=['GET'])
def obtener_notificaciones_pendientes():
    """
    Obtiene todas las notificaciones pendientes para el personal
    
    GET /api/chatbot/notificaciones/pendientes
    """
    try:
        db = get_db_session()
        
        notificaciones = db.query(NotificacionMesero, Sesion).join(
            Sesion, NotificacionMesero.sesion_id == Sesion.id
        ).filter(
            NotificacionMesero.atendida == False
        ).order_by(
            NotificacionMesero.prioridad.desc(),
            NotificacionMesero.fecha_notificacion.asc()
        ).all()
        
        resultado = []
        for notificacion, sesion in notificaciones:
            resultado.append({
                'id': notificacion.id,
                'mesa': sesion.mesa,
                'cliente': sesion.nombre_cliente or 'Anónimo',
                'tipo': notificacion.tipo_notificacion,
                'mensaje': notificacion.mensaje,
                'prioridad': notificacion.prioridad,
                'fecha': notificacion.fecha_notificacion.isoformat(),
                'tiempo_espera': str(datetime.utcnow() - notificacion.fecha_notificacion)
            })
        
        db.close()
        
        return jsonify({
            'success': True,
            'notificaciones': resultado,
            'total': len(resultado),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_api_bp.route('/notificaciones', methods=['GET'])
def obtener_notificaciones():
    """
    Alias para obtener notificaciones pendientes (compatibilidad dashboard)
    
    GET /api/chatbot/notificaciones
    """
    return obtener_notificaciones_pendientes()

# ==================== ENDPOINTS DE ANALYTICS ====================

@chatbot_api_bp.route('/analytics/resumen', methods=['GET'])
def obtener_resumen_analytics():
    """
    Obtiene un resumen de analytics del chatbot
    
    GET /api/chatbot/analytics/resumen?dias=7
    """
    try:
        dias = request.args.get('dias', 7, type=int)
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        
        db = get_db_session()
        
        # Sesiones activas
        sesiones_activas = db.query(Sesion).filter(
            Sesion.activa == True,
            Sesion.fecha_ultimo_acceso >= fecha_inicio
        ).count()
        
        # Calificaciones promedio
        calificaciones = db.query(func.avg(Calificacion.estrellas)).filter(
            Calificacion.fecha_calificacion >= fecha_inicio
        ).scalar()
        
        # Total de comentarios
        comentarios_total = db.query(Comentario).filter(
            Comentario.fecha_comentario >= fecha_inicio
        ).count()
        
        # Notificaciones pendientes
        notificaciones_pendientes = db.query(NotificacionMesero).filter(
            NotificacionMesero.atendida == False
        ).count()
        
        # Mesas más activas
        mesas_activas = db.query(
            Sesion.mesa, 
            func.count(Sesion.id).label('total_sesiones')
        ).filter(
            Sesion.fecha_inicio >= fecha_inicio
        ).group_by(Sesion.mesa).order_by(
            func.count(Sesion.id).desc()
        ).limit(5).all()
        
        db.close()
        
        return jsonify({
            'success': True,
            'periodo_dias': dias,
            'resumen': {
                'sesiones_activas': sesiones_activas,
                'calificacion_promedio': round(calificaciones or 0, 2),
                'total_comentarios': comentarios_total,
                'notificaciones_pendientes': notificaciones_pendientes,
                'mesas_mas_activas': [
                    {'mesa': mesa, 'sesiones': total} 
                    for mesa, total in mesas_activas
                ]
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ENDPOINTS DE CONFIGURACIÓN ====================

@chatbot_api_bp.route('/configuracion', methods=['GET'])
def obtener_configuracion():
    """
    Obtiene toda la configuración del chatbot
    
    GET /api/chatbot/configuracion
    """
    try:
        db = get_db_session()
        
        configuraciones = db.query(ConfiguracionChatbot).all()
        
        resultado = {}
        for config in configuraciones:
            valor = config.valor
            # Convertir según el tipo
            if config.tipo == 'integer':
                valor = int(valor)
            elif config.tipo == 'boolean':
                valor = valor.lower() == 'true'
            elif config.tipo == 'json':
                valor = json.loads(valor)
            
            resultado[config.clave] = {
                'valor': valor,
                'tipo': config.tipo,
                'descripcion': config.descripcion
            }
        
        db.close()
        
        return jsonify({
            'success': True,
            'configuracion': resultado,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_api_bp.route('/saludo', methods=['GET'])
def obtener_saludo_dinamico():
    """
    Obtiene el saludo apropiado según la hora del día
    
    GET /api/chatbot/saludo?mesa=1&nombre=Juan
    """
    try:
        mesa = request.args.get('mesa', '1')
        nombre = request.args.get('nombre', '')
        
        hora_actual = datetime.now().hour
        
        # Determinar saludo según la hora
        if 6 <= hora_actual < 12:
            saludo_base = "Buenos días"
        elif 12 <= hora_actual < 18:
            saludo_base = "Buenas tardes"
        else:
            saludo_base = "Buenas noches"
        
        # Personalizar mensaje
        if nombre:
            mensaje_personalizado = f"{saludo_base}, {nombre}! Es un placer atenderte en la mesa {mesa}."
        else:
            mensaje_personalizado = f"{saludo_base}! Bienvenido a la mesa {mesa}."
        
        return jsonify({
            'success': True,
            'saludo_base': saludo_base,
            'mensaje_completo': mensaje_personalizado,
            'hora_actual': hora_actual,
            'mesa': mesa,
            'nombre': nombre,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# SISTEMA DE PERSONALIZACIÓN DE TEMAS
# ============================================

@chatbot_api_bp.route('/temas', methods=['GET'])
def obtener_temas():
    """
    Obtiene la lista completa de temas disponibles
    
    Returns:
        JSON: Lista de temas con sus propiedades y estado
    """
    try:
        db = SessionLocal()
        
        # Obtener todos los temas con sus propiedades
        temas = db.query(TemaPersonalizacion).all()
        
        temas_data = []
        for tema in temas:
            # Obtener las propiedades del tema
            propiedades = db.query(PropiedadTema).filter_by(tema_id=tema.id).all()
            
            # Organizar propiedades por categoría
            props_por_categoria = {}
            for prop in propiedades:
                if prop.categoria not in props_por_categoria:
                    props_por_categoria[prop.categoria] = {}
                props_por_categoria[prop.categoria][prop.propiedad] = prop.valor
            
            tema_info = {
                'id': tema.id,
                'nombre': tema.nombre,
                'descripcion': tema.descripcion,
                'activo': tema.activo,
                'predefinido': tema.predefinido,
                'fecha_creacion': tema.fecha_creacion.isoformat(),
                'propiedades': props_por_categoria,
                'total_propiedades': len(propiedades)
            }
            temas_data.append(tema_info)
        
        # Obtener tema activo
        tema_activo = db.query(TemaPersonalizacion).filter_by(activo=True).first()
        
        return jsonify({
            'success': True,
            'temas': temas_data,
            'tema_activo_id': tema_activo.id if tema_activo else None,
            'total_temas': len(temas_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener temas: {str(e)}'
        }), 500
    finally:
        db.close()

@chatbot_api_bp.route('/temas/<int:tema_id>/activar', methods=['POST'])
def activar_tema(tema_id):
    """
    Activa un tema específico (desactiva todos los demás)
    """
    try:
        db = SessionLocal()
        
        # Verificar que el tema existe
        tema_nuevo = db.query(TemaPersonalizacion).filter_by(id=tema_id).first()
        if not tema_nuevo:
            return jsonify({
                'success': False,
                'error': 'Tema no encontrado'
            }), 404
        
        # Desactivar todos los temas
        db.query(TemaPersonalizacion).update({'activo': False})
        
        # Activar el tema seleccionado
        tema_nuevo.activo = True
        
        # Actualizar configuración global
        config_tema = db.query(ConfiguracionChatbot).filter_by(
            clave='tema_activo'
        ).first()
        
        if config_tema:
            config_tema.valor = tema_nuevo.nombre
        else:
            nueva_config = ConfiguracionChatbot(
                clave='tema_activo',
                valor=tema_nuevo.nombre,
                tipo='string',
                descripcion='Tema actualmente activo en el chatbot'
            )
            db.add(nueva_config)
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Tema "{tema_nuevo.nombre}" activado exitosamente',
            'tema_activado': {
                'id': tema_nuevo.id,
                'nombre': tema_nuevo.nombre,
                'descripcion': tema_nuevo.descripcion
            }
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al activar tema: {str(e)}'
        }), 500
    finally:
        db.close()

@chatbot_api_bp.route('/tema/activo', methods=['GET'])
def obtener_tema_activo():
    """
    Obtiene el tema actualmente activo con sus propiedades
    
    Returns:
        JSON: Tema activo con propiedades
    """
    try:
        db = SessionLocal()
        
        # Buscar el tema activo
        tema_activo = db.query(TemaPersonalizacion).filter_by(activo=True).first()
        
        if not tema_activo:
            return jsonify({
                'success': False,
                'error': 'No hay tema activo configurado'
            }), 404
        
        # Obtener todas las propiedades
        propiedades = db.query(PropiedadTema).filter_by(tema_id=tema_activo.id).all()
        
        # Convertir propiedades a diccionario
        props_dict = {}
        for prop in propiedades:
            props_dict[prop.propiedad] = prop.valor
        
        return jsonify({
            'success': True,
            'id': tema_activo.id,
            'nombre': tema_activo.nombre,
            'descripcion': tema_activo.descripcion,
            'propiedades': props_dict,
            'predefinido': tema_activo.predefinido,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@chatbot_api_bp.route('/temas/activo/css', methods=['GET'])
def obtener_css_tema_activo():
    """
    Genera el código CSS para el tema actualmente activo
    
    Returns:
        CSS: Código CSS listo para aplicar
    """
    try:
        db = SessionLocal()
        
        # Buscar el tema activo
        tema_activo = db.query(TemaPersonalizacion).filter_by(activo=True).first()
        
        if not tema_activo:
            return "/* No hay tema activo configurado */", 404
        
        # Obtener todas las propiedades
        propiedades = db.query(PropiedadTema).filter_by(tema_id=tema_activo.id).all()
        
        # Generar CSS
        css_content = f"""
/* =====================================
   TEMA ACTIVO: {tema_activo.nombre.upper()}
   Descripción: {tema_activo.descripcion}
   Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
   ===================================== */

:root {{
"""
        
        # Agregar variables CSS para cada propiedad
        for prop in propiedades:
            variable_name = prop.propiedad.replace('_', '-')
            # Si la propiedad ya tiene --, no agregar otro --
            if variable_name.startswith('--'):
                css_content += f"    {variable_name}: {prop.valor};\n"
            else:
                css_content += f"    --{variable_name}: {prop.valor};\n"
        
        css_content += "}\n\n"
        
        # Agregar estilos específicos aplicando las variables
        css_content += """
/* Estilos del Chatbot con Tema Personalizado */
.chatbot-container {
    background: var(--color-fondo, linear-gradient(135deg, #667eea 0%, #764ba2 100%));
    color: var(--color-texto, #ffffff);
    font-family: var(--fuente-principal, 'Playfair Display, serif');
    transition: var(--transicion, 0.3s ease);
}

.btn-chatbot, .btn-primary {
    background: var(--color-boton, #FFD700);
    border-radius: var(--boton-border-radius, 25px);
    padding: var(--boton-padding, 12px 25px);
    box-shadow: var(--boton-sombra, 0 4px 15px rgba(255, 215, 0, 0.3));
    font-family: var(--fuente-botones, 'Caveat, cursive');
    transition: var(--transicion, 0.3s ease);
    border: none;
    color: var(--color-texto, #ffffff);
}

.btn-chatbot:hover, .btn-primary:hover {
    background: var(--color-boton-hover, #FFA500);
}

.card, .message-card, .chatbot-card {
    background: var(--color-tarjeta, rgba(255, 255, 255, 0.1));
    backdrop-filter: blur(var(--backdrop-blur, 10px));
    border-radius: var(--boton-border-radius, 25px);
}

.chatbot-title, h1 {
    font-size: var(--tamaño-titulo, 3rem);
    font-family: var(--fuente-principal, 'Playfair Display, serif');
}

.chatbot-subtitle, h2 {
    font-size: var(--tamaño-subtitulo, 1.5rem);
    font-family: var(--fuente-secundaria, 'Merriweather, serif');
}
"""
        
        # Configurar headers para CSS
        response = make_response(css_content)
        response.headers['Content-Type'] = 'text/css'
        response.headers['Cache-Control'] = 'public, max-age=1800'
        
        return response
        
    except Exception as e:
        return f"/* Error al generar CSS del tema activo: {str(e)} */", 500
    finally:
        db.close()

@chatbot_api_bp.route('/temas', methods=['POST'])
def crear_tema_personalizado():
    """
    Crea un nuevo tema personalizado
    """
    try:
        data = request.get_json()
        
        if not data or 'nombre' not in data:
            return jsonify({
                'success': False,
                'error': 'Nombre del tema es requerido'
            }), 400
        
        db = SessionLocal()
        
        # Verificar que el nombre no exista
        tema_existente = db.query(TemaPersonalizacion).filter_by(
            nombre=data['nombre']
        ).first()
        
        if tema_existente:
            return jsonify({
                'success': False,
                'error': f'Ya existe un tema con el nombre "{data["nombre"]}"'
            }), 400
        
        # Crear el tema principal
        nuevo_tema = TemaPersonalizacion(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', 'Tema personalizado'),
            activo=False,
            predefinido=False
        )
        
        db.add(nuevo_tema)
        db.flush()
        
        # Procesar las propiedades si se proporcionaron
        total_propiedades = 0
        if 'propiedades' in data:
            for categoria, props in data['propiedades'].items():
                for propiedad, valor in props.items():
                    prop = PropiedadTema(
                        tema_id=nuevo_tema.id,
                        propiedad=propiedad,
                        valor=str(valor),
                        categoria=categoria
                    )
                    db.add(prop)
                    total_propiedades += 1
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Tema "{data["nombre"]}" creado exitosamente',
            'tema': {
                'id': nuevo_tema.id,
                'nombre': nuevo_tema.nombre,
                'descripcion': nuevo_tema.descripcion,
                'total_propiedades': total_propiedades
            }
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al crear tema: {str(e)}'
        }), 500
    finally:
        db.close()


# ========== ENDPOINTS DE FONDOS PERSONALIZADOS ==========

@chatbot_api_bp.route('/fondos', methods=['GET'])
def obtener_fondos():
    """Obtener todos los fondos personalizados"""
    db = SessionLocal()
    try:
        from .models import FondoPersonalizado
        fondos = db.query(FondoPersonalizado).all()
        return jsonify([{
            'id': fondo.id,
            'nombre': fondo.nombre,
            'archivo_url': fondo.archivo_url,
            'miniatura_url': fondo.miniatura_url,
            'dimensiones': fondo.dimensiones,
            'tamaño_archivo': fondo.tamaño_archivo,
            'tipo_archivo': fondo.tipo_archivo,
            'fecha_subida': fondo.fecha_subida.isoformat(),
            'contador_uso': fondo.contador_uso,
            'activo': fondo.activo
        } for fondo in fondos])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@chatbot_api_bp.route('/fondos/upload', methods=['POST'])
def subir_fondo():
    """Subir un nuevo fondo personalizado"""
    db = SessionLocal()
    try:
        import os
        from werkzeug.utils import secure_filename
        from PIL import Image
        import uuid
        from .models import FondoPersonalizado
        
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se proporcionó ningún archivo'}), 400
        
        archivo = request.files['archivo']
        nombre = request.form.get('nombre', '')
        
        if archivo.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        # Validar tipo de archivo
        EXTENSIONES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        extension = os.path.splitext(archivo.filename)[1].lower()
        
        if extension not in EXTENSIONES_PERMITIDAS:
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Generar nombre único
        nombre_archivo = f"{uuid.uuid4().hex}{extension}"
        nombre_miniatura = f"thumb_{nombre_archivo}"
        
        # Crear directorios si no existen
        upload_dir = os.path.join('modulos', 'chatbot', 'static', 'fondos')
        thumb_dir = os.path.join(upload_dir, 'thumbnails')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)
        
        # Guardar archivo original
        ruta_archivo = os.path.join(upload_dir, nombre_archivo)
        archivo.save(ruta_archivo)
        
        # Crear miniatura
        with Image.open(ruta_archivo) as img:
            # Obtener dimensiones originales
            ancho, alto = img.size
            dimensiones = f"{ancho}x{alto}"
            
            # Crear miniatura (200x150 max)
            img.thumbnail((200, 150), Image.Resampling.LANCZOS)
            ruta_miniatura = os.path.join(thumb_dir, nombre_miniatura)
            img.save(ruta_miniatura)
        
        # Obtener tamaño del archivo
        tamaño_archivo = os.path.getsize(ruta_archivo)
        
        # Crear registro en base de datos
        fondo = FondoPersonalizado(
            nombre=nombre or f"Fondo {len(db.query(FondoPersonalizado).all()) + 1}",
            archivo_url=f"/chatbot/static/fondos/{nombre_archivo}",
            miniatura_url=f"/chatbot/static/fondos/thumbnails/{nombre_miniatura}",
            dimensiones=dimensiones,
            tamaño_archivo=tamaño_archivo,
            tipo_archivo=extension[1:].upper(),
            activo=True
        )
        
        db.add(fondo)
        db.commit()
        
        return jsonify({
            'message': 'Fondo subido correctamente',
            'fondo': {
                'id': fondo.id,
                'nombre': fondo.nombre,
                'archivo_url': fondo.archivo_url,
                'miniatura_url': fondo.miniatura_url,
                'dimensiones': fondo.dimensiones,
                'tamaño_archivo': fondo.tamaño_archivo,
                'tipo_archivo': fondo.tipo_archivo
            }
        }), 201
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@chatbot_api_bp.route('/fondos/<int:fondo_id>', methods=['DELETE'])
def eliminar_fondo(fondo_id):
    """Eliminar un fondo personalizado"""
    db = SessionLocal()
    try:
        import os
        from .models import FondoPersonalizado
        
        fondo = db.query(FondoPersonalizado).get(fondo_id)
        if not fondo:
            return jsonify({'error': 'Fondo no encontrado'}), 404
        
        # Eliminar archivos del sistema
        try:
            ruta_archivo = os.path.join('modulos', 'chatbot', 'static', 'fondos', 
                                       os.path.basename(fondo.archivo_url))
            ruta_miniatura = os.path.join('modulos', 'chatbot', 'static', 'fondos', 'thumbnails',
                                        os.path.basename(fondo.miniatura_url))
            
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            if os.path.exists(ruta_miniatura):
                os.remove(ruta_miniatura)
        except Exception as e:
            print(f"Error eliminando archivos: {e}")
        
        # Eliminar registro de base de datos
        db.delete(fondo)
        db.commit()
        
        return jsonify({'message': 'Fondo eliminado correctamente'})
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@chatbot_api_bp.route('/temas/<int:tema_id>/fondo', methods=['PUT'])
def actualizar_fondo_tema(tema_id):
    """Actualizar el fondo de un tema específico"""
    db = SessionLocal()
    try:
        from .models import TemaPersonalizacion, PropiedadTema, FondoPersonalizado
        
        tema = db.query(TemaPersonalizacion).get(tema_id)
        if not tema:
            return jsonify({'error': 'Tema no encontrado'}), 404
        
        data = request.get_json()
        fondo_id = data.get('fondo_id')
        
        if fondo_id:
            fondo = db.query(FondoPersonalizado).get(fondo_id)
            if not fondo:
                return jsonify({'error': 'Fondo no encontrado'}), 404
            
            # Incrementar contador de uso del fondo
            fondo.contador_uso += 1
            
            # Actualizar o crear propiedades de fondo
            propiedades_fondo = {
                'fondo_tipo': 'imagen',
                'fondo_imagen_url': fondo.archivo_url,
                'fondo_overlay': data.get('overlay', 'rgba(0, 0, 0, 0.3)'),
                'fondo_attachment': data.get('attachment', 'fixed'),
                'fondo_size': data.get('size', 'cover')
            }
            
            for clave, valor in propiedades_fondo.items():
                propiedad = db.query(PropiedadTema).filter_by(
                    tema_id=tema.id,
                    propiedad=clave
                ).first()
                
                if propiedad:
                    propiedad.valor = valor
                else:
                    nueva_propiedad = PropiedadTema(
                        tema_id=tema.id,
                        categoria='fondos',
                        propiedad=clave,
                        valor=valor
                    )
                    db.add(nueva_propiedad)
        
        else:
            # Restaurar fondo por defecto (gradient)
            propiedad_tipo = db.query(PropiedadTema).filter_by(
                tema_id=tema.id,
                propiedad='fondo_tipo'
            ).first()
            if propiedad_tipo:
                propiedad_tipo.valor = 'gradient'
            
            propiedad_url = db.query(PropiedadTema).filter_by(
                tema_id=tema.id,
                propiedad='fondo_imagen_url'
            ).first()
            if propiedad_url:
                propiedad_url.valor = ''
        
        db.commit()
        
        return jsonify({
            'message': 'Fondo del tema actualizado correctamente',
            'tema_id': tema.id
        })
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()