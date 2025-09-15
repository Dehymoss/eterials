#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR SISTEMA COMPLETO - Eterials Chatbot
===============================================

Sistema unificado de verificación para todos los módulos del proyecto.
Consolida todas las pruebas, tests y verificaciones en un solo archivo.

Autor: Sistema Eterials
Fecha: 14/08/2025
Versión: 1.0.0

POLÍTICA DE INTEGRACIÓN:
- TODOS los nuevos tests DEBEN agregarse a este archivo
- PROHIBIDO crear archivos de test individuales
- Mantener modularidad con funciones separadas
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
BASE_URL = "http://127.0.0.1:8080"
DATABASE_PATH = "modulos/backend/menu/database/menu.db"

class VerificadorSistema:
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
            {"url": "/menu-admin/productos/sugerir-imagenes?nombre=pizza", "nombre": "api_imagenes", "metodo": "GET"},
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
                url = f"{BASE_URL}/menu-admin/productos/sugerir-imagenes?nombre={termino}"
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
        
        # Verificar modelos del proyecto
        try:
            from modulos.backend.menu.database.models.producto import Producto
            from modulos.backend.menu.database.models.categoria import Categoria
            self.log_resultado("importaciones", "modelos_propios", True, "Modelos SQLAlchemy del proyecto importados correctamente")
        except Exception as e:
            self.log_resultado("importaciones", "modelos_propios", False, f"Error importando modelos: {str(e)}")
    
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
            upload_url = f"{self.base_url}/menu-admin/subir-imagen"
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
        print(f"   Porcentaje de éxito: {(tests_exitosos/total_tests)*100:.1f}%")
        
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
        else:
            print(f"❌ Módulo '{modulo}' no reconocido")
            print("Módulos disponibles: base_datos, conectividad, apis, imagenes, importaciones, cocina, anti_duplicacion, config_menu")
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
        """Verificar sistema completo de configuración de menú"""
        print("\n🔧 Verificando Sistema de Configuración de Menú...")
        
        api_base = f"{self.base_url}/admin/configuracion-menu/api"
        
        # Test 1: API obtener configuración
        try:
            response = requests.get(f"{api_base}/obtener", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    config = data.get('configuracion', {})
                    self.log_resultado('config_menu', 'obtener_config', True, 
                                     f"Menu activo: {config.get('menu_activo', 'N/A')}")
                else:
                    self.log_resultado('config_menu', 'obtener_config', False, 
                                     f"Error en respuesta: {data.get('message', 'Unknown')}")
            else:
                self.log_resultado('config_menu', 'obtener_config', False, 
                                 f"HTTP {response.status_code}")
        except Exception as e:
            self.log_resultado('config_menu', 'obtener_config', False, str(e))

        # Test 2: Cambio rápido de menú
        try:
            # Cambio a externo
            payload = {"menu_activo": "externo"}
            response = requests.post(f"{api_base}/cambiar", json=payload, timeout=5)
            cambio_externo_ok = response.status_code == 200 and response.json().get('success')
            
            # Cambio de vuelta a propio
            payload = {"menu_activo": "propio"}
            response = requests.post(f"{api_base}/cambiar", json=payload, timeout=5)
            cambio_propio_ok = response.status_code == 200 and response.json().get('success')
            
            if cambio_externo_ok and cambio_propio_ok:
                self.log_resultado('config_menu', 'cambio_rapido', True, "Cambios bidireccionales OK")
            else:
                self.log_resultado('config_menu', 'cambio_rapido', False, "Error en cambios")
                
        except Exception as e:
            self.log_resultado('config_menu', 'cambio_rapido', False, str(e))

        # Test 3: Actualización configuración completa
        try:
            config_test = {
                "menu_externo_url": "https://treinta.co/menu-test",
                "menu_externo_nombre": "Menú Test",
                "redirect_automatico": "false",
                "mensaje_mantenimiento": "Sistema de prueba"
            }
            response = requests.post(f"{api_base}/actualizar", json=config_test, timeout=5)
            if response.status_code == 200 and response.json().get('success'):
                self.log_resultado('config_menu', 'config_completa', True, "Actualización completa OK")
            else:
                self.log_resultado('config_menu', 'config_completa', False, "Error actualización")
        except Exception as e:
            self.log_resultado('config_menu', 'config_completa', False, str(e))

        # Test 4: API de estado
        try:
            response = requests.get(f"{api_base}/estado", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_resultado('config_menu', 'api_estado', True, 
                                     f"Estado: {data.get('menu_activo')}")
                else:
                    self.log_resultado('config_menu', 'api_estado', False, "Error estado")
            else:
                self.log_resultado('config_menu', 'api_estado', False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_resultado('config_menu', 'api_estado', False, str(e))

        # Test 5: Frontend integración
        try:
            # Página configuración
            response = requests.get(f"{self.base_url}/admin/configuracion-menu", timeout=5)
            config_page_ok = response.status_code == 200 and "Configuración de Menú" in response.text
            
            # Dashboard admin
            response = requests.get(f"{self.base_url}/admin", timeout=5)
            dashboard_ok = response.status_code == 200 and "Configuración de Menú" in response.text
            
            # Menú público (verificación básica)
            response = requests.get(f"{self.base_url}/menu/general", timeout=5)
            menu_ok = response.status_code == 200
            
            if config_page_ok and dashboard_ok and menu_ok:
                self.log_resultado('config_menu', 'frontend_integration', True, "Todas las páginas OK")
            else:
                self.log_resultado('config_menu', 'frontend_integration', False, 
                                 f"Config:{config_page_ok}, Dashboard:{dashboard_ok}, Menu:{menu_ok}")
                                 
        except Exception as e:
            self.log_resultado('config_menu', 'frontend_integration', False, str(e))

def main():
    """Función principal con manejo de argumentos"""
    parser = argparse.ArgumentParser(description="Verificador Sistema Completo - Eterials")
    parser.add_argument('--modulo', type=str, help='Verificar módulo específico (base_datos, conectividad, apis, imagenes, importaciones, cocina)')
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
    main()
