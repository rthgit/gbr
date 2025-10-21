#!/usr/bin/env python3
"""
ANALYZE REAL FERMI DATA
=======================

Analizza dati REALI scaricati da Fermi LAT per effetti QG.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import os
import numpy as np
import pandas as pd
import json
from datetime import datetime
from scipy import stats
from sklearn.linear_model import RANSACRegressor
from sklearn.utils import resample
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.time import Time
import warnings
warnings.filterwarnings('ignore')

def convert_numpy_types(obj):
    """
    Converte tipi NumPy in tipi Python standard per JSON
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def load_fermi_fits_data(fits_file):
    """
    Carica dati da file FITS di Fermi LAT
    """
    print(f"   📊 Loading {fits_file}...")
    
    try:
        with fits.open(fits_file) as hdul:
            # Prendi la prima tabella HDU
            data = hdul[1].data
            
            # Estrai colonne principali
            if 'ENERGY' in data.dtype.names:
                energy = data['ENERGY']  # MeV
            elif 'ENERG' in data.dtype.names:
                energy = data['ENERG']  # MeV
            else:
                print(f"   ❌ No energy column found in {fits_file}")
                return None
            
            if 'TIME' in data.dtype.names:
                time = data['TIME']  # MET seconds
            elif 'EVENT_TIME' in data.dtype.names:
                time = data['EVENT_TIME']  # MET seconds
            else:
                print(f"   ❌ No time column found in {fits_file}")
                return None
            
            # Converti energia da MeV a GeV
            energy_gev = energy / 1000.0
            
            print(f"   ✅ Loaded {len(energy)} photons")
            print(f"   📊 Energy range: {energy_gev.min():.3f} - {energy_gev.max():.3f} GeV")
            print(f"   ⏱️ Time range: {time.min():.1f} - {time.max():.1f} s")
            
            return {
                'energy': energy_gev,
                'time': time,
                'n_photons': len(energy),
                'energy_min': float(energy_gev.min()),
                'energy_max': float(energy_gev.max()),
                'time_min': float(time.min()),
                'time_max': float(time.max())
            }
            
    except Exception as e:
        print(f"   ❌ Error loading {fits_file}: {e}")
        return None

def analyze_qg_effects(grb_name, data):
    """
    Analizza effetti QG sui dati reali
    """
    print(f"   🔍 Analyzing QG effects for {grb_name}...")
    
    if data is None:
        return None
    
    energy = data['energy']
    time = data['time']
    n_photons = data['n_photons']
    
    # Calcola tempi relativi (rimuovi offset)
    time_rel = time - time.min()
    
    # Analisi correlazione Pearson
    pearson_r, pearson_p = stats.pearsonr(energy, time_rel)
    sigma = abs(pearson_r * np.sqrt((n_photons-2)/(1-pearson_r**2)))
    
    # Analisi correlazione Spearman
    spearman_r, spearman_p = stats.spearmanr(energy, time_rel)
    
    # RANSAC regression per gestire outlier
    X = energy.reshape(-1, 1)
    y = time_rel
    
    ransac = RANSACRegressor(random_state=42)
    ransac.fit(X, y)
    
    inlier_mask = ransac.inlier_mask_
    n_inliers = np.sum(inlier_mask)
    n_outliers = n_photons - n_inliers
    
    # Stima E_QG (semplificata)
    if ransac.estimator_.coef_[0] != 0:
        # Fattore cosmologico approssimativo
        K_z = 1e16  # s (placeholder)
        E_QG = K_z / abs(ransac.estimator_.coef_[0])
        E_QG_planck = E_QG / 1.22e19  # Normalizza a E_Planck
    else:
        E_QG = np.inf
        E_QG_planck = np.inf
    
    # Bootstrap per intervalli di confidenza
    n_bootstrap = 1000
    bootstrap_correlations = []
    
    for _ in range(n_bootstrap):
        indices = np.random.choice(n_photons, n_photons, replace=True)
        r_boot, _ = stats.pearsonr(energy[indices], time_rel[indices])
        bootstrap_correlations.append(r_boot)
    
    bootstrap_mean = np.mean(bootstrap_correlations)
    bootstrap_std = np.std(bootstrap_correlations)
    bootstrap_ci = np.percentile(bootstrap_correlations, [2.5, 97.5])
    
    # Permutation test
    n_permutations = 10000
    perm_correlations = []
    
    for _ in range(n_permutations):
        energy_perm = np.random.permutation(energy)
        r_perm, _ = stats.pearsonr(energy_perm, time_rel)
        perm_correlations.append(r_perm)
    
    perm_p_value = np.sum(np.abs(perm_correlations) >= abs(pearson_r)) / n_permutations
    
    # Risultati
    results = {
        'grb_name': grb_name,
        'n_photons': n_photons,
        'energy_range': [data['energy_min'], data['energy_max']],
        'time_range': [data['time_min'], data['time_max']],
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'pearson_sigma': float(sigma),
        'spearman_r': float(spearman_r),
        'spearman_p': float(spearman_p),
        'ransac_slope': float(ransac.estimator_.coef_[0]),
        'ransac_intercept': float(ransac.estimator_.intercept_),
        'n_inliers': int(n_inliers),
        'n_outliers': int(n_outliers),
        'inlier_fraction': float(n_inliers / n_photons),
        'E_QG_GeV': float(E_QG),
        'E_QG_planck': float(E_QG_planck),
        'bootstrap_mean': float(bootstrap_mean),
        'bootstrap_std': float(bootstrap_std),
        'bootstrap_ci': [float(bootstrap_ci[0]), float(bootstrap_ci[1])],
        'permutation_p': float(perm_p_value),
        'significant': bool(sigma > 3.0 and pearson_p < 0.05),
        'data_quality': 'real_fermi'
    }
    
    print(f"   📊 {grb_name}: r={pearson_r:.4f}, σ={sigma:.2f}, p={pearson_p:.4f}")
    print(f"   📊 RANSAC: slope={ransac.estimator_.coef_[0]:.2e}, inliers={n_inliers}/{n_photons}")
    print(f"   📊 E_QG: {E_QG:.2e} GeV ({E_QG_planck:.2e} E_Planck)")
    print(f"   📊 SIGNIFICANT: {results['significant']}")
    
    return results

