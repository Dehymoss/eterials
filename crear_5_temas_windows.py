#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup de 5 Temas Predefinidos Estilo Windows para Chatbot
=========================================================
Crea 5 temas inspirados en Windows: Clásico, Oscuro, Colorido, Natural, Elegante
"""

from modulos.backend.chatbot.models import TemaPersonalizacion, PropiedadTema
from modulos.backend.chatbot.api_endpoints import get_db_session
from datetime import datetime

def crear_5_temas_windows():
    """Crear los 5 temas predefinidos estilo Windows"""
    
    db = get_db_session()
    
    # Limpiar temas existentes si los hay
    print("🧹 Limpiando temas existentes...")
    db.query(PropiedadTema).delete()
    db.query(TemaPersonalizacion).delete()
    db.commit()
    
    print("🎨 Creando 5 temas estilo Windows...")
    
    # 1. TEMA CLÁSICO (Café - ACTIVO por defecto)
    tema_clasico = TemaPersonalizacion(
        nombre="☕ Café Clásico",
        descripcion="Tema clásico con colores cálidos de café y madera",
        activo=True,
        predefinido=True
    )
    db.add(tema_clasico)
    db.commit()
    
    propiedades_clasico = [
        ('colores', '--color-primary', '#d4af37', 'color'),           # Dorado café
        ('colores', '--color-secondary', '#2c1810', 'color'),         # Marrón oscuro
        ('colores', '--color-accent', '#f4e4c1', 'color'),            # Crema
        ('colores', '--color-text-light', '#f9f7f1', 'color'),        # Blanco cálido
        ('colores', '--color-text-dark', '#2c1810', 'color'),         # Marrón texto
        ('fondos', '--background-image', "url('assets/clean-gray-paper.png')", 'image'),
        ('efectos', '--shadow-elegant', '0 8px 32px rgba(212, 175, 55, 0.2)', 'css'),
        ('general', '--border-radius', '8px', 'size'),
        ('general', '--font-family', "'Patrick Hand', cursive", 'font')
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_clasico:
        prop = PropiedadTema(tema_id=tema_clasico.id, categoria=categoria, propiedad=propiedad, valor=valor, tipo=tipo)
        db.add(prop)
    
    # 2. TEMA OSCURO (Dark Mode)
    tema_oscuro = TemaPersonalizacion(
        nombre="🌙 Modo Oscuro",
        descripcion="Tema oscuro moderno para ambientes con poca luz",
        activo=False,
        predefinido=True
    )
    db.add(tema_oscuro)
    db.commit()
    
    propiedades_oscuro = [
        ('colores', '--color-primary', '#00d4aa', 'color'),           # Verde agua brillante
        ('colores', '--color-secondary', '#1a1a1a', 'color'),         # Negro profundo
        ('colores', '--color-accent', '#2d3748', 'color'),            # Gris oscuro
        ('colores', '--color-text-light', '#ffffff', 'color'),        # Blanco puro
        ('colores', '--color-text-dark', '#000000', 'color'),         # Negro para contraste
        ('fondos', '--background-image', 'linear-gradient(135deg, #1a1a1a 0%, #2d3748 50%, #1a1a1a 100%)', 'gradient'),
        ('efectos', '--shadow-elegant', '0 8px 32px rgba(0, 212, 170, 0.3)', 'css'),
        ('general', '--border-radius', '12px', 'size'),
        ('general', '--font-family', "'Segoe UI', Arial, sans-serif", 'font')
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_oscuro:
        prop = PropiedadTema(tema_id=tema_oscuro.id, categoria=categoria, propiedad=propiedad, valor=valor, tipo=tipo)
        db.add(prop)
    
    # 3. TEMA COLORIDO (Vibrante)
    tema_colorido = TemaPersonalizacion(
        nombre="🌈 Colorido Vibrante",
        descripcion="Tema alegre con colores vibrantes y gradientes llamativos",
        activo=False,
        predefinido=True
    )
    db.add(tema_colorido)
    db.commit()
    
    propiedades_colorido = [
        ('colores', '--color-primary', '#ff6b6b', 'color'),           # Rojo coral
        ('colores', '--color-secondary', '#4ecdc4', 'color'),         # Turquesa
        ('colores', '--color-accent', '#ffe66d', 'color'),            # Amarillo brillante
        ('colores', '--color-text-light', '#ffffff', 'color'),        # Blanco
        ('colores', '--color-text-dark', '#2c3e50', 'color'),         # Azul oscuro
        ('fondos', '--background-image', 'linear-gradient(45deg, #ff6b6b 0%, #4ecdc4 35%, #45b7d1 65%, #96ceb4 100%)', 'gradient'),
        ('efectos', '--shadow-elegant', '0 8px 32px rgba(255, 107, 107, 0.4)', 'css'),
        ('general', '--border-radius', '15px', 'size'),
        ('general', '--font-family', "'Comic Sans MS', cursive", 'font')
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_colorido:
        prop = PropiedadTema(tema_id=tema_colorido.id, categoria=categoria, propiedad=propiedad, valor=valor, tipo=tipo)
        db.add(prop)
    
    # 4. TEMA NATURAL (Verde)
    tema_natural = TemaPersonalizacion(
        nombre="🌿 Natural Verde",
        descripcion="Tema inspirado en la naturaleza con verdes y marrones tierra",
        activo=False,
        predefinido=True
    )
    db.add(tema_natural)
    db.commit()
    
    propiedades_natural = [
        ('colores', '--color-primary', '#27ae60', 'color'),           # Verde bosque
        ('colores', '--color-secondary', '#2c3e32', 'color'),         # Verde muy oscuro
        ('colores', '--color-accent', '#a8d8a8', 'color'),            # Verde pastel
        ('colores', '--color-text-light', '#f8f9fa', 'color'),        # Blanco natural
        ('colores', '--color-text-dark', '#1b4332', 'color'),         # Verde muy oscuro
        ('fondos', '--background-image', 'linear-gradient(135deg, #2d5a27 0%, #4a7c59 50%, #81b882 100%)', 'gradient'),
        ('efectos', '--shadow-elegant', '0 8px 32px rgba(39, 174, 96, 0.25)', 'css'),
        ('general', '--border-radius', '10px', 'size'),
        ('general', '--font-family', "'Georgia', serif", 'font')
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_natural:
        prop = PropiedadTema(tema_id=tema_natural.id, categoria=categoria, propiedad=propiedad, valor=valor, tipo=tipo)
        db.add(prop)
    
    # 5. TEMA ELEGANTE (Dorado/Negro)
    tema_elegante = TemaPersonalizacion(
        nombre="✨ Elegante Dorado",
        descripcion="Tema sofisticado con dorado y negro para ocasiones especiales",
        activo=False,
        predefinido=True
    )
    db.add(tema_elegante)
    db.commit()
    
    propiedades_elegante = [
        ('colores', '--color-primary', '#ffd700', 'color'),           # Oro brillante
        ('colores', '--color-secondary', '#1c1c1c', 'color'),         # Negro elegante
        ('colores', '--color-accent', '#c9b037', 'color'),            # Oro oscuro
        ('colores', '--color-text-light', '#ffffff', 'color'),        # Blanco puro
        ('colores', '--color-text-dark', '#000000', 'color'),         # Negro profundo
        ('fondos', '--background-image', 'linear-gradient(135deg, #1c1c1c 0%, #2c2c2c 25%, #1c1c1c 50%, #2c2c2c 75%, #1c1c1c 100%)', 'gradient'),
        ('efectos', '--shadow-elegant', '0 12px 40px rgba(255, 215, 0, 0.3)', 'css'),
        ('general', '--border-radius', '6px', 'size'),
        ('general', '--font-family', "'Playfair Display', serif", 'font')
    ]
    
    for categoria, propiedad, valor, tipo in propiedades_elegante:
        prop = PropiedadTema(tema_id=tema_elegante.id, categoria=categoria, propiedad=propiedad, valor=valor, tipo=tipo)
        db.add(prop)
    
    db.commit()
    
    print("✅ 5 Temas estilo Windows creados exitosamente:")
    print("   1. ☕ Café Clásico (ACTIVO)")
    print("   2. 🌙 Modo Oscuro")
    print("   3. 🌈 Colorido Vibrante") 
    print("   4. 🌿 Natural Verde")
    print("   5. ✨ Elegante Dorado")
    
    db.close()

if __name__ == "__main__":
    crear_5_temas_windows()