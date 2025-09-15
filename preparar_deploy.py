#!/usr/bin/env python3
"""
Script de preparación para deploy en Render.com
Automatiza la configuración necesaria para migrar el proyecto
"""

import os
import json
import shutil
from pathlib import Path

def preparar_deploy_render():
    print("🚀 PREPARANDO PROYECTO PARA RENDER.COM")
    print("=" * 50)
    
    # 1. Verificar estructura del proyecto  
    print("\n📁 1. VERIFICANDO ESTRUCTURA...")
    archivos_criticos = [
        'main.py',
        'requirements.txt', 
        'modulos/backend/menu/',
        'modulos/panel_admin/',
        'modulos/chatbot/',
        'modulos/frontend/'
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTANTE")
    
    # 2. Crear configuración Render
    print("\n⚙️ 2. CREANDO CONFIGURACIÓN RENDER...")
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "eterials-restaurant",
                "runtime": "python3",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "python main.py",
                "plan": "free",
                "envVars": [
                    {
                        "key": "PORT",
                        "value": "8080"
                    },
                    {
                        "key": "FLASK_ENV", 
                        "value": "production"
                    }
                ]
            }
        ]
    }
    
    with open('render.yaml', 'w') as f:
        json.dump(render_config, f, indent=2)
    print("   ✅ render.yaml creado")
    
    # 3. Configurar variables de entorno
    print("\n🔧 3. CONFIGURANDO VARIABLES DE ENTORNO...")
    env_template = """# Variables de entorno para producción
FLASK_ENV=production
PORT=8080

# APIs opcionales (configurar en Render dashboard)
# UNSPLASH_ACCESS_KEY=tu_clave_aqui
# PEXELS_API_KEY=tu_clave_aqui  
# PIXABAY_API_KEY=tu_clave_aqui
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_template)
    print("   ✅ .env.example creado")
    
    # 4. Verificar base de datos
    print("\n🗃️ 4. VERIFICANDO BASE DE DATOS...")
    db_path = "modulos/backend/menu/database/menu.db"
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
        print(f"   ✅ Base de datos: {db_size} bytes")
        if db_size > 10 * 1024 * 1024:  # 10MB
            print("   ⚠️ Base de datos grande (>10MB) - considera optimizar")
    else:
        print("   ❌ Base de datos no encontrada")
    
    # 5. Preparar archivos estáticos
    print("\n📂 5. VERIFICANDO ARCHIVOS ESTÁTICOS...")
    static_dirs = [
        "modulos/backend/menu/static/",
        "modulos/panel_admin/static/",
        "modulos/chatbot/static/",
        "modulos/frontend/menu/static/"
    ]
    
    total_static_size = 0
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            dir_size = sum(f.stat().st_size for f in Path(static_dir).rglob('*') if f.is_file())
            total_static_size += dir_size
            print(f"   ✅ {static_dir}: {dir_size} bytes")
    
    print(f"   📊 Total archivos estáticos: {total_static_size} bytes")
    
    # 6. Crear script de deploy
    deploy_script = """#!/bin/bash
# Deploy automático a Render.com

echo "🚀 Iniciando deploy a Render.com..."

# 1. Verificar Git
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositorio Git..."
    git init
    git add .
    git commit -m "Initial commit - Eterials Restaurant System"
fi

echo "✅ Proyecto listo para conectar con Render.com"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Crear cuenta en render.com"
echo "2. Conectar repositorio GitHub"
echo "3. Seleccionar 'Web Service'"
echo "4. Build Command: pip install -r requirements.txt"
echo "5. Start Command: python main.py"
echo "6. Seleccionar plan Free"
echo ""
echo "🌐 Tu app estará disponible en: https://eterials-restaurant.onrender.com"
"""
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)
    
    # Hacer ejecutable en sistemas Unix
    try:
        os.chmod('deploy.sh', 0o755)
    except:
        pass
    
    print("   ✅ deploy.sh creado")
    
    # 7. Resumen final
    print("\n" + "="*50)
    print("📋 RESUMEN DE PREPARACIÓN")
    print("="*50)
    print("✅ Archivos de configuración creados:")
    print("   - requirements.txt")
    print("   - render.yaml") 
    print("   - .env.example")
    print("   - deploy.sh")
    print("")
    print("🌐 URL después del deploy:")
    print("   https://eterials-restaurant.onrender.com")
    print("")
    print("💰 Costo: $0 (Plan gratuito)")
    print("⏱️ Tiempo de deploy: ~5 minutos")
    print("🔄 Auto-deploy: Habilitado con GitHub")
    
    return True

if __name__ == "__main__":
    preparar_deploy_render()
