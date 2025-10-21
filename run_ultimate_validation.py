#!/usr/bin/env python3
"""
RUN ULTIMATE VALIDATION - Script semplice per eseguire ultimate validation
"""

import subprocess
import sys
import os

def main():
    """Esegue ultimate validation all GRB"""
    
    print("🚀 Avvio Ultimate Validation All GRB...")
    
    # Verifica che il file esista
    if not os.path.exists('ultimate_validation_all_grb.py'):
        print("❌ File ultimate_validation_all_grb.py non trovato!")
        return
    
    try:
        # Esegui il script
        result = subprocess.run([sys.executable, 'ultimate_validation_all_grb.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print("📊 OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ ERRORI:")
            print(result.stderr)
            
        print(f"✅ Completato con exit code: {result.returncode}")
        
    except Exception as e:
        print(f"❌ Errore esecuzione: {e}")

if __name__ == "__main__":
    main()