def create_diagnostic_plots(grb_name, data, results):
    """
    Crea plot diagnostici per i dati reali
    """
    print(f"   🎨 Creating diagnostic plots for {grb_name}...")
    
    if data is None:
        return
    
    energy = data['energy']
    time = data['time']
    time_rel = time - time.min()
    
    # Crea figura con subplot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'{grb_name} - Real Fermi LAT Data Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Energy vs Time
    axes[0,0].scatter(time_rel, energy, alpha=0.6, s=20)
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Energy (GeV)')
    axes[0,0].set_yscale('log')
    axes[0,0].set_title('Energy vs Time')
    axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: Energy histogram
    axes[0,1].hist(energy, bins=50, alpha=0.7, edgecolor='black')
    axes[0,1].set_xlabel('Energy (GeV)')
    axes[0,1].set_ylabel('Counts')
    axes[0,1].set_xscale('log')
    axes[0,1].set_title('Energy Distribution')
    axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Time histogram
    axes[1,0].hist(time_rel, bins=50, alpha=0.7, edgecolor='black')
    axes[1,0].set_xlabel('Time (s)')
    axes[1,0].set_ylabel('Counts')
    axes[1,0].set_title('Time Distribution')
    axes[1,0].grid(True, alpha=0.3)
    
    # Plot 4: Correlation scatter
    axes[1,1].scatter(energy, time_rel, alpha=0.6, s=20)
    axes[1,1].set_xlabel('Energy (GeV)')
    axes[1,1].set_ylabel('Time (s)')
    axes[1,1].set_xscale('log')
    axes[1,1].set_title(f'Correlation: r={results["pearson_r"]:.3f}, σ={results["pearson_sigma"]:.1f}')
    axes[1,1].grid(True, alpha=0.3)
    
    # Aggiungi linea di fit se significativo
    if results['significant']:
        z = np.polyfit(energy, time_rel, 1)
        p = np.poly1d(z)
        energy_sorted = np.sort(energy)
        axes[1,1].plot(energy_sorted, p(energy_sorted), 'r-', linewidth=2, label='Linear fit')
        axes[1,1].legend()
    
    plt.tight_layout()
    
    # Salva plot
    plot_filename = f'real_fermi_analysis_{grb_name.lower()}.png'
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Plot saved: {plot_filename}")

def analyze_real_fermi_data():
    """
    Analizza tutti i dati reali scaricati
    """
    print("🚀 ANALYZE REAL FERMI DATA")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Lista dei file FITS scaricati
    fits_files = [
        ('GRB221009A', 'L251021103213F357373F22_PH00.fits'),
        ('GRB190114C', 'L251021103308F357373F87_PH00.fits'),
        ('GRB090510', 'L251021103420F357373F11_PH00.fits'),
        ('GRB180720B', 'L251021103510F357373F22_PH00.fits'),
        ('GRB160625B', 'L251021103601F357373F17_PH00.fits')
    ]
    
    # Crea directory per risultati
    os.makedirs('real_fermi_analysis', exist_ok=True)
    
    # Analizza ogni GRB
    all_results = {}
    
    for grb_name, fits_file in fits_files:
        print(f"\n🔍 Analyzing {grb_name}...")
        
        # Carica dati
        data = load_fermi_fits_data(fits_file)
        
        # Analizza effetti QG
        results = analyze_qg_effects(grb_name, data)
        
        if results:
            # Crea plot diagnostici
            create_diagnostic_plots(grb_name, data, results)
            
            # Salva risultati
            all_results[grb_name] = results
    
    # Salva tutti i risultati
    with open('real_fermi_analysis/analysis_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    # Crea riassunto
    print("\n" + "=" * 60)
    print("🎯 REAL FERMI DATA ANALYSIS SUMMARY")
    print("=" * 60)
    
    for grb_name, results in all_results.items():
        print(f"📊 {grb_name}:")
        print(f"   Photons: {results['n_photons']}")
        print(f"   Energy: {results['energy_range'][0]:.3f} - {results['energy_range'][1]:.3f} GeV")
        print(f"   Correlation: r={results['pearson_r']:.4f}, σ={results['pearson_sigma']:.2f}")
        print(f"   E_QG: {results['E_QG_GeV']:.2e} GeV ({results['E_QG_planck']:.2e} E_Planck)")
        print(f"   SIGNIFICANT: {results['significant']}")
        print()
    
    print("=" * 60)
    print("🎉 REAL FERMI DATA ANALYSIS COMPLETE!")
    print("📊 Check 'real_fermi_analysis/' directory for results")
    print("=" * 60)

if __name__ == "__main__":
    analyze_real_fermi_data()