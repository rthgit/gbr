#!/usr/bin/env python3
"""
CONVERT FULL FITS FILES TO CSV
Convert the newly downloaded FITS files to CSV format for analysis
"""

import os
import pandas as pd
from astropy.io import fits
from pathlib import Path
import numpy as np

def convert_fits_to_csv(fits_file, csv_file):
    """Convert a FITS file to CSV"""
    print(f"Converting: {fits_file}")
    
    try:
        # Open FITS file
        with fits.open(fits_file) as hdu_list:
            # Get data from HDU 1 (event data)
            data = hdu_list[1].data
            
            # Extract relevant columns
            df = pd.DataFrame({
                'ENERGY': data['ENERGY'],
                'TIME': data['TIME'],
                'RA': data['RA'],
                'DEC': data['DEC']
            })
            
            # Save to CSV
            df.to_csv(csv_file, index=False)
            
            print(f"  ✅ Converted: {csv_file}")
            print(f"  Photons: {len(df)}")
            print(f"  Energy range: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
            print(f"  Time range: {df['TIME'].min():.1f} - {df['TIME'].max():.1f} s")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("CONVERTING FULL FITS FILES TO CSV")
    print("=" * 60)
    
    # List of FITS files to convert
    fits_files = [
        "GRB090902B_PH00.fits",
        "GRB090902B_SC00.fits",
        "GRB130427A_PH00.fits",
        "GRB130427A_SC00.fits",
        "GRB160625B_PH00.fits",
        "GRB160625B_SC00.fits",
        "GRB090926A_PH00.fits",
        "GRB090926A_SC00.fits",
        "GRB090510_PH00.fits",
        "GRB090510_SC00.fits",
        "GRB080916C_PH00.fits",
        "GRB080916C_SC00.fits"
    ]
    
    print(f"Converting {len(fits_files)} FITS files...")
    
    success_count = 0
    for fits_file in fits_files:
        if os.path.exists(fits_file):
            csv_file = fits_file.replace('.fits', '.csv')
            if convert_fits_to_csv(fits_file, csv_file):
                success_count += 1
            print()
        else:
            print(f"❌ File not found: {fits_file}")
    
    print("=" * 60)
    print(f"CONVERSION COMPLETE!")
    print(f"Successfully converted: {success_count}/{len(fits_files)} files")
    
    if success_count == len(fits_files):
        print("✅ All files converted successfully!")
        print("\nNext step:")
        print("Run: python grb_analysis_with_full_data.py")
    else:
        print(f"❌ {len(fits_files) - success_count} files failed to convert")
    
    print("=" * 60)

if __name__ == "__main__":
    main()