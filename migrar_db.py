#!/usr/bin/env python3
"""
Script de migración para agregar nuevas columnas a la base de datos
Fecha: 28/07/2025
"""

import sqlite3
import os
from pathlib import Path

def migrar_base_datos():
    """Migrar la base de datos para agregar las nuevas columnas"""
    
    # Ruta a la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'modulos', 'backend', 'menu', 'database', 'menu.db')
    
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos en: {db_path}")
        return False
    
    print(f"🔧 Iniciando migración de base de datos: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(productos)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        
        print(f"📋 Columnas existentes en productos: {columnas_existentes}")
        
        # Lista de nuevas columnas a agregar
        nuevas_columnas = [
            ('instrucciones_preparacion', 'TEXT'),
            ('notas_cocina', 'TEXT'),
            ('codigo', 'VARCHAR(20)')
        ]
        
        columnas_agregadas = []
        
        for nombre_col, tipo_col in nuevas_columnas:
            if nombre_col not in columnas_existentes:
                try:
                    query = f"ALTER TABLE productos ADD COLUMN {nombre_col} {tipo_col}"
                    cursor.execute(query)
                    columnas_agregadas.append(nombre_col)
                    print(f"✅ Columna agregada: {nombre_col} ({tipo_col})")
                except sqlite3.Error as e:
                    print(f"❌ Error agregando columna {nombre_col}: {e}")
            else:
                print(f"⚠️ Columna {nombre_col} ya existe, omitiendo...")
        
        # Verificar tabla ingredientes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ingredientes'")
        tabla_ingredientes = cursor.fetchone()
        
        if not tabla_ingredientes:
            print("🔧 Creando tabla de ingredientes...")
            cursor.execute("""
                CREATE TABLE ingredientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    cantidad VARCHAR(50),
                    unidad VARCHAR(20),
                    costo FLOAT DEFAULT 0.0,
                    obligatorio BOOLEAN DEFAULT 1,
                    activo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            """)
            print("✅ Tabla ingredientes creada")
        else:
            print("⚠️ Tabla ingredientes ya existe")
        
        # Verificar tabla categorias
        cursor.execute("PRAGMA table_info(categorias)")
        columnas_categorias = [col[1] for col in cursor.fetchall()]
        
        if 'id' in columnas_categorias:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='categorias'")
            estructura_categorias = cursor.fetchone()[0]
            
            if 'INTEGER' not in estructura_categorias or 'AUTOINCREMENT' not in estructura_categorias:
                print("🔧 La tabla categorías necesita actualizarse para usar ID INTEGER...")
                # Respaldar datos existentes
                cursor.execute("SELECT * FROM categorias")
                categorias_backup = cursor.fetchall()
                
                # Recrear tabla con estructura correcta
                cursor.execute("DROP TABLE categorias")
                cursor.execute("""
                    CREATE TABLE categorias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo VARCHAR(255) NOT NULL,
                        descripcion TEXT,
                        icono VARCHAR(255),
                        orden INTEGER,
                        activa BOOLEAN DEFAULT 1
                    )
                """)
                
                # Insertar datos de respaldo (solo si hay datos)
                if categorias_backup:
                    categorias_ejemplos = [
                        ("Entradas", "Platos para comenzar la comida", "🥗", 1, True),
                        ("Platos Principales", "Platos principales del menú", "🍽️", 2, True),
                        ("Postres", "Dulces y postres deliciosos", "🍰", 3, True),
                        ("Bebidas", "Bebidas frías y calientes", "🥤", 4, True),
                    ]
                    
                    cursor.executemany("""
                        INSERT INTO categorias (titulo, descripcion, icono, orden, activa) 
                        VALUES (?, ?, ?, ?, ?)
                    """, categorias_ejemplos)
                    
                print("✅ Tabla categorías actualizada con estructura INTEGER")
        
        # Confirmar cambios
        conn.commit()
        
        # Mostrar resumen
        if columnas_agregadas:
            print(f"\n🎉 Migración completada exitosamente!")
            print(f"📝 Columnas agregadas: {', '.join(columnas_agregadas)}")
        else:
            print(f"\n✅ Base de datos ya estaba actualizada")
        
        # Verificar estructura final
        cursor.execute("PRAGMA table_info(productos)")
        columnas_finales = [col[1] for col in cursor.fetchall()]
        print(f"📋 Estructura final de productos: {columnas_finales}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def verificar_migracion():
    """Verificar que la migración se haya aplicado correctamente"""
    db_path = os.path.join(os.path.dirname(__file__), 'modulos', 'backend', 'menu', 'database', 'menu.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Probar una consulta con las nuevas columnas
        cursor.execute("SELECT id, nombre, instrucciones_preparacion, notas_cocina FROM productos LIMIT 1")
        resultado = cursor.fetchone()
        
        print("✅ Verificación exitosa: Las nuevas columnas están disponibles")
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración de base de datos...")
    
    if migrar_base_datos():
        print("\n🔍 Verificando migración...")
        if verificar_migracion():
            print("\n🎉 ¡Migración completada y verificada exitosamente!")
            print("📊 Puedes reiniciar el servidor para usar las nuevas funcionalidades")
        else:
            print("\n⚠️ Migración aplicada pero hay problemas en la verificación")
    else:
        print("\n❌ Error durante la migración")
