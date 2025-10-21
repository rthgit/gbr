#!/usr/bin/env python3
"""
TEST DIRETTO PER METODOLOGIA AVANZATA
====================================

Esegue direttamente il test senza problemi PowerShell
"""

import sys
import os

# Aggiungi il percorso corrente
sys.path.insert(0, os.getcwd())

# Importa ed esegue il test
try:
    from advanced_methodology_test import main
    print("="*70)
    print("ESECUZIONE DIRETTA TEST METODOLOGIA AVANZATA")
    print("="*70)
    main()
except Exception as e:
    print(f"Errore: {e}")
    import traceback
    traceback.print_exc()

