#!/usr/bin/env python3
"""
Script per eseguire analisi batch GRB
Bypass PowerShell issues
"""

import subprocess
import sys
import os

def run_batch_analysis():
    """Esegui analisi batch GRB"""
    print("🚀 Eseguendo analisi batch GRB...")
    
    try:
        # Esegui batch_grb_analyzer.py
        result = subprocess.run([sys.executable, "batch_grb_analyzer.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Analisi batch completata con successo!")
        else:
            print("❌ Errore nell'analisi batch")
            
    except Exception as e:
        print(f"❌ Errore nell'esecuzione: {e}")

if __name__ == "__main__":
    run_batch_analysis()