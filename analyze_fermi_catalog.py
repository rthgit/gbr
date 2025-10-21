#!/usr/bin/env python3
"""
Analyze Fermi LAT Catalog File
Read and examine the structure of gll_psc_v35.fit
"""

import os
from astropy.io import fits
import pandas as pd
import numpy as np

def analyze_fermi_catalog(filename):
    """Analyze the Fermi LAT catalog file"""
    
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        return None
    
    print(f"Analyzing Fermi LAT catalog: {filename}")
    print("=" * 60)
    
    try:
        # Open FITS file
        with fits.open(filename) as hdul:
            print(f"Number of HDUs: {len(hdul)}")
            print()
            
            # Examine each HDU
            for i, hdu in enumerate(hdul):
                print(f"HDU {i}: {hdu.name}")
                print(f"  Type: {type(hdu).__name__}")
                
                if hdu.data is not None:
                    print(f"  Data shape: {hdu.data.shape}")
                    print(f"  Data type: {hdu.data.dtype}")
                    
                    if hasattr(hdu.data, 'dtype') and hdu.data.dtype.names:
                        print(f"  Columns: {len(hdu.data.dtype.names)}")
                        print("  Column names:")
                        for j, col_name in enumerate(hdu.data.dtype.names[:10]):
                            print(f"    {j+1:2d}. {col_name}")
                        if len(hdu.data.dtype.names) > 10:
                            print(f"    ... and {len(hdu.data.dtype.names)-10} more")
                    else:
                        print(f"  Data preview: {hdu.data[:5] if len(hdu.data) > 0 else 'Empty'}")
                else:
                    print("  No data")
                
                # Show header info
                if hdu.header:
                    print(f"  Header cards: {len(hdu.header)}")
                    print("  Important header info:")
                    important_keys = ['EXTNAME', 'NAXIS1', 'NAXIS2', 'TFORM1', 'TTYPE1', 'TUNIT1']
                    for key in important_keys:
                        if key in hdu.header:
                            print(f"    {key}: {hdu.header[key]}")
                
                print()
            
            # Focus on the main data table (usually HDU 1)
            if len(hdul) > 1 and hdul[1].data is not None:
                print("=" * 60)
                print("MAIN DATA TABLE ANALYSIS")
                print("=" * 60)
                
                data = hdul[1].data
                print(f"Total sources: {len(data)}")
                print()
                
                # Convert to pandas for easier analysis
                df = pd.DataFrame(data)
                print("Column information:")
                for i, col in enumerate(df.columns):
                    print(f"  {i+1:2d}. {col:20s} - {df[col].dtype}")
                
                print()
                
                # Look for GRB sources
                if 'Source_Name' in df.columns:
                    grb_mask = df['Source_Name'].astype(str).str.contains('GRB', na=False)
                    grb_sources = df[grb_mask]
                    print(f"GRB sources found: {len(grb_sources)}")
                    
                    if len(grb_sources) > 0:
                        print("\nFirst 10 GRB sources:")
                        for i, (idx, row) in enumerate(grb_sources.head(10).iterrows()):
                            name = row['Source_Name']
                            ra = row.get('RAJ2000', 'N/A')
                            dec = row.get('DEJ2000', 'N/A')
                            ts = row.get('Signif_Avg', 'N/A')
                            print(f"  {i+1:2d}. {name:15s} RA={ra:8.3f} Dec={dec:8.3f} TS={ts}")
                
                # Look for other important columns
                print("\nKey columns for QG analysis:")
                key_columns = ['Source_Name', 'RAJ2000', 'DEJ2000', 'Signif_Avg', 'Energy_Flux', 'Spectral_Index']
                for col in key_columns:
                    if col in df.columns:
                        print(f"  ✓ {col}")
                    else:
                        print(f"  ✗ {col} (not found)")
                
                return df
                
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        return None

def main():
    """Main function"""
    filename = 'gll_psc_v35.fit'
    
    if not os.path.exists(filename):
        print(f"File {filename} not found in current directory!")
        print("Available files:")
        for f in os.listdir('.'):
            if f.endswith('.fit') or f.endswith('.fits'):
                print(f"  - {f}")
        return
    
    # Analyze the catalog
    df = analyze_fermi_catalog(filename)
    
    if df is not None:
        print("=" * 60)
        print("ANALYSIS COMPLETED")
        print("=" * 60)
        print("This catalog contains:")
        print(f"  - Total sources: {len(df)}")
        
        if 'Source_Name' in df.columns:
            grb_count = len(df[df['Source_Name'].astype(str).str.contains('GRB', na=False)])
            print(f"  - GRB sources: {grb_count}")
        
        print("\nReady for QG analysis!")

if __name__ == "__main__":
    main()
