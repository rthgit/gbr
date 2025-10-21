#!/usr/bin/env python3
"""
Analyze Fermi LAT Catalog File - Fixed Version
Handle multi-dimensional arrays properly
"""

import os
from astropy.io import fits
import pandas as pd
import numpy as np

def analyze_fermi_catalog_fixed(filename):
    """Analyze the Fermi LAT catalog file with proper array handling"""
    
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
            
            # Focus on main catalog (HDU 1)
            if len(hdul) > 1:
                hdu = hdul[1]  # LAT_Point_Source_Catalog
                data = hdu.data
                
                print(f"Main catalog: {len(data)} sources")
                print(f"Columns: {len(data.dtype.names)}")
                print()
                
                # Convert to DataFrame handling multi-dimensional arrays
                df_data = {}
                for col_name in data.dtype.names:
                    col_data = data[col_name]
                    
                    # Handle multi-dimensional arrays
                    if col_data.ndim > 1:
                        # For arrays like Flux_Band (8,) and Flux_History (14,)
                        if col_data.shape[1] <= 20:  # Reasonable size
                            # Create separate columns for each element
                            for i in range(col_data.shape[1]):
                                df_data[f"{col_name}_{i}"] = col_data[:, i]
                        else:
                            # For very large arrays, just take first element
                            df_data[col_name] = col_data[:, 0]
                    else:
                        df_data[col_name] = col_data
                
                # Create DataFrame
                df = pd.DataFrame(df_data)
                
                print("Key columns for QG analysis:")
                key_columns = ['Source_Name', 'RAJ2000', 'DEJ2000', 'Signif_Avg', 
                             'Energy_Flux100', 'PL_Index', 'Variability_Index', 'CLASS1']
                
                for col in key_columns:
                    if col in df.columns:
                        print(f"  ✓ {col}")
                    else:
                        print(f"  ✗ {col} (not found)")
                
                print()
                
                # Look for GRB sources
                if 'Source_Name' in df.columns:
                    grb_mask = df['Source_Name'].astype(str).str.contains('GRB', na=False)
                    grb_sources = df[grb_mask]
                    print(f"GRB sources found: {len(grb_sources)}")
                    
                    if len(grb_sources) > 0:
                        print("\nGRB sources in catalog:")
                        for i, (idx, row) in enumerate(grb_sources.head(20).iterrows()):
                            name = row['Source_Name']
                            ra = row.get('RAJ2000', 'N/A')
                            dec = row.get('DEJ2000', 'N/A')
                            signif = row.get('Signif_Avg', 'N/A')
                            energy_flux = row.get('Energy_Flux100', 'N/A')
                            var_index = row.get('Variability_Index', 'N/A')
                            class1 = row.get('CLASS1', 'N/A')
                            
                            print(f"  {i+1:2d}. {name:15s} RA={ra:8.3f} Dec={dec:8.3f} "
                                  f"Signif={signif:6.2f} Flux={energy_flux:8.2e} "
                                  f"Var={var_index:6.2f} Class={class1}")
                        
                        if len(grb_sources) > 20:
                            print(f"  ... and {len(grb_sources)-20} more GRB sources")
                
                # Analyze source types
                if 'CLASS1' in df.columns:
                    print(f"\nSource classification:")
                    class_counts = df['CLASS1'].value_counts()
                    for class_name, count in class_counts.head(10).items():
                        print(f"  {class_name:10s}: {count:4d} sources")
                
                # Analyze significance distribution
                if 'Signif_Avg' in df.columns:
                    print(f"\nSignificance statistics:")
                    signif_stats = df['Signif_Avg'].describe()
                    print(f"  Mean: {signif_stats['mean']:.2f}")
                    print(f"  Median: {signif_stats['50%']:.2f}")
                    print(f"  Max: {signif_stats['max']:.2f}")
                    print(f"  Min: {signif_stats['min']:.2f}")
                
                # Save GRB sources for QG analysis
                if len(grb_sources) > 0:
                    grb_sources.to_csv('fermi_grb_sources_from_catalog.csv', index=False)
                    print(f"\n✓ GRB sources saved to: fermi_grb_sources_from_catalog.csv")
                
                return df, grb_sources
                
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        return None, None

def main():
    """Main function"""
    filename = r'C:\Users\PC\Desktop\VELOCITA\' DELLA LUCE\gll_psc_v35.fit'
    
    if not os.path.exists(filename):
        print(f"File {filename} not found in current directory!")
        return
    
    # Analyze the catalog
    df, grb_sources = analyze_fermi_catalog_fixed(filename)
    
    if df is not None:
        print("\n" + "=" * 60)
        print("FERMI LAT CATALOG ANALYSIS COMPLETED")
        print("=" * 60)
        print(f"Total sources in catalog: {len(df)}")
        if grb_sources is not None:
            print(f"GRB sources found: {len(grb_sources)}")
        print("\nReady for QG analysis on real GRB data!")
        print("=" * 60)

if __name__ == "__main__":
    main()
