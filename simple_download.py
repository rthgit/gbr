#!/usr/bin/env python3
"""
Download semplice dei file GRB usando Python
"""

import urllib.request
import os

def download_file(url, filename):
    """Scarica un file da URL"""
    try:
        print(f"Scaricando {filename}...")
        urllib.request.urlretrieve(url, filename)
        size = os.path.getsize(filename)
        print(f"✅ {filename} scaricato ({size/1024:.1f} KB)")
        return True
    except Exception as e:
        print(f"❌ Errore nel download di {filename}: {e}")
        return False

def main():
    print("="*60)
    print("DOWNLOAD GRB REALI FERMI LAT")
    print("="*60)
    
    # URL dei file da scaricare
    files_to_download = [
        {
            'url': 'https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161615F357373F52_EV00.fits',
            'filename': 'L251020161615F357373F52_EV00.fits',
            'description': 'GRB090902 (3972 fotoni)'
        },
        {
            'url': 'https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161912F357373F19_EV00.fits',
            'filename': 'L251020161912F357373F19_EV00.fits',
            'description': 'GRB090510 (2371 fotoni)'
        },
        {
            'url': 'https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020162012F357373F30_EV00.fits',
            'filename': 'L251020162012F357373F30_EV00.fits',
            'description': 'GRB130427A (16 fotoni)'
        }
    ]
    
    # Scarica tutti i file
    success_count = 0
    for file_info in files_to_download:
        print(f"\n{file_info['description']}:")
        if download_file(file_info['url'], file_info['filename']):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"DOWNLOAD COMPLETATO: {success_count}/{len(files_to_download)} file")
    print(f"{'='*60}")
    
    # Verifica file esistenti
    print("\nVERIFICA FILE DISPONIBILI:")
    all_files = [
        'L251020154246F357373F64_EV00.fits',  # GRB080916C
        'L251020161615F357373F52_EV00.fits',  # GRB090902
        'L251020161912F357373F19_EV00.fits',  # GRB090510
        'L251020162012F357373F30_EV00.fits'   # GRB130427A
    ]
    
    for filename in all_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({size/1024:.1f} KB)")
        else:
            print(f"❌ {filename} (MANCANTE)")
    
    print(f"\n🎯 PRONTO PER ANALISI MULTI-GRB!")

if __name__ == "__main__":
    main()

