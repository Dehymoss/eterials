#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicializador de Base de Datos del Chatbot
==========================================
Script para crear tablas y cargar datos por defecto del sistema de chatbot.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modulos.backend.menu.database.base import Base  # Usar la base existente del sistema
from modulos.backend.chatbot.models import (
    Sesion, Calificacion, Comentario, NotificacionMesero,
    Analytics, ConfiguracionChatbot, TemaPersonalizacion, PropiedadTema,
    FondoPersonalizado, inicializar_datos_chatbot
)

def inicializar_base_datos_chatbot():
    """
    Función principal para inicializar la base de datos del chatbot
    """
    print("🚀 Inicializando Base de Datos del Chatbot")
    print("=" * 50)
    
    try:
        # Conectar a la base de datos principal
        engine = create_engine('sqlite:///modulos/backend/menu/menu.db')
        
        # Crear todas las tablas del chatbot
        print("📊 Creando tablas del chatbot...")
        Base.metadata.create_all(engine, checkfirst=True)
        print("✅ Tablas creadas exitosamente")
        
        # Crear sesión
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Inicializar datos por defecto
        print("\n🎨 Cargando datos por defecto...")
        inicializar_datos_chatbot(session)
        
        # Verificar creación
        print("\n🔍 Verificando datos creados...")
        
        # Contar configuraciones
        total_configs = session.query(ConfiguracionChatbot).count()
        print(f"📋 Configuraciones cargadas: {total_configs}")
        
        # Contar temas
        total_temas = session.query(TemaPersonalizacion).count()
        print(f"🎨 Temas predefinidos: {total_temas}")
        
        # Contar propiedades de temas
        total_propiedades = session.query(PropiedadTema).count()
        print(f"🎯 Propiedades de temas: {total_propiedades}")
        
        # Mostrar tema activo
        tema_activo = session.query(TemaPersonalizacion).filter_by(activo=True).first()
        if tema_activo:
            print(f"🌟 Tema activo: {tema_activo.nombre}")
        else:
            print("⚠️ No hay tema activo configurado")
        
        session.close()
        
        print("\n" + "=" * 50)
        print("✨ Inicialización del chatbot completada exitosamente")
        print("🌐 El sistema está listo para usarse")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")
        return False

def verificar_estado_chatbot():
    """
    Verifica el estado actual de la base de datos del chatbot
    """
    print("🔍 Verificando estado del sistema de chatbot...")
    
    try:
        engine = create_engine('sqlite:///modulos/backend/menu/menu.db')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar tablas principales
        tablas_esperadas = [
            ('Sesiones', Sesion),
            ('Calificaciones', Calificacion),
            ('Comentarios', Comentario),
            ('Notificaciones', NotificacionMesero),
            ('Analytics', Analytics),
            ('Configuraciones', ConfiguracionChatbot),
            ('Temas', TemaPersonalizacion),
            ('Propiedades de Temas', PropiedadTema)
        ]
        
        print("\n📊 Estado de las tablas:")
        for nombre, modelo in tablas_esperadas:
            try:
                count = session.query(modelo).count()
                print(f"  ✅ {nombre}: {count} registros")
            except Exception as e:
                print(f"  ❌ {nombre}: Error - {str(e)}")
        
        # Verificar configuraciones críticas
        print("\n⚙️ Configuraciones críticas:")
        configs_criticas = ['saludo_manana', 'saludo_tarde', 'saludo_noche', 'tema_activo']
        
        for config_key in configs_criticas:
            config = session.query(ConfiguracionChatbot).filter_by(clave=config_key).first()
            if config:
                print(f"  ✅ {config_key}: {config.valor}")
            else:
                print(f"  ❌ {config_key}: No configurada")
        
        # Verificar tema activo
        print("\n🎨 Estado de temas:")
        tema_activo = session.query(TemaPersonalizacion).filter_by(activo=True).first()
        if tema_activo:
            propiedades_count = session.query(PropiedadTema).filter_by(tema_id=tema_activo.id).count()
            print(f"  🌟 Tema activo: {tema_activo.nombre}")
            print(f"  🎯 Propiedades: {propiedades_count}")
        else:
            print("  ⚠️ No hay tema activo")
        
        # Verificar fondos personalizados (NUEVO)
        print("\n🖼️ Fondos personalizados:")
        fondos = session.query(FondoPersonalizado).all()
        if fondos:
            total_espacio = sum(f.tamaño_archivo for f in fondos)
            print(f"  📊 Total fondos: {len(fondos)}")
            print(f"  💾 Espacio usado: {total_espacio / (1024*1024):.2f} MB")
            mas_usado = max(fondos, key=lambda f: f.contador_uso) if fondos else None
            if mas_usado:
                print(f"  🏆 Más usado: {mas_usado.nombre} ({mas_usado.contador_uso} usos)")
        else:
            print("  📷 No hay fondos personalizados subidos")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verificar":
        verificar_estado_chatbot()
    else:
        inicializar_base_datos_chatbot()