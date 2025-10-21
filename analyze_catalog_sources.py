#!/usr/bin/env python3
"""
Analyze all sources in Fermi LAT catalog to find GRBs
"""

import os
from astropy.io import fits
import pandas as pd
import numpy as np

def analyze_catalog_sources():
    """Analyze all sources to find GRBs and other transient sources"""
    
    # Change to the correct directory
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    filename = 'gll_psc_v35.fit'
    
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        return None
    
    print(f"Analyzing {filename}...")
    
    try:
        with fits.open(filename) as hdul:
            hdu = hdul[1]  # LAT_Point_Source_Catalog
            data = hdu.data
            
            print(f"Total sources: {len(data)}")
            
            # Analyze source names and classifications
            source_names = []
            classifications = []
            significances = []
            energy_fluxes = []
            variability_indices = []
            
            for source in data:
                # Handle source name
                source_name = source['Source_Name']
                if isinstance(source_name, bytes):
                    source_name = source_name.decode('utf-8').strip()
                else:
                    source_name = str(source_name).strip()
                
                # Handle classification
                class1 = source['CLASS1']
                if isinstance(class1, bytes):
                    class1 = class1.decode('utf-8').strip()
                else:
                    class1 = str(class1).strip()
                
                source_names.append(source_name)
                classifications.append(class1)
                significances.append(float(source['Signif_Avg']))
                energy_fluxes.append(float(source['Energy_Flux100']))
                variability_indices.append(float(source['Variability_Index']))
            
            # Create DataFrame
            df = pd.DataFrame({
                'Source_Name': source_names,
                'CLASS1': classifications,
                'Signif_Avg': significances,
                'Energy_Flux100': energy_fluxes,
                'Variability_Index': variability_indices
            })
            
            print("\nSource classifications:")
            class_counts = df['CLASS1'].value_counts()
            for class_name, count in class_counts.head(20).items():
                print(f"  {class_name:15s}: {count:4d} sources")
            
            # Look for transient or variable sources
            print(f"\nHigh variability sources (Var_Index > 100):")
            high_var = df[df['Variability_Index'] > 100]
            print(f"Found {len(high_var)} highly variable sources")
            
            if len(high_var) > 0:
                print("\nTop 20 most variable sources:")
                top_var = high_var.nlargest(20, 'Variability_Index')
                for i, (idx, row) in enumerate(top_var.iterrows()):
                    print(f"  {i+1:2d}. {row['Source_Name']:18s} "
                          f"Var={row['Variability_Index']:8.2f} "
                          f"Class={row['CLASS1']:8s} "
                          f"Signif={row['Signif_Avg']:6.2f}")
            
            # Look for sources with "GRB" in name (case insensitive)
            grb_mask = df['Source_Name'].str.contains('GRB', case=False, na=False)
            grb_sources = df[grb_mask]
            print(f"\nSources with 'GRB' in name: {len(grb_sources)}")
            
            # Look for sources with "Burst" in name
            burst_mask = df['Source_Name'].str.contains('Burst', case=False, na=False)
            burst_sources = df[burst_mask]
            print(f"Sources with 'Burst' in name: {len(burst_sources)}")
            
            # Look for sources with date-like patterns (YYYYMMDD)
            date_mask = df['Source_Name'].str.contains(r'\d{8}', na=False)
            date_sources = df[date_mask]
            print(f"Sources with date pattern: {len(date_sources)}")
            
            # Look for unassociated sources (might be GRBs)
            unassociated = df[df['CLASS1'] == '']
            print(f"Unassociated sources: {len(unassociated)}")
            
            if len(unassociated) > 0:
                print("\nTop 20 unassociated sources by significance:")
                top_unassoc = unassociated.nlargest(20, 'Signif_Avg')
                for i, (idx, row) in enumerate(top_unassoc.iterrows()):
                    print(f"  {i+1:2d}. {row['Source_Name']:18s} "
                          f"Signif={row['Signif_Avg']:6.2f} "
                          f"Flux={row['Energy_Flux100']:8.2e}")
            
            # Look for sources with high significance and high variability
            high_sig_var = df[(df['Signif_Avg'] > 20) & (df['Variability_Index'] > 50)]
            print(f"\nHigh significance + high variability sources: {len(high_sig_var)}")
            
            if len(high_sig_var) > 0:
                print("\nHigh sig + var sources:")
                for i, (idx, row) in enumerate(high_sig_var.head(20).iterrows()):
                    print(f"  {i+1:2d}. {row['Source_Name']:18s} "
                          f"Signif={row['Signif_Avg']:6.2f} "
                          f"Var={row['Variability_Index']:6.2f} "
                          f"Class={row['CLASS1']}")
            
            # Save results
            df.to_csv('fermi_catalog_all_sources.csv', index=False)
            print(f"\nAll sources saved to: fermi_catalog_all_sources.csv")
            
            if len(high_var) > 0:
                high_var.to_csv('fermi_high_variability_sources.csv', index=False)
                print(f"High variability sources saved to: fermi_high_variability_sources.csv")
            
            if len(unassociated) > 0:
                unassociated.to_csv('fermi_unassociated_sources.csv', index=False)
                print(f"Unassociated sources saved to: fermi_unassociated_sources.csv")
            
            return df
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """Main function"""
    print("Fermi LAT Catalog Source Analyzer")
    print("=" * 50)
    
    df = analyze_catalog_sources()
    
    if df is not None:
        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETED!")
        print("=" * 50)
        print(f"Analyzed {len(df)} sources from Fermi LAT catalog")
        print("Check CSV files for detailed results")
        print("=" * 50)

if __name__ == "__main__":
    main()
