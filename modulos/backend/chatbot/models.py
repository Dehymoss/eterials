#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos SQLAlchemy para el Backend del Chatbot
=============================================
Define todas las tablas necesarias para el sistema del chatbot.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from modulos.backend.menu.database.base import Base  # Usar la misma base del sistema

class Sesion(Base):
    """
    Tabla para trackear sesiones de usuarios en el chatbot
    """
    __tablename__ = 'chatbot_sesiones'
    
    id = Column(Integer, primary_key=True)
    mesa = Column(String(20), nullable=False)  # Mesa o "barra"
    nombre_cliente = Column(String(100))  # Nombre del cliente (opcional)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_ultimo_acceso = Column(DateTime, default=datetime.utcnow)
    dispositivo = Column(String(200))  # User-Agent del dispositivo
    ip_cliente = Column(String(45))  # IP del cliente
    activa = Column(Boolean, default=True)
    
    # Relaciones
    calificaciones = relationship("Calificacion", back_populates="sesion")
    comentarios = relationship("Comentario", back_populates="sesion")
    notificaciones = relationship("NotificacionMesero", back_populates="sesion")

class Calificacion(Base):
    """
    Tabla para almacenar calificaciones de 1 a 5 estrellas
    """
    __tablename__ = 'chatbot_calificaciones'
    
    id = Column(Integer, primary_key=True)
    sesion_id = Column(Integer, ForeignKey('chatbot_sesiones.id'), nullable=False)
    estrellas = Column(Integer, nullable=False)  # 1-5
    fecha_calificacion = Column(DateTime, default=datetime.utcnow)
    categoria = Column(String(50))  # 'servicio', 'comida', 'ambiente', 'general'
    
    # Relación
    sesion = relationship("Sesion", back_populates="calificaciones")

class Comentario(Base):
    """
    Tabla para comentarios y sugerencias de los clientes
    """
    __tablename__ = 'chatbot_comentarios'
    
    id = Column(Integer, primary_key=True)
    sesion_id = Column(Integer, ForeignKey('chatbot_sesiones.id'), nullable=False)
    texto_comentario = Column(Text, nullable=False)
    tipo = Column(String(30))  # 'sugerencia', 'queja', 'felicitacion', 'general'
    fecha_comentario = Column(DateTime, default=datetime.utcnow)
    moderado = Column(Boolean, default=False)  # Para moderar comentarios
    
    # Relación
    sesion = relationship("Sesion", back_populates="comentarios")

class NotificacionMesero(Base):
    """
    Tabla para notificaciones al personal (llamar mesero, etc.)
    """
    __tablename__ = 'chatbot_notificaciones'
    
    id = Column(Integer, primary_key=True)
    sesion_id = Column(Integer, ForeignKey('chatbot_sesiones.id'), nullable=False)
    tipo_notificacion = Column(String(50), nullable=False)  # 'llamar_mesero', 'pedido_especial', 'emergencia'
    mensaje = Column(Text)  # Mensaje adicional opcional
    fecha_notificacion = Column(DateTime, default=datetime.utcnow)
    atendida = Column(Boolean, default=False)
    atendida_por = Column(String(100))  # Nombre del mesero/staff que atendió
    fecha_atencion = Column(DateTime)
    prioridad = Column(String(20), default='normal')  # 'baja', 'normal', 'alta', 'urgente'
    
    # Relación
    sesion = relationship("Sesion", back_populates="notificaciones")

class Analytics(Base):
    """
    Tabla para métricas y analytics del chatbot
    """
    __tablename__ = 'chatbot_analytics'
    
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    mesa = Column(String(20))
    evento = Column(String(50))  # 'acceso', 'calificacion', 'comentario', 'notificacion'
    valor_numerico = Column(Float)  # Para calificaciones, tiempo de sesión, etc.
    valor_texto = Column(String(500))  # Para tracking de acciones específicas
    metadatos = Column(Text)  # JSON con datos adicionales
    
class ConfiguracionChatbot(Base):
    """
    Tabla para configuraciones del chatbot
    """
    __tablename__ = 'chatbot_configuracion'
    
    id = Column(Integer, primary_key=True)
    clave = Column(String(100), nullable=False, unique=True)
    valor = Column(Text, nullable=False)
    tipo = Column(String(20), default='string')  # 'string', 'integer', 'boolean', 'json'
    descripcion = Column(Text)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow)

# ELIMINADO: Clases TemaPersonalizacion y PropiedadTema
# Motivo: Simplificación del sistema - solo mantener cambio de fondos

