#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Models.py - Inicializador de Base de Datos
==========================================
Funciones para inicializar y verificar la base de datos del sistema.
"""

import os
import sqlite3

def init_db():
    """
    Inicializa y verifica la base de datos del sistema.
    Verifica que existe menu.db en la ubicación correcta.
    """
    try:
        # Ruta a la base de datos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'menu.db')
        
        # Verificar que la base de datos existe
        if os.path.exists(db_path):
            # Verificar que podemos conectarnos
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar que tiene tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            conn.close()
            
            if tables:
                print(f"📊 Base de datos encontrada con {len(tables)} tablas")
                return True
            else:
                print("⚠️ Base de datos vacía, es necesario migrar")
                return False
        else:
            print("❌ Base de datos no encontrada en:", db_path)
            return False
            
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def get_db_path():
    """Retorna la ruta completa a la base de datos"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'menu.db')