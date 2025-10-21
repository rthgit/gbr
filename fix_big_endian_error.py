#!/usr/bin/env python3
"""
FIX BIG-ENDIAN ERROR
Fix the "Big-endian buffer not supported on little-endian compiler" error
"""

import os
import numpy as np
import pandas as pd
from astropy.io import fits
import struct

def fix_fits_endianness(input_file, output_file):
    """Fix endianness issues in FITS files"""
    
    print(f"Fixing endianness: {input_file} -> {output_file}")
    
    try:
        # Read the FITS file
        with fits.open(input_file) as hdul:
            # Create new HDU list
            new_hdul = fits.HDUList()
            
            # Copy primary HDU (usually just header)
            new_hdul.append(hdul[0])
            
            # Process data HDUs
            for i, hdu in enumerate(hdul[1:], 1):
                print(f"  Processing HDU {i}...")
                
                # Create new data array with correct endianness
                if hdu.data is not None:
                    # Convert to little-endian
                    new_data = hdu.data.astype(hdu.data.dtype.newbyteorder('<'))
                    
                    # Create new HDU with corrected data
                    new_hdu = fits.BinTableHDU(data=new_data, header=hdu.header)
                    new_hdul.append(new_hdu)
                else:
                    # Just copy the HDU if no data
                    new_hdul.append(hdu)
            
            # Write corrected file
            new_hdul.writeto(output_file, overwrite=True)
            print(f"  ✅ Fixed: {output_file}")
            
    except Exception as e:
        print(f"  ❌ Error fixing {input_file}: {e}")
        return False
    
    return True

def convert_fits_to_csv(fits_file, csv_file):
    """Convert FITS file to CSV with proper endianness handling"""
    
    print(f"Converting: {fits_file} -> {csv_file}")
    
    try:
        # Read FITS file
        with fits.open(fits_file) as hdul:
            # Find data HDU (usually HDU 1)
            data_hdu = None
            for hdu in hdul[1:]:
                if hdu.data is not None and len(hdu.data) > 0:
                    data_hdu = hdu
                    break
            
            if data_hdu is None:
                print(f"  ❌ No data found in {fits_file}")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(data_hdu.data)
            
            # Fix any remaining endianness issues
            for col in df.columns:
                if df[col].dtype.kind in ['f', 'i']:  # float or int
                    df[col] = df[col].astype(df[col].dtype.newbyteorder('<'))
            
            # Save as CSV
            df.to_csv(csv_file, index=False)
            print(f"  ✅ Converted: {csv_file}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Error converting {fits_file}: {e}")
        return False

def main():
    """Main function"""
    print("FIX BIG-ENDIAN ERROR")
    print("=" * 50)
    
    # Change to correct directory
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    # Check for GRB data directory
    grb_data_dir = "grb_data"
    if not os.path.exists(grb_data_dir):
        print(f"GRB data directory {grb_data_dir} not found!")
        return
    
    # Find all FITS files
    fits_files = []
    for root, dirs, files in os.walk(grb_data_dir):
        for file in files:
            if file.endswith('.fits'):
                fits_files.append(os.path.join(root, file))
    
    print(f"Found {len(fits_files)} FITS files:")
    for fits_file in fits_files:
        print(f"  - {fits_file}")
    
    if not fits_files:
        print("No FITS files found!")
        return
    
    # Fix each FITS file
    fixed_files = []
    for fits_file in fits_files:
        # Create fixed filename
        base_name = os.path.splitext(fits_file)[0]
        fixed_file = f"{base_name}_fixed.fits"
        
        # Fix endianness
        if fix_fits_endianness(fits_file, fixed_file):
            fixed_files.append(fixed_file)
            
            # Also convert to CSV
            csv_file = f"{base_name}_fixed.csv"
            convert_fits_to_csv(fixed_file, csv_file)
    
    print(f"\n✅ Fixed {len(fixed_files)} FITS files")
    print("Fixed files:")
    for fixed_file in fixed_files:
        print(f"  - {fixed_file}")
    
    print("\nNow you can run the analysis with the fixed files!")

if __name__ == "__main__":
    main()
