"""
Script para limpiar la base de datos y resolver inconsistencias
Fecha: 31/07/2025
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Importar modelos y base en orden específico
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar base primero
from modulos.backend.menu.database.base import Base

# Importar modelos en orden de dependencias (sin relaciones circulares)
from modulos.backend.menu.database.models.categoria import Categoria
from modulos.backend.menu.database.models.subcategoria import Subcategoria  
from modulos.backend.menu.database.models.producto import Producto
from modulos.backend.menu.database.models.ingrediente import Ingrediente

def limpiar_base_datos():
    """Limpia toda la base de datos y la recrea"""
    
    print("🧹 Iniciando limpieza de base de datos...")
    
    # Configurar base de datos
    DB_PATH = os.path.join(os.path.dirname(__file__), 'modulos', 'backend', 'menu', 'database', 'menu.db')
    engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
    
    print(f"📍 Base de datos: {DB_PATH}")
    
    try:
        # 1. Eliminar todas las tablas existentes
        print("🗑️ Eliminando tablas existentes...")
        Base.metadata.drop_all(engine)
        print("✅ Tablas eliminadas")
        
        # 2. Recrear todas las tablas con las relaciones correctas
        print("🏗️ Recreando tablas con relaciones corregidas...")
        Base.metadata.create_all(engine)
        print("✅ Tablas recreadas")
        
        # 3. Crear sesión para insertar datos iniciales
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # 4. Insertar categorías base
        print("📂 Insertando categorías base...")
        categorias_base = [
            Categoria(titulo="Entradas", descripcion="Aperitivos y entradas", icono="🥗", orden=1, activa=True),
            Categoria(titulo="Platos Principales", descripcion="Platos fuertes", icono="🍽️", orden=2, activa=True),
            Categoria(titulo="Postres", descripcion="Dulces y postres", icono="🍰", orden=3, activa=True),
            Categoria(titulo="Bebidas", descripcion="Bebidas frías y calientes", icono="🥤", orden=4, activa=True),
            Categoria(titulo="Pizza", descripcion="Pizzas artesanales", icono="🍕", orden=5, activa=True),
            Categoria(titulo="Hamburguesas", descripcion="Hamburguesas gourmet", icono="🍔", orden=6, activa=True)
        ]
        
        for categoria in categorias_base:
            session.add(categoria)
        
        session.commit()
        print(f"✅ {len(categorias_base)} categorías insertadas")
        
        # 5. Insertar subcategorías base
        print("📋 Insertando subcategorías base...")
        subcategorias_base = [
            Subcategoria(nombre="Ensaladas", categoria_id=1, activa=True),
            Subcategoria(nombre="Sopas", categoria_id=1, activa=True),
            Subcategoria(nombre="Carnes", categoria_id=2, activa=True),
            Subcategoria(nombre="Pastas", categoria_id=2, activa=True),
            Subcategoria(nombre="Mariscos", categoria_id=2, activa=True),
            Subcategoria(nombre="Helados", categoria_id=3, activa=True),
            Subcategoria(nombre="Tortas", categoria_id=3, activa=True),
            Subcategoria(nombre="Frías", categoria_id=4, activa=True),
            Subcategoria(nombre="Calientes", categoria_id=4, activa=True),
            Subcategoria(nombre="Clásica", categoria_id=5, activa=True),
            Subcategoria(nombre="Gourmet", categoria_id=5, activa=True),
            Subcategoria(nombre="Tradicional", categoria_id=6, activa=True),
            Subcategoria(nombre="Premium", categoria_id=6, activa=True)
        ]
        
        for subcategoria in subcategorias_base:
            session.add(subcategoria)
            
        session.commit()
        print(f"✅ {len(subcategorias_base)} subcategorías insertadas")
        
        # 6. Verificar relaciones
        print("🔍 Verificando relaciones...")
        
        # Verificar que las categorías se pueden consultar
        total_categorias = session.query(Categoria).count()
        print(f"✅ Categorías en BD: {total_categorias}")
        
        # Verificar que las subcategorías se pueden consultar
        total_subcategorias = session.query(Subcategoria).count()
        print(f"✅ Subcategorías en BD: {total_subcategorias}")
        
        # Verificar relaciones
        primera_categoria = session.query(Categoria).first()
        if primera_categoria:
            print(f"✅ Primera categoría: {primera_categoria.titulo}")
            subcats = primera_categoria.subcategorias
            print(f"✅ Subcategorías de '{primera_categoria.titulo}': {len(subcats)}")
        
        session.close()
        
        print("\n🎉 ¡Base de datos limpiada y configurada correctamente!")
        print("📋 Estado actual:")
        print(f"   - Categorías: {total_categorias}")
        print(f"   - Subcategorías: {total_subcategorias}")
        print("   - Productos: 0 (base limpia)")
        print("   - Ingredientes: 0 (base limpia)")
        print("\n✅ Lista para insertar productos reales")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧹 SCRIPT DE LIMPIEZA DE BASE DE DATOS")
    print("   Sistema de Gestión de Restaurante Eterials")
    print("   Fecha: 31/07/2025")
    print("=" * 60)
    
    resultado = limpiar_base_datos()
    
    if resultado:
        print("\n🚀 La base de datos está lista para productos reales")
    else:
        print("\n💥 Hubo errores durante la limpieza")
    
    print("=" * 60)