class FondoPersonalizado(Base):
    __tablename__ = 'fondos_personalizados'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    archivo_url = Column(String(500), nullable=False)  # Ruta al archivo subido
    archivo_base64 = Column(Text)  # Contenido de la imagen en base64 (NUEVO)
    archivo_original = Column(String(200))  # Nombre original del archivo
    tipo_archivo = Column(String(10))  # jpg, png, webp, gif
    tamaño_archivo = Column(Integer)  # Tamaño en bytes
    dimensiones = Column(String(20))  # ej: "1920x1080"
    activo = Column(Boolean, default=True)
    publico = Column(Boolean, default=True)  # Si otros temas pueden usarlo
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    fecha_uso = Column(DateTime)  # Última vez que se aplicó a un tema
    uso_contador = Column(Integer, default=0)  # Cuántas veces se ha usado
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'archivo_url': self.archivo_url,
            'archivo_original': self.archivo_original,
            'tipo_archivo': self.tipo_archivo,
            'tamaño_archivo': self.tamaño_archivo,
            'dimensiones': self.dimensiones,
            'activo': self.activo,
            'publico': self.publico,
            'fecha_subida': self.fecha_subida.isoformat() if self.fecha_subida else None,
            'fecha_uso': self.fecha_uso.isoformat() if self.fecha_uso else None,
            'uso_contador': self.uso_contador
        }

# ELIMINADO: ColoresAdaptativos - Sistema simplificado solo para cambiar fondos

# Configuraciones por defecto
CONFIGURACIONES_DEFAULT = [
    {
        'clave': 'saludo_manana',
        'valor': 'Buenos días',
        'tipo': 'string',
        'descripcion': 'Saludo para horas de la mañana (6:00 - 11:59)'
    },
    {
        'clave': 'saludo_tarde', 
        'valor': 'Buenas tardes',
        'tipo': 'string',
        'descripcion': 'Saludo para horas de la tarde (12:00 - 17:59)'
    },
    {
        'clave': 'saludo_noche',
        'valor': 'Buenas noches', 
        'tipo': 'string',
        'descripcion': 'Saludo para horas de la noche (18:00 - 5:59)'
    },
    {
        'clave': 'timeout_inactividad',
        'valor': '600000',
        'tipo': 'integer',
        'descripcion': 'Tiempo en ms para logout por inactividad (default: 10 min)'
    },
    {
        'clave': 'notificaciones_habilitadas',
        'valor': 'true',
        'tipo': 'boolean',
        'descripcion': 'Habilitar sistema de notificaciones al personal'
    },
    {
        'clave': 'tema_activo',
        'valor': 'eterials_clasico',
        'tipo': 'string',
        'descripcion': 'Tema actualmente activo en el chatbot'
    }
]

# ELIMINADO: TEMAS_PREDEFINIDOS - Sistema simplificado solo fondos

# ELIMINADO: crear_temas_predefinidos - Sistema simplificado solo fondos

def crear_configuraciones_default(db_session):
    """
    Crea las configuraciones por defecto del chatbot
    
    Args:
        db_session: Sesión de SQLAlchemy para realizar operaciones
    """
    try:
        for config_data in CONFIGURACIONES_DEFAULT:
            # Verificar si la configuración ya existe
            config_existente = db_session.query(ConfiguracionChatbot).filter_by(
                clave=config_data['clave']
            ).first()
            
            if not config_existente:
                config = ConfiguracionChatbot(
                    clave=config_data['clave'],
                    valor=config_data['valor'],
                    tipo=config_data['tipo'],
                    descripcion=config_data['descripcion']
                )
                db_session.add(config)
                print(f"✅ Configuración '{config_data['clave']}' creada")
            else:
                print(f"⚠️ Configuración '{config_data['clave']}' ya existe")
        
        db_session.commit()
        print("⚙️ Todas las configuraciones por defecto han sido procesadas")
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Error al crear configuraciones: {str(e)}")
        raise

def inicializar_datos_chatbot(db_session):
    """
    Función principal para inicializar todos los datos por defecto del chatbot
    
    Args:
        db_session: Sesión de SQLAlchemy para realizar operaciones
    """
    print("🚀 Inicializando datos por defecto del chatbot...")
    
    # Crear configuraciones por defecto
    crear_configuraciones_default(db_session)
    
    # ELIMINADO: crear_temas_predefinidos - Sistema simplificado solo fondos
    
    print("✨ Inicialización completa del chatbot finalizada")