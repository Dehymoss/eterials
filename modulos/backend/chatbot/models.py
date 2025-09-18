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
import sys
import os

# Agregar el directorio padre al path para importar la base
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
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

class TemaPersonalizacion(Base):
    """
    Tabla para temas de personalización de la interfaz
    """
    __tablename__ = 'chatbot_temas'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    activo = Column(Boolean, default=False)
    predefinido = Column(Boolean, default=False)  # Temas que vienen por defecto
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow)
    
    # Relación con propiedades del tema
    propiedades = relationship("PropiedadTema", back_populates="tema", cascade="all, delete-orphan")

class PropiedadTema(Base):
    """
    Propiedades específicas de cada tema (colores, fuentes, etc.)
    """
    __tablename__ = 'chatbot_tema_propiedades'
    
    id = Column(Integer, primary_key=True)
    tema_id = Column(Integer, ForeignKey('chatbot_temas.id'), nullable=False)
    categoria = Column(String(50), nullable=False)  # 'colores', 'fuentes', 'botones', 'efectos', 'fondos'
    propiedad = Column(String(100), nullable=False)  # 'color_primario', 'fuente_titulo', etc.
    valor = Column(Text, nullable=False)  # Valor CSS o configuración
    tipo = Column(String(20), default='color')  # 'color', 'font', 'size', 'url', 'number'
    
    # Relación
    tema = relationship("TemaPersonalizacion", back_populates="propiedades")

class FondoPersonalizado(Base):
    __tablename__ = 'fondos_personalizados'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    archivo_url = Column(String(500), nullable=False)  # Ruta al archivo subido
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

# Temas predefinidos del sistema
TEMAS_PREDEFINIDOS = [
    {
        'nombre': 'eterials_clasico',
        'descripcion': 'Tema clásico de Eterials con colores dorados y elegantes',
        'activo': True,
        'predefinido': True,
        'propiedades': {
            # Colores principales
            'color_primario': '#FFD700',           # Dorado principal
            'color_secundario': '#1e3c72',         # Azul marino
            'color_fondo': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color_texto': '#ffffff',
            'color_texto_secundario': '#f0f0f0',
            'color_boton': '#FFD700',
            'color_boton_hover': '#FFA500',
            'color_tarjeta': 'rgba(255, 255, 255, 0.1)',
            
            # Fuentes
            'fuente_principal': 'Playfair Display, serif',
            'fuente_secundaria': 'Merriweather, serif',
            'fuente_botones': 'Caveat, cursive',
            'tamaño_titulo': '3rem',
            'tamaño_subtitulo': '1.5rem',
            'tamaño_texto': '1rem',
            
            # Botones
            'boton_border_radius': '25px',
            'boton_padding': '12px 25px',
            'boton_sombra': '0 4px 15px rgba(255, 215, 0, 0.3)',
            
            # Efectos
            'animacion_hover': 'transform: translateY(-2px)',
            'transicion': '0.3s ease',
            'backdrop_blur': '10px',
            
            # Fondos
            'fondo_tipo': 'gradient',  # 'gradient', 'imagen', 'color'
            'fondo_imagen_url': '',
            'fondo_overlay': 'rgba(0, 0, 0, 0.3)',  # Overlay para mejorar legibilidad
            'fondo_attachment': 'fixed',  # 'fixed', 'scroll'
            'fondo_size': 'cover',  # 'cover', 'contain', 'auto'
            
            # Logos y assets
            'logo_url': '/chatbot/static/assets/logo.png',
            'taza_url': '/chatbot/static/assets/taza.png'
        }
    },
    {
        'nombre': 'minimalista_oscuro',
        'descripcion': 'Tema minimalista con colores oscuros y líneas limpias',
        'activo': False,
        'predefinido': True,
        'propiedades': {
            # Colores principales
            'color_primario': '#00d4aa',           # Verde azulado
            'color_secundario': '#2d3748',         # Gris oscuro
            'color_fondo': 'linear-gradient(135deg, #1a202c 0%, #2d3748 100%)',
            'color_texto': '#ffffff',
            'color_texto_secundario': '#a0aec0',
            'color_boton': '#00d4aa',
            'color_boton_hover': '#00b894',
            'color_tarjeta': 'rgba(45, 55, 72, 0.8)',
            
            # Fuentes
            'fuente_principal': 'Inter, sans-serif',
            'fuente_secundaria': 'System UI, sans-serif',
            'fuente_botones': 'Inter, sans-serif',
            'tamaño_titulo': '2.5rem',
            'tamaño_subtitulo': '1.25rem',
            'tamaño_texto': '0.95rem',
            
            # Botones
            'boton_border_radius': '8px',
            'boton_padding': '10px 20px',
            'boton_sombra': '0 2px 10px rgba(0, 212, 170, 0.2)',
            
            # Efectos
            'animacion_hover': 'transform: scale(1.02)',
            'transicion': '0.2s ease',
            'backdrop_blur': '5px',
            
            # Fondos
            'fondo_tipo': 'gradient',
            'fondo_imagen_url': '',
            'fondo_overlay': 'rgba(0, 0, 0, 0.5)',
            'fondo_attachment': 'fixed',
            'fondo_size': 'cover',
            
            # Logos y assets
            'logo_url': '/chatbot/static/assets/logo.png',
            'taza_url': '/chatbot/static/assets/taza.png'
        }
    },
    {
        'nombre': 'caffe_warmth',
        'descripcion': 'Tema cálido inspirado en café con tonos marrones y cremas',
        'activo': False,
        'predefinido': True,
        'propiedades': {
            # Colores principales
            'color_primario': '#D2691E',           # Chocolate
            'color_secundario': '#8B4513',         # Marrón silla
            'color_fondo': 'linear-gradient(135deg, #DEB887 0%, #D2691E 50%, #8B4513 100%)',
            'color_texto': '#4a2c2a',
            'color_texto_secundario': '#6b4423',
            'color_boton': '#D2691E',
            'color_boton_hover': '#CD853F',
            'color_tarjeta': 'rgba(222, 184, 135, 0.3)',
            
            # Fuentes
            'fuente_principal': 'Dancing Script, cursive',
            'fuente_secundaria': 'Patrick Hand, cursive',
            'fuente_botones': 'Caveat, cursive',
            'tamaño_titulo': '3.5rem',
            'tamaño_subtitulo': '1.8rem',
            'tamaño_texto': '1.1rem',
            
            # Botones
            'boton_border_radius': '20px',
            'boton_padding': '15px 30px',
            'boton_sombra': '0 6px 20px rgba(210, 105, 30, 0.4)',
            
            # Efectos
            'animacion_hover': 'transform: rotate(1deg) scale(1.05)',
            'transicion': '0.4s ease',
            'backdrop_blur': '8px',
            
            # Fondos
            'fondo_tipo': 'gradient',
            'fondo_imagen_url': '',
            'fondo_overlay': 'rgba(139, 69, 19, 0.25)',  # Overlay café cálido
            'fondo_attachment': 'fixed',
            'fondo_size': 'cover',
            
            # Logos y assets
            'logo_url': '/chatbot/static/assets/logo.png',
            'taza_url': '/chatbot/static/assets/taza.png'
        }
    },
    {
        'nombre': 'neon_nights',
        'descripcion': 'Tema futurista con colores neón y efectos brillantes',
        'activo': False,
        'predefinido': True,
        'propiedades': {
            # Colores principales
            'color_primario': '#ff006e',           # Rosa neón
            'color_secundario': '#00f5ff',         # Cyan neón
            'color_fondo': 'linear-gradient(45deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
            'color_texto': '#ffffff',
            'color_texto_secundario': '#e94560',
            'color_boton': 'linear-gradient(45deg, #ff006e, #00f5ff)',
            'color_boton_hover': 'linear-gradient(45deg, #00f5ff, #ff006e)',
            'color_tarjeta': 'rgba(255, 0, 110, 0.1)',
            
            # Fuentes
            'fuente_principal': 'Orbitron, monospace',
            'fuente_secundaria': 'Exo 2, sans-serif',
            'fuente_botones': 'Orbitron, monospace',
            'tamaño_titulo': '2.8rem',
            'tamaño_subtitulo': '1.4rem',
            'tamaño_texto': '1rem',
            
            # Botones
            'boton_border_radius': '15px',
            'boton_padding': '12px 24px',
            'boton_sombra': '0 0 20px rgba(255, 0, 110, 0.5), 0 0 40px rgba(0, 245, 255, 0.3)',
            
            # Efectos
            'animacion_hover': 'transform: translateY(-3px) scale(1.05)',
            'transicion': '0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            'backdrop_blur': '15px',
            
            # Fondos
            'fondo_tipo': 'gradient',
            'fondo_imagen_url': '',
            'fondo_overlay': 'rgba(255, 0, 110, 0.15)',  # Overlay neón suave
            'fondo_attachment': 'fixed',
            'fondo_size': 'cover',
            
            # Logos y assets
            'logo_url': '/chatbot/static/assets/logo.png',
            'taza_url': '/chatbot/static/assets/taza.png'
        }
    }
]

