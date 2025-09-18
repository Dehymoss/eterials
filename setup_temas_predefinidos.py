#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup de Temas Predefinidos para Chatbot
========================================
Crea los temas por defecto del sistema con sus propiedades CSS.
"""

from modulos.backend.chatbot.models import TemaPersonalizacion, PropiedadTema, FondoPersonalizado
from modulos.backend.chatbot.api_endpoints import get_db_session
from datetime import datetime

def crear_temas_predefinidos():
    """Crear los 4 temas predefinidos del sistema"""
    
    db = get_db_session()
    
    # Verificar si ya existen temas
    temas_existentes = db.query(TemaPersonalizacion).count()
    if temas_existentes > 0:
        print(f"✅ Ya existen {temas_existentes} temas en la base de datos")
        db.close()
        return
    
    print("🎨 Creando temas predefinidos...")
    
    # Tema 1: Café Clásico (ACTIVO por defecto)
    tema_clasico = TemaPersonalizacion(
        nombre="Café Clásico",
        descripcion="Tema por defecto con colores cálidos de café",
        activo=True,
        predefinido=True
    )
    db.add(tema_clasico)
    db.commit()
    
    # Propiedades del tema clásico
    propiedades_clasico = [
        ("--color-primary", "#d4af37"),          # Dorado elegante
        ("--color-secondary", "#2c1810"),        # Marrón oscuro café
        ("--color-accent", "#f4e4c1"),           # Crema cálido
        ("--color-text-light", "#f9f7f1"),       # Blanco cálido
        ("--color-text-dark", "#2c1810"),        # Texto oscuro
        ("--background-image", "url('assets/clean-gray-paper.png')"),
        ("--shadow-elegant", "0 8px 32px rgba(212, 175, 55, 0.2)")
    ]
    
    for propiedad, valor in propiedades_clasico:
        # Determinar categoría basada en la propiedad
        if 'color' in propiedad:
            categoria = 'colores'
        elif 'background' in propiedad:
            categoria = 'fondos'
        elif 'shadow' in propiedad:
            categoria = 'efectos'
        else:
            categoria = 'general'
            
        prop = PropiedadTema(
            tema_id=tema_clasico.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo='color' if 'color' in propiedad else 'css'
        )
        db.add(prop)
    
    # Tema 2: Noche Moderna
    tema_noche = TemaPersonalizacion(
        nombre="Noche Moderna",
        descripcion="Tema oscuro moderno con acentos azules",
        activo=False,
        predefinido=True
    )
    db.add(tema_noche)
    db.commit()
    
    propiedades_noche = [
        ("--color-primary", "#4a90e2"),          # Azul moderno
        ("--color-secondary", "#1a1a1a"),        # Negro profundo
        ("--color-accent", "#2d3748"),           # Gris oscuro
        ("--color-text-light", "#ffffff"),       # Blanco puro
        ("--color-text-dark", "#1a1a1a"),        # Negro para contraste
        ("--background-image", "linear-gradient(135deg, #1a1a1a 0%, #2d3748 100%)"),
        ("--shadow-elegant", "0 8px 32px rgba(74, 144, 226, 0.3)")
    ]
    
    for propiedad, valor in propiedades_noche:
        # Determinar categoría basada en la propiedad
        if 'color' in propiedad:
            categoria = 'colores'
        elif 'background' in propiedad:
            categoria = 'fondos'
        elif 'shadow' in propiedad:
            categoria = 'efectos'
        else:
            categoria = 'general'
            
        prop = PropiedadTema(
            tema_id=tema_noche.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo='color' if 'color' in propiedad else 'css'
        )
        db.add(prop)
    
    # Tema 3: Vintage Rosado
    tema_vintage = TemaPersonalizacion(
        nombre="Vintage Rosado",
        descripcion="Tema vintage con tonos rosados y dorados",
        activo=False,
        predefinido=True
    )
    db.add(tema_vintage)
    db.commit()
    
    propiedades_vintage = [
        ("--color-primary", "#e91e63"),          # Rosa vibrante
        ("--color-secondary", "#4a2c2a"),        # Marrón vintage
        ("--color-accent", "#f8bbd9"),           # Rosa claro
        ("--color-text-light", "#fff8f0"),       # Crema vintage
        ("--color-text-dark", "#4a2c2a"),        # Marrón oscuro
        ("--background-image", "linear-gradient(45deg, #f8bbd9 0%, #e91e63 100%)"),
        ("--shadow-elegant", "0 8px 32px rgba(233, 30, 99, 0.2)")
    ]
    
    for propiedad, valor in propiedades_vintage:
        # Determinar categoría basada en la propiedad
        if 'color' in propiedad:
            categoria = 'colores'
        elif 'background' in propiedad:
            categoria = 'fondos'
        elif 'shadow' in propiedad:
            categoria = 'efectos'
        else:
            categoria = 'general'
            
        prop = PropiedadTema(
            tema_id=tema_vintage.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo='color' if 'color' in propiedad else 'css'
        )
        db.add(prop)
    
    # Tema 4: Naturaleza Verde
    tema_naturaleza = TemaPersonalizacion(
        nombre="Naturaleza Verde",
        descripcion="Tema natural con verdes y marrones tierra",
        activo=False,
        predefinido=True
    )
    db.add(tema_naturaleza)
    db.commit()
    
    propiedades_naturaleza = [
        ("--color-primary", "#4caf50"),          # Verde natural
        ("--color-secondary", "#2e4d2e"),        # Verde oscuro
        ("--color-accent", "#81c784"),           # Verde claro
        ("--color-text-light", "#f1f8e9"),       # Verde muy claro
        ("--color-text-dark", "#1b5e20"),        # Verde muy oscuro
        ("--background-image", "linear-gradient(135deg, #4caf50 0%, #81c784 100%)"),
        ("--shadow-elegant", "0 8px 32px rgba(76, 175, 80, 0.2)")
    ]
    
    for propiedad, valor in propiedades_naturaleza:
        # Determinar categoría basada en la propiedad
        if 'color' in propiedad:
            categoria = 'colores'
        elif 'background' in propiedad:
            categoria = 'fondos'
        elif 'shadow' in propiedad:
            categoria = 'efectos'
        else:
            categoria = 'general'
            
        prop = PropiedadTema(
            tema_id=tema_naturaleza.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo='color' if 'color' in propiedad else 'css'
        )
        db.add(prop)
    
    db.commit()
    
    print("✅ Temas predefinidos creados exitosamente:")
    print("   1. ☕ Café Clásico (ACTIVO)")
    print("   2. 🌙 Noche Moderna")
    print("   3. 🌸 Vintage Rosado")
    print("   4. 🌿 Naturaleza Verde")
    
    db.close()

if __name__ == "__main__":
    crear_temas_predefinidos()