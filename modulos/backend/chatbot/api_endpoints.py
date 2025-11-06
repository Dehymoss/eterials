"""API Endpoints para el Backend del Chatbot"""

from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
import json
import os

from .models import (
    Sesion, Calificacion, Comentario, NotificacionMesero, 
    Analytics, ConfiguracionChatbot, FondoPersonalizado
)

chatbot_api_bp = Blueprint('chatbot_api', __name__, url_prefix='/api/chatbot')

def get_db_session():
    """Obtener sesión de base de datos"""
    engine = create_engine('sqlite:///modulos/backend/menu/menu.db')
    Session = sessionmaker(bind=engine)
    return Session()

def _guardar_configuracion_fondo(db, tipo, valor, descripcion_valor):
    """Guarda la configuración del fondo en la base de datos"""
    config_tipo = db.query(ConfiguracionChatbot).filter_by(clave='fondo_tipo').first()
    if not config_tipo:
        config_tipo = ConfiguracionChatbot(
            clave='fondo_tipo', 
            valor=tipo, 
            descripcion='Tipo de fondo activo'
        )
        db.add(config_tipo)
    else:
        config_tipo.valor = tipo
        config_tipo.fecha_modificacion = datetime.utcnow()
    
    config_valor = db.query(ConfiguracionChatbot).filter_by(clave='fondo_valor').first()
    if not config_valor:
        config_valor = ConfiguracionChatbot(
            clave='fondo_valor', 
            valor=valor, 
            descripcion=descripcion_valor
        )
        db.add(config_valor)
    else:
        config_valor.valor = valor
        config_valor.fecha_modificacion = datetime.utcnow()

def _validar_datos_calificacion(data):
    """Validar datos de entrada para calificación"""
    sesion_id = data.get('sesion_id')
    estrellas = data.get('estrellas')
    categoria = data.get('categoria', 'general')
    
    if not sesion_id or not estrellas or estrellas < 1 or estrellas > 5:
        return None, {'success': False, 'error': 'Datos inválidos. Se requiere sesion_id y estrellas (1-5)'}
    
    return {'sesion_id': sesion_id, 'estrellas': estrellas, 'categoria': categoria}, None

def _verificar_sesion_calificacion(db, sesion_id):
    """Verificar que la sesión existe y está activa para calificación"""
    sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
    if not sesion:
        return None, {'success': False, 'error': 'Sesión no encontrada'}
    
    if not sesion.activa:
        return None, {'success': False, 'error': 'No se puede calificar una sesión inactiva'}
    
    return sesion, None

def _actualizar_calificacion_existente(db, calificacion_existente, estrellas, categoria, sesion_id):
    """Actualizar una calificación que ya existe"""
    calificacion_existente.estrellas = estrellas
    calificacion_existente.fecha_calificacion = datetime.utcnow()
    db.commit()
    
    return {
        'success': True,
        'accion': 'actualizada',
        'calificacion_id': calificacion_existente.id,
        'sesion_id': sesion_id,
        'estrellas': estrellas,
        'categoria': categoria,
        'mensaje': 'Calificación actualizada correctamente'
    }

def _crear_nueva_calificacion(db, sesion_id, estrellas, categoria, sesion):
    """Crear nueva calificación y registro de analytics"""
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
    
    return {
        'success': True,
        'mensaje': f'Calificación de {estrellas} estrellas guardada',
        'timestamp': datetime.utcnow().isoformat()
    }
