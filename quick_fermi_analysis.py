#!/usr/bin/env python3
"""
Quick analysis of Fermi LAT catalog
"""

import os
from astropy.io import fits
import pandas as pd

# Change to the correct directory
os.chdir(r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE")

filename = 'gll_psc_v35.fit'

if not os.path.exists(filename):
    print(f"File {filename} not found!")
    print("Available files:")
    for f in os.listdir('.'):
        if f.endswith('.fit') or f.endswith('.fits'):
            print(f"  - {f}")
else:
    print(f"Analyzing {filename}...")
    
    # Open FITS file
    with fits.open(filename) as hdul:
        print(f"Number of HDUs: {len(hdul)}")
        
        # Main catalog
        hdu = hdul[1]  # LAT_Point_Source_Catalog
        data = hdu.data
        
        print(f"Total sources: {len(data)}")
        print(f"Columns: {len(data.dtype.names)}")
        
        # Convert to DataFrame
        df_data = {}
        for col_name in data.dtype.names:
            col_data = data[col_name]
            
            if col_data.ndim > 1:
                # Handle multi-dimensional arrays
                if col_data.shape[1] <= 20:
                    for i in range(col_data.shape[1]):
                        df_data[f"{col_name}_{i}"] = col_data[:, i]
                else:
                    df_data[col_name] = col_data[:, 0]
            else:
                df_data[col_name] = col_data
        
        df = pd.DataFrame(df_data)
        
        # Look for GRB sources
        if 'Source_Name' in df.columns:
            grb_mask = df['Source_Name'].astype(str).str.contains('GRB', na=False)
            grb_sources = df[grb_mask]
            
            print(f"\nGRB sources found: {len(grb_sources)}")
            
            if len(grb_sources) > 0:
                print("\nFirst 20 GRB sources:")
                for i, (idx, row) in enumerate(grb_sources.head(20).iterrows()):
                    name = row['Source_Name']
                    ra = row.get('RAJ2000', 'N/A')
                    dec = row.get('DEJ2000', 'N/A')
                    signif = row.get('Signif_Avg', 'N/A')
                    
                    print(f"  {i+1:2d}. {name:15s} RA={ra:8.3f} Dec={dec:8.3f} Signif={signif:6.2f}")
                
                # Save GRB sources
                grb_sources.to_csv('fermi_grb_sources_from_catalog.csv', index=False)
                print(f"\nGRB sources saved to: fermi_grb_sources_from_catalog.csv")
        
        # Source types
        if 'CLASS1' in df.columns:
            print(f"\nSource types:")
            class_counts = df['CLASS1'].value_counts()
            for class_name, count in class_counts.head(10).items():
                print(f"  {class_name:10s}: {count:4d}")
        
        print("\nAnalysis completed!")