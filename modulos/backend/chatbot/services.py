#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicios y Utilidades para el Backend del Chatbot
==================================================
Funciones de migración, inicialización y utilidades.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base, ConfiguracionChatbot, CONFIGURACIONES_DEFAULT
import json
import os

def crear_tablas_chatbot():
    """
    Crea todas las tablas necesarias para el backend del chatbot
    """
    try:
        # Usar la misma base de datos del sistema principal
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'menu', 
            'menu.db'
        )
        
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Crear todas las tablas del chatbot
        Base.metadata.create_all(engine, checkfirst=True)
        
        print("✅ Tablas del chatbot creadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas del chatbot: {e}")
        return False

def inicializar_configuracion_default():
    """
    Inicializa la configuración por defecto del chatbot
    """
    try:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'menu', 
            'menu.db'
        )
        
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Insertar configuraciones por defecto si no existen
        configuraciones_insertadas = 0
        
        for config_data in CONFIGURACIONES_DEFAULT:
            existe = db.query(ConfiguracionChatbot).filter(
                ConfiguracionChatbot.clave == config_data['clave']
            ).first()
            
            if not existe:
                nueva_config = ConfiguracionChatbot(
                    clave=config_data['clave'],
                    valor=config_data['valor'],
                    tipo=config_data['tipo'],
                    descripcion=config_data['descripcion']
                )
                db.add(nueva_config)
                configuraciones_insertadas += 1
        
        db.commit()
        db.close()
        
        print(f"✅ {configuraciones_insertadas} configuraciones inicializadas")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando configuración: {e}")
        return False

def verificar_estado_backend():
    """
    Verifica que el backend del chatbot esté correctamente configurado
    """
    try:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'menu', 
            'menu.db'
        )
        
        if not os.path.exists(db_path):
            return {
                'success': False,
                'error': 'Base de datos no encontrada',
                'tablas_chatbot': [],
                'configuraciones': 0
            }
        
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Verificar tablas del chatbot
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'chatbot_%'"
            ))
            tablas_chatbot = [row[0] for row in result]
        
        # Verificar configuraciones
        Session = sessionmaker(bind=engine)
        db = Session()
        
        total_configuraciones = db.query(ConfiguracionChatbot).count()
        
        db.close()
        
        return {
            'success': True,
            'tablas_chatbot': tablas_chatbot,
            'total_tablas': len(tablas_chatbot),
            'configuraciones': total_configuraciones,
            'base_datos': db_path
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'tablas_chatbot': [],
            'configuraciones': 0
        }

def migrar_datos_frontend_a_backend():
    """
    Función para migrar datos del frontend actual al nuevo backend
    (Se ejecutará cuando estemos listos para migrar)
    """
    # TODO: Implementar cuando hagamos la migración
    # Por ahora solo documentamos qué haría:
    """
    1. Extraer configuraciones hardcodeadas del JavaScript
    2. Migrar textos de saludo a la tabla de configuración
    3. Migrar URLs de módulos a configuración
    4. Crear sesiones históricas si hay datos en localStorage
    """
    pass

def generar_script_migracion():
    """
    Genera un script SQL para verificar la migración
    """
    script_sql = """
-- Script de verificación del backend del chatbot
-- Ejecutar después de crear las tablas

-- Verificar que las tablas existen
SELECT 'Tablas del chatbot:' as info;
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'chatbot_%';

-- Verificar configuraciones
SELECT 'Total configuraciones:' as info;
SELECT COUNT(*) as total FROM chatbot_configuracion;

-- Mostrar configuraciones
SELECT 'Configuraciones actuales:' as info;
SELECT clave, valor, tipo, descripcion FROM chatbot_configuracion;

-- Verificar estructura de tablas principales
SELECT 'Estructura tabla sesiones:' as info;
PRAGMA table_info(chatbot_sesiones);

SELECT 'Estructura tabla calificaciones:' as info;
PRAGMA table_info(chatbot_calificaciones);

SELECT 'Estructura tabla notificaciones:' as info;
PRAGMA table_info(chatbot_notificaciones);
"""
    
    return script_sql

if __name__ == "__main__":
    print("🚀 Inicializando backend del chatbot...")
    
    # Crear tablas
    if crear_tablas_chatbot():
        print("✅ Tablas creadas")
        
        # Inicializar configuración
        if inicializar_configuracion_default():
            print("✅ Configuración inicializada")
            
            # Verificar estado
            estado = verificar_estado_backend()
            if estado['success']:
                print(f"✅ Backend listo: {estado['total_tablas']} tablas, {estado['configuraciones']} configuraciones")
            else:
                print(f"❌ Error en verificación: {estado['error']}")
        else:
            print("❌ Error en configuración")
    else:
        print("❌ Error creando tablas")