def crear_temas_predefinidos(db_session):
    """
    Crea los temas predefinidos del sistema en la base de datos
    
    Args:
        db_session: Sesión de SQLAlchemy para realizar operaciones
    """
    try:
        for tema_data in TEMAS_PREDEFINIDOS:
            # Verificar si el tema ya existe
            tema_existente = db_session.query(TemaPersonalizacion).filter_by(
                nombre=tema_data['nombre']
            ).first()
            
            if not tema_existente:
                # Crear el tema principal
                tema = TemaPersonalizacion(
                    nombre=tema_data['nombre'],
                    descripcion=tema_data['descripcion'],
                    activo=tema_data['activo'],
                    predefinido=tema_data['predefinido']
                )
                db_session.add(tema)
                db_session.flush()  # Para obtener el ID
                
                # Crear las propiedades del tema
                for propiedad, valor in tema_data['propiedades'].items():
                    # Determinar la categoría basada en el nombre de la propiedad
                    if propiedad.startswith('color_'):
                        categoria = 'colores'
                    elif propiedad.startswith('fuente_') or propiedad.startswith('tamaño_'):
                        categoria = 'fuentes'
                    elif propiedad.startswith('boton_'):
                        categoria = 'botones'
                    else:
                        categoria = 'efectos'
                    
                    prop = PropiedadTema(
                        tema_id=tema.id,
                        propiedad=propiedad,
                        valor=str(valor),
                        categoria=categoria
                    )
                    db_session.add(prop)
                
                print(f"✅ Tema '{tema_data['nombre']}' creado exitosamente")
            else:
                print(f"⚠️ Tema '{tema_data['nombre']}' ya existe, omitiendo...")
        
        db_session.commit()
        print("🎨 Todos los temas predefinidos han sido procesados")
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Error al crear temas predefinidos: {str(e)}")
        raise

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
    
    # Crear temas predefinidos
    crear_temas_predefinidos(db_session)
    
    print("✨ Inicialización completa del chatbot finalizada")