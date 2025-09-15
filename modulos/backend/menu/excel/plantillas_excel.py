import pandas as pd

import pandas as pd

# Plantilla PRODUCTOS - Actualizada con TODOS los campos de la BD (27/08/2025)
PRODUCTOS_COLUMNS = [
    'id', 'codigo', 'nombre', 'descripcion', 'precio', 
    'categoria_id', 'categoria_nombre', 'subcategoria_id', 'subcategoria_nombre',
    'imagen_url', 'tiempo_preparacion', 'instrucciones_preparacion', 'notas_cocina',
    'disponible', 'activo', 'tipo_producto', 'fecha_creacion', 'fecha_actualizacion'
]

# Plantilla CATEGORÍAS - Actualizada con TODOS los campos de la BD (27/08/2025)
CATEGORIAS_COLUMNS = [
    'id', 'codigo', 'titulo', 'descripcion', 'icono', 'orden', 'activa'
]

# Plantilla SUBCATEGORÍAS - Actualizada con TODOS los campos de la BD (27/08/2025)
SUBCATEGORIAS_COLUMNS = [
    'id', 'codigo', 'nombre', 'descripcion', 'categoria_id', 'categoria_nombre', 'tipo', 'activa'
]

# Plantilla INGREDIENTES - Actualizada con TODOS los campos de la BD (27/08/2025)
INGREDIENTES_COLUMNS = [
    'id', 'codigo', 'producto_id', 'producto_nombre', 'nombre', 'cantidad', 'unidad', 'costo', 'obligatorio', 'activo'
]

# Plantilla avanzada de recetas con ingredientes (actualizada 27/08/2025)
ADVANCED_COLUMNS = [
    'id', 'codigo', 'nombre', 'descripcion', 'precio', 'categoria', 'subcategoria',
    'tipo_producto', 'tiempo_preparacion', 'instrucciones_preparacion', 'notas_cocina',
    'ingrediente_1', 'cantidad_1', 'unidad_1',
    'ingrediente_2', 'cantidad_2', 'unidad_2',
    'ingrediente_3', 'cantidad_3', 'unidad_3',
    'ingrediente_4', 'cantidad_4', 'unidad_4',
    'ingrediente_5', 'cantidad_5', 'unidad_5',
    'ingrediente_6', 'cantidad_6', 'unidad_6',
    'imagen_url', 'disponible', 'activo'
]

