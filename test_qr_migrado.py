#!/usr/bin/env python3
"""
Test de migración del sistema QR - Sin dependencias C++
Verifica que el sistema QR funcione con QRCode.js después de la migración
"""

import requests
import sys
import time
from pathlib import Path

def test_qr_system():
    """Test del sistema QR migrado"""
    print("🧪 TESTING SISTEMA QR MIGRADO - SIN DEPENDENCIAS C++")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8080"
    tests_passed = 0
    total_tests = 4
    
    try:
        # Test 1: Servidor funcionando
        print("1️⃣ Verificando servidor Flask...")
        response = requests.get(f"{base_url}/admin", timeout=5)
        if response.status_code == 200:
            print("   ✅ Servidor Flask funcionando en puerto 8080")
            tests_passed += 1
        else:
            print(f"   ❌ Servidor responde código {response.status_code}")
            
        # Test 2: Endpoint QR existe
        print("2️⃣ Verificando endpoint generador QR...")
        response = requests.get(f"{base_url}/admin/generador-qr", timeout=5)
        if response.status_code == 200:
            print("   ✅ Endpoint /admin/generador-qr accesible")
            tests_passed += 1
        else:
            print(f"   ❌ Endpoint QR error {response.status_code}")
            
        # Test 3: HTML contiene QRCode.js
        print("3️⃣ Verificando que usa QRCode.js...")
        if "qrcode.min.js" in response.text:
            print("   ✅ HTML carga QRCode.js (sin dependencias Python)")
            tests_passed += 1
        else:
            print("   ❌ No encuentra referencia a QRCode.js")
            
        # Test 4: Archivos estáticos existen
        print("4️⃣ Verificando archivos JavaScript...")
        qrcode_path = Path("modulos/panel_admin/static/js/qrcode.min.js")
        generador_path = Path("modulos/panel_admin/static/js/generador-qr.js")
        
        if qrcode_path.exists() and generador_path.exists():
            print("   ✅ Archivos QRCode.js y generador-qr.js existen")
            tests_passed += 1
        else:
            print("   ❌ Faltan archivos JavaScript necesarios")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        
    # Resumen
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN: {tests_passed}/{total_tests} tests pasaron")
    
    if tests_passed == total_tests:
        print("🎉 ¡MIGRACIÓN QR EXITOSA!")
        print("✅ Sistema QR funcional sin dependencias C++")
        print("🚀 LISTO PARA DEPLOYMENT EN RENDER.COM")
        return True
    else:
        print("⚠️ Algunos tests fallaron - revisar problemas")
        return False

if __name__ == "__main__":
    success = test_qr_system()
    sys.exit(0 if success else 1)