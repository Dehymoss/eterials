#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crear 5 Temas Únicos y Hermosos para Eterials Café
==================================================
Basados en la estética actual del café con opciones de personalización completa.
"""

from modulos.backend.chatbot.models import TemaPersonalizacion, PropiedadTema
from modulos.backend.chatbot.api_endpoints import get_db_session
from datetime import datetime

def limpiar_temas_existentes():
    """Limpiar temas existentes para empezar desde cero"""
    db = get_db_session()
    
    # Eliminar propiedades primero (foreign key)
    db.query(PropiedadTema).delete()
    db.commit()
    
    # Eliminar temas
    db.query(TemaPersonalizacion).delete()
    db.commit()
    
    print("🗑️ Temas anteriores eliminados")
    db.close()

def crear_temas_eterials():
    """Crear los 5 temas únicos para Eterials Café"""
    
    db = get_db_session()
    print("🎨 Creando 5 temas únicos de Eterials Café...")
    
    # ====================================================================
    # TEMA 1: ☕ CAFÉ DORADO CLÁSICO (Tema actual mejorado)
    # ====================================================================
    tema_dorado = TemaPersonalizacion(
        nombre="☕ Café Dorado Clásico",
        descripcion="Elegancia dorada con texturas de papel vintage - El alma de Eterials",
        activo=True,
        predefinido=True
    )
    db.add(tema_dorado)
    db.commit()
    
    propiedades_dorado = [
        # Colores principales
        ("colores", "--color-primary", "#d4af37", "color"),           # Dorado elegante
        ("colores", "--color-secondary", "#2c1810", "color"),         # Marrón café oscuro
        ("colores", "--color-accent", "#f4e4c1", "color"),            # Crema cálido
        ("colores", "--color-text-light", "#fffbe7", "color"),        # Blanco cálido
        ("colores", "--color-text-dark", "#2c1810", "color"),         # Marrón oscuro
        
        # Tipografías
        ("tipografia", "--font-primary", "'Dancing Script', cursive", "font"),    # Títulos elegantes
        ("tipografia", "--font-secondary", "'Patrick Hand', cursive", "font"),    # Texto general
        ("tipografia", "--font-accent", "'Playfair Display', serif", "font"),     # Acentos
        
        # Fondos
        ("fondos", "--background-primary", "#232323", "color"),       # Fondo base
        ("fondos", "--background-image", "url('assets/clean-gray-paper.png')", "image"),
        ("fondos", "--background-overlay", "rgba(30, 30, 30, 0.3)", "color"),
        
        # Botones
        ("botones", "--button-bg", "linear-gradient(135deg, #d4af37 0%, #b8941f 100%)", "gradient"),
        ("botones", "--button-hover", "linear-gradient(135deg, #e6c547 0%, #d4af37 100%)", "gradient"),
        ("botones", "--button-radius", "25px", "size"),
        ("botones", "--button-shadow", "0 8px 32px rgba(212, 175, 55, 0.4)", "shadow"),
        
        # Efectos
        ("efectos", "--shadow-elegant", "0 8px 32px rgba(212, 175, 55, 0.2)", "shadow"),
        ("efectos", "--glow-primary", "0 0 15px #FFD700, 0 0 30px #FFA500", "glow"),
        ("efectos", "--animation-speed", "3s", "time")
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_dorado:
        prop = PropiedadTema(
            tema_id=tema_dorado.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo=tipo
        )
        db.add(prop)
    
    # ====================================================================
    # TEMA 2: 🌙 NOCHE URBANA MODERNA
    # ====================================================================
    tema_urbano = TemaPersonalizacion(
        nombre="🌙 Noche Urbana Moderna",
        descripcion="Diseño moderno con neones azules y gradientes urbanos",
        activo=False,
        predefinido=True
    )
    db.add(tema_urbano)
    db.commit()
    
    propiedades_urbano = [
        # Colores principales
        ("colores", "--color-primary", "#00d4ff", "color"),           # Cyan neón
        ("colores", "--color-secondary", "#1a1a2e", "color"),         # Azul muy oscuro
        ("colores", "--color-accent", "#16213e", "color"),            # Azul medio
        ("colores", "--color-text-light", "#ffffff", "color"),        # Blanco puro
        ("colores", "--color-text-dark", "#0f1419", "color"),         # Negro azulado
        
        # Tipografías
        ("tipografia", "--font-primary", "'Orbitron', sans-serif", "font"),      # Futurista
        ("tipografia", "--font-secondary", "'Roboto', sans-serif", "font"),       # Moderna
        ("tipografia", "--font-accent", "'Exo 2', sans-serif", "font"),           # Tecnológica
        
        # Fondos
        ("fondos", "--background-primary", "#0f1419", "color"),       # Negro azulado
        ("fondos", "--background-image", "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f1419 100%)", "gradient"),
        ("fondos", "--background-overlay", "rgba(0, 212, 255, 0.1)", "color"),
        
        # Botones
        ("botones", "--button-bg", "linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)", "gradient"),
        ("botones", "--button-hover", "linear-gradient(135deg, #33ddff 0%, #00d4ff 100%)", "gradient"),
        ("botones", "--button-radius", "8px", "size"),
        ("botones", "--button-shadow", "0 0 20px rgba(0, 212, 255, 0.6)", "shadow"),
        
        # Efectos
        ("efectos", "--shadow-elegant", "0 8px 32px rgba(0, 212, 255, 0.3)", "shadow"),
        ("efectos", "--glow-primary", "0 0 15px #00d4ff, 0 0 30px #0099cc", "glow"),
        ("efectos", "--animation-speed", "2s", "time")
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_urbano:
        prop = PropiedadTema(
            tema_id=tema_urbano.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo=tipo
        )
        db.add(prop)
    
    # ====================================================================
    # TEMA 3: 🌺 SAKURA ROSADO ELEGANTE
    # ====================================================================
    tema_sakura = TemaPersonalizacion(
        nombre="🌺 Sakura Rosado Elegante",
        descripcion="Inspirado en flores de cerezo con tonos rosados y dorados suaves",
        activo=False,
        predefinido=True
    )
    db.add(tema_sakura)
    db.commit()
    
    propiedades_sakura = [
        # Colores principales
        ("colores", "--color-primary", "#ff6b9d", "color"),           # Rosa vibrante
        ("colores", "--color-secondary", "#4a2c2a", "color"),         # Marrón cálido
        ("colores", "--color-accent", "#ffc0cb", "color"),            # Rosa claro
        ("colores", "--color-text-light", "#fff8f0", "color"),        # Crema rosado
        ("colores", "--color-text-dark", "#3d1a1a", "color"),         # Marrón oscuro
        
        # Tipografías
        ("tipografia", "--font-primary", "'Pacifico', cursive", "font"),          # Suave y curva
        ("tipografia", "--font-secondary", "'Quicksand', sans-serif", "font"),    # Moderna y limpia
        ("tipografia", "--font-accent", "'Dancing Script', cursive", "font"),     # Elegante
        
        # Fondos
        ("fondos", "--background-primary", "#fff8f0", "color"),       # Crema muy suave
        ("fondos", "--background-image", "linear-gradient(45deg, #fff8f0 0%, #ffc0cb 50%, #ff6b9d 100%)", "gradient"),
        ("fondos", "--background-overlay", "rgba(255, 192, 203, 0.2)", "color"),
        
        # Botones
        ("botones", "--button-bg", "linear-gradient(135deg, #ff6b9d 0%, #e91e63 100%)", "gradient"),
        ("botones", "--button-hover", "linear-gradient(135deg, #ff8fab 0%, #ff6b9d 100%)", "gradient"),
        ("botones", "--button-radius", "30px", "size"),
        ("botones", "--button-shadow", "0 8px 25px rgba(255, 107, 157, 0.4)", "shadow"),
        
        # Efectos
        ("efectos", "--shadow-elegant", "0 8px 32px rgba(255, 107, 157, 0.2)", "shadow"),
        ("efectos", "--glow-primary", "0 0 15px #ff6b9d, 0 0 30px #ffc0cb", "glow"),
        ("efectos", "--animation-speed", "4s", "time")
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_sakura:
        prop = PropiedadTema(
            tema_id=tema_sakura.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo=tipo
        )
        db.add(prop)
    
    # ====================================================================
    # TEMA 4: 🌿 NATURA VERDE ORGÁNICO
    # ====================================================================
    tema_natura = TemaPersonalizacion(
        nombre="🌿 Natura Verde Orgánico",
        descripcion="Inspirado en la naturaleza con verdes frescos y texturas orgánicas",
        activo=False,
        predefinido=True
    )
    db.add(tema_natura)
    db.commit()
    
    propiedades_natura = [
        # Colores principales
        ("colores", "--color-primary", "#4caf50", "color"),           # Verde natural
        ("colores", "--color-secondary", "#2e4d2e", "color"),         # Verde bosque
        ("colores", "--color-accent", "#81c784", "color"),            # Verde claro
        ("colores", "--color-text-light", "#f1f8e9", "color"),        # Verde muy claro
        ("colores", "--color-text-dark", "#1b5e20", "color"),         # Verde muy oscuro
        
        # Tipografías
        ("tipografia", "--font-primary", "'Comfortaa', cursive", "font"),         # Orgánica
        ("tipografia", "--font-secondary", "'Open Sans', sans-serif", "font"),    # Limpia
        ("tipografia", "--font-accent", "'Merriweather', serif", "font"),         # Natural
        
        # Fondos
        ("fondos", "--background-primary", "#f1f8e9", "color"),       # Verde muy claro
        ("fondos", "--background-image", "linear-gradient(135deg, #4caf50 0%, #81c784 50%, #c8e6c9 100%)", "gradient"),
        ("fondos", "--background-overlay", "rgba(76, 175, 80, 0.1)", "color"),
        
        # Botones
        ("botones", "--button-bg", "linear-gradient(135deg, #4caf50 0%, #388e3c 100%)", "gradient"),
        ("botones", "--button-hover", "linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)", "gradient"),
        ("botones", "--button-radius", "20px", "size"),
        ("botones", "--button-shadow", "0 8px 25px rgba(76, 175, 80, 0.4)", "shadow"),
        
        # Efectos
        ("efectos", "--shadow-elegant", "0 8px 32px rgba(76, 175, 80, 0.2)", "shadow"),
        ("efectos", "--glow-primary", "0 0 15px #4caf50, 0 0 30px #81c784", "glow"),
        ("efectos", "--animation-speed", "5s", "time")
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_natura:
        prop = PropiedadTema(
            tema_id=tema_natura.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo=tipo
        )
        db.add(prop)
    
    # ====================================================================
    # TEMA 5: 🌟 GALAXIA PÚRPURA MÍSTICO
    # ====================================================================
    tema_galaxia = TemaPersonalizacion(
        nombre="🌟 Galaxia Púrpura Místico",
        descripcion="Inspirado en el cosmos con púrpuras profundos y destellos dorados",
        activo=False,
        predefinido=True
    )
    db.add(tema_galaxia)
    db.commit()
    
    propiedades_galaxia = [
        # Colores principales
        ("colores", "--color-primary", "#9c27b0", "color"),           # Púrpura vibrante
        ("colores", "--color-secondary", "#1a0033", "color"),         # Púrpura muy oscuro
        ("colores", "--color-accent", "#ba68c8", "color"),            # Púrpura claro
        ("colores", "--color-text-light", "#fce4ec", "color"),        # Rosa muy claro
        ("colores", "--color-text-dark", "#4a148c", "color"),         # Púrpura oscuro
        
        # Tipografías
        ("tipografia", "--font-primary", "'Cinzel', serif", "font"),              # Elegante y místico
        ("tipografia", "--font-secondary", "'Raleway', sans-serif", "font"),      # Moderna
        ("tipografia", "--font-accent", "'Great Vibes', cursive", "font"),        # Mística
        
        # Fondos
        ("fondos", "--background-primary", "#1a0033", "color"),       # Púrpura muy oscuro
        ("fondos", "--background-image", "radial-gradient(circle, #4a148c 0%, #1a0033 50%, #000000 100%)", "gradient"),
        ("fondos", "--background-overlay", "rgba(156, 39, 176, 0.15)", "color"),
        
        # Botones
        ("botones", "--button-bg", "linear-gradient(135deg, #9c27b0 0%, #673ab7 100%)", "gradient"),
        ("botones", "--button-hover", "linear-gradient(135deg, #ab47bc 0%, #9c27b0 100%)", "gradient"),
        ("botones", "--button-radius", "15px", "size"),
        ("botones", "--button-shadow", "0 0 25px rgba(156, 39, 176, 0.6)", "shadow"),
        
        # Efectos
        ("efectos", "--shadow-elegant", "0 8px 32px rgba(156, 39, 176, 0.3)", "shadow"),
        ("efectos", "--glow-primary", "0 0 15px #9c27b0, 0 0 30px #ba68c8, 0 0 45px #d1c4e9", "glow"),
        ("efectos", "--animation-speed", "6s", "time")
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_galaxia:
        prop = PropiedadTema(
            tema_id=tema_galaxia.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo=tipo
        )
        db.add(prop)
    
    db.commit()
    
    print("✅ 5 temas únicos creados exitosamente:")
    print("   1. ☕ Café Dorado Clásico (ACTIVO)")
    print("   2. 🌙 Noche Urbana Moderna")
    print("   3. 🌺 Sakura Rosado Elegante")
    print("   4. 🌿 Natura Verde Orgánico")
    print("   5. 🌟 Galaxia Púrpura Místico")
    print()
    print("🎨 Características de cada tema:")
    print("   • Colores únicos (5 variables)")
    print("   • Tipografías específicas (3 fuentes)")
    print("   • Fondos personalizados (gradientes/imágenes)")
    print("   • Estilos de botones (forma, sombras, efectos)")
    print("   • Efectos especiales (brillos, animaciones)")
    
    db.close()

def verificar_temas_creados():
    """Verificar que los temas se crearon correctamente"""
    db = get_db_session()
    
    temas = db.query(TemaPersonalizacion).all()
    print(f"\n📊 Verificación: {len(temas)} temas en base de datos")
    
    for tema in temas:
        props = db.query(PropiedadTema).filter_by(tema_id=tema.id).count()
        print(f"   • {tema.nombre}: {props} propiedades")
    
    db.close()

if __name__ == "__main__":
    print("🎨 CREANDO SISTEMA DE TEMAS ETERIALS CAFÉ")
    print("=" * 60)
    
    # Limpiar temas existentes
    limpiar_temas_existentes()
    
    # Crear nuevos temas
    crear_temas_eterials()
    
    # Verificar
    verificar_temas_creados()
    
    print("\n🚀 ¡Sistema de temas listo para usar!")
    print("   📍 URL Dashboard: http://127.0.0.1:8080/admin/chatbot")
    print("   🎯 Sección: Gestión de Temas")