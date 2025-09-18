#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agregar propiedades al tema Café Clásico
"""

from modulos.backend.chatbot.models import TemaPersonalizacion, PropiedadTema
from modulos.backend.chatbot.api_endpoints import get_db_session

def agregar_propiedades_tema():
    db = get_db_session()
    tema = db.query(TemaPersonalizacion).first()
    
    if not tema:
        print("❌ No se encontró el tema")
        return
    
    # Verificar si ya tiene propiedades
    props_existentes = db.query(PropiedadTema).filter_by(tema_id=tema.id).count()
    if props_existentes > 0:
        print(f"✅ El tema ya tiene {props_existentes} propiedades")
        db.close()
        return
    
    print(f"🎨 Agregando propiedades al tema: {tema.nombre}")
    
    propiedades = [
        ('colores', '--color-primary', '#d4af37', 'color'),
        ('colores', '--color-secondary', '#2c1810', 'color'),
        ('colores', '--color-accent', '#f4e4c1', 'color'),
        ('colores', '--color-text-light', '#f9f7f1', 'color'),
        ('colores', '--color-text-dark', '#2c1810', 'color'),
        ('fondos', '--background-image', "url('assets/clean-gray-paper.png')", 'css'),
        ('efectos', '--shadow-elegant', '0 8px 32px rgba(212, 175, 55, 0.2)', 'css')
    ]
    
    for categoria, propiedad, valor, tipo in propiedades:
        prop = PropiedadTema(
            tema_id=tema.id,
            categoria=categoria,
            propiedad=propiedad,
            valor=valor,
            tipo=tipo
        )
        db.add(prop)
    
    db.commit()
    print('✅ Propiedades agregadas al tema Café Clásico')
    print(f'   - {len(propiedades)} propiedades configuradas')
    db.close()

if __name__ == "__main__":
    agregar_propiedades_tema()