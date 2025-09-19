#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migración para agregar campo base64 a FondoPersonalizado
======================================================
Agrega el campo archivo_base64 a la tabla fondos_personalizados
"""

import sys
import os
from sqlalchemy import text

# Agregar paths
sys.path.append(os.path.dirname(__file__))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crear configuración de sesión igual al sistema principal
engine = create_engine('sqlite:///modulos/backend/menu/menu.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrar_fondos_base64():
    """Agregar campo archivo_base64 a la tabla fondos_personalizados"""
    db = SessionLocal()
    try:
        print("🔄 Iniciando migración de fondos a base64...")
        
        # Verificar si el campo ya existe
        result = db.execute(text("PRAGMA table_info(fondos_personalizados)"))
        columnas = [row[1] for row in result.fetchall()]
        
        if 'archivo_base64' in columnas:
            print("✅ El campo archivo_base64 ya existe")
            return True
        
        # Agregar el nuevo campo
        print("📝 Agregando campo archivo_base64...")
        db.execute(text("ALTER TABLE fondos_personalizados ADD COLUMN archivo_base64 TEXT"))
        
        db.commit()
        print("✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    migrar_fondos_base64()