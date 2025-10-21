#!/usr/bin/env python3
"""
Script download automatico - Nessuna registrazione richiesta
"""

import sys
import os
from auto_downloader import AutoDownloader

def main():
    print("DOWNLOAD AUTOMATICO - ACCESSO DIRETTO")
    print("="*50)
    
    downloader = AutoDownloader()
    
    # Test accesso diretto
    results = downloader.test_direct_access()
    
    # Conta successi
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nRISULTATO: {success_count}/{total_count} API accessibili")
    
    if success_count >= 3:
        print("OK: ACCESSO DIRETTO SUFFICIENTE!")
        print("   Puoi scaricare dati senza registrazione")
    else:
        print("WARNING: REGISTRAZIONE RACCOMANDATA")
        print("   Registrati per accesso completo")
    
    print("\nPer registrazione gratuita:")
    print("   python auto_downloader.py --guide")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--guide":
        downloader = AutoDownloader()
        downloader.create_registration_guide()
    else:
        main()
