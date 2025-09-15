"""
Generador DINÁMICO de plantilla de ingredientes
Solo se ejecuta si hay productos tipo 'preparado' en la BD
"""
import pandas as pd
import os
import tempfile
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from modulos.backend.menu.database.models.producto import Producto

class GeneradorIngredientes:
    def __init__(self):
        # Configurar BD
        DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend', 'menu', 'menu.db')
        self.engine = create_engine(f'sqlite:///{DB_PATH}')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def obtener_productos_preparados(self):
        """Obtiene productos tipo 'preparado' de la BD"""
        return self.session.query(Producto).filter(
            Producto.tipo_producto == 'preparado',
            Producto.activo == True
        ).all()
    
    def generar_plantilla_ingredientes(self, nombre_archivo: str = "plantilla_ingredientes.xlsx") -> str:
        """
        Genera plantilla de ingredientes SOLO si hay productos preparados
        """
        try:
            # Verificar si hay productos preparados
            productos_preparados = self.obtener_productos_preparados()
            
            if not productos_preparados:
                raise Exception("No hay productos tipo 'preparado' en la base de datos. Primero carga productos con tipo_producto='preparado'")
            
            # Crear archivo temporal
            temp_dir = tempfile.gettempdir()
            archivo_completo = os.path.join(temp_dir, nombre_archivo)
            
            # Columnas para ingredientes
            columnas = [
                'producto_id',
                'producto_nombre',
                'ingrediente_nombre',
                'cantidad',
                'unidad_medida',
                'costo',
                'obligatorio'
            ]
            
            # Generar filas ejemplo para cada producto preparado
            datos_ejemplo = []
            for producto in productos_preparados:
                datos_ejemplo.append([
                    producto.id,
                    producto.nombre,
                    'Harina de trigo',  # Ejemplo ingrediente
                    500.0,
                    'gr',
                    1200.0,
                    True
                ])
                datos_ejemplo.append([
                    producto.id,
                    producto.nombre,
                    'Queso mozzarella',  # Ejemplo ingrediente 2
                    200.0,
                    'gr',
                    3500.0,
                    True
                ])
            
            # Crear DataFrame
            df = pd.DataFrame(datos_ejemplo, columns=columnas)
            
            # Guardar en Excel
            with pd.ExcelWriter(archivo_completo, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Ingredientes', index=False)
                
                # Formato
                workbook = writer.book
                worksheet = writer.sheets['Ingredientes']
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#FFE4B5',
                    'border': 1
                })
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    
                worksheet.set_column('A:G', 18)
            
            return archivo_completo
            
        except Exception as e:
            raise Exception(f"Error al generar plantilla ingredientes: {str(e)}")
        finally:
            self.session.close()

# Función standalone
def generar_plantilla_ingredientes(nombre_archivo=None):
    if nombre_archivo is None:
        carpeta_destino = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'plantillas')
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
        nombre_archivo = os.path.join(carpeta_destino, 'plantilla_ingredientes.xlsx')
    
    generador = GeneradorIngredientes()
    return generador.generar_plantilla_ingredientes(nombre_archivo)