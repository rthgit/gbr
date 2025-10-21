#!/usr/bin/env python3
"""
CHECK FILES - Controlla file disponibili
"""

import os

def main():
    """Controlla file disponibili"""
    
    print("🔍 Controllo file disponibili...")
    
    # Lista tutti i file
    all_files = os.listdir('.')
    
    # Filtra file FITS
    fits_files = [f for f in all_files if f.endswith('.fits')]
    
    print(f"\n📁 File FITS disponibili ({len(fits_files)}):")
    for i, f in enumerate(sorted(fits_files), 1):
        print(f"  {i:2d}. {f}")
    
    # Cerca file GRB221009A
    grb221009a_files = [f for f in fits_files if 'L25102020315294ADC46894' in f]
    
    print(f"\n🔍 File GRB221009A trovati ({len(grb221009a_files)}):")
    for f in grb221009a_files:
        print(f"  📊 {f}")
    
    # Cerca file GRB090902 per confronto
    grb090902_files = [f for f in fits_files if 'L251020161615F357373F52' in f]
    
    print(f"\n🔍 File GRB090902 trovati ({len(grb090902_files)}):")
    for f in grb090902_files:
        print(f"  📊 {f}")
    
    print(f"\n✅ Totale file FITS: {len(fits_files)}")

if __name__ == "__main__":
    main()