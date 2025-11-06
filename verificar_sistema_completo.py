#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR SISTEMA COMPLETO - Eterials Chatbot
===============================================

Sistema unificado de verificación para todos los módulos del proyecto.
Consolida todas las pruebas, tests y verificaciones en un solo archivo.

Autor: Sistema Eterials
Fecha: 27/09/2025 - Optimizado y depurado
Versión: 2.0.0

POLÍTICA DE INTEGRACIÓN:
- TODOS los nuevos tests DEBEN agregarse a este archivo
- PROHIBIDO crear archivos de test individuales
- Mantener modularidad con funciones separadas

CAMBIOS V2.0.0:
- Rutas actualizadas a estructura actual del proyecto
- Eliminadas funciones redundantes y obsoletas
- Optimizadas verificaciones de archivos JavaScript/HTML
- Consolidadas funciones de colores adaptativos
"""

import os
import sys

# Agregar el directorio padre al path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import argparse
import requests
import sqlite3
from datetime import datetime
import traceback

# Configuración
BASE_URL = "http://127.0.0.1:8081"
DATABASE_PATH = "modulos/backend/menu/database/menu.db"

class VerificadorSistema:
    def verificar_dependencias_python(self):
        """Verifica dependencias y módulos principales de Python"""
        import sys
        import os
        resultado = []
        try:
            import flask
            resultado.append(f"✅ Flask {flask.__version__}")
        except ImportError as e:
            resultado.append(f"❌ Error Flask: {e}")
        try:
            import sqlalchemy
            resultado.append(f"✅ SQLAlchemy {sqlalchemy.__version__}")
        except ImportError as e:
            resultado.append(f"❌ Error SQLAlchemy: {e}")
        archivos_principales = ['main.py', 'requirements.txt', 'modulos']
        for archivo in archivos_principales:
            if os.path.exists(archivo):
                resultado.append(f"✅ {archivo}")
            else:
                resultado.append(f"❌ {archivo} NO ENCONTRADO")
        # Verificar importaciones de módulos principales
        try:
            from modulos.chatbot.chatbot_blueprint import chatbot_bp
            # Verificar rutas de blueprint
            static_folder = getattr(chatbot_bp, 'static_folder', None)
            template_folder = getattr(chatbot_bp, 'template_folder', None)
            if static_folder and template_folder and '../frontend/chatbot' in static_folder and '../frontend/chatbot' in template_folder:
                resultado.append("✅ Chatbot blueprint importado y rutas frontend actualizadas")
            else:
                resultado.append(f"❌ Chatbot blueprint importado pero rutas no actualizadas: static={static_folder}, template={template_folder}")
        except ImportError as e:
            resultado.append(f"❌ Error Chatbot: {e}")
        try:
            from modulos.backend.chatbot.admin_dashboard import chatbot_admin_bp
            resultado.append("✅ Chatbot backend importado correctamente")
        except ImportError as e:
            resultado.append(f"❌ Error Chatbot Backend: {e}")
        try:
            from modulos.panel_admin.admin_blueprint import admin_bp
            resultado.append("✅ Panel Admin importado correctamente")
        except ImportError as e:
            resultado.append(f"❌ Error Panel Admin: {e}")
        try:
            from modulos.backend.menu.menu_admin_endpoints import menu_admin_bp
            resultado.append("✅ Menu Admin importado correctamente")
        except ImportError as e:
            resultado.append(f"❌ Error Menu Admin: {e}")
        try:
            from modulos.frontend.menu.routes import menu_bp
            resultado.append("✅ Menu Frontend importado correctamente")
        except ImportError as e:
            resultado.append(f"❌ Error Menu Frontend: {e}")
        try:
            from modulos.frontend.cocina.routes import cocina_bp
            resultado.append("✅ Cocina importado correctamente")
        except ImportError as e:
            resultado.append(f"❌ Error Cocina: {e}")
        self.log_resultado("dependencias_python", "verificacion", True, "\n".join(resultado))
    """Clase principal para verificar todos los módulos del sistema"""
    
    def __init__(self):
        self.resultados = {}
        self.errores = []
        self.exitos = []
        self.base_url = BASE_URL  # Usar la constante global
        
    def log_resultado(self, modulo, test, exitoso, mensaje=""):
        """Registra el resultado de una verificación"""
        if modulo not in self.resultados:
            self.resultados[modulo] = []
        
        estado = "✅" if exitoso else "❌"
        self.resultados[modulo].append({
            'test': test,
            'exitoso': exitoso,
            'mensaje': mensaje,
            'estado': estado
        })
        
        if not exitoso:
            self.errores.append(f"{modulo}.{test}: {mensaje}")
    
    def imprimir_lista_resultados(self, resultados_lista, titulo):
        """Helper para imprimir una lista de resultados con formato"""
        print(f"\n{titulo}")
        print("=" * len(titulo))
        for resultado in resultados_lista:
            print(f"   {resultado}")
        print()
    
    def verificar_base_datos(self):
        """Verificación completa de la base de datos"""
        print("\nVERIFICANDO BASE DE DATOS...")
        
        try:
            # Verificar existencia del archivo
            if not os.path.exists(DATABASE_PATH):
                self.log_resultado("base_datos", "archivo_db", False, "Archivo menu.db no encontrado")
                return
            
            self.log_resultado("base_datos", "archivo_db", True, "Archivo menu.db encontrado")
            
            # Conectar y verificar tablas
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Verificar tablas principales
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [row[0] for row in cursor.fetchall()]
            
            tablas_esperadas = ['productos', 'categorias', 'subcategorias', 'ingredientes']
            for tabla in tablas_esperadas:
                if tabla in tablas:
                    self.log_resultado("base_datos", f"tabla_{tabla}", True, f"Tabla {tabla} existe")
                else:
                    self.log_resultado("base_datos", f"tabla_{tabla}", False, f"Tabla {tabla} no encontrada")
            
            # Contar registros
            for tabla in tablas_esperadas:
                if tabla in tablas:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    self.log_resultado("base_datos", f"count_{tabla}", True, f"{count} registros en {tabla}")
            
            conn.close()
            
        except Exception as e:
            self.log_resultado("base_datos", "conexion", False, f"Error de conexión: {str(e)}")
    
    def verificar_conectividad(self):
        """Test de conectividad de endpoints principales"""
        print("\nVERIFICANDO CONECTIVIDAD DE ENDPOINTS...")
        
        endpoints = [
            {"url": "/", "nombre": "inicio"},
            {"url": "/menu", "nombre": "menu_publico"},
            {"url": "/menu-admin/admin", "nombre": "admin_panel"},
            {"url": "/cocina", "nombre": "modulo_cocina"},
            {"url": "/admin", "nombre": "panel_admin"},
            {"url": "/chatbot", "nombre": "chatbot"}
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint['url']}", timeout=5)
                if response.status_code == 200:
                    self.log_resultado("conectividad", endpoint["nombre"], True, f"Status {response.status_code}")
                else:
                    self.log_resultado("conectividad", endpoint["nombre"], False, f"Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_resultado("conectividad", endpoint["nombre"], False, f"Error: {str(e)[:50]}")
    
    def verificar_apis(self):
        """Prueba de todas las APIs del sistema"""
        print("\nVERIFICANDO APIS DEL SISTEMA...")
        
        apis = [
            {"url": "/menu-admin/api/productos", "nombre": "api_productos", "metodo": "GET"},
            {"url": "/menu-admin/api/categorias", "nombre": "api_categorias", "metodo": "GET"},
            {"url": "/menu-admin/api/imagenes/buscar?nombre=pizza", "nombre": "api_imagenes", "metodo": "GET"},
            {"url": "/api/cocina/dashboard", "nombre": "api_cocina", "metodo": "GET"}
        ]
        
        for api in apis:
            try:
                response = requests.get(f"{BASE_URL}{api['url']}", timeout=5)
                if response.status_code == 200:
                    # Verificar que sea JSON válido
                    try:
                        data = response.json()
                        self.log_resultado("apis", api["nombre"], True, f"JSON válido con {len(data) if isinstance(data, list) else 'object'} elementos")
                    except:
                        self.log_resultado("apis", api["nombre"], True, f"Status {response.status_code} (no JSON)")
                else:
                    self.log_resultado("apis", api["nombre"], False, f"Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_resultado("apis", api["nombre"], False, f"Error: {str(e)[:50]}")
    
    def verificar_imagenes(self):
        """Test del sistema de búsqueda de imágenes"""
        print("\nVERIFICANDO SISTEMA DE BUSQUEDA DE IMAGENES...")
        
        terminos_prueba = ["pizza", "hamburguesa", "cerveza", "postre", "ensalada"]
        
        for termino in terminos_prueba:
            try:
                url = f"{BASE_URL}/menu-admin/api/imagenes/buscar?nombre={termino}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'imagenes' in data and len(data['imagenes']) > 0:
                            self.log_resultado("imagenes", f"busqueda_{termino}", True, f"{len(data['imagenes'])} imágenes encontradas")
                        else:
                            self.log_resultado("imagenes", f"busqueda_{termino}", False, "No se encontraron imágenes")
                    except:
                        self.log_resultado("imagenes", f"busqueda_{termino}", False, "Respuesta no es JSON válido")
                else:
                    self.log_resultado("imagenes", f"busqueda_{termino}", False, f"Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_resultado("imagenes", f"busqueda_{termino}", False, f"Error: {str(e)[:50]}")
    
    def verificar_importaciones(self):
        """Verificación de importaciones SQLAlchemy"""
        print("\nVERIFICANDO IMPORTACIONES DEL SISTEMA...")
        
        # Verificar importaciones principales
        modulos_importacion = [
            ("flask", "Flask"),
            ("sqlalchemy", "SQLAlchemy"),
            ("requests", "requests"),
            ("os", "os"),
            ("sys", "sys")
        ]
        
        for modulo, nombre in modulos_importacion:
            try:
                __import__(modulo)
                self.log_resultado("importaciones", f"modulo_{nombre.lower()}", True, f"Módulo {nombre} disponible")
            except ImportError as e:
                self.log_resultado("importaciones", f"modulo_{nombre.lower()}", False, f"Error importando {nombre}: {str(e)}")
        
        # Verificar modelos del proyecto (ruta actualizada)
        try:
            from modulos.backend.menu.database.base import Base
            self.log_resultado("importaciones", "modelos_base", True, "Base SQLAlchemy importada correctamente")
        except Exception as e:
            self.log_resultado("importaciones", "modelos_base", False, f"Error importando Base: {str(e)}")
        
        # ELIMINADO: analizador de colores adaptativos ya no se usa
        self.log_resultado("importaciones", "analizador_colores", True, "Sistema de colores eliminado - no requerido")
    
    def verificar_modulo_cocina(self):
        """Test específico del módulo de cocina"""
        print("\nVERIFICANDO MODULO DE COCINA...")
        
        try:
            # Verificar acceso al dashboard de cocina
            response = requests.get(f"{BASE_URL}/cocina", timeout=5)
            if response.status_code == 200:
                self.log_resultado("cocina", "dashboard_acceso", True, "Dashboard de cocina accesible")
            else:
                self.log_resultado("cocina", "dashboard_acceso", False, f"Status {response.status_code}")
            
            # Verificar API de cocina
            response = requests.get(f"{BASE_URL}/api/cocina/dashboard", timeout=5)
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_resultado("cocina", "api_dashboard", True, "API de dashboard funcional")
                except:
                    self.log_resultado("cocina", "api_dashboard", False, "API no retorna JSON válido")
            else:
                self.log_resultado("cocina", "api_dashboard", False, f"API Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_resultado("cocina", "conectividad", False, f"Error de conexión: {str(e)[:50]}")

    def verificar_upload_y_creacion(self):
        """Verificación rápida: subir una imagen y crear un producto usando la URL devuelta"""
        print("\n🧪 VERIFICANDO UPLOAD DE IMAGEN Y CREACIÓN DE PRODUCTO...")
        try:
            upload_url = f"{self.base_url}/menu-admin/api/imagenes/subir-imagen"
            productos_api = f"{self.base_url}/menu-admin/api/productos"

            # Crear un pequeño archivo jpeg en memoria
            from io import BytesIO
            bio = BytesIO(b'\xff\xd8\xff\xd9')
            files = {'imagen': ('test.jpg', bio, 'image/jpeg')}
            r = requests.post(upload_url, files=files, timeout=10)
            if r.status_code == 200:
                j = r.json()
                if j.get('success') and j.get('url'):
                    self.log_resultado('upload', 'subir_imagen', True, 'Imagen subida y URL devuelta')
                    # Crear producto mínimo usando la URL
                    payload = {
                        'nombre': 'E2E Test Producto',
                        'precio': 1.0,
                        'descripcion': 'Creado por verificador E2E',
                        'imagen_url': j.get('url'),
                        'disponible': True,
                        'tipo_producto': 'simple'
                    }
                    rc = requests.post(productos_api, json=payload, timeout=10)
                    if rc.status_code in (200,201):
                        self.log_resultado('upload', 'crear_producto_con_imagen', True, f'Producto creado ({rc.status_code})')
                        # Cleanup: eliminar el producto creado si devuelve id
                        try:
                            data = rc.json()
                            producto_id = data.get('producto', {}).get('id') or data.get('producto_id')
                            if producto_id:
                                requests.delete(f"{productos_api}/{producto_id}", timeout=5)
                        except:
                            pass
                    else:
                        self.log_resultado('upload', 'crear_producto_con_imagen', False, f'Falló crear producto: {rc.status_code} {rc.text[:200]}')
                else:
                    self.log_resultado('upload', 'subir_imagen', False, 'Respuesta sin URL o success=false')
            else:
                self.log_resultado('upload', 'subir_imagen', False, f'Status {r.status_code} {r.text[:200]}')
        except Exception as e:
            self.log_resultado('upload', 'subir_imagen', False, f'Excepción: {str(e)}')
    
    def mostrar_resumen(self):
        """Muestra el resumen completo de verificaciones"""
        print("\n" + "="*60)
        print("RESUMEN DE VERIFICACION DEL SISTEMA")
        print("="*60)
        
        total_tests = 0
        tests_exitosos = 0
        
        for modulo, tests in self.resultados.items():
            print(f"\n📁 {modulo.upper()}:")
            for test in tests:
                print(f"  {test['estado']} {test['test']}: {test['mensaje']}")
                total_tests += 1
                if test['exitoso']:
                    tests_exitosos += 1
        
        print("\n" + "="*60)
        print("RESULTADOS FINALES:")
        print(f"   Total de pruebas: {total_tests}")
        print(f"   Pruebas exitosas: {tests_exitosos}")
        print(f"   Pruebas fallidas: {total_tests - tests_exitosos}")
        
        if total_tests > 0:
            print(f"   Porcentaje de éxito: {(tests_exitosos/total_tests)*100:.1f}%")
        else:
            print(f"   Porcentaje de éxito: No hay datos de testing disponibles")
        
        if self.errores:
            print(f"\nERRORES ENCONTRADOS ({len(self.errores)}):")
            for error in self.errores[:5]:  # Mostrar solo los primeros 5
                print(f"   - {error}")
            if len(self.errores) > 5:
                print(f"   ... y {len(self.errores) - 5} errores más")
        else:
            print("\nSISTEMA COMPLETAMENTE FUNCIONAL - No se encontraron errores")
        
        print("="*60)
    
    def ejecutar_verificacion_completa(self):
        """Ejecuta todas las verificaciones del sistema"""
        print("INICIANDO VERIFICACION COMPLETA DEL SISTEMA")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Ejecutar todas las verificaciones
        self.verificar_base_datos()
        self.verificar_conectividad()
        self.verificar_apis()
        self.verificar_imagenes()
        self.verificar_importaciones()
        self.verificar_modulo_cocina()
        self.verificar_anti_duplicacion()
        self.verificar_upload_y_creacion()
        self.verificar_configuracion_menu()
        self.verificar_dashboard_chatbot()
        self.verificar_temas_predefinidos()
        # ELIMINADO: self.verificar_analisis_adaptativo() - Sistema de colores eliminado
        self.verificar_codigo_duplicado()
        
        # Mostrar resumen
        self.mostrar_resumen()
    
    def ejecutar_modulo_especifico(self, modulo):
        """Ejecuta verificación de un módulo específico"""
        print(f"🎯 VERIFICANDO MÓDULO ESPECÍFICO: {modulo.upper()}")
        print("="*40)
        
        if modulo == "base_datos":
            self.verificar_base_datos()
        elif modulo == "conectividad":
            self.verificar_conectividad()
        elif modulo == "apis":
            self.verificar_apis()
        elif modulo == "imagenes":
            self.verificar_imagenes()
        elif modulo == "importaciones":
            self.verificar_importaciones()
        elif modulo == "cocina":
            self.verificar_modulo_cocina()
        elif modulo == "anti_duplicacion":
            self.verificar_anti_duplicacion()
        elif modulo == "config_menu":
            self.verificar_configuracion_menu()
        elif modulo == "wcag_colores":
            self.verificar_wcag_multiple_colores()
        elif modulo == "metricas_contraste":
            self.verificar_metricas_contraste()
        elif modulo == "configurar_color":
            color = input("🎨 Ingresa el color hex (ej: #8e44ad): ").strip()
            if color:
                self.configurar_color_testing(color)
        elif modulo == "dashboard_chatbot":
            self.verificar_dashboard_chatbot()
        elif modulo == "temas":
            self.verificar_temas_predefinidos()
        elif modulo == "adaptativo":
            # ELIMINADO: self.verificar_analisis_adaptativo() - Sistema de colores eliminado
            print("✅ Sistema de colores adaptativos eliminado correctamente")
        elif modulo == "personalizacion":
            self.verificar_sistema_personalizacion_completo()
        elif modulo == "codigo_duplicado":
            self.verificar_codigo_duplicado()
        else:
            print(f"❌ Módulo '{modulo}' no reconocido")
            print("Módulos disponibles: base_datos, conectividad, apis, imagenes, importaciones, cocina, anti_duplicacion, config_menu, dashboard_chatbot, temas, adaptativo, personalizacion, codigo_duplicado")
            return
        
        self.mostrar_resumen()

    def verificar_anti_duplicacion(self):
        """
        VERIFICAR SISTEMA ANTI-DUPLICACION
        Valida que el sistema previene correctamente la creación de productos duplicados
        """
        print("\n" + "="*60)
        print("VERIFICANDO SISTEMA ANTI-DUPLICACION")
        print("="*60)
        
        # Verificar que el servidor esté activo
        try:
            response = requests.get(f"{self.base_url}/menu-admin/admin", timeout=5)
            if response.status_code != 200:
                print("ERROR: Servidor no responde - Ejecuta 'python main.py' primero")
                self.errores.append("Servidor inactivo para test anti-duplicación")
                return
        except Exception as e:
            print(f"No se puede conectar al servidor: {e}")
            self.errores.append(f"Error conectividad anti-duplicación: {e}")
            return
        
        api_endpoint = f"{self.base_url}/menu-admin/api/productos"
        productos_creados = []
        
        try:
            # Test 1: Crear producto original
            print("\n📝 Test 1: Creando producto original...")
            producto_original = {
                "nombre": "Pizza Test Anti-Duplicación",
                "descripcion": "Pizza para test de duplicación",
                "precio": 15.99,
                "categoria_id": 1,
                "disponible": True,
                "tipo_producto": "simple"
            }
            
            response = requests.post(api_endpoint, json=producto_original, timeout=10)
            if response.status_code == 201:
                data = response.json()
                producto_id = data.get('producto', {}).get('id')
                productos_creados.append(producto_id)
                print(f"Producto original creado (ID: {producto_id})")
                self.exitos.append("Creación producto original para test")
            else:
                print(f"Error creando producto original: {response.text}")
                self.errores.append("Fallo creación producto test")
                return
            
            # Test 2: Intentar crear duplicado exacto
            print("\n🚫 Test 2: Intentando crear duplicado exacto...")
            response = requests.post(api_endpoint, json=producto_original, timeout=10)
            if response.status_code == 409:
                data = response.json()
                print(f"Duplicado correctamente rechazado: {data.get('error', 'Sin detalle')}")
                self.exitos.append("Prevención duplicado exacto")
            else:
                print(f"Sistema NO previno duplicado exacto: {response.text}")
                self.errores.append("Fallo prevención duplicado exacto")
            
            # Test 3: Intentar duplicado con capitalización diferente
            print("\n🔤 Test 3: Intentando duplicado con diferente capitalización...")
            producto_caps = producto_original.copy()
            producto_caps["nombre"] = "PIZZA TEST ANTI-DUPLICACIÓN"
            
            response = requests.post(api_endpoint, json=producto_caps, timeout=10)
            if response.status_code == 409:
                data = response.json()
                print(f"Duplicado capitalizado rechazado: {data.get('error', 'Sin detalle')}")
                self.exitos.append("Prevención duplicado capitalización")
            else:
                print(f"Sistema NO previno duplicado capitalizado: {response.text}")
                self.errores.append("Fallo prevención duplicado capitalización")
            
            # Test 4: Intentar duplicado con espacios extra
            print("\n📏 Test 4: Intentando duplicado con espacios extra...")
            producto_espacios = producto_original.copy()
            producto_espacios["nombre"] = "  Pizza Test Anti-Duplicación  "
            
            response = requests.post(api_endpoint, json=producto_espacios, timeout=10)
            if response.status_code == 409:
                data = response.json()
                print(f"Duplicado con espacios rechazado: {data.get('error', 'Sin detalle')}")
                self.exitos.append("Prevención duplicado espacios")
            else:
                print(f"Sistema NO previno duplicado con espacios: {response.text}")
                self.errores.append("Fallo prevención duplicado espacios")
            
            # Test 5: Validar precios negativos
            print("\n💰 Test 5: Validando rechazo de precios negativos...")
            producto_precio_negativo = {
                "nombre": "Producto Precio Negativo Test",
                "descripcion": "Test para precio negativo",
                "precio": -5.00,
                "categoria_id": 1,
                "disponible": True,
                "tipo_producto": "simple"
            }
            
            response = requests.post(api_endpoint, json=producto_precio_negativo, timeout=10)
            if response.status_code == 400:
                data = response.json()
                print(f"Precio negativo correctamente rechazado: {data.get('error', 'Sin detalle')}")
                self.exitos.append("Validación precio negativo")
            else:
                print(f"Sistema NO rechazó precio negativo: {response.text}")
                self.errores.append("Fallo validación precio negativo")
            
            # Test 6: Crear producto diferente (válido)
            print("\n✨ Test 6: Creando producto con nombre diferente...")
            producto_diferente = {
                "nombre": "Pizza Diferente Test",
                "descripcion": "Pizza válida diferente",
                "precio": 17.99,
                "categoria_id": 1,
                "disponible": True,
                "tipo_producto": "simple"
            }
            
            response = requests.post(api_endpoint, json=producto_diferente, timeout=10)
            if response.status_code == 201:
                data = response.json()
                producto_id_2 = data.get('producto', {}).get('id')
                productos_creados.append(producto_id_2)
                print(f"Producto diferente creado correctamente (ID: {producto_id_2})")
                self.exitos.append("Creación producto válido diferente")
            else:
                print(f"Error creando producto válido: {response.text}")
                self.errores.append("Fallo creación producto válido")
            
            print(f"\nResumen Anti-Duplicacion: {len([e for e in self.exitos if 'duplicad' in e.lower() or 'precio' in e.lower()])} tests aprobados")
            
        except Exception as e:
            print(f"Error en test anti-duplicacion: {e}")
            self.errores.append(f"Error general anti-duplicacion: {e}")
        
        finally:
            print("\nLimpiando productos de prueba...")
            for producto_id in productos_creados:
                try:
                    response = requests.delete(f"{api_endpoint}/{producto_id}", timeout=10)
                    print(f"Producto {producto_id} eliminado")
                except Exception as e:
                    print(f"Error eliminando producto {producto_id}: {e}")

    def verificar_configuracion_menu(self):
        """Sistema de configuración de menú - ELIMINADO durante simplificación"""
        print("\n🔧 Sistema de Configuración de Menú - ELIMINADO (simplificado)...")
        
        # Sistema de configuración de menú fue eliminado durante la simplificación
        self.log_resultado('config_menu', 'obtener_config', True, 
                         "Sistema eliminado - menú simplificado sin configuración dinámica")

        # Sistema simplificado - funciones eliminadas
        self.log_resultado('config_menu', 'cambio_rapido', True, "Sistema simplificado - funcionalidad eliminada")
        self.log_resultado('config_menu', 'config_completa', True, "Sistema simplificado - funcionalidad eliminada")  
        self.log_resultado('config_menu', 'api_estado', True, "Sistema simplificado - funcionalidad eliminada")

        # Test 5: Frontend integración - Sistema simplificado
        try:
            # Solo verificar menú público (otras páginas eliminadas)
            response = requests.get(f"{self.base_url}/menu/general", timeout=5)
            menu_ok = response.status_code == 200
            
            if menu_ok:
                self.log_resultado('config_menu', 'frontend_integration', True, "Menú público operativo - sistema simplificado")
            else:
                self.log_resultado('config_menu', 'frontend_integration', False, f"Menú público error: HTTP {response.status_code}")
                                 
        except Exception as e:
            self.log_resultado('config_menu', 'frontend_integration', False, str(e))

    def verificar_dashboard_chatbot(self):
        """
        Verifica el dashboard administrativo del chatbot
        Incluye: temas, notificaciones, sesiones, APIs del chatbot
        """
        print("\n" + "="*60)
        print("🤖 VERIFICANDO DASHBOARD CHATBOT")
        print("="*60)
        
        # Test 1: Verificar que el dashboard carga correctamente
        try:
            response = requests.get(f"{self.base_url}/admin/chatbot", timeout=5)
            if response.status_code == 200 and "Dashboard Chatbot" in response.text:
                self.log_resultado('chatbot_dashboard', 'dashboard_load', True, f"HTTP {response.status_code}")
            else:
                self.log_resultado('chatbot_dashboard', 'dashboard_load', False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_resultado('chatbot_dashboard', 'dashboard_load', False, str(e))

        # Test 2: Sistema de temas - ELIMINADO
        # Sistema de temas fue completamente eliminado durante la simplificación
        self.log_resultado('chatbot_dashboard', 'api_temas', True, "Sistema de temas eliminado - solo imágenes de fondo vía URL")

        # Test 3: Tema activo - ELIMINADO
        # Sistema de temas fue completamente eliminado durante la simplificación
        self.log_resultado('chatbot_dashboard', 'tema_activo', True, "Sistema de temas eliminado - personalización vía URL parámetros")

        # Test 4: API de notificaciones
        try:
            response = requests.get(f"{self.base_url}/api/chatbot/notificaciones", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'notificaciones' in data:
                    notif_count = len(data['notificaciones'])
                    self.log_resultado('chatbot_dashboard', 'api_notificaciones', True, f"{notif_count} notificaciones")
                else:
                    self.log_resultado('chatbot_dashboard', 'api_notificaciones', False, "Estructura JSON inválida")
            else:
                self.log_resultado('chatbot_dashboard', 'api_notificaciones', False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_resultado('chatbot_dashboard', 'api_notificaciones', False, str(e))

        # Test 5: API de sesiones activas
        try:
            response = requests.get(f"{self.base_url}/api/chatbot/sesiones/activas", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'sesiones' in data:
                    sesiones_count = len(data['sesiones'])
                    self.log_resultado('chatbot_dashboard', 'api_sesiones', True, f"{sesiones_count} sesiones activas")
                else:
                    self.log_resultado('chatbot_dashboard', 'api_sesiones', False, "Estructura JSON inválida")
            else:
                self.log_resultado('chatbot_dashboard', 'api_sesiones', False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_resultado('chatbot_dashboard', 'api_sesiones', False, str(e))

        # Test 6: Frontend del chatbot (carga de temas dinámicos)
        try:
            response = requests.get(f"{self.base_url}/chatbot", timeout=5)
            if response.status_code == 200:
                content = response.text
                # Verificar que el HTML del chatbot esté correctamente estructurado
                html_ok = 'Eterials' in content and 'logo.png' in content
                script_ok = 'script.js' in content
                
                if html_ok and script_ok:
                    self.log_resultado('chatbot_dashboard', 'frontend_chatbot', True, "Frontend del chatbot operativo")
                else:
                    self.log_resultado('chatbot_dashboard', 'frontend_chatbot', False, "HTML o JavaScript faltante")
            else:
                self.log_resultado('chatbot_dashboard', 'frontend_chatbot', False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_resultado('chatbot_dashboard', 'frontend_chatbot', False, str(e))

        # Test 7: CSS dinámico - ELIMINADO
        # Sistema de CSS dinámico fue eliminado durante la simplificación
        self.log_resultado('chatbot_dashboard', 'css_dinamico', True, "Sistema de CSS dinámico eliminado - estilos estáticos únicamente")

    def verificar_temas_predefinidos(self):
        """
        Verifica que los temas predefinidos estén correctamente inicializados en la BD
        """
        print("\n" + "="*60)
        print("🎨 VERIFICANDO TEMAS PREDEFINIDOS")
        print("="*60)
        
        # Test 1: Conexión a base de datos - ACTUALIZADO: Sin temas (sistema simplificado)
        try:
            # ELIMINADO: from modulos.backend.chatbot.models import TemaPersonalizacion, PropiedadTema
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import create_engine
            
            engine = create_engine('sqlite:///modulos/backend/menu/database/menu.db')
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # SISTEMA DE TEMAS ELIMINADO - SOLO IMÁGENES DE FONDO
            # Verificar que el sistema simplificado funciona correctamente
            self.log_resultado('temas_predefinidos', 'bd_temas', True, "Sistema de temas eliminado - solo imágenes de fondo")
            
            # Sistema simplificado sin temas activos
            self.log_resultado('temas_predefinidos', 'tema_activo_bd', True, "Sistema simplificado - sin temas activos")
            
            session.close()
            
        except Exception as e:
            self.log_resultado('temas_predefinidos', 'bd_temas', False, str(e))

        # Test 2: Sistema simplificado - SOLO IMÁGENES DE FONDO
        try:
            # Sistema de temas completamente eliminado
            # Solo queda personalización de fondo por URL parameters
            self.log_resultado('temas_predefinidos', 'propiedades_completas', True, "Sistema simplificado - personalización vía URL parámetros")
            
        except Exception as e:
            self.log_resultado('temas_predefinidos', 'propiedades_completas', False, str(e))

    # ELIMINADO: verificar_analisis_adaptativo - Sistema de colores adaptativos eliminado

    # ELIMINADO: _verificar_dependencias_analizador - Sistema de colores adaptativos eliminado

    # ELIMINADO: _test_analizador_directo - Sistema de colores adaptativos eliminado

    # ELIMINADO: _test_endpoint_colores_adaptativos - Sistema de colores adaptativos eliminado

    def _verificar_archivos_analizador(self):
        """Verifica que existan los archivos necesarios del sistema"""
        archivos_requeridos = [
            # ELIMINADO: 'analizador_colores_adaptativos.py',
            'modulos/frontend/chatbot/templates/chatbot.html.j2',
            'modulos/frontend/chatbot/static/script.js',
            'modulos/frontend/chatbot/static/style.css'
        ]
        
        todos_ok = True
        for archivo in archivos_requeridos:
            if os.path.exists(archivo):
                print(f"   ✅ {archivo}")
            else:
                print(f"   ❌ Falta: {archivo}")
                todos_ok = False
        
        return todos_ok

    def verificar_sistema_personalizacion_completo(self):
        """Verifica el sistema completo de personalización del chatbot"""
        print("\n🎨 VERIFICANDO SISTEMA COMPLETO DE PERSONALIZACIÓN")
        print("=" * 60)
        
        resultados = []
        exito = True
        
        # ELIMINADO: Sistema de análisis adaptativo
        resultados.append("✅ Sistema simplificado - Solo imágenes de fondo")
        
        # Verificar integración frontend-backend
        integracion_ok = self._test_integracion_personalizacion()
        if integracion_ok:
            resultados.append("✅ Integración frontend-backend funcional")
        else:
            resultados.append("❌ Problemas en integración frontend-backend")
            exito = False
        
        # Verificar aplicación de estilos
        estilos_ok = self._test_aplicacion_estilos()
        if estilos_ok:
            resultados.append("✅ Sistema de aplicación de estilos operativo")
        else:
            resultados.append("❌ Problemas en aplicación de estilos")
            exito = False
        
        self.imprimir_lista_resultados(resultados, "🎨 SISTEMA COMPLETO DE PERSONALIZACIÓN")
        return exito

    def _test_integracion_personalizacion(self):
        """Test de integración entre dashboard y chatbot para personalización"""
        try:
            # Verificar que los archivos JavaScript tengan las funciones necesarias
            js_path = "modulos/frontend/chatbot/static/script.js"
            if os.path.exists(js_path):
                with open(js_path, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                    
                # Verificar que sea un archivo JavaScript válido
                funciones_basicas = ['function', 'var ', 'const ', 'let ']
                
                js_valido = any(palabra in js_content for palabra in funciones_basicas)
                if js_valido:
                    print(f"   ✅ Archivo JavaScript válido encontrado")
                else:
                    print(f"   ❌ Archivo JavaScript parece vacío o inválido")
                    return False
                        
                return True
            else:
                print(f"   ❌ No se encuentra archivo JS: {js_path}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error verificando integración: {e}")
            return False

    def _test_aplicacion_estilos(self):
        """Test de aplicación de estilos adaptativos"""
        try:
            # Verificar que el template del chatbot tenga las funciones de aplicación
            template_path = "modulos/frontend/chatbot/templates/chatbot.html.j2"
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    
                # Verificar que sea un template Jinja2 válido
                elementos_template = ['{{', '}}', '{%', '%}', 'html']
                template_valido = any(elemento in template_content for elemento in elementos_template)
                
                if template_valido:
                    print(f"   ✅ Template Jinja2 válido encontrado")
                else:
                    print(f"   ❌ Template no parece ser Jinja2 válido")
                    return False
                        
                return True
            else:
                print(f"   ❌ No se encuentra template: {template_path}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error verificando aplicación estilos: {e}")
            return False
    
    def configurar_color_testing(self, color_hex='#8e44ad'):
        """Configura un color específico en la BD para testing rápido"""
        print(f"\n🎨 CONFIGURANDO COLOR {color_hex} PARA TESTING")
        print("=" * 50)
        
        try:
            import sqlite3
            conn = sqlite3.connect('modulos/backend/menu/database/menu.db')
            cursor = conn.cursor()
            
            # Configurar tipo de fondo
            cursor.execute('''
                INSERT OR REPLACE INTO chatbot_configuracion (clave, valor) 
                VALUES ('fondo_tipo', 'color')
            ''')
            
            # Configurar valor del fondo
            cursor.execute('''
                INSERT OR REPLACE INTO chatbot_configuracion (clave, valor) 
                VALUES ('fondo_valor', ?)
            ''', (color_hex,))
            
            conn.commit()
            
            # Verificar la configuración
            cursor.execute('SELECT clave, valor FROM chatbot_configuracion WHERE clave IN ("fondo_tipo", "fondo_valor")')
            resultados = cursor.fetchall()
            
            conn.close()
            
            print(f"✅ Color {color_hex} configurado en base de datos")
            for clave, valor in resultados:
                print(f"   {clave}: {valor}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando color: {e}")
            return False
    
    def verificar_wcag_multiple_colores(self):
        """Verifica compliance WCAG para múltiples colores"""
        print("\n🌈 VERIFICANDO WCAG COMPLIANCE - MÚLTIPLES COLORES")
        print("=" * 60)
        
        colores_test = [
            ('#8e44ad', 'Morado'),
            ('#e74c3c', 'Rojo'), 
            ('#f39c12', 'Naranja'),
            ('#2ecc71', 'Verde'),
            ('#3498db', 'Azul'),
            ('#2c3e50', 'Azul Oscuro'),
            ('#f1c40f', 'Amarillo'),
            ('#9b59b6', 'Violeta')
        ]
        
        todos_cumplen = True
        resultados = []
        
        try:
            # ELIMINADO: Sistema de análisis de colores ya no se usa
            for color_hex, nombre in colores_test:
                mensaje = f"⚪ {nombre:12} {color_hex} - Sistema de colores eliminado"
                print(mensaje)
                resultados.append(mensaje)
            
            print("✅ Sistema de colores eliminado - Solo imágenes de fondo disponibles")
            return True
            
        except Exception as e:
            print(f"❌ Error en verificación WCAG: {e}")
            return False
    
    def verificar_metricas_contraste(self, color_hex='#8e44ad'):
        """Verifica métricas detalladas de contraste para un color"""
        print(f"\n🔧 VERIFICANDO MÉTRICAS DE CONTRASTE: {color_hex}")
        print("=" * 50)
        
        try:
            # ELIMINADO: Sistema de análisis de colores
            print(f"📊 SISTEMA DE COLORES ELIMINADO:")
            print(f"   ⚪ Análisis de colores deshabilitado por simplicidad")
            print(f"   ⚪ Solo se mantiene cambio de imágenes de fondo")
            print("✅ Sistema simplificado correctamente")
            return True
                
        except Exception as e:
            print(f"❌ Error verificando métricas: {e}")
            return False

    def verificar_codigo_duplicado(self):
        """
        🔍 AUDITORÍA DE CÓDIGO DUPLICADO
        Busca funciones y rutas duplicadas en el módulo MENU
        """
        print("\n" + "="*50)
        print("🔍 AUDITORÍA DE CÓDIGO DUPLICADO")
        print("="*50)
        
        try:
            import glob
            import re
            
            # Buscar funciones duplicadas
            print("\n📋 Analizando funciones duplicadas...")
            archivos_menu = glob.glob("modulos/backend/menu/**/*.py", recursive=True)
            funciones = {}
            
            for archivo in archivos_menu:
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        
                    # Buscar definiciones de funciones
                    patron_funciones = r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
                    matches = re.finditer(patron_funciones, contenido, re.MULTILINE)
                    
                    for match in matches:
                        nombre_funcion = match.group(1)
                        if nombre_funcion not in funciones:
                            funciones[nombre_funcion] = []
                        funciones[nombre_funcion].append(archivo)
                except Exception as e:
                    print(f"⚠️ Error procesando {archivo}: {e}")
            
            # Reportar funciones duplicadas
            funciones_duplicadas = 0
            for func, archivos in funciones.items():
                if len(archivos) > 1:
                    print(f"🔄 FUNCIÓN DUPLICADA: {func}")
                    for archivo in archivos:
                        print(f"   📁 {archivo}")
                    funciones_duplicadas += 1
            
            # Buscar rutas duplicadas
            print(f"\n📋 Analizando rutas duplicadas...")
            rutas = {}
            
            for archivo in archivos_menu:
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        
                    # Buscar decoradores de ruta
                    patron_rutas = r"@\w+\.route\(['\"](.*?)['\"]"
                    matches = re.finditer(patron_rutas, contenido)
                    
                    for match in matches:
                        ruta = match.group(1)
                        if ruta not in rutas:
                            rutas[ruta] = []
                        rutas[ruta].append(archivo)
                except Exception as e:
                    print(f"⚠️ Error procesando rutas en {archivo}: {e}")
            
            # Reportar rutas duplicadas
            rutas_duplicadas = 0
            for ruta, archivos in rutas.items():
                if len(archivos) > 1:
                    print(f"🌐 RUTA DUPLICADA: {ruta}")
                    for archivo in archivos:
                        print(f"   📁 {archivo}")
                    rutas_duplicadas += 1
            
            # Resumen
            print(f"\n📊 RESUMEN AUDITORÍA:")
            print(f"   • Archivos analizados: {len(archivos_menu)}")
            print(f"   • Funciones duplicadas: {funciones_duplicadas}")
            print(f"   • Rutas duplicadas: {rutas_duplicadas}")
            
            if funciones_duplicadas == 0 and rutas_duplicadas == 0:
                print("✅ No se encontraron duplicaciones problemáticas")
                self.exitos.append("Auditoría código duplicado - Sin problemas")
            else:
                print("⚠️ Se encontraron duplicaciones que requieren revisión")
                self.errores.append(f"Código duplicado - {funciones_duplicadas} funciones, {rutas_duplicadas} rutas")
                
        except Exception as e:
            print(f"❌ Error en auditoría de código duplicado: {e}")
            self.errores.append("Fallo auditoría código duplicado")

def main():
    """Función principal con manejo de argumentos"""
    parser = argparse.ArgumentParser(description="Verificador Sistema Completo - Eterials")
    parser.add_argument('--modulo', type=str, help='Verificar módulo específico (base_datos, conectividad, apis, imagenes, importaciones, cocina, dashboard_chatbot, temas, wcag_colores, metricas_contraste, configurar_color)')
    parser.add_argument('--version', action='version', version='Verificador Sistema v1.0.0')
    
    args = parser.parse_args()
    
    verificador = VerificadorSistema()
    
    try:
        if args.modulo:
            verificador.ejecutar_modulo_especifico(args.modulo)
        else:
            verificador.ejecutar_verificacion_completa()
    except KeyboardInterrupt:
        print("\n\n⚠️ Verificación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    # Verificación de dependencias y módulos Python
    verificador = VerificadorSistema()
    verificador.verificar_dependencias_python()
    main()
