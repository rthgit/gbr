#!/usr/bin/env python3
"""
DOWNLOAD AND SAVE FITS FILES
=============================

Download e salva i file FITS reali da Fermi LAT.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import os
import requests
import time
from datetime import datetime

def download_and_save_fits(url, filename):
    """
    Download e salva un file FITS
    """
    print(f"🛰️ Downloading {filename}...")
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            # Salva il file
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"   ✅ {filename}: {file_size:,} bytes downloaded and saved")
            return True
        else:
            print(f"   ❌ {filename}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ {filename}: {e}")
        return False

def download_all_anomalous_fits():
    """
    Download tutti i file FITS anomali
    """
    print("🚀 DOWNLOAD AND SAVE ANOMALOUS FITS FILES")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Lista dei file FITS da scaricare
    fits_files = [
        # GRB221009A
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021105813F357373F65_PH00.fits', 'L251021105813F357373F65_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021105813F357373F65_SC00.fits', 'L251021105813F357373F65_SC00.fits'),
        
        # GRB190114C
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021105939F357373F58_PH00.fits', 'L251021105939F357373F58_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021105939F357373F58_SC00.fits', 'L251021105939F357373F58_SC00.fits'),
        
        # GRB090926A
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110034F357373F27_PH00.fits', 'L251021110034F357373F27_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110034F357373F27_SC00.fits', 'L251021110034F357373F27_SC00.fits'),
        
        # GRB160625B
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110134F357373F33_PH00.fits', 'L251021110134F357373F33_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110134F357373F33_SC00.fits', 'L251021110134F357373F33_SC00.fits'),
        
        # GRB180720B
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110233F357373F36_PH00.fits', 'L251021110233F357373F36_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110233F357373F36_SC00.fits', 'L251021110233F357373F36_SC00.fits'),
        
        # GRB131231A
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110325F357373F43_PH00.fits', 'L251021110325F357373F43_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110325F357373F43_SC00.fits', 'L251021110325F357373F43_SC00.fits'),
        
        # GRB130427A
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110442F357373F27_PH00.fits', 'L251021110442F357373F27_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110442F357373F27_SC00.fits', 'L251021110442F357373F27_SC00.fits'),
        
        # GRB190829A
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110535F357373F42_PH00.fits', 'L251021110535F357373F42_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110535F357373F42_SC00.fits', 'L251021110535F357373F42_SC00.fits'),
        
        # GRB080916C
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110629F357373F55_PH00.fits', 'L251021110629F357373F55_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110629F357373F55_SC00.fits', 'L251021110629F357373F55_SC00.fits'),
        
        # GRB091024
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110739F357373F39_PH00.fits', 'L251021110739F357373F39_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110739F357373F39_SC00.fits', 'L251021110739F357373F39_SC00.fits'),
        
        # GRB090323
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110835F357373F04_SC00.fits', 'L251021110835F357373F04_SC00.fits'),
        
        # GRB240825A
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110941F357373F53_PH00.fits', 'L251021110941F357373F53_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021110941F357373F53_SC00.fits', 'L251021110941F357373F53_SC00.fits'),
        
        # GRB090820
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021111027F357373F43_PH00.fits', 'L251021111027F357373F43_PH00.fits'),
        ('https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021111027F357373F43_SC00.fits', 'L251021111027F357373F43_SC00.fits')
    ]
    
    # Download tutti i file
    success_count = 0
    total_count = len(fits_files)
    
    for i, (url, filename) in enumerate(fits_files, 1):
        print(f"\n📊 Downloading {i}/{total_count}...")
        
        if download_and_save_fits(url, filename):
            success_count += 1
        
        # Pausa tra download
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"🎉 DOWNLOAD COMPLETE!")
    print(f"📊 Successfully downloaded: {success_count}/{total_count} files")
    print("=" * 60)
    
    return success_count == total_count

if __name__ == "__main__":
    download_all_anomalous_fits()
