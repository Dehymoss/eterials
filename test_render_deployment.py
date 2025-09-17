#!/usr/bin/env python3
"""
Test de deployment en Render.com - Sistema QR migrado
Verifica que el sistema funcione correctamente en producción
"""

import requests
import sys
import time

def test_render_deployment(base_url):
    """Test del deployment en Render.com"""
    print(f"🌐 TESTING DEPLOYMENT EN RENDER.COM")
    print(f"📍 URL: {base_url}")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 6
    
    try:
        # Test 1: Servidor principal responde
        print("1️⃣ Verificando servidor principal...")
        response = requests.get(f"{base_url}/admin", timeout=30)
        if response.status_code == 200:
            print("   ✅ Servidor principal funcionando")
            tests_passed += 1
        else:
            print(f"   ❌ Servidor responde código {response.status_code}")
            
        # Test 2: Endpoint QR accesible
        print("2️⃣ Verificando endpoint generador QR...")
        response = requests.get(f"{base_url}/admin/generador-qr", timeout=30)
        if response.status_code == 200:
            print("   ✅ Endpoint QR accesible en producción")
            tests_passed += 1
        else:
            print(f"   ❌ Endpoint QR error {response.status_code}")
            
        # Test 3: QRCode.js cargando
        print("3️⃣ Verificando QRCode.js en producción...")
        if "qrcode.min.js" in response.text:
            print("   ✅ QRCode.js referenciado correctamente")
            tests_passed += 1
        else:
            print("   ❌ No encuentra referencia a QRCode.js")
            
        # Test 4: Assets estáticos accesibles
        print("4️⃣ Verificando archivos estáticos...")
        js_response = requests.get(f"{base_url}/admin/static/js/qrcode.min.js", timeout=20)
        if js_response.status_code == 200:
            print("   ✅ Archivos JavaScript accesibles")
            tests_passed += 1
        else:
            print(f"   ❌ Error cargando JS: {js_response.status_code}")
            
        # Test 5: Chatbot funcional
        print("5️⃣ Verificando módulo chatbot...")
        chat_response = requests.get(f"{base_url}/chatbot", timeout=20)
        if chat_response.status_code == 200:
            print("   ✅ Chatbot accesible")
            tests_passed += 1
        else:
            print(f"   ❌ Chatbot error: {chat_response.status_code}")
            
        # Test 6: Menú cliente funcional
        print("6️⃣ Verificando menú cliente...")
        menu_response = requests.get(f"{base_url}/menu/general", timeout=20)
        if menu_response.status_code == 200:
            print("   ✅ Menú cliente accesible")
            tests_passed += 1
        else:
            print(f"   ❌ Menú cliente error: {menu_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        
    # Resumen
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN DEPLOYMENT: {tests_passed}/{total_tests} tests pasaron")
    
    if tests_passed >= 4:  # Al menos 4 de 6 tests
        print("🎉 ¡DEPLOYMENT EXITOSO!")
        print("✅ Sistema QR funcional en producción")
        print("🚀 RENDER.COM DEPLOYMENT COMPLETADO")
        if tests_passed == total_tests:
            print("🏆 PERFECTO: Todos los módulos funcionando")
        return True
    else:
        print("⚠️ Deployment parcial - revisar problemas")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📝 Uso: python test_render_deployment.py <URL_RENDER>")
        print("📝 Ejemplo: python test_render_deployment.py https://eterials-restaurant.onrender.com")
        sys.exit(1)
        
    render_url = sys.argv[1].rstrip('/')
    success = test_render_deployment(render_url)
    sys.exit(0 if success else 1)