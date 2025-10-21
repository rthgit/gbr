#!/usr/bin/env python3
"""
RUN GRB221009A ANALYSIS - Script per eseguire analisi GRB221009A
"""

import subprocess
import sys
import os

def main():
    """Esegue analisi GRB221009A"""
    
    print("🚀 Avvio Analisi GRB221009A (BOAT)...")
    
    # Verifica che il file esista
    if not os.path.exists('analyze_grb221009a.py'):
        print("❌ File analyze_grb221009a.py non trovato!")
        return
    
    try:
        # Esegui il script
        result = subprocess.run([sys.executable, 'analyze_grb221009a.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print("📊 OUTPUT:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ ERRORI:")
            print(result.stderr)
            
        print(f"✅ Completato con exit code: {result.returncode}")
        
        # Verifica file generati
        if os.path.exists('grb221009a_analysis.json'):
            print("✅ File risultati: grb221009a_analysis.json")
        if os.path.exists('grb221009a_analysis.png'):
            print("✅ File grafici: grb221009a_analysis.png")
        
    except Exception as e:
        print(f"❌ Errore esecuzione: {e}")

if __name__ == "__main__":
    main()
