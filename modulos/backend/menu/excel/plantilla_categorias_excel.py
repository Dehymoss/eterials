import pandas as pd
import xlsxwriter

# Plantilla de categorías y subcategorías
CATEGORIA_COLUMNS = [
    'id', 'titulo', 'descripcion', 'icono', 'orden', 'activa'
]
SUBCATEGORIA_COLUMNS = [
    'id', 'nombre', 'descripcion', 'categoria_id', 'tipo', 'activa'
]

# Ejemplo de datos para facilitar edición
CATEGORIA_EJEMPLO = [
    ['1', 'Pizzas', 'Categoría de pizzas artesanales', '🍕', 1, True]
]
SUBCATEGORIA_EJEMPLO = [
    ['1', 'Pizza Margarita', 'Pizza tradicional italiana', '1', 'producto', True]
]

def generar_plantilla_categorias(nombre_archivo=None):
    import os
    import tempfile
    
    # Si no se especifica archivo, usar directorio temporal
    if nombre_archivo is None:
        carpeta_destino = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'plantillas')
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
        nombre_archivo = os.path.join(carpeta_destino, 'plantilla_categorias.xlsx')
    
    # Generar DataFrames con ejemplos y columnas
    df_cat = pd.DataFrame(CATEGORIA_EJEMPLO, columns=CATEGORIA_COLUMNS)
    df_subcat = pd.DataFrame(SUBCATEGORIA_EJEMPLO, columns=SUBCATEGORIA_COLUMNS)
    
    with pd.ExcelWriter(nombre_archivo, engine='xlsxwriter') as writer:
        df_cat.to_excel(writer, sheet_name='Categorias', index=False)
        df_subcat.to_excel(writer, sheet_name='Subcategorias', index=False)
    
    print(f'✅ Plantilla de categorías y subcategorías generada: {nombre_archivo}')
    return nombre_archivo

def main():
    generar_plantilla_categorias()

if __name__ == "__main__":
    main()
