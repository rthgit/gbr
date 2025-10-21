#!/usr/bin/env python3
"""
ANALYZE REAL FERMI CATALOG
Using the ACTUAL Fermi LAT catalog data - NO SIMULATIONS!
Extracting ALL information without loss
"""

import os
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
from datetime import datetime
from astropy.io import fits

def load_fermi_catalog_complete():
    """Load the complete Fermi catalog with ALL information"""
    
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    print("LOADING COMPLETE FERMI CATALOG - NO SIMULATIONS!")
    print("=" * 60)
    
    fermi_catalog_file = 'gll_psc_v35.fit'
    if not os.path.exists(fermi_catalog_file):
        print(f"Fermi catalog file {fermi_catalog_file} not found!")
        return None
    
    print(f"Loading Fermi catalog: {fermi_catalog_file}")
    
    try:
        with fits.open(fermi_catalog_file) as hdul:
            # Get the main catalog data
            catalog_data = hdul[1].data
            
            print(f"Catalog loaded successfully!")
            print(f"  - Total sources: {len(catalog_data)}")
            print(f"  - Data type: {catalog_data.dtype}")
            print(f"  - Column names: {list(catalog_data.dtype.names)}")
            
            # Extract ALL columns without loss
            catalog_dict = {}
            for col_name in catalog_data.dtype.names:
                col_data = catalog_data[col_name]
                print(f"  - {col_name}: shape={col_data.shape}, dtype={col_data.dtype}")
                
                # Store the raw data - no conversion to DataFrame yet
                catalog_dict[col_name] = col_data
            
            return catalog_dict, catalog_data, hdul
            
    except Exception as e:
        print(f"Error loading Fermi catalog: {e}")
        return None, None, None

def extract_all_source_information(catalog_dict):
    """Extract ALL source information from the catalog"""
    
    print("\nEXTRACTING ALL SOURCE INFORMATION")
    print("=" * 60)
    
    # Get basic information for all sources
    source_info = []
    
    n_sources = len(catalog_dict['Source_Name'])
    print(f"Processing {n_sources} sources...")
    
    for i in range(n_sources):
        source_data = {}
        
        # Basic identification
        source_data['index'] = i
        source_data['source_name'] = str(catalog_dict['Source_Name'][i]).strip()
        
        # Position
        source_data['ra'] = catalog_dict['RAJ2000'][i]
        source_data['dec'] = catalog_dict['DEJ2000'][i]
        source_data['glon'] = catalog_dict['GLON'][i]
        source_data['glat'] = catalog_dict['GLAT'][i]
        
        # Flux and significance
        source_data['energy_flux'] = catalog_dict['Energy_Flux100'][i]
        source_data['flux_uncertainty'] = catalog_dict['Unc_Energy_Flux100'][i]
        source_data['significance'] = catalog_dict['Signif_Avg'][i]
        source_data['significance_peak'] = catalog_dict['Signif_Peak'][i]
        
        # Variability
        source_data['variability_index'] = catalog_dict['Variability_Index'][i]
        source_data['frac_variability'] = catalog_dict['Frac_Variability'][i]
        
        # Spectral information
        source_data['spectrum_type'] = str(catalog_dict['SpectrumType'][i]).strip()
        source_data['pl_index'] = catalog_dict['PL_Index'][i]
        source_data['pl_flux_density'] = catalog_dict['PL_Flux_Density'][i]
        
        # Classification
        source_data['class1'] = str(catalog_dict['CLASS1'][i]).strip()
        source_data['class2'] = str(catalog_dict['CLASS2'][i]).strip()
        source_data['assoc1'] = str(catalog_dict['ASSOC1'][i]).strip()
        source_data['assoc2'] = str(catalog_dict['ASSOC2'][i]).strip()
        
        # Flags
        source_data['flags'] = catalog_dict['Flags'][i]
        
        source_info.append(source_data)
    
    print(f"Extracted information for {len(source_info)} sources")
    
    return source_info

def identify_grb_candidates(source_info):
    """Identify GRB candidates from the real catalog"""
    
    print("\nIDENTIFYING GRB CANDIDATES FROM REAL CATALOG")
    print("=" * 60)
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(source_info)
    
    print(f"Total sources in catalog: {len(df)}")
    
    # Look for GRB candidates using multiple criteria
    
    # 1. Unassociated sources (no known class)
    unassociated = (df['class1'] == '') & (df['class2'] == '')
    print(f"Unassociated sources: {unassociated.sum()}")
    
    # 2. High variability sources (typical of GRBs)
    high_variability = df['variability_index'] > 100
    print(f"High variability (>100): {high_variability.sum()}")
    
    # 3. Sources with reasonable flux
    reasonable_flux = df['energy_flux'] > 1e-12
    print(f"Reasonable flux (>1e-12): {reasonable_flux.sum()}")
    
    # 4. Sources with reasonable significance
    reasonable_sig = df['significance'] > 5
    print(f"Reasonable significance (>5sigma): {reasonable_sig.sum()}")
    
    # 5. Look for sources with "GRB" in name or association
    has_grb_name = df['source_name'].str.contains('GRB', case=False, na=False)
    has_grb_assoc = df['assoc1'].str.contains('GRB', case=False, na=False) | df['assoc2'].str.contains('GRB', case=False, na=False)
    has_grb = has_grb_name | has_grb_assoc
    print(f"Sources with GRB in name/association: {has_grb.sum()}")
    
    # 6. Combine criteria for GRB candidates
    grb_candidates = df[
        (unassociated & high_variability & reasonable_flux & reasonable_sig) |
        has_grb
    ].copy()
    
    print(f"\nGRB candidates found: {len(grb_candidates)}")
    
    if len(grb_candidates) > 0:
        print(f"\nTop GRB candidates:")
        top_candidates = grb_candidates.nlargest(20, 'variability_index')
        for i, (_, row) in enumerate(top_candidates.iterrows()):
            print(f"  {i+1}. {row['source_name']} - Variability: {row['variability_index']:.1f}, Significance: {row['significance']:.1f}sigma, Class: {row['class1']}")
    
    return grb_candidates, df

