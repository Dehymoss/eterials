#!/usr/bin/env python3
"""
Script para iniciar el servidor Eterials con limpieza completa de puertos
Resuelve problemas de puerto ocupado de forma definitiva
"""

import subprocess
import psutil
import time
import os
import sys

def limpiar_puerto_agresivo(puerto=8080):
    """Limpieza agresiva del puerto especificado"""
    print(f"🧹 Iniciando limpieza AGRESIVA del puerto {puerto}...")
    
    # Paso 1: Terminar todos los procesos Python activos
    print("⚡ Terminando procesos Python existentes...")
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'main.py' in cmdline or 'flask' in cmdline.lower():
                        print(f"🔄 Terminando proceso Python: {proc.info['pid']}")
                        proc = psutil.Process(proc.info['pid'])
                        proc.terminate()
                        proc.wait(timeout=2)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
    except Exception as e:
        print(f"⚠️ Error terminando procesos Python: {e}")
    
    # Paso 2: Usar netstat para encontrar y terminar procesos específicos del puerto
    print(f"🔍 Buscando procesos usando puerto {puerto}...")
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        pids_found = set()
        for line in lines:
            if f':{puerto}' in line:
                parts = line.split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pids_found.add(int(parts[-1]))
        
        if pids_found:
            print(f"📍 PIDs encontrados en puerto {puerto}: {pids_found}")
            for pid in pids_found:
                try:
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        print(f"⚡ Terminando {proc.name()} (PID: {pid})")
                        proc.kill()
                        proc.wait()
                except Exception as e:
                    print(f"⚠️ Error con PID {pid}: {e}")
        
    except Exception as e:
        print(f"⚠️ Error con netstat: {e}")
    
    # Paso 3: Comando taskkill como medida adicional
    print("🔧 Aplicando taskkill como medida de seguridad...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'pythonw.exe'], capture_output=True)
    except Exception:
        pass
    
    # Paso 4: Esperar y verificar
    print("⏳ Esperando 3 segundos para que se liberen los recursos...")
    time.sleep(3)
    
    # Verificación final
    try:
        result_final = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        if f':{puerto}' in result_final.stdout:
            print(f"⚠️ Aún hay conexiones residuales en puerto {puerto}")
            # Mostrar líneas específicas para debugging
            for line in result_final.stdout.split('\n'):
                if f':{puerto}' in line:
                    print(f"   {line.strip()}")
        else:
            print(f"✅ Puerto {puerto} completamente liberado")
    except Exception:
        pass

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    try:
        import psutil
        return True
    except ImportError:
        print("❌ Error: psutil no está instalado")
        print("🔧 Instalando psutil...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'psutil'], check=True)
            print("✅ psutil instalado correctamente")
            return True
        except Exception as e:
            print(f"❌ No se pudo instalar psutil: {e}")
            return False

def main():
    """Función principal"""
    print("🚀 SCRIPT DE LIMPIEZA COMPLETA - Sistema Eterials Restaurant")
    print("=" * 60)
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("❌ No se pueden instalar las dependencias necesarias")
        return
    
    # Limpieza agresiva
    limpiar_puerto_agresivo(8080)
    limpiar_puerto_agresivo(8081)
    limpiar_puerto_agresivo(5001)
    
    print("=" * 60)
    print("🎉 Limpieza completa terminada")
    print("🚀 Iniciando servidor principal...")
    print("=" * 60)
    
    # Iniciar main.py
    try:
        os.system('python main.py')
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    main()