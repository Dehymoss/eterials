from flask import Blueprint, render_template, send_from_directory
from modulos.backend.chatbot.models import ConfiguracionChatbot, FondoPersonalizado
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# Solo definimos el blueprint, no una nueva app Flask
chatbot_bp = Blueprint(
    'chatbot',
    __name__,
    template_folder='../frontend/chatbot/templates',
    static_folder='../frontend/chatbot/static'  # Corregido: apuntar al directorio correcto
)

def get_db_session():
    """Obtener sesión de base de datos"""
    engine = create_engine('sqlite:///modulos/backend/menu/menu.db')
    Session = sessionmaker(bind=engine)
    return Session()

@chatbot_bp.route('/')
def chatbot():
    # CARGAR CONFIGURACIÓN ACTUAL DE LA BASE DE DATOS
    try:
        db = get_db_session()
        
        # Buscar configuración de fondo simplificada
        fondo_css = ""
        
        # Buscar configuración por clave-valor
        config_tipo = db.query(ConfiguracionChatbot).filter_by(clave='fondo_tipo').first()
        config_valor = db.query(ConfiguracionChatbot).filter_by(clave='fondo_valor').first()
        
        if config_tipo and config_valor:
            if config_tipo.valor == 'color':
                fondo_css = f"background-color: {config_valor.valor} !important; background-image: none !important;"
                    
            elif config_tipo.valor == 'imagen':
                # Convertir ID a URL de archivo estático
                try:
                    import os
                    import glob
                    
                    # Obtener lista de archivos disponibles
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    fondos_path = os.path.join(project_root, 'modulos', 'chatbot', 'static', 'fondos')
                    
                    # ✅ SOPORTE COMPLETO PARA TODOS LOS TIPOS DE IMAGEN
                    extensiones_soportadas = ['*.svg', '*.png', '*.jpg', '*.jpeg', '*.webp', '*.gif', '*.bmp']
                    archivos_imagen = []
                    for extension in extensiones_soportadas:
                        patron = os.path.join(fondos_path, extension)
                        archivos_encontrados = glob.glob(patron)
                        # También buscar versiones en mayúsculas
                        patron_upper = os.path.join(fondos_path, extension.upper())
                        archivos_encontrados.extend(glob.glob(patron_upper))
                        archivos_imagen.extend(archivos_encontrados)
                    
                    # Eliminar duplicados y ordenar archivos para consistencia
                    archivos_imagen = list(set(archivos_imagen))
                    archivos_imagen.sort()
                    
                    # Verificar si hay fondos disponibles
                    if not archivos_imagen:
                        print("📁 Carpeta de fondos vacía - Usando fondo negro por defecto")
                        fondo_css = "background-color: #000000;"
                    else:
                        # Convertir ID a archivo
                        fondo_id = int(config_valor.valor)
                        if 1 <= fondo_id <= len(archivos_imagen):
                            archivo_path = archivos_imagen[fondo_id - 1]
                            nombre_archivo = os.path.basename(archivo_path) 
                            fondo_url = f"/chatbot/static/fondos/{nombre_archivo}"
                            fondo_css = f"background-image: url('{fondo_url}'); background-size: cover; background-position: center; background-attachment: fixed;"
                            print(f"✅ Fondo aplicado: {nombre_archivo}")
                        else:
                            print(f"⚠️ ID de fondo fuera de rango: {fondo_id} - Usando fondo negro por defecto")
                            fondo_css = "background-color: #000000;"
                        
                except (ValueError, TypeError, IndexError) as e:
                    print(f"⚠️ Error aplicando fondo: {e} - Usando fondo negro por defecto")
                    fondo_css = "background-color: #000000;"
        
        db.close()
        
        # Si no se configuró ningún fondo, usar negro por defecto
        if not fondo_css:
            print("🖤 Sin configuración de fondo - Usando fondo negro por defecto")
            fondo_css = "background-color: #000000;"
        
        return render_template('chatbot.html.j2', 
                             fondo_css=fondo_css)
    except Exception as e:
        print(f"Error cargando configuración: {e}")
        return render_template('chatbot.html.j2', 
                             fondo_css="")

@chatbot_bp.route('/static/fondos/<filename>')
def serve_fondo(filename):
    """Servir archivos de fondos desde la ubicación correcta"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        fondos_path = os.path.join(project_root, 'modulos', 'chatbot', 'static', 'fondos')
        print(f"🖼️ Sirviendo fondo: {filename} desde {fondos_path}")
        return send_from_directory(fondos_path, filename)
    except Exception as e:
        print(f"❌ Error sirviendo fondo {filename}: {e}")
        return "Archivo no encontrado", 404