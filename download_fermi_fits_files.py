#!/usr/bin/env python3
"""
DOWNLOAD FERMI FITS FILES
=========================

Download i file FITS reali da Fermi LAT usando Python.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import os
import requests
import time
from datetime import datetime

def download_fermi_fits_file(url, filename):
    """
    Download un file FITS da Fermi LAT
    """
    print(f"🛰️ Downloading {filename}...")
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            # Salva il file
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"   ✅ {filename}: {file_size:,} bytes downloaded")
            return True
        else:
            print(f"   ❌ {filename}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ {filename}: {e}")
        return False

def download_all_fermi_fits():
    """
    Download tutti i file FITS di Fermi LAT
    """
    print("🚀 DOWNLOAD FERMI FITS FILES")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Lista dei file FITS da scaricare
    fits_files = [
        # GRB221009A
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103213F357373F22_PH00.fits', 'L251021103213F357373F22_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103213F357373F22_SC00.fits', 'L251021103213F357373F22_SC00.fits'),
        
        # GRB190114C
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103308F357373F87_PH00.fits', 'L251021103308F357373F87_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103308F357373F87_SC00.fits', 'L251021103308F357373F87_SC00.fits'),
        
        # GRB090510
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103420F357373F11_PH00.fits', 'L251021103420F357373F11_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103420F357373F11_SC00.fits', 'L251021103420F357373F11_SC00.fits'),
        
        # GRB180720B
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103510F357373F22_PH00.fits', 'L251021103510F357373F22_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103510F357373F22_SC00.fits', 'L251021103510F357373F22_SC00.fits'),
        
        # GRB160625B
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103601F357373F17_PH00.fits', 'L251021103601F357373F17_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021103601F357373F17_SC00.fits', 'L251021103601F357373F17_SC00.fits')
    ]
    
    # Download tutti i file
    success_count = 0
    total_count = len(fits_files)
    
    for i, (url, filename) in enumerate(fits_files, 1):
        print(f"\n📊 Downloading {i}/{total_count}...")
        
        if download_fermi_fits_file(url, filename):
            success_count += 1
        
        # Pausa tra download
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"🎉 DOWNLOAD COMPLETE!")
    print(f"📊 Successfully downloaded: {success_count}/{total_count} files")
    print("=" * 60)
    
    return success_count == total_count

if __name__ == "__main__":
    download_all_fermi_fits()
