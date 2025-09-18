#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard y Panel de Administración para el Chatbot
===================================================
Endpoints para el panel de administración del chatbot.
"""

from flask import Blueprint, render_template, jsonify, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, desc
from datetime import datetime, timedelta
import json
import os

# Importar modelos
from .models import Sesion, Calificacion, Comentario, NotificacionMesero, Analytics
from .services import verificar_estado_backend

# Blueprint para el dashboard administrativo
chatbot_admin_bp = Blueprint('chatbot_admin', __name__, 
                           template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                           static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                           url_prefix='/admin/chatbot')

def get_db_session():
    """Obtener sesión de base de datos"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'menu', 
        'menu.db'
    )
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()

# ==================== RUTAS DEL DASHBOARD ====================

@chatbot_admin_bp.route('/')
def dashboard_principal():
    """Dashboard principal del chatbot"""
    return render_template('chatbot_admin_dashboard.html')

@chatbot_admin_bp.route('/notificaciones')
def panel_notificaciones():
    """Panel para gestionar notificaciones del personal"""
    return render_template('chatbot_notificaciones.html')

@chatbot_admin_bp.route('/analytics')
def panel_analytics():
    """Panel de analytics y reportes"""
    return render_template('chatbot_analytics.html')

@chatbot_admin_bp.route('/configuracion')
def panel_configuracion():
    """Panel de configuración del chatbot"""
    return render_template('chatbot_configuracion.html')

# ==================== APIs DEL DASHBOARD ====================