def generar_plantilla_productos(nombre_archivo='plantilla_productos_completa.xlsx'):
    """Genera plantilla completa para productos con TODOS los campos de BD"""
    # Crear DataFrame con ejemplos
    data = [
        {
            'id': '',  # Se asigna automáticamente
            'codigo': 'BEBCOC001',  # Ejemplo de código automático
            'nombre': 'Coca Cola 355ml',
            'descripcion': 'Bebida gaseosa refrescante',
            'precio': 2.50,
            'categoria_id': 1,  # ID de categoría Bebidas
            'categoria_nombre': 'Bebidas',  # Solo referencia
            'subcategoria_id': 1,  # ID de subcategoría
            'subcategoria_nombre': 'Gaseosas',  # Solo referencia
            'imagen_url': 'https://ejemplo.com/coca-cola.jpg',
            'tiempo_preparacion': '',
            'instrucciones_preparacion': '',
            'notas_cocina': '',
            'disponible': True,
            'activo': True,
            'tipo_producto': 'simple',
            'fecha_creacion': '',  # Se asigna automáticamente
            'fecha_actualizacion': ''  # Se asigna automáticamente
        },
        {
            'id': '',
            'codigo': 'PIZMAR001',
            'nombre': 'Pizza Margherita',
            'descripcion': 'Pizza clásica italiana con tomate, mozzarella y albahaca',
            'precio': 15.99,
            'categoria_id': 2,  # ID de categoría Platos Principales
            'categoria_nombre': 'Platos Principales',
            'subcategoria_id': 2,  # ID de subcategoría Pizzas
            'subcategoria_nombre': 'Pizzas',
            'imagen_url': 'https://ejemplo.com/pizza-margherita.jpg',
            'tiempo_preparacion': '25 minutos',
            'instrucciones_preparacion': '1. Extender la masa\n2. Aplicar salsa de tomate\n3. Agregar mozzarella\n4. Hornear a 220°C por 12-15 min\n5. Agregar albahaca fresca',
            'notas_cocina': 'Precalentar horno 10 min antes. Masa debe estar a temperatura ambiente.',
            'disponible': True,
            'activo': True,
            'tipo_producto': 'preparado',
            'fecha_creacion': '',
            'fecha_actualizacion': ''
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(nombre_archivo, index=False)
    print(f'✅ Plantilla completa de productos generada: {nombre_archivo}')

def generar_plantilla_categorias(nombre_archivo='plantilla_categorias_completa.xlsx'):
    """Genera plantilla completa para categorías con TODOS los campos de BD"""
    data = [
        {
            'id': '',  # Se asigna automáticamente
            'codigo': 'CATBEB001',  # Ejemplo de código automático
            'titulo': 'Bebidas',
            'descripcion': 'Toda clase de bebidas: alcohólicas, sin alcohol, calientes, frías',
            'icono': '🥤',
            'orden': 1,
            'activa': True
        },
        {
            'id': '',
            'codigo': 'CATPLA001',
            'titulo': 'Platos Principales',
            'descripcion': 'Platos principales del menú: pizzas, pastas, carnes, pescados',
            'icono': '🍽️',
            'orden': 2,
            'activa': True
        },
        {
            'id': '',
            'codigo': 'CATPOS001',
            'titulo': 'Postres',
            'descripcion': 'Postres y dulces para finalizar la comida',
            'icono': '🍰',
            'orden': 3,
            'activa': True
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(nombre_archivo, index=False)
    print(f'✅ Plantilla completa de categorías generada: {nombre_archivo}')

def generar_plantilla_subcategorias(nombre_archivo='plantilla_subcategorias_completa.xlsx'):
    """Genera plantilla completa para subcategorías con TODOS los campos de BD"""
    data = [
        {
            'id': '',  # Se asigna automáticamente
            'codigo': 'SUBGAS001',  # Ejemplo de código automático
            'nombre': 'Gaseosas',
            'descripcion': 'Bebidas gaseosas y refrescos',
            'categoria_id': 1,  # ID de categoría Bebidas
            'categoria_nombre': 'Bebidas',  # Solo referencia
            'tipo': 'sin_alcohol',
            'activa': True
        },
        {
            'id': '',
            'codigo': 'SUBPIZ001',
            'nombre': 'Pizzas',
            'descripcion': 'Pizzas artesanales y clásicas',
            'categoria_id': 2,  # ID de categoría Platos Principales
            'categoria_nombre': 'Platos Principales',
            'tipo': 'plato_principal',
            'activa': True
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(nombre_archivo, index=False)
    print(f'✅ Plantilla completa de subcategorías generada: {nombre_archivo}')

def generar_plantilla_ingredientes(nombre_archivo='plantilla_ingredientes_completa.xlsx'):
    """Genera plantilla completa para ingredientes con TODOS los campos de BD"""
    data = [
        {
            'id': '',  # Se asigna automáticamente
            'codigo': 'INGTOM001',  # Ejemplo de código automático
            'producto_id': 2,  # ID del producto Pizza Margherita
            'producto_nombre': 'Pizza Margherita',  # Solo referencia
            'nombre': 'Tomate',
            'cantidad': '200',
            'unidad': 'g',
            'costo': 1.50,
            'obligatorio': True,
            'activo': True
        },
        {
            'id': '',
            'codigo': 'INGMOZ001',
            'producto_id': 2,
            'producto_nombre': 'Pizza Margherita',
            'nombre': 'Queso mozzarella',
            'cantidad': '150',
            'unidad': 'g',
            'costo': 3.00,
            'obligatorio': True,
            'activo': True
        },
        {
            'id': '',
            'codigo': 'INGALB001',
            'producto_id': 2,
            'producto_nombre': 'Pizza Margherita',
            'nombre': 'Albahaca fresca',
            'cantidad': '5',
            'unidad': 'hojas',
            'costo': 0.50,
            'obligatorio': False,
            'activo': True
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(nombre_archivo, index=False)
    print(f'✅ Plantilla completa de ingredientes generada: {nombre_archivo}')

def generar_todas_las_plantillas():
    """Genera todas las plantillas de Excel actualizadas"""
    print("🏭 Generando plantillas Excel actualizadas...")
    generar_plantilla_productos()
    generar_plantilla_categorias()
    generar_plantilla_subcategorias()
    generar_plantilla_ingredientes()
    print("🎉 ¡Todas las plantillas generadas exitosamente!")

# Funciones de compatibilidad con código anterior
def generar_plantilla_basica(nombre_archivo='plantilla_productos_basica.xlsx'):
    """Función de compatibilidad - redirige a plantilla completa"""
    return generar_plantilla_productos(nombre_archivo)

def generar_plantilla_avanzada(nombre_archivo='plantilla_recetas_completas.xlsx'):
    """Función de compatibilidad - redirige a plantilla completa"""
    return generar_plantilla_productos(nombre_archivo)
