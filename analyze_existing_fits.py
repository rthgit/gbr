#!/usr/bin/env python3
"""
ANALYZE EXISTING FITS FILES
===========================

Analizza i file FITS già scaricati per effetti QG.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import os
import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import RANSACRegressor
import json
from datetime import datetime

def load_fits_file(filename):
    """
    Carica un file FITS e estrae i dati
    """
    try:
        with fits.open(filename) as hdul:
            # Cerca la tabella degli eventi
            for hdu in hdul:
                if hasattr(hdu, 'data') and hdu.data is not None:
                    if 'TIME' in hdu.data.dtype.names:
                        return hdu.data
            return None
    except Exception as e:
        print(f"   ❌ Error loading {filename}: {e}")
        return None

def analyze_qg_effects(data, grb_name):
    """
    Analizza gli effetti QG in un dataset
    """
    if data is None or len(data) == 0:
        return None
    
    # Estrai colonne
    times = data['TIME']
    energies = data['ENERGY']
    
    # Converti energie in GeV se necessario
    if energies.max() > 1000:  # Probabilmente in MeV
        energies = energies / 1000.0
    
    # Calcola correlazioni
    pearson_r, pearson_p = stats.pearsonr(energies, times)
    spearman_r, spearman_p = stats.spearmanr(energies, times)
    
    # RANSAC regression
    X = energies.reshape(-1, 1)
    y = times
    
    ransac = RANSACRegressor(random_state=42)
    ransac.fit(X, y)
    
    slope = ransac.estimator_.coef_[0]
    intercept = ransac.estimator_.intercept_
    inliers = ransac.inlier_mask_
    
    # Stima E_QG (semplificata)
    if slope != 0:
        E_QG = 1.0 / abs(slope)  # Semplificazione
        E_Planck = 1.22e19  # GeV
        E_QG_ratio = E_QG / E_Planck
    else:
        E_QG = np.inf
        E_QG_ratio = np.inf
    
    return {
        'grb_name': grb_name,
        'n_photons': len(data),
        'energy_range': [energies.min(), energies.max()],
        'time_range': [times.min(), times.max()],
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'ransac_slope': slope,
        'ransac_intercept': intercept,
        'ransac_inliers': inliers.sum(),
        'ransac_outliers': (~inliers).sum(),
        'E_QG_GeV': E_QG,
        'E_QG_E_Planck': E_QG_ratio,
        'significant': abs(pearson_r) > 0.3 and pearson_p < 0.05
    }

def analyze_all_fits():
    """
    Analizza tutti i file FITS presenti
    """
    print("🚀 ANALYZING EXISTING FITS FILES")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Trova tutti i file FITS
    fits_files = [f for f in os.listdir('.') if f.endswith('.fits')]
    
    if not fits_files:
        print("❌ No FITS files found!")
        return
    
    print(f"🔍 Found {len(fits_files)} FITS files")
    
    results = []
    
    for i, filename in enumerate(fits_files, 1):
        print(f"\n📊 Analyzing {i}/{len(fits_files)}: {filename}")
        
        # Carica dati
        data = load_fits_file(filename)
        
        if data is not None:
            # Analizza effetti QG
            result = analyze_qg_effects(data, filename)
            
            if result:
                results.append(result)
                
                print(f"   ✅ {result['grb_name']}: {result['n_photons']} photons")
                print(f"   📊 Energy: {result['energy_range'][0]:.3f} - {result['energy_range'][1]:.3f} GeV")
                print(f"   📊 Time: {result['time_range'][0]:.1f} - {result['time_range'][1]:.1f} s")
                print(f"   📊 Pearson: r={result['pearson_r']:.4f}, p={result['pearson_p']:.4f}")
                print(f"   📊 RANSAC: slope={result['ransac_slope']:.6f}, inliers={result['ransac_inliers']}")
                print(f"   📊 E_QG: {result['E_QG_GeV']:.2e} GeV ({result['E_QG_E_Planck']:.2e} E_Planck)")
                print(f"   📊 SIGNIFICANT: {result['significant']}")
            else:
                print(f"   ❌ Failed to analyze {filename}")
        else:
            print(f"   ❌ Failed to load {filename}")
    
    # Salva risultati
    if results:
        # Converti numpy types per JSON
        def convert_numpy_types(obj):
            if isinstance(obj, np.float32):
                return float(obj)
            elif isinstance(obj, np.float64):
                return float(obj)
            elif isinstance(obj, np.int32):
                return int(obj)
            elif isinstance(obj, np.int64):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        # Converti tutti i risultati
        results_clean = convert_numpy_types(results)
        
        with open('fits_analysis_results.json', 'w') as f:
            json.dump(results_clean, f, indent=2)
        
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print(f"📊 Successfully analyzed: {len(results)}/{len(fits_files)} files")
        print("📁 Results saved to: fits_analysis_results.json")
        
        # Trova effetti significativi
        significant = [r for r in results if r['significant']]
        if significant:
            print(f"\n🚨 SIGNIFICANT QG EFFECTS FOUND: {len(significant)}")
            for result in significant:
                print(f"   • {result['grb_name']}: r={result['pearson_r']:.4f}, p={result['pearson_p']:.4f}")
        else:
            print("\n📊 No significant QG effects found in current dataset")
    
    return results

if __name__ == "__main__":
    analyze_all_fits()