@chatbot_admin_bp.route('/api/dashboard/resumen')
def api_resumen_dashboard():
    """
    API para obtener resumen del dashboard
    """
    try:
        # Verificar estado del backend
        estado_backend = verificar_estado_backend()
        if not estado_backend['success']:
            return jsonify({
                'success': False,
                'error': 'Backend del chatbot no configurado',
                'backend_estado': estado_backend
            }), 500
        
        db = get_db_session()
        
        # Fecha de inicio (últimos 7 días)
        fecha_inicio = datetime.utcnow() - timedelta(days=7)
        
        # Métricas principales
        sesiones_activas = db.query(Sesion).filter(
            Sesion.activa == True
        ).count()
        
        sesiones_hoy = db.query(Sesion).filter(
            Sesion.fecha_inicio >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # Calificaciones
        calificaciones_query = db.query(func.avg(Calificacion.estrellas)).filter(
            Calificacion.fecha_calificacion >= fecha_inicio
        )
        calificacion_promedio = calificaciones_query.scalar() or 0
        
        total_calificaciones = db.query(Calificacion).filter(
            Calificacion.fecha_calificacion >= fecha_inicio
        ).count()
        
        # Comentarios
        comentarios_nuevos = db.query(Comentario).filter(
            Comentario.fecha_comentario >= fecha_inicio,
            Comentario.moderado == False
        ).count()
        
        # Notificaciones pendientes
        notificaciones_pendientes = db.query(NotificacionMesero).filter(
            NotificacionMesero.atendida == False
        ).count()
        
        notificaciones_urgentes = db.query(NotificacionMesero).filter(
            NotificacionMesero.atendida == False,
            NotificacionMesero.prioridad.in_(['alta', 'urgente'])
        ).count()
        
        # Actividad por mesa (top 5)
        actividad_mesas = db.query(
            Sesion.mesa,
            func.count(Sesion.id).label('total_sesiones')
        ).filter(
            Sesion.fecha_inicio >= fecha_inicio
        ).group_by(
            Sesion.mesa
        ).order_by(
            desc('total_sesiones')
        ).limit(5).all()
        
        # Distribución de calificaciones
        distribucion_calificaciones = db.query(
            Calificacion.estrellas,
            func.count(Calificacion.id).label('cantidad')
        ).filter(
            Calificacion.fecha_calificacion >= fecha_inicio
        ).group_by(
            Calificacion.estrellas
        ).all()
        
        db.close()
        
        # Preparar respuesta
        resumen = {
            'sesiones': {
                'activas': sesiones_activas,
                'hoy': sesiones_hoy
            },
            'calificaciones': {
                'promedio': round(calificacion_promedio, 2),
                'total': total_calificaciones,
                'distribucion': [
                    {'estrellas': estrellas, 'cantidad': cantidad}
                    for estrellas, cantidad in distribucion_calificaciones
                ]
            },
            'comentarios': {
                'nuevos_sin_moderar': comentarios_nuevos
            },
            'notificaciones': {
                'pendientes': notificaciones_pendientes,
                'urgentes': notificaciones_urgentes
            },
            'mesas_activas': [
                {'mesa': mesa, 'sesiones': total}
                for mesa, total in actividad_mesas
            ]
        }
        
        return jsonify({
            'success': True,
            'resumen': resumen,
            'periodo': '7 días',
            'backend_estado': estado_backend,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@chatbot_admin_bp.route('/api/notificaciones/tiempo-real')
def api_notificaciones_tiempo_real():
    """
    API para obtener notificaciones en tiempo real
    """
    try:
        db = get_db_session()
        
        # Obtener notificaciones pendientes con datos de sesión
        notificaciones = db.query(NotificacionMesero, Sesion).join(
            Sesion, NotificacionMesero.sesion_id == Sesion.id
        ).filter(
            NotificacionMesero.atendida == False
        ).order_by(
            desc(NotificacionMesero.prioridad),
            NotificacionMesero.fecha_notificacion
        ).all()
        
        resultado = []
        for notificacion, sesion in notificaciones:
            tiempo_espera = datetime.utcnow() - notificacion.fecha_notificacion
            
            resultado.append({
                'id': notificacion.id,
                'mesa': sesion.mesa,
                'cliente': sesion.nombre_cliente or 'Anónimo',
                'tipo': notificacion.tipo_notificacion,
                'mensaje': notificacion.mensaje,
                'prioridad': notificacion.prioridad,
                'fecha': notificacion.fecha_notificacion.isoformat(),
                'tiempo_espera_minutos': int(tiempo_espera.total_seconds() / 60),
                'es_urgente': notificacion.prioridad in ['alta', 'urgente']
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

@chatbot_admin_bp.route('/api/notificacion/<int:notificacion_id>/atender', methods=['POST'])
def api_atender_notificacion(notificacion_id):
    """
    Marcar una notificación como atendida
    """
    try:
        data = request.get_json() or {}
        atendida_por = data.get('atendida_por', 'Staff')
        
        db = get_db_session()
        
        notificacion = db.query(NotificacionMesero).filter(
            NotificacionMesero.id == notificacion_id
        ).first()
        
        if not notificacion:
            return jsonify({
                'success': False,
                'error': 'Notificación no encontrada'
            }), 404
        
        notificacion.atendida = True
        notificacion.atendida_por = atendida_por
        notificacion.fecha_atencion = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'mensaje': f'Notificación {notificacion_id} marcada como atendida',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_admin_bp.route('/api/comentarios/sin-moderar')
def api_comentarios_sin_moderar():
    """
    Obtener comentarios que necesitan moderación
    """
    try:
        db = get_db_session()
        
        comentarios = db.query(Comentario, Sesion).join(
            Sesion, Comentario.sesion_id == Sesion.id
        ).filter(
            Comentario.moderado == False
        ).order_by(
            desc(Comentario.fecha_comentario)
        ).limit(50).all()
        
        resultado = []
        for comentario, sesion in comentarios:
            resultado.append({
                'id': comentario.id,
                'mesa': sesion.mesa,
                'cliente': sesion.nombre_cliente or 'Anónimo',
                'texto': comentario.texto_comentario,
                'tipo': comentario.tipo,
                'fecha': comentario.fecha_comentario.isoformat()
            })
        
        db.close()
        
        return jsonify({
            'success': True,
            'comentarios': resultado,
            'total': len(resultado),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_admin_bp.route('/api/analytics/graficos')
def api_analytics_graficos():
    """
    Datos para gráficos de analytics
    """
    try:
        dias = request.args.get('dias', 30, type=int)
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        
        db = get_db_session()
        
        # Actividad por día
        actividad_diaria = db.query(
            func.date(Sesion.fecha_inicio).label('fecha'),
            func.count(Sesion.id).label('sesiones')
        ).filter(
            Sesion.fecha_inicio >= fecha_inicio
        ).group_by(
            func.date(Sesion.fecha_inicio)
        ).order_by('fecha').all()
        
        # Calificaciones por día
        calificaciones_diarias = db.query(
            func.date(Calificacion.fecha_calificacion).label('fecha'),
            func.avg(Calificacion.estrellas).label('promedio')
        ).filter(
            Calificacion.fecha_calificacion >= fecha_inicio
        ).group_by(
            func.date(Calificacion.fecha_calificacion)
        ).order_by('fecha').all()
        
        # Tipos de notificaciones
        tipos_notificaciones = db.query(
            NotificacionMesero.tipo_notificacion,
            func.count(NotificacionMesero.id).label('cantidad')
        ).filter(
            NotificacionMesero.fecha_notificacion >= fecha_inicio
        ).group_by(
            NotificacionMesero.tipo_notificacion
        ).all()
        
        db.close()
        
        return jsonify({
            'success': True,
            'graficos': {
                'actividad_diaria': [
                    {'fecha': str(fecha), 'sesiones': sesiones}
                    for fecha, sesiones in actividad_diaria
                ],
                'calificaciones_diarias': [
                    {'fecha': str(fecha), 'promedio': round(float(promedio), 2)}
                    for fecha, promedio in calificaciones_diarias
                ],
                'tipos_notificaciones': [
                    {'tipo': tipo, 'cantidad': cantidad}
                    for tipo, cantidad in tipos_notificaciones
                ]
            },
            'periodo_dias': dias,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== GESTIÓN DE TEMAS ====================

@chatbot_admin_bp.route('/temas')
def gestion_temas():
    """
    Página de gestión de temas del chatbot
    """
    try:
        from .models import TemaPersonalizacion, PropiedadTema
        
        db = get_db_session()
        
        # Obtener todos los temas
        temas = db.query(TemaPersonalizacion).all()
        
        # Obtener tema activo
        tema_activo = db.query(TemaPersonalizacion).filter_by(activo=True).first()
        
        # Estadísticas de temas
        stats_temas = {
            'total_temas': len(temas),
            'temas_predefinidos': len([t for t in temas if t.predefinido]),
            'temas_personalizados': len([t for t in temas if not t.predefinido]),
            'tema_activo': tema_activo.nombre if tema_activo else 'Ninguno'
        }
        
        # Preparar datos de temas para el template
        temas_data = []
        for tema in temas:
            propiedades = db.query(PropiedadTema).filter_by(tema_id=tema.id).all()
            temas_data.append({
                'id': tema.id,
                'nombre': tema.nombre,
                'descripcion': tema.descripcion,
                'activo': tema.activo,
                'predefinido': tema.predefinido,
                'total_propiedades': len(propiedades),
                'fecha_creacion': tema.fecha_creacion.strftime('%d/%m/%Y')
            })
        
        db.close()
        
        return render_template('admin_temas_chatbot.html', 
                             temas=temas_data, 
                             stats=stats_temas)
        
    except Exception as e:
        return f"Error al cargar gestión de temas: {str(e)}", 500

@chatbot_admin_bp.route('/temas/preview')
def preview_chatbot():
    """
    Vista previa del chatbot con el tema activo aplicado
    """
    try:
        from .models import TemaPersonalizacion, PropiedadTema
        
        db = get_db_session()
        
        # Obtener tema activo
        tema_activo = db.query(TemaPersonalizacion).filter_by(activo=True).first()
        
        if not tema_activo:
            return "No hay tema activo configurado", 404
        
        # Obtener propiedades del tema
        propiedades = db.query(PropiedadTema).filter_by(tema_id=tema_activo.id).all()
        
        # Crear diccionario de propiedades CSS
        css_vars = {}
        for prop in propiedades:
            variable_name = prop.propiedad.replace('_', '-')
            css_vars[variable_name] = prop.valor
        
        db.close()
        
        return render_template('preview_chatbot.html', 
                             tema_nombre=tema_activo.nombre,
                             css_vars=css_vars)
        
    except Exception as e:
        return f"Error al cargar preview: {str(e)}", 500


# ============= GESTIÓN DE FONDOS PERSONALIZADOS =============

@chatbot_admin_bp.route('/fondos')
def gestionar_fondos():
    """Página de gestión de fondos personalizados"""
    try:
        from .models import FondoPersonalizado
        
        db = get_db_session()
        fondos = db.query(FondoPersonalizado).order_by(FondoPersonalizado.fecha_subida.desc()).all()
        
        # Calcular estadísticas
        total_fondos = len(fondos)
        espacio_usado = sum(f.tamaño_archivo for f in fondos)
        mas_usado = max(fondos, key=lambda f: f.contador_uso) if fondos else None
        
        estadisticas = {
            'total_fondos': total_fondos,
            'espacio_usado': espacio_usado,
            'espacio_usado_mb': round(espacio_usado / (1024 * 1024), 2),
            'mas_usado': mas_usado
        }
        
        db.close()
        
        return render_template('admin/fondos.html', 
                             fondos=fondos, 
                             estadisticas=estadisticas)
    except Exception as e:
        return f"Error al cargar gestión de fondos: {str(e)}", 500


@chatbot_admin_bp.route('/temas/<int:tema_id>/personalizar')
def personalizar_tema(tema_id):
    """Página de personalización de tema específico"""
    try:
        from .models import TemaPersonalizacion, PropiedadTema, FondoPersonalizado
        
        db = get_db_session()
        
        tema = db.query(TemaPersonalizacion).get(tema_id)
        if not tema:
            return "Tema no encontrado", 404
        
        propiedades = db.query(PropiedadTema).filter_by(tema_id=tema.id).all()
        fondos_disponibles = db.query(FondoPersonalizado).filter_by(activo=True).all()
        
        # Organizar propiedades por categoría
        props_organizadas = {}
        for prop in propiedades:
            if prop.categoria not in props_organizadas:
                props_organizadas[prop.categoria] = {}
            props_organizadas[prop.categoria][prop.propiedad] = prop.valor
        
        db.close()
        
        return render_template('admin/personalizar_tema.html', 
                             tema=tema, 
                             propiedades=props_organizadas,
                             fondos=fondos_disponibles)
    except Exception as e:
        return f"Error al cargar personalización de tema: {str(e)}", 500


@chatbot_admin_bp.route('/temas/<int:tema_id>/preview')
def preview_tema_especifico(tema_id):
    """Vista previa de un tema específico"""
    try:
        from .models import TemaPersonalizacion, PropiedadTema
        
        db = get_db_session()
        
        tema = db.query(TemaPersonalizacion).get(tema_id)
        if not tema:
            return "Tema no encontrado", 404
        
        propiedades = db.query(PropiedadTema).filter_by(tema_id=tema.id).all()
        
        # Organizar propiedades por categoría
        props_organizadas = {}
        css_vars = {}
        
        for prop in propiedades:
            if prop.categoria not in props_organizadas:
                props_organizadas[prop.categoria] = {}
            props_organizadas[prop.categoria][prop.propiedad] = prop.valor
            
            # También crear variables CSS
            variable_name = prop.propiedad.replace('_', '-')
            css_vars[variable_name] = prop.valor
        
        db.close()
        
        return render_template('admin/preview_tema.html', 
                             tema=tema, 
                             propiedades=props_organizadas,
                             css_vars=css_vars)
    except Exception as e:
        return f"Error al cargar preview del tema: {str(e)}", 500