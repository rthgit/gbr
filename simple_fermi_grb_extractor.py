#!/usr/bin/env python3
"""
Simple GRB extractor from Fermi LAT catalog
"""

import os
from astropy.io import fits
import pandas as pd

# Change to the correct directory
os.chdir(r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE")

filename = 'gll_psc_v35.fit'

if not os.path.exists(filename):
    print(f"File {filename} not found!")
else:
    print(f"Extracting GRB sources from {filename}...")
    
    # Open FITS file
    with fits.open(filename) as hdul:
        # Main catalog
        hdu = hdul[1]  # LAT_Point_Source_Catalog
        data = hdu.data
        
        print(f"Total sources: {len(data)}")
        
        # Extract basic info for each source
        sources = []
        for i, source in enumerate(data):
            source_info = {
                'Source_Name': source['Source_Name'].decode('utf-8') if isinstance(source['Source_Name'], bytes) else str(source['Source_Name']),
                'RAJ2000': float(source['RAJ2000']),
                'DEJ2000': float(source['DEJ2000']),
                'Signif_Avg': float(source['Signif_Avg']),
                'Energy_Flux100': float(source['Energy_Flux100']),
                'PL_Index': float(source['PL_Index']),
                'Variability_Index': float(source['Variability_Index']),
                'CLASS1': source['CLASS1'].decode('utf-8') if isinstance(source['CLASS1'], bytes) else str(source['CLASS1']),
                'CLASS2': source['CLASS2'].decode('utf-8') if isinstance(source['CLASS2'], bytes) else str(source['CLASS2'])
            }
            sources.append(source_info)
        
        # Create DataFrame
        df = pd.DataFrame(sources)
        
        print(f"DataFrame created with {len(df)} sources")
        
        # Look for GRB sources
        grb_mask = df['Source_Name'].str.contains('GRB', na=False)
        grb_sources = df[grb_mask]
        
        print(f"\nGRB sources found: {len(grb_sources)}")
        
        if len(grb_sources) > 0:
            print("\nGRB sources in Fermi LAT catalog:")
            for i, (idx, row) in enumerate(grb_sources.iterrows()):
                name = row['Source_Name']
                ra = row['RAJ2000']
                dec = row['DEJ2000']
                signif = row['Signif_Avg']
                energy_flux = row['Energy_Flux100']
                pl_index = row['PL_Index']
                var_index = row['Variability_Index']
                class1 = row['CLASS1']
                
                print(f"  {i+1:2d}. {name:15s} RA={ra:8.3f} Dec={dec:8.3f} "
                      f"Signif={signif:6.2f} Flux={energy_flux:8.2e} "
                      f"Index={pl_index:6.2f} Var={var_index:6.2f} Class={class1}")
            
            # Save GRB sources
            grb_sources.to_csv('fermi_grb_sources_from_catalog.csv', index=False)
            print(f"\n✓ GRB sources saved to: fermi_grb_sources_from_catalog.csv")
            
            # Statistics
            print(f"\nGRB Statistics:")
            print(f"  Mean significance: {grb_sources['Signif_Avg'].mean():.2f}")
            print(f"  Max significance: {grb_sources['Signif_Avg'].max():.2f}")
            print(f"  Mean energy flux: {grb_sources['Energy_Flux100'].mean():.2e}")
            print(f"  Mean spectral index: {grb_sources['PL_Index'].mean():.2f}")
        
        # Source types summary
        print(f"\nAll source types in catalog:")
        class_counts = df['CLASS1'].value_counts()
        for class_name, count in class_counts.head(15).items():
            print(f"  {class_name:10s}: {count:4d} sources")
        
        print(f"\n✓ Analysis completed!")
        print(f"✓ Ready for QG analysis on {len(grb_sources)} GRB sources!")
