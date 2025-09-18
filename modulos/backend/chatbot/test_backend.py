#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing Completo del Backend del Chatbot
========================================
Script para probar todas las funcionalidades del backend antes de la migración.
"""

import requests
import json
import time
from datetime import datetime

class ChatbotBackendTester:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/chatbot"
        self.admin_base = f"{base_url}/admin/chatbot"
        self.sesion_id = None
        self.tests_passed = 0
        self.total_tests = 0
        
    def log(self, mensaje, exito=True):
        """Registrar resultado de test"""
        icono = "✅" if exito else "❌"
        print(f"{icono} {mensaje}")
        self.total_tests += 1
        if exito:
            self.tests_passed += 1
    
    def test_inicializar_backend(self):
        """Test 1: Verificar que el backend esté inicializado"""
        print("\n🔧 Test 1: Inicialización del Backend")
        
        try:
            from modulos.backend.chatbot.services import verificar_estado_backend
            estado = verificar_estado_backend()
            
            if estado['success']:
                self.log(f"Backend inicializado con {estado['total_tablas']} tablas")
                self.log(f"Configuraciones: {estado['configuraciones']}")
                return True
            else:
                self.log(f"Backend no inicializado: {estado['error']}", False)
                return False
                
        except Exception as e:
            self.log(f"Error verificando backend: {e}", False)
            return False
    
    def test_crear_sesion(self):
        """Test 2: Crear sesión de chatbot"""
        print("\n👤 Test 2: Creación de Sesión")
        
        payload = {
            "mesa": "5",
            "nombre_cliente": "Juan Test",
            "dispositivo": "Test Browser",
            "ip_cliente": "192.168.1.100"
        }
        
        try:
            response = requests.post(f"{self.api_base}/sesion/iniciar", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.sesion_id = data['sesion_id']
                    self.log(f"Sesión creada con ID: {self.sesion_id}")
                    return True
                else:
                    self.log(f"Error en respuesta: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error creando sesión: {e}", False)
            return False
    
    def test_actualizar_sesion(self):
        """Test 3: Actualizar datos de sesión"""
        print("\n🔄 Test 3: Actualización de Sesión")
        
        if not self.sesion_id:
            self.log("No hay sesión activa para actualizar", False)
            return False
        
        payload = {
            "nombre_cliente": "Juan Test Actualizado",
            "actualizar_ultimo_acceso": True
        }
        
        try:
            response = requests.put(f"{self.api_base}/sesion/{self.sesion_id}/actualizar", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.log("Sesión actualizada correctamente")
                    return True
                else:
                    self.log(f"Error actualizando: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error actualizando sesión: {e}", False)
            return False
    
    def test_calificacion(self):
        """Test 4: Guardar calificación"""
        print("\n⭐ Test 4: Sistema de Calificaciones")
        
        if not self.sesion_id:
            self.log("No hay sesión activa para calificar", False)
            return False
        
        payload = {
            "sesion_id": self.sesion_id,
            "estrellas": 5,
            "categoria": "servicio"
        }
        
        try:
            response = requests.post(f"{self.api_base}/calificacion", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.log("Calificación guardada: 5 estrellas")
                    return True
                else:
                    self.log(f"Error guardando calificación: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error en calificación: {e}", False)
            return False
    
    def test_comentario(self):
        """Test 5: Guardar comentario"""
        print("\n💬 Test 5: Sistema de Comentarios")
        
        if not self.sesion_id:
            self.log("No hay sesión activa para comentar", False)
            return False
        
        payload = {
            "sesion_id": self.sesion_id,
            "texto_comentario": "Excelente servicio y comida deliciosa! Test automatizado.",
            "tipo": "felicitacion"
        }
        
        try:
            response = requests.post(f"{self.api_base}/comentario", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.log("Comentario guardado correctamente")
                    return True
                else:
                    self.log(f"Error guardando comentario: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error en comentario: {e}", False)
            return False
    
    def test_notificacion_mesero(self):
        """Test 6: Notificación al mesero"""
        print("\n🔔 Test 6: Sistema de Notificaciones")
        
        if not self.sesion_id:
            self.log("No hay sesión activa para notificar", False)
            return False
        
        payload = {
            "sesion_id": self.sesion_id,
            "tipo_notificacion": "llamar_mesero",
            "mensaje": "Necesito ayuda con el menú - Test automatizado",
            "prioridad": "normal"
        }
        
        try:
            response = requests.post(f"{self.api_base}/notificacion/mesero", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.log("Notificación enviada al mesero")
                    return True
                else:
                    self.log(f"Error enviando notificación: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error en notificación: {e}", False)
            return False
    
    def test_obtener_notificaciones_pendientes(self):
        """Test 7: Obtener notificaciones pendientes"""
        print("\n📋 Test 7: Consulta de Notificaciones Pendientes")
        
        try:
            response = requests.get(f"{self.api_base}/notificaciones/pendientes")
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    total = data['total']
                    self.log(f"Notificaciones pendientes obtenidas: {total}")
                    return True
                else:
                    self.log(f"Error obteniendo notificaciones: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error consultando notificaciones: {e}", False)
            return False
    
    def test_saludo_dinamico(self):
        """Test 8: Saludo dinámico"""
        print("\n👋 Test 8: Saludo Dinámico")
        
        try:
            response = requests.get(f"{self.api_base}/saludo?mesa=5&nombre=Juan")
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    saludo = data['saludo_base']
                    mensaje = data['mensaje_completo']
                    self.log(f"Saludo generado: {saludo}")
                    self.log(f"Mensaje: {mensaje[:50]}...")
                    return True
                else:
                    self.log(f"Error generando saludo: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error en saludo dinámico: {e}", False)
            return False
    
    def test_analytics_resumen(self):
        """Test 9: Analytics y resumen"""
        print("\n📊 Test 9: Analytics y Resumen")
        
        try:
            response = requests.get(f"{self.api_base}/analytics/resumen?dias=7")
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    resumen = data['resumen']
                    self.log(f"Sesiones activas: {resumen['sesiones_activas']}")
                    self.log(f"Calificación promedio: {resumen['calificacion_promedio']}")
                    self.log(f"Comentarios: {resumen['total_comentarios']}")
                    return True
                else:
                    self.log(f"Error en analytics: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error en analytics: {e}", False)
            return False
    
    def test_configuracion(self):
        """Test 10: Configuración del chatbot"""
        print("\n⚙️ Test 10: Sistema de Configuración")
        
        try:
            response = requests.get(f"{self.api_base}/configuracion")
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    config = data['configuracion']
                    self.log(f"Configuraciones cargadas: {len(config)}")
                    
                    # Verificar configuraciones específicas
                    if 'saludo_manana' in config:
                        self.log(f"Saludo mañana: {config['saludo_manana']['valor']}")
                    if 'timeout_inactividad' in config:
                        self.log(f"Timeout: {config['timeout_inactividad']['valor']}ms")
                    
                    return True
                else:
                    self.log(f"Error en configuración: {data['error']}", False)
                    return False
            else:
                self.log(f"Error HTTP: {response.status_code}", False)
                return False
                
        except Exception as e:
            self.log(f"Error en configuración: {e}", False)
            return False
    
    def ejecutar_todos_los_tests(self):
        """Ejecutar toda la suite de tests"""
        print("🧪 INICIANDO TESTING COMPLETO DEL BACKEND CHATBOT")
        print("=" * 60)
        
        inicio = time.time()
        
        # Lista de tests a ejecutar
        tests = [
            self.test_inicializar_backend,
            self.test_crear_sesion,
            self.test_actualizar_sesion,
            self.test_calificacion,
            self.test_comentario,
            self.test_notificacion_mesero,
            self.test_obtener_notificaciones_pendientes,
            self.test_saludo_dinamico,
            self.test_analytics_resumen,
            self.test_configuracion
        ]
        
        # Ejecutar tests
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log(f"Error ejecutando {test.__name__}: {e}", False)
            
            # Pequeña pausa entre tests
            time.sleep(0.5)
        
        # Resumen final
        fin = time.time()
        duracion = fin - inicio
        
        print("\n" + "=" * 60)
        print(f"📊 RESUMEN FINAL DEL TESTING")
        print(f"✅ Tests exitosos: {self.tests_passed}/{self.total_tests}")
        print(f"⏱️ Duración: {duracion:.2f} segundos")
        
        porcentaje_exito = (self.tests_passed / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        if porcentaje_exito >= 80:
            print("🎉 BACKEND LISTO PARA MIGRACIÓN")
        elif porcentaje_exito >= 60:
            print("⚠️ Backend funcional pero con problemas menores")
        else:
            print("❌ Backend requiere correcciones antes de migrar")
        
        print(f"📈 Tasa de éxito: {porcentaje_exito:.1f}%")
        print("=" * 60)
        
        return porcentaje_exito >= 80

if __name__ == "__main__":
    # Verificar que el servidor esté corriendo
    print("🔍 Verificando que el servidor local esté activo...")
    
    try:
        response = requests.get("http://127.0.0.1:8080/admin/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor local activo")
            
            # Ejecutar tests
            tester = ChatbotBackendTester()
            exito = tester.ejecutar_todos_los_tests()
            
            if exito:
                print("\\n🚀 ¡Backend del chatbot listo para producción!")
            else:
                print("\\n🔧 Backend requiere ajustes antes del deployment")
                
        else:
            print("❌ Servidor no responde correctamente")
            
    except Exception as e:
        print(f"❌ Error conectando con servidor: {e}")
        print("💡 Asegúrate de que el servidor esté corriendo en puerto 8080")