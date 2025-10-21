#!/usr/bin/env python3
"""
DOWNLOAD AND SAVE FITS FILES
Download Fermi LAT GRB data and save as FITS files
"""

import requests
import os
from pathlib import Path

def download_fits_file(url, filename):
    """Download a FITS file and save it"""
    print(f"Downloading: {filename}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Save file
        with open(filename, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"  Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)")
        
        print(f"  ✅ Saved: {filename} ({downloaded} bytes)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("DOWNLOADING FERMI LAT GRB FITS FILES")
    print("=" * 60)
    
    # GRB URLs and filenames
    grb_files = [
        # GRB090902B
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021181931F357373F30_PH00.fits", "GRB090902B_PH00.fits"),
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021181931F357373F30_SC00.fits", "GRB090902B_SC00.fits"),
        
        # GRB130427A
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182127F357373F16_PH00.fits", "GRB130427A_PH00.fits"),
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182127F357373F16_SC00.fits", "GRB130427A_SC00.fits"),
        
        # GRB160625B
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182503F357373F90_PH00.fits", "GRB160625B_PH00.fits"),
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182503F357373F90_SC00.fits", "GRB160625B_SC00.fits"),
        
        # GRB090926A
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182639F357373F18_PH00.fits", "GRB090926A_PH00.fits"),
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182639F357373F18_SC00.fits", "GRB090926A_SC00.fits"),
        
        # GRB090510
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182806F357373F48_PH00.fits", "GRB090510_PH00.fits"),
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182806F357373F48_SC00.fits", "GRB090510_SC00.fits"),
        
        # GRB080916C
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182937F357373F85_PH00.fits", "GRB080916C_PH00.fits"),
        ("https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251021182937F357373F85_SC00.fits", "GRB080916C_SC00.fits"),
    ]
    
    print(f"Downloading {len(grb_files)} FITS files...")
    
    success_count = 0
    for url, filename in grb_files:
        if download_fits_file(url, filename):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"DOWNLOAD COMPLETE!")
    print(f"Successfully downloaded: {success_count}/{len(grb_files)} files")
    
    if success_count == len(grb_files):
        print("✅ All files downloaded successfully!")
        print("\nNext steps:")
        print("1. Run: python convert_full_fits_to_csv.py")
        print("2. Run: python grb_analysis_with_full_data.py")
    else:
        print(f"❌ {len(grb_files) - success_count} files failed to download")
    
    print("=" * 60)

if __name__ == "__main__":
    main()