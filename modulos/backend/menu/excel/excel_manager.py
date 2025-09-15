"""
Generador de Plantillas Excel para Sistema Eterials
"""
import pandas as pd
import os
import tempfile
import uuid
from typing import Dict, List, Optional

class ExcelProductManager:
    def __init__(self):
        """Inicializar el generador de plantillas"""
        pass
    
    def generar_plantilla_excel(self, nombre_archivo: str = "plantilla_productos.xlsx") -> str:
        """
        Genera plantilla Excel para productos normales basada en la estructura de la BD
        """
        try:
            # Crear archivo en directorio temporal
            temp_dir = tempfile.gettempdir()
            archivo_completo = os.path.join(temp_dir, nombre_archivo)
            
            # Columnas basicas
            columnas = [
                'nombre',
                'precio', 
                'descripcion',
                'categoria',
                'disponible',
                'imagen_url',
                'tiempo_preparacion'
            ]
            
            # Datos de ejemplo
            datos_ejemplo = [
                [
                    'Cappuccino Artesanal',
                    '8500',
                    'Delicioso cappuccino con granos colombianos',
                    'Bebidas Calientes',
                    'Si',
                    '',
                    '5-7 minutos'
                ]
            ]
            
            # Crear DataFrame
            df = pd.DataFrame(datos_ejemplo, columns=columnas)
            
            # Guardar archivo Excel
            df.to_excel(archivo_completo, index=False, engine='xlsxwriter')
            
            print(f"Plantilla generada: {archivo_completo}")
            return archivo_completo
            
        except Exception as e:
            print(f"Error generando plantilla: {str(e)}")
            raise e
    
    def procesar_archivo_excel(self, ruta_archivo: str) -> Dict:
        """
        Procesa un archivo Excel segun el tipo de plantilla
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(ruta_archivo, sheet_name=0)
            
            productos = []
            errores = []
            
            for index, fila in df.iterrows():
                try:
                    # Validar campos requeridos
                    if pd.isna(fila.get('nombre')) or not str(fila.get('nombre')).strip():
                        errores.append(f"Fila {index + 2}: Nombre es requerido")
                        continue
                        
                    if pd.isna(fila.get('precio')):
                        errores.append(f"Fila {index + 2}: Precio es requerido")
                        continue
                        
                    if pd.isna(fila.get('categoria')) or not str(fila.get('categoria')).strip():
                        errores.append(f"Fila {index + 2}: Categoria es requerida")
                        continue
                    
                    # Crear producto basico
                    producto = {
                        'id': str(uuid.uuid4()),
                        'nombre': str(fila.get('nombre', '')).strip(),
                        'precio': float(str(fila.get('precio', 0)).replace(',', '.')),
                        'descripcion': str(fila.get('descripcion', '')).strip(),
                        'categoria': str(fila.get('categoria', '')).strip(),
                        'disponible': str(fila.get('disponible', 'Si')).lower() in ['si', 'true', '1', 'yes'],
                        'imagen_url': str(fila.get('imagen_url', '')).strip(),
                        'tiempo_preparacion': str(fila.get('tiempo_preparacion', '')).strip()
                    }
                    
                    productos.append(producto)
                    
                except Exception as e:
                    errores.append(f"Fila {index + 2}: Error - {str(e)}")
                    continue
            
            return {
                'productos': productos,
                'errores': errores,
                'total_procesados': len(productos) + len(errores)
            }
            
        except Exception as e:
            return {
                'productos': [],
                'errores': [f"Error al leer archivo: {str(e)}"],
                'total_procesados': 0
            }

# Crear instancia global para compatibilidad
excel_manager = ExcelProductManager()

# Funciones compatibles con el codigo existente
def generar_plantilla_excel(nombre_archivo: str = "plantilla_productos.xlsx") -> str:
    """Funcion de compatibilidad para productos"""
    return excel_manager.generar_plantilla_excel(nombre_archivo)