# ENDPOINTS DE SESIONES

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
    """Valida si una sesión sigue siendo válida"""
    try:
        session = get_db_session()
        sesion = session.query(Sesion).filter_by(id=sesion_id).first()
        
        if not sesion:
            return jsonify({'success': False, 'valida': False, 'error': 'Sesión no encontrada'}), 404
        
        if not sesion.activa:
            return jsonify({'success': True, 'valida': False, 'razon': 'Sesión inactiva'})
        
        return jsonify({'success': True, 'valida': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

@chatbot_api_bp.route('/sesiones/activas', methods=['GET'])
def obtener_sesiones_activas():
    """
    Obtiene todas las sesiones activas para el dashboard administrativo
    
    GET /api/chatbot/sesiones/activas
    """
    try:
        db = get_db_session()
        
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

# ENDPOINTS DE CALIFICACIONES

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
        
        # Validar datos de entrada
        datos_validos, error = _validar_datos_calificacion(data)
        if error:
            return jsonify(error), 400
        
        sesion_id = datos_validos['sesion_id']
        estrellas = datos_validos['estrellas']
        categoria = datos_validos['categoria']
        
        db = get_db_session()
        
        # Verificar sesión
        sesion, error = _verificar_sesion_calificacion(db, sesion_id)
        if error:
            db.close()
            return jsonify(error), 404 if 'no encontrada' in error['error'] else 400
        
        # Verificar si ya existe una calificación
        from .models import Calificacion
        calificacion_existente = db.query(Calificacion).filter(
            Calificacion.sesion_id == sesion_id,
            Calificacion.categoria == categoria
        ).first()
        
        if calificacion_existente:
            # Actualizar calificación existente
            resultado = _actualizar_calificacion_existente(
                db, calificacion_existente, estrellas, categoria, sesion_id
            )
            db.close()
            return jsonify(resultado)
        
        # Crear nueva calificación
        resultado = _crear_nueva_calificacion(db, sesion_id, estrellas, categoria, sesion)
        db.close()
        return jsonify(resultado)
        
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
        db = get_db_session()
        
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

# ENDPOINTS DE COMENTARIOS

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

# ENDPOINTS DE NOTIFICACIONES

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

# ENDPOINTS DE ANALYTICS

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

@chatbot_api_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas generales del chatbot para el dashboard"""
    try:
        db = get_db_session()
        
        total_sesiones = db.query(Sesion).count()
        sesiones_activas = db.query(Sesion).filter(Sesion.activa == True).count()
        
        calificaciones = db.query(Calificacion).all()
        promedio_calificacion = 0
        if calificaciones:
            promedio_calificacion = sum(c.estrellas for c in calificaciones) / len(calificaciones)
        
        actividad_reciente = db.query(Analytics).count()
        
        db.close()
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'total_sesiones': total_sesiones,
                'sesiones_activas': sesiones_activas,
                'promedio_calificacion': round(promedio_calificacion, 2),
                'actividad_24h': actividad_reciente,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': True,
            'estadisticas': {
                'total_sesiones': 0,
                'sesiones_activas': 0,
                'promedio_calificacion': 0,
                'actividad_24h': 0,
                'timestamp': datetime.utcnow().isoformat()
            }
        })

# ENDPOINTS DE CONFIGURACIÓN

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

def _validar_archivo_subido(request):
    """Validar que el archivo subido sea válido"""
    if 'archivo' not in request.files:
        return None, {'error': 'No se proporcionó ningún archivo'}
    
    archivo = request.files['archivo']
    if archivo.filename == '':
        return None, {'error': 'No se seleccionó ningún archivo'}
    
    EXTENSIONES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    extension = os.path.splitext(archivo.filename)[1].lower()
    
    if extension not in EXTENSIONES_PERMITIDAS:
        return None, {'error': f'Tipo de archivo no permitido. Extensiones válidas: {", ".join(EXTENSIONES_PERMITIDAS)}'}
    
    return archivo, None

def _guardar_archivo_fondo(archivo):
    """Guardar archivo de fondo en el sistema de archivos"""
    import uuid
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    fondos_path = os.path.join(project_root, 'modulos', 'chatbot', 'static', 'fondos')
    os.makedirs(fondos_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = os.path.splitext(archivo.filename)[1].lower()
    nombre_unico = f"fondo_{timestamp}_{uuid.uuid4().hex[:8]}{extension}"
    
    archivo_path = os.path.join(fondos_path, nombre_unico)
    archivo.save(archivo_path)
    
    return {
        'nombre_archivo': nombre_unico,
        'ruta_completa': archivo_path,
        'tamaño_bytes': os.path.getsize(archivo_path),
        'extension': extension
    }

# ================================================================================
# ENDPOINTS DE FONDOS
# ================================================================================

@chatbot_api_bp.route('/fondos/upload', methods=['POST'])
def subir_fondo():
    """
    Subir un nuevo fondo personalizado
    
    POST /api/chatbot/fondos/upload
    FormData: {
        "archivo": file,
        "nombre": "string (opcional)"
    }
    """
    try:
        print("🔄 Procesando upload de fondo...")
        
        # Validar archivo subido
        archivo, error = _validar_archivo_subido(request)
        if error:
            print(f"❌ Error validación: {error}")
            return jsonify(error), 400
        
        # Obtener nombre del formulario
        nombre = request.form.get('nombre', '')
        if not nombre:
            nombre = os.path.splitext(archivo.filename)[0]
        
        print(f"📁 Archivo: {archivo.filename}")
        print(f"🏷️ Nombre: {nombre}")
        
        # Guardar archivo físicamente
        archivo_info = _guardar_archivo_fondo(archivo)
        print(f"💾 Guardado: {archivo_info['nombre_archivo']}")
        
        # Registrar en base de datos
        db = get_db_session()
        
        nuevo_fondo = FondoPersonalizado(
            nombre=nombre,
            archivo_url=f"/chatbot/static/fondos/{archivo_info['nombre_archivo']}",
            archivo_original=archivo.filename,
            tamaño_archivo=archivo_info['tamaño_bytes'],
            tipo_archivo=archivo_info['extension'],
            activo=True
        )
        
        db.add(nuevo_fondo)
        db.commit()
        
        fondo_id = nuevo_fondo.id
        print(f"✅ Fondo creado con ID: {fondo_id}")
        
        return jsonify({
            'success': True,
            'message': 'Fondo subido correctamente',
            'fondo': {
                'id': fondo_id,
                'nombre': nombre,
                'archivo_url': nuevo_fondo.archivo_url,
                'archivo_original': archivo.filename,
                'tamaño_archivo': archivo_info['tamaño_bytes'],
                'tipo_archivo': archivo_info['extension']
            }
        }), 201
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        print(f"❌ Error en upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al subir fondo: {str(e)}'
        }), 500
    finally:
        if 'db' in locals():
            db.close()

@chatbot_api_bp.route('/fondos/existentes', methods=['GET'])
def obtener_fondos_existentes():
    """
    SISTEMA SIMPLIFICADO: Fondos desde archivos estáticos (SVG, PNG, JPG, JPEG)
    
    GET /api/chatbot/fondos/existentes
    """
    try:
        import os
        import glob
        
        fondos_encontrados = []
        
        # Obtener ruta al directorio de fondos (UBICACIÓN ÚNICA)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        fondos_path = os.path.join(project_root, 'modulos', 'chatbot', 'static', 'fondos')
        
        # ✅ SOPORTE COMPLETO PARA TODOS LOS TIPOS DE IMAGEN
        extensiones_soportadas = ['*.svg', '*.png', '*.jpg', '*.jpeg', '*.webp', '*.gif', '*.bmp']
        
        # Buscar todos los archivos de imagen en el directorio
        archivos_imagen = []
        for extension in extensiones_soportadas:
            patron = os.path.join(fondos_path, extension)
            archivos_encontrados = glob.glob(patron)
            # También buscar versiones en mayúsculas
            patron_upper = os.path.join(fondos_path, extension.upper())
            archivos_encontrados.extend(glob.glob(patron_upper))
            archivos_imagen.extend(archivos_encontrados)
        
        # Eliminar duplicados y ordenar archivos para consistencia
        archivos_imagen = list(set(archivos_imagen))
        archivos_imagen.sort()
        
        # ✅ NUEVO: Solo retornar lista vacía si no hay fondos subidos por usuario
        if not archivos_imagen:
            print(f"📁 Carpeta fondos vacía: {fondos_path}")
            return jsonify([])
        
        # Procesar cada archivo encontrado (solo fondos realmente subidos por usuario)
        for i, archivo_path in enumerate(archivos_imagen, 1):
            if os.path.isfile(archivo_path):
                nombre_archivo = os.path.basename(archivo_path)
                nombre_base = os.path.splitext(nombre_archivo)[0]
                extension = os.path.splitext(nombre_archivo)[1].upper().replace('.', '')
                
                # Generar nombres legibles basados en el archivo real
                if nombre_archivo.startswith('fondo_'):
                    # Para archivos generados por upload: extraer fecha del nombre
                    timestamp_part = nombre_archivo[6:21]  # "20251105_211734"
                    nombre_legible = f"Fondo subido {timestamp_part}"
                elif nombre_archivo.startswith('test_'):
                    nombre_legible = nombre_base.replace('_', ' ').title()
                else:
                    # Para otros archivos, usar el nombre real del archivo
                    nombre_legible = nombre_base.replace('_', ' ').title()
                
                # Generar descripción automática
                if extension == 'SVG':
                    descripcion = f"Fondo vectorial {nombre_legible}"
                else:
                    descripcion = f"Imagen de fondo {extension}"
                
                # Información del archivo
                tamano_bytes = os.path.getsize(archivo_path)
                tamano_mb = round(tamano_bytes / (1024*1024), 2)
                
                fondo_info = {
                    'id': i,
                    'nombre': nombre_legible,
                    'nombre_archivo': nombre_archivo,
                    'descripcion': descripcion,
                    'tipo': extension,
                    'tamano_bytes': tamano_bytes,
                    'tamano_mb': tamano_mb,
                    'dimensiones': 'auto',
                    'fecha_subida': '',
                    'uso_contador': 0,
                    'activo': True,
                    'publico': True,
                    # URL directa al archivo
                    'url_preview': f"/chatbot/static/fondos/{nombre_archivo}",
                    'tiene_imagen_base64': False,  # Usar archivos directos
                    'es_desde_bd': False  # Archivos estáticos
                }
                fondos_encontrados.append(fondo_info)
        
        # Estadísticas
        total_fondos = len(fondos_encontrados)
        total_espacio_mb = sum(f['tamano_mb'] for f in fondos_encontrados)
        
        return jsonify({
            'success': True,
            'fondos': fondos_encontrados,
            'estadisticas': {
                'total_fondos': total_fondos,
                'total_espacio_mb': round(total_espacio_mb, 2),
                'carpetas_escaneadas': ['archivos_estaticos'],
                'fuente': 'archivos_svg_estaticos'
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo fondos: {str(e)}',
            'fondos': [],
            'estadisticas': {
                'total_fondos': 0,
                'total_espacio_mb': 0,
                'carpetas_escaneadas': [],
                'fuente': 'error'
            }
        }), 500


@chatbot_api_bp.route('/configuracion/menus', methods=['GET'])
def obtener_configuracion_menus():
    """Obtiene la configuración actual de menús"""
    session = get_db_session()
    try:
        def obtener_config(clave, default):
            config = session.query(ConfiguracionChatbot).filter_by(clave=clave).first()
            if config:
                if config.tipo == 'boolean':
                    return config.valor.lower() == 'true'
                return config.valor
            return default
        
        configuracion = {
            'menu_principal_activo': obtener_config('menu_principal_activo', True),
            'menu_principal_url': obtener_config('menu_principal_url', '/menu/general'),
            'menu_alternativo_activo': obtener_config('menu_alternativo_activo', False),
            'menu_alternativo_url': obtener_config('menu_alternativo_url', '')
        }
            
        return jsonify({'success': True, 'configuracion': configuracion})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error obteniendo configuración: {str(e)}'}), 500
    finally:
        session.close()

@chatbot_api_bp.route('/configuracion/menus', methods=['POST'])
def guardar_configuracion_menus():
    """Guarda la configuración de menús"""
    session = get_db_session()
    try:
        data = request.get_json()
        
        def guardar_config(clave, valor, tipo='string'):
            config = session.query(ConfiguracionChatbot).filter_by(clave=clave).first()
            if not config:
                config = ConfiguracionChatbot(
                    clave=clave,
                    valor=str(valor),
                    tipo=tipo,
                    descripcion=f'Configuración de menú: {clave}'
                )
                session.add(config)
            else:
                config.valor = str(valor)
                config.fecha_modificacion = datetime.utcnow()
        
        if 'menu_principal_activo' in data:
            guardar_config('menu_principal_activo', data['menu_principal_activo'], 'boolean')
        if 'menu_principal_url' in data:
            guardar_config('menu_principal_url', data['menu_principal_url'], 'string')
        if 'menu_alternativo_activo' in data:
            guardar_config('menu_alternativo_activo', data['menu_alternativo_activo'], 'boolean')
        if 'menu_alternativo_url' in data:
            guardar_config('menu_alternativo_url', data['menu_alternativo_url'], 'string')
        
        session.commit()
        
        return jsonify({'success': True, 'message': 'Configuración de menús guardada exitosamente'})
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': f'Error guardando configuración: {str(e)}'}), 500
    finally:
        session.close()

@chatbot_api_bp.route('/fondos/aplicar', methods=['POST'])
def aplicar_fondo():
    """
    Aplica un fondo personalizado al chatbot
    
    POST /api/chatbot/fondos/aplicar
    Body: {
        "fondo_tipo": "imagen",
        "fondo_valor": "1",
        "fondo_url": "/chatbot/static/fondos/archivo.jpg"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        fondo_tipo = data.get('fondo_tipo', 'imagen')
        fondo_valor = str(data.get('fondo_valor', ''))
        fondo_url = data.get('fondo_url', '')
        
        if not fondo_valor:
            return jsonify({
                'success': False,
                'error': 'Se requiere fondo_valor'
            }), 400
        
        print(f"🎨 Aplicando fondo: tipo={fondo_tipo}, valor={fondo_valor}")
        
        session = get_db_session()
        
        # Guardar configuración en base de datos
        _guardar_configuracion_fondo(session, fondo_tipo, fondo_valor, f'Fondo aplicado: {fondo_url}')
        
        session.commit()
        session.close()
        
        print(f"✅ Fondo aplicado exitosamente: {fondo_valor}")
        
        return jsonify({
            'success': True,
            'message': f'Fondo aplicado correctamente',
            'fondo_aplicado': {
                'tipo': fondo_tipo,
                'valor': fondo_valor,
                'url': fondo_url
            }
        })
        
    except Exception as e:
        print(f"❌ Error aplicando fondo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error aplicando fondo: {str(e)}'
        }), 500

@chatbot_api_bp.route('/fondos/restablecer', methods=['POST'])
def restablecer_fondo():
    """
    Restablece el fondo del chatbot al negro por defecto
    
    POST /api/chatbot/fondos/restablecer
    Body: {
        "accion": "restablecer_negro"
    }
    """
    try:
        print("🖤 Iniciando restablecimiento de fondo al negro por defecto...")
        
        data = request.get_json()
        if not data or data.get('accion') != 'restablecer_negro':
            return jsonify({
                'success': False,
                'error': 'Acción no válida. Se esperaba "restablecer_negro"'
            }), 400
        
        session = get_db_session()
        
        # Eliminar configuraciones de fondo existentes
        config_tipo = session.query(ConfiguracionChatbot).filter_by(clave='fondo_tipo').first()
        config_valor = session.query(ConfiguracionChatbot).filter_by(clave='fondo_valor').first()
        
        if config_tipo:
            session.delete(config_tipo)
            print("🗑️ Configuración fondo_tipo eliminada")
            
        if config_valor:
            session.delete(config_valor)
            print("🗑️ Configuración fondo_valor eliminada")
        
        # Guardar cambios
        session.commit()
        session.close()
        
        print("✅ Fondo restablecido a negro por defecto exitosamente")
        
        return jsonify({
            'success': True,
            'message': 'Fondo restablecido a negro por defecto',
            'accion_realizada': 'configuracion_fondo_eliminada',
            'resultado': 'fondo_negro_por_defecto'
        })
        
    except Exception as e:
        print(f"❌ Error restableciendo fondo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error restableciendo fondo: {str(e)}'
        }), 500
