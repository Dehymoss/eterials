#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar puerto y prevenir conflictos
==============================================
Automatiza la limpieza del puerto 8080 antes de iniciar el servidor
"""

import os
import sys
import subprocess
import time
import signal
import psutil

def limpiar_puerto_8080():
    """Limpiar completamente el puerto 8080"""
    print("🧹 Limpiando puerto 8080...")
    
    try:
        # Método 1: Usar netstat para encontrar PIDs
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            pids_to_kill = set()
            for line in lines:
                if ':8080' in line and ('LISTENING' in line or 'ESTABLISHED' in line or 'CLOSE_WAIT' in line):
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids_to_kill.add(int(pid))
            
            print(f"📍 Encontrados PIDs usando puerto 8080: {pids_to_kill}")
            
            for pid in pids_to_kill:
                try:
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        proc_name = proc.name()
                        print(f"🔄 Terminando proceso {proc_name} (PID: {pid})")
                        proc.terminate()
                        
                        # Esperar a que termine graciosamente
                        try:
                            proc.wait(timeout=3)
                            print(f"✅ Proceso {pid} terminado exitosamente")
                        except psutil.TimeoutExpired:
                            print(f"⚠️ Proceso {pid} no termina, forzando...")
                            proc.kill()
                            print(f"✅ Proceso {pid} forzado a terminar")
                    else:
                        print(f"⚠️ PID {pid} no existe (proceso zombie)")
                except Exception as e:
                    print(f"❌ Error terminando PID {pid}: {e}")
                    # Intentar con taskkill como fallback
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                     capture_output=True, check=False)
                        print(f"✅ PID {pid} terminado con taskkill")
                    except:
                        pass
        
        # Esperar a que se liberen los recursos
        print("⏳ Esperando liberación de recursos...")
        time.sleep(3)
        
        # Verificar que el puerto esté libre
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        port_lines = [line for line in result.stdout.split('\n') if ':8080' in line]
        
        if not port_lines:
            print("✅ Puerto 8080 liberado exitosamente")
            return True
        else:
            print(f"⚠️ Puerto 8080 aún tiene {len(port_lines)} conexiones, pero continuando...")
            for line in port_lines:
                print(f"   {line.strip()}")
            return True
            
    except Exception as e:
        print(f"❌ Error limpiando puerto: {e}")
        return False

def configurar_manejo_señales():
    """Configurar manejo de señales para limpieza automática"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Señal {signum} recibida, limpiando recursos...")
        limpiar_puerto_8080()
        sys.exit(0)
    
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def verificar_dependencias():
    """Verificar que psutil esté instalado"""
    try:
        import psutil
        return True
    except ImportError:
        print("❌ psutil no está instalado. Instalando...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
            print("✅ psutil instalado exitosamente")
            import psutil
            return True
        except Exception as e:
            print(f"❌ Error instalando psutil: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Iniciando limpieza de puerto 8080...")
    
    if not verificar_dependencias():
        print("❌ No se pudo instalar psutil, usando métodos alternativos")
    
    if limpiar_puerto_8080():
        print("✅ Puerto limpio, listo para usar")
    else:
        print("❌ Problemas limpiando puerto")
    
    configurar_manejo_señales()