def analyze_catalog_statistics(df):
    """Analyze catalog statistics"""
    
    print("\nCATALOG STATISTICS ANALYSIS")
    print("=" * 60)
    
    print(f"Catalog overview:")
    print(f"  - Total sources: {len(df)}")
    print(f"  - Mean significance: {df['significance'].mean():.2f}sigma")
    print(f"  - Max significance: {df['significance'].max():.2f}sigma")
    print(f"  - Mean variability: {df['variability_index'].mean():.2f}")
    print(f"  - Max variability: {df['variability_index'].max():.2f}")
    
    # Significance distribution
    sig_3sigma = (df['significance'] > 3).sum()
    sig_5sigma = (df['significance'] > 5).sum()
    sig_10sigma = (df['significance'] > 10).sum()
    
    print(f"\nSignificance distribution:")
    print(f"  - >3sigma: {sig_3sigma} sources")
    print(f"  - >5sigma: {sig_5sigma} sources")
    print(f"  - >10sigma: {sig_10sigma} sources")
    
    # Variability distribution
    var_100 = (df['variability_index'] > 100).sum()
    var_500 = (df['variability_index'] > 500).sum()
    var_1000 = (df['variability_index'] > 1000).sum()
    
    print(f"\nVariability distribution:")
    print(f"  - >100: {var_100} sources")
    print(f"  - >500: {var_500} sources")
    print(f"  - >1000: {var_1000} sources")
    
    # Source classes
    class_counts = df['class1'].value_counts()
    print(f"\nSource classes (top 10):")
    for class_name, count in class_counts.head(10).items():
        if class_name != '':
            print(f"  - {class_name}: {count} sources")
    
    return {
        'total_sources': len(df),
        'mean_significance': df['significance'].mean(),
        'max_significance': df['significance'].max(),
        'mean_variability': df['variability_index'].mean(),
        'max_variability': df['variability_index'].max(),
        'sig_3sigma': sig_3sigma,
        'sig_5sigma': sig_5sigma,
        'sig_10sigma': sig_10sigma,
        'var_100': var_100,
        'var_500': var_500,
        'var_1000': var_1000
    }

def save_complete_analysis(grb_candidates, df, catalog_stats):
    """Save complete analysis results"""
    
    print("\nSAVING COMPLETE ANALYSIS RESULTS")
    print("=" * 60)
    
    # Save GRB candidates
    grb_candidates.to_csv('fermi_grb_candidates_real.csv', index=False)
    print(f"Saved GRB candidates: fermi_grb_candidates_real.csv")
    
    # Save complete catalog
    df.to_csv('fermi_catalog_complete_real.csv', index=False)
    print(f"Saved complete catalog: fermi_catalog_complete_real.csv")
    
    # Save statistics
    with open('fermi_catalog_stats_real.json', 'w') as f:
        json.dump(catalog_stats, f, indent=2)
    print(f"Saved statistics: fermi_catalog_stats_real.json")
    
    # Generate summary report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'catalog_file': 'gll_psc_v35.fit',
        'total_sources': catalog_stats['total_sources'],
        'grb_candidates_found': len(grb_candidates),
        'catalog_statistics': catalog_stats,
        'top_grb_candidates': grb_candidates.nlargest(10, 'variability_index')[['source_name', 'variability_index', 'significance', 'class1']].to_dict('records')
    }
    
    with open('fermi_analysis_report_real.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Saved report: fermi_analysis_report_real.json")

def main():
    """Main function"""
    print("ANALYZE REAL FERMI CATALOG - NO SIMULATIONS!")
    print("=" * 70)
    print("Using the ACTUAL Fermi LAT catalog data...")
    print("Extracting ALL information without loss...")
    
    # Load complete Fermi catalog
    catalog_dict, catalog_data, hdul = load_fermi_catalog_complete()
    if catalog_dict is None:
        return
    
    # Extract all source information
    source_info = extract_all_source_information(catalog_dict)
    
    # Identify GRB candidates
    grb_candidates, df = identify_grb_candidates(source_info)
    
    # Analyze catalog statistics
    catalog_stats = analyze_catalog_statistics(df)
    
    # Save complete analysis
    save_complete_analysis(grb_candidates, df, catalog_stats)
    
    print("\n" + "=" * 70)
    print("REAL FERMI CATALOG ANALYSIS COMPLETED!")
    print("=" * 70)
    print(f"Total sources analyzed: {catalog_stats['total_sources']}")
    print(f"GRB candidates found: {len(grb_candidates)}")
    print(f"Max significance: {catalog_stats['max_significance']:.2f}sigma")
    print(f"Max variability: {catalog_stats['max_variability']:.2f}")
    
    print(f"\nFiles created:")
    print(f"  - fermi_grb_candidates_real.csv")
    print(f"  - fermi_catalog_complete_real.csv")
    print(f"  - fermi_catalog_stats_real.json")
    print(f"  - fermi_analysis_report_real.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
