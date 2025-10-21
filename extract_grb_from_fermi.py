#!/usr/bin/env python3
"""
Extract GRB sources from Fermi LAT catalog
Simple version that works with the actual file
"""

import os
import sys
from astropy.io import fits
import pandas as pd

def extract_grb_sources():
    """Extract GRB sources from the Fermi catalog"""
    
    # Change to the correct directory
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    current_dir = os.getcwd()
    print(f"Changed to directory: {current_dir}")
    
    # Look for the file
    filename = 'gll_psc_v35.fit'
    
    if not os.path.exists(filename):
        print(f"File {filename} not found in current directory!")
        print("Available files:")
        for f in os.listdir('.'):
            if f.endswith('.fit') or f.endswith('.fits'):
                print(f"  - {f}")
        return None
    
    print(f"Found file: {filename}")
    print("Opening Fermi LAT catalog...")
    
    try:
        # Open FITS file
        with fits.open(filename) as hdul:
            print(f"Number of HDUs: {len(hdul)}")
            
            # Get main catalog (HDU 1)
            hdu = hdul[1]  # LAT_Point_Source_Catalog
            data = hdu.data
            
            print(f"Total sources: {len(data)}")
            print(f"Data type: {data.dtype}")
            
            # Extract GRB sources directly
            grb_sources = []
            
            for i, source in enumerate(data):
                # Handle both string and bytes
                source_name = source['Source_Name']
                if isinstance(source_name, bytes):
                    source_name = source_name.decode('utf-8').strip()
                else:
                    source_name = str(source_name).strip()
                
                if 'GRB' in source_name:
                    # Handle CLASS1 field
                    class1 = source['CLASS1']
                    if isinstance(class1, bytes):
                        class1 = class1.decode('utf-8').strip()
                    else:
                        class1 = str(class1).strip()
                    
                    grb_info = {
                        'Source_Name': source_name,
                        'RAJ2000': float(source['RAJ2000']),
                        'DEJ2000': float(source['DEJ2000']),
                        'Signif_Avg': float(source['Signif_Avg']),
                        'Energy_Flux100': float(source['Energy_Flux100']),
                        'PL_Index': float(source['PL_Index']),
                        'Variability_Index': float(source['Variability_Index']),
                        'CLASS1': class1 if class1 else 'Unknown'
                    }
                    grb_sources.append(grb_info)
            
            print(f"\nGRB sources found: {len(grb_sources)}")
            
            if len(grb_sources) > 0:
                # Create DataFrame
                df_grb = pd.DataFrame(grb_sources)
                
                print("\nGRB sources in Fermi LAT catalog:")
                print("=" * 80)
                for i, (idx, row) in enumerate(df_grb.iterrows()):
                    print(f"{i+1:2d}. {row['Source_Name']:15s} "
                          f"RA={row['RAJ2000']:8.3f} Dec={row['DEJ2000']:8.3f} "
                          f"Signif={row['Signif_Avg']:6.2f} "
                          f"Flux={row['Energy_Flux100']:8.2e} "
                          f"Var={row['Variability_Index']:6.2f} "
                          f"Class={row['CLASS1']}")
                
                # Save to CSV
                df_grb.to_csv('fermi_grb_sources.csv', index=False)
                print(f"\n✓ GRB sources saved to: fermi_grb_sources.csv")
                
                # Summary statistics
                print(f"\nSummary:")
                print(f"  Total GRB sources: {len(df_grb)}")
                print(f"  Mean significance: {df_grb['Signif_Avg'].mean():.2f}")
                print(f"  Max significance: {df_grb['Signif_Avg'].max():.2f}")
                print(f"  Min significance: {df_grb['Signif_Avg'].min():.2f}")
                
                # Class distribution
                class_counts = df_grb['CLASS1'].value_counts()
                print(f"\nGRB classifications:")
                for class_name, count in class_counts.items():
                    print(f"  {class_name}: {count}")
                
                return df_grb
            else:
                print("No GRB sources found in catalog!")
                return None
                
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

def main():
    """Main function"""
    print("Fermi LAT GRB Source Extractor")
    print("=" * 50)
    
    grb_df = extract_grb_sources()
    
    if grb_df is not None:
        print("\n" + "=" * 50)
        print("EXTRACTION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Found {len(grb_df)} GRB sources in Fermi LAT catalog")
        print("Ready for QG analysis on real GRB data!")
        print("=" * 50)

if __name__ == "__main__":
    main()
