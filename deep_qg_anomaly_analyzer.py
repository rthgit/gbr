#!/usr/bin/env python3
"""
DEEP QG ANOMALY ANALYZER
========================

Analisi approfondita per QG e pattern anomali nascosti nei dati.
Cerca gravità quantistica non solo nei dati conosciuti ma in quello che manca.

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
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
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

def detect_hidden_qg_patterns(grb_name, data):
    """
    Rileva pattern QG nascosti e anomalie specifiche
    """
    print(f"   🔍 Detecting hidden QG patterns for {grb_name}...")
    
    if data is None:
        return None
    
    energy = data['energy']
    time = data['time']
    n_photons = data['n_photons']
    
    # Calcola tempi relativi
    time_rel = time - time.min()
    
    # 1. ANALISI CORRELAZIONE ENERGIA-TEMPO STANDARD
    pearson_r, pearson_p = stats.pearsonr(energy, time_rel)
    sigma = abs(pearson_r * np.sqrt((n_photons-2)/(1-pearson_r**2)))
    
    # 2. ANALISI CORRELAZIONE LOG-ENERGIA vs TEMPO
    log_energy = np.log10(energy)
    log_pearson_r, log_pearson_p = stats.pearsonr(log_energy, time_rel)
    log_sigma = abs(log_pearson_r * np.sqrt((n_photons-2)/(1-log_pearson_r**2)))
    
    # 3. ANALISI CORRELAZIONE ENERGIA vs LOG-TEMPO
    log_time = np.log10(time_rel + 1)  # +1 per evitare log(0)
    energy_logtime_r, energy_logtime_p = stats.pearsonr(energy, log_time)
    energy_logtime_sigma = abs(energy_logtime_r * np.sqrt((n_photons-2)/(1-energy_logtime_r**2)))
    
    # 4. ANALISI CORRELAZIONE LOG-ENERGIA vs LOG-TEMPO
    log_log_r, log_log_p = stats.pearsonr(log_energy, log_time)
    log_log_sigma = abs(log_log_r * np.sqrt((n_photons-2)/(1-log_log_r**2)))
    
    # 5. ANALISI SPETTRALE (FFT) PER PERIODICITÀ
    if n_photons > 10:
        # Calcola FFT del segnale energia-tempo
        dt = np.diff(time_rel)
        if len(dt) > 0 and np.std(dt) > 0:
            # Interpola su griglia temporale uniforme
            time_uniform = np.linspace(time_rel.min(), time_rel.max(), min(1000, n_photons))
            energy_interp = np.interp(time_uniform, time_rel, energy)
            
            # FFT
            fft = np.fft.fft(energy_interp)
            freqs = np.fft.fftfreq(len(energy_interp), d=np.mean(dt))
            
            # Trova picchi significativi
            power = np.abs(fft)**2
            significant_peaks = power > 3 * np.std(power)
            n_peaks = np.sum(significant_peaks)
        else:
            n_peaks = 0
            freqs = np.array([])
            power = np.array([])
    else:
        n_peaks = 0
        freqs = np.array([])
        power = np.array([])
    
    # 6. ANALISI CLUSTERING PER PATTERN NASCOSTI
    if n_photons > 10:
        # Prepara dati per clustering
        X = np.column_stack([energy, time_rel])
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # DBSCAN clustering
        dbscan = DBSCAN(eps=0.5, min_samples=3)
        clusters = dbscan.fit_predict(X_scaled)
        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
        n_outliers = list(clusters).count(-1)
    else:
        n_clusters = 0
        n_outliers = 0
    
    # 7. ANALISI RANSAC MULTIPLA
    X = energy.reshape(-1, 1)
    y = time_rel
    
    ransac = RANSACRegressor(random_state=42)
    ransac.fit(X, y)
    
    inlier_mask = ransac.inlier_mask_
    n_inliers = np.sum(inlier_mask)
    n_outliers_ransac = n_photons - n_inliers
    
    # 8. ANALISI ENERGIA-TEMPO INVERSA
    # Cerca se tempo dipende da energia (inverso del QG standard)
    X_inv = time_rel.reshape(-1, 1)
    y_inv = energy
    
    ransac_inv = RANSACRegressor(random_state=42)
    ransac_inv.fit(X_inv, y_inv)
    
    inlier_mask_inv = ransac_inv.inlier_mask_
    n_inliers_inv = np.sum(inlier_mask_inv)
    
    # 9. ANALISI ENERGIA-TEMPO QUADRATICA
    # Cerca dipendenze quadratiche (QG non-lineare)
    X_quad = np.column_stack([energy, energy**2])
    y_quad = time_rel
    
    try:
        from sklearn.linear_model import LinearRegression
        quad_model = LinearRegression()
        quad_model.fit(X_quad, y_quad)
        quad_r2 = quad_model.score(X_quad, y_quad)
    except:
        quad_r2 = 0
    
    # 10. ANALISI ENERGIA-TEMPO CUBICA
    # Cerca dipendenze cubiche (QG estremo)
    X_cubic = np.column_stack([energy, energy**2, energy**3])
    y_cubic = time_rel
    
    try:
        cubic_model = LinearRegression()
        cubic_model.fit(X_cubic, y_cubic)
        cubic_r2 = cubic_model.score(X_cubic, y_cubic)
    except:
        cubic_r2 = 0
    
    # 11. ANALISI ENERGIA-TEMPO ESPONENZIALE
    # Cerca dipendenze esponenziali (QG esponenziale)
    X_exp = np.column_stack([energy, np.exp(energy/10)])  # Normalizza per stabilità
    y_exp = time_rel
    
    try:
        exp_model = LinearRegression()
        exp_model.fit(X_exp, y_exp)
        exp_r2 = exp_model.score(X_exp, y_exp)
    except:
        exp_r2 = 0
    
    # 12. ANALISI ENERGIA-TEMPO LOGARITMICA
    # Cerca dipendenze logaritmiche (QG logaritmico)
    X_log = np.column_stack([energy, np.log(energy + 1)])  # +1 per evitare log(0)
    y_log = time_rel
    
    try:
        log_model = LinearRegression()
        log_model.fit(X_log, y_log)
        log_r2 = log_model.score(X_log, y_log)
    except:
        log_r2 = 0
    
    # 13. ANALISI ENERGIA-TEMPO SINUSOIDALE
    # Cerca dipendenze sinusoidali (QG oscillatorio)
    X_sin = np.column_stack([energy, np.sin(energy), np.cos(energy)])
    y_sin = time_rel
    
    try:
        sin_model = LinearRegression()
        sin_model.fit(X_sin, y_sin)
        sin_r2 = sin_model.score(X_sin, y_sin)
    except:
        sin_r2 = 0
    
    # 14. ANALISI ENERGIA-TEMPO POLINOMIALE
    # Cerca dipendenze polinomiali (QG polinomiale)
    X_poly = np.column_stack([energy, energy**2, energy**3, energy**4])
    y_poly = time_rel
    
    try:
        poly_model = LinearRegression()
        poly_model.fit(X_poly, y_poly)
        poly_r2 = poly_model.score(X_poly, y_poly)
    except:
        poly_r2 = 0
    
    # 15. ANALISI ENERGIA-TEMPO RIDOTTA
    # Cerca dipendenze ridotte (QG ridotto)
    X_reduced = np.column_stack([energy, 1/energy, 1/energy**2])
    y_reduced = time_rel
    
    try:
        reduced_model = LinearRegression()
        reduced_model.fit(X_reduced, y_reduced)
        reduced_r2 = reduced_model.score(X_reduced, y_reduced)
    except:
        reduced_r2 = 0
    
    # 16. ANALISI ENERGIA-TEMPO MISTA
    # Cerca dipendenze miste (QG misto)
    X_mixed = np.column_stack([energy, np.log(energy + 1), np.exp(energy/10), np.sin(energy)])
    y_mixed = time_rel
    
    try:
        mixed_model = LinearRegression()
        mixed_model.fit(X_mixed, y_mixed)
        mixed_r2 = mixed_model.score(X_mixed, y_mixed)
    except:
        mixed_r2 = 0
    
    # 17. ANALISI ENERGIA-TEMPO RIDOTTA INVERSA
    # Cerca dipendenze ridotte inverse (QG ridotto inverso)
    X_reduced_inv = np.column_stack([time_rel, 1/time_rel, 1/time_rel**2])
    y_reduced_inv = energy
    
    try:
        reduced_inv_model = LinearRegression()
        reduced_inv_model.fit(X_reduced_inv, y_reduced_inv)
        reduced_inv_r2 = reduced_inv_model.score(X_reduced_inv, y_reduced_inv)
    except:
        reduced_inv_r2 = 0
    
    # 18. ANALISI ENERGIA-TEMPO RIDOTTA MISTA
    # Cerca dipendenze ridotte miste (QG ridotto misto)
    X_reduced_mixed = np.column_stack([energy, 1/energy, np.log(energy + 1), np.exp(energy/10)])
    y_reduced_mixed = time_rel
    
    try:
        reduced_mixed_model = LinearRegression()
        reduced_mixed_model.fit(X_reduced_mixed, y_reduced_mixed)
        reduced_mixed_r2 = reduced_mixed_model.score(X_reduced_mixed, y_reduced_mixed)
    except:
        reduced_mixed_r2 = 0
    
    # 19. ANALISI ENERGIA-TEMPO RIDOTTA MISTA INVERSA
    # Cerca dipendenze ridotte miste inverse (QG ridotto misto inverso)
    X_reduced_mixed_inv = np.column_stack([time_rel, 1/time_rel, np.log(time_rel + 1), np.exp(time_rel/10)])
    y_reduced_mixed_inv = energy
    
    try:
        reduced_mixed_inv_model = LinearRegression()
        reduced_mixed_inv_model.fit(X_reduced_mixed_inv, y_reduced_mixed_inv)
        reduced_mixed_inv_r2 = reduced_mixed_inv_model.score(X_reduced_mixed_inv, y_reduced_mixed_inv)
    except:
        reduced_mixed_inv_r2 = 0
    
    # 20. ANALISI ENERGIA-TEMPO RIDOTTA MISTA INVERSA RIDOTTA
    # Cerca dipendenze ridotte miste inverse ridotte (QG ridotto misto inverso ridotto)
    X_reduced_mixed_inv_reduced = np.column_stack([time_rel, 1/time_rel, np.log(time_rel + 1), np.exp(time_rel/10), 1/time_rel**2])
    y_reduced_mixed_inv_reduced = energy
    
    try:
        reduced_mixed_inv_reduced_model = LinearRegression()
        reduced_mixed_inv_reduced_model.fit(X_reduced_mixed_inv_reduced, y_reduced_mixed_inv_reduced)
        reduced_mixed_inv_reduced_r2 = reduced_mixed_inv_reduced_model.score(X_reduced_mixed_inv_reduced, y_reduced_mixed_inv_reduced)
    except:
        reduced_mixed_inv_reduced_r2 = 0
    
    # Risultati
    results = {
        'grb_name': grb_name,
        'n_photons': n_photons,
        'energy_range': [data['energy_min'], data['energy_max']],
        'time_range': [data['time_min'], data['time_max']],
        
        # Correlazioni standard
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'pearson_sigma': float(sigma),
        
        # Correlazioni log
        'log_pearson_r': float(log_pearson_r),
        'log_pearson_p': float(log_pearson_p),
        'log_pearson_sigma': float(log_sigma),
        
        # Correlazioni energia-logtempo
        'energy_logtime_r': float(energy_logtime_r),
        'energy_logtime_p': float(energy_logtime_p),
        'energy_logtime_sigma': float(energy_logtime_sigma),
        
        # Correlazioni log-log
        'log_log_r': float(log_log_r),
        'log_log_p': float(log_log_p),
        'log_log_sigma': float(log_log_sigma),
        
        # Analisi spettrale
        'n_spectral_peaks': int(n_peaks),
        'has_spectral_periodicity': bool(n_peaks > 0),
        
        # Clustering
        'n_clusters': int(n_clusters),
        'n_outliers_clustering': int(n_outliers),
        'has_clustering_patterns': bool(n_clusters > 1),
        
        # RANSAC
        'ransac_slope': float(ransac.estimator_.coef_[0]),
        'ransac_intercept': float(ransac.estimator_.intercept_),
        'n_inliers': int(n_inliers),
        'n_outliers_ransac': int(n_outliers_ransac),
        'inlier_fraction': float(n_inliers / n_photons),
        
        # RANSAC inverso
        'ransac_inv_slope': float(ransac_inv.estimator_.coef_[0]),
        'ransac_inv_intercept': float(ransac_inv.estimator_.intercept_),
        'n_inliers_inv': int(n_inliers_inv),
        'inlier_fraction_inv': float(n_inliers_inv / n_photons),
        
        # Modelli avanzati
        'quadratic_r2': float(quad_r2),
        'cubic_r2': float(cubic_r2),
        'exponential_r2': float(exp_r2),
        'logarithmic_r2': float(log_r2),
        'sinusoidal_r2': float(sin_r2),
        'polynomial_r2': float(poly_r2),
        'reduced_r2': float(reduced_r2),
        'mixed_r2': float(mixed_r2),
        'reduced_inv_r2': float(reduced_inv_r2),
        'reduced_mixed_r2': float(reduced_mixed_r2),
        'reduced_mixed_inv_r2': float(reduced_mixed_inv_r2),
        'reduced_mixed_inv_reduced_r2': float(reduced_mixed_inv_reduced_r2),
        
        # Significatività
        'significant_linear': bool(sigma > 3.0 and pearson_p < 0.05),
        'significant_log': bool(log_sigma > 3.0 and log_pearson_p < 0.05),
        'significant_energy_logtime': bool(energy_logtime_sigma > 3.0 and energy_logtime_p < 0.05),
        'significant_log_log': bool(log_log_sigma > 3.0 and log_log_p < 0.05),
        
        # Pattern nascosti
        'has_hidden_patterns': bool(n_clusters > 1 or n_peaks > 0 or max(quad_r2, cubic_r2, exp_r2, log_r2, sin_r2, poly_r2, reduced_r2, mixed_r2, reduced_inv_r2, reduced_mixed_r2, reduced_mixed_inv_r2, reduced_mixed_inv_reduced_r2) > 0.5),
        'best_model': max([
            ('linear', abs(pearson_r)),
            ('log', abs(log_pearson_r)),
            ('energy_logtime', abs(energy_logtime_r)),
            ('log_log', abs(log_log_r)),
            ('quadratic', quad_r2),
            ('cubic', cubic_r2),
            ('exponential', exp_r2),
            ('logarithmic', log_r2),
            ('sinusoidal', sin_r2),
            ('polynomial', poly_r2),
            ('reduced', reduced_r2),
            ('mixed', mixed_r2),
            ('reduced_inv', reduced_inv_r2),
            ('reduced_mixed', reduced_mixed_r2),
            ('reduced_mixed_inv', reduced_mixed_inv_r2),
            ('reduced_mixed_inv_reduced', reduced_mixed_inv_reduced_r2)
        ], key=lambda x: x[1])[0],
        
        'data_quality': 'real_fermi'
    }
    
    print(f"   📊 {grb_name}: Linear r={pearson_r:.4f}, σ={sigma:.2f}")
    print(f"   📊 Log r={log_pearson_r:.4f}, σ={log_sigma:.2f}")
    print(f"   📊 Energy-LogTime r={energy_logtime_r:.4f}, σ={energy_logtime_sigma:.2f}")
    print(f"   📊 Log-Log r={log_log_r:.4f}, σ={log_log_sigma:.2f}")
    print(f"   📊 Spectral peaks: {n_peaks}, Clusters: {n_clusters}")
    print(f"   📊 Best model: {results['best_model']}")
    print(f"   📊 Hidden patterns: {results['has_hidden_patterns']}")
    
    return results

def create_advanced_diagnostic_plots(grb_name, data, results):
    """
    Crea plot diagnostici avanzati per pattern nascosti
    """
    print(f"   🎨 Creating advanced diagnostic plots for {grb_name}...")
    
    if data is None:
        return
    
    energy = data['energy']
    time = data['time']
    time_rel = time - time.min()
    
    # Crea figura con subplot multipli
    fig, axes = plt.subplots(3, 3, figsize=(18, 15))
    fig.suptitle(f'{grb_name} - Advanced QG Pattern Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Energy vs Time (standard)
    axes[0,0].scatter(time_rel, energy, alpha=0.6, s=20)
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Energy (GeV)')
    axes[0,0].set_yscale('log')
    axes[0,0].set_title(f'Energy vs Time (r={results["pearson_r"]:.3f})')
    axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: Log Energy vs Time
    axes[0,1].scatter(time_rel, np.log10(energy), alpha=0.6, s=20)
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Log10(Energy)')
    axes[0,1].set_title(f'Log Energy vs Time (r={results["log_pearson_r"]:.3f})')
    axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Energy vs Log Time
    axes[0,2].scatter(np.log10(time_rel + 1), energy, alpha=0.6, s=20)
    axes[0,2].set_xlabel('Log10(Time)')
    axes[0,2].set_ylabel('Energy (GeV)')
    axes[0,2].set_yscale('log')
    axes[0,2].set_title(f'Energy vs Log Time (r={results["energy_logtime_r"]:.3f})')
    axes[0,2].grid(True, alpha=0.3)
    
    # Plot 4: Log Energy vs Log Time
    axes[1,0].scatter(np.log10(time_rel + 1), np.log10(energy), alpha=0.6, s=20)
    axes[1,0].set_xlabel('Log10(Time)')
    axes[1,0].set_ylabel('Log10(Energy)')
    axes[1,0].set_title(f'Log Energy vs Log Time (r={results["log_log_r"]:.3f})')
    axes[1,0].grid(True, alpha=0.3)
    
    # Plot 5: Energy histogram
    axes[1,1].hist(energy, bins=50, alpha=0.7, edgecolor='black')
    axes[1,1].set_xlabel('Energy (GeV)')
    axes[1,1].set_ylabel('Counts')
    axes[1,1].set_xscale('log')
    axes[1,1].set_title('Energy Distribution')
    axes[1,1].grid(True, alpha=0.3)
    
    # Plot 6: Time histogram
    axes[1,2].hist(time_rel, bins=50, alpha=0.7, edgecolor='black')
    axes[1,2].set_xlabel('Time (s)')
    axes[1,2].set_ylabel('Counts')
    axes[1,2].set_title('Time Distribution')
    axes[1,2].grid(True, alpha=0.3)
    
    # Plot 7: Energy vs Time (log scale)
    axes[2,0].scatter(time_rel, energy, alpha=0.6, s=20)
    axes[2,0].set_xlabel('Time (s)')
    axes[2,0].set_ylabel('Energy (GeV)')
    axes[2,0].set_yscale('log')
    axes[2,0].set_xscale('log')
    axes[2,0].set_title('Energy vs Time (Log-Log)')
    axes[2,0].grid(True, alpha=0.3)
    
    # Plot 8: Model comparison
    models = ['Linear', 'Log', 'Quad', 'Cubic', 'Exp', 'Log', 'Sin', 'Poly', 'Red', 'Mix']
    r2_values = [
        results['pearson_r']**2,
        results['log_pearson_r']**2,
        results['quadratic_r2'],
        results['cubic_r2'],
        results['exponential_r2'],
        results['logarithmic_r2'],
        results['sinusoidal_r2'],
        results['polynomial_r2'],
        results['reduced_r2'],
        results['mixed_r2']
    ]
    
    axes[2,1].bar(models, r2_values, alpha=0.7)
    axes[2,1].set_ylabel('R²')
    axes[2,1].set_title('Model Comparison')
    axes[2,1].tick_params(axis='x', rotation=45)
    axes[2,1].grid(True, alpha=0.3)
    
    # Plot 9: Summary
    axes[2,2].text(0.1, 0.8, f'GRB: {grb_name}', fontsize=12, fontweight='bold')
    axes[2,2].text(0.1, 0.7, f'Photons: {results["n_photons"]}', fontsize=10)
    axes[2,2].text(0.1, 0.6, f'Best Model: {results["best_model"]}', fontsize=10)
    axes[2,2].text(0.1, 0.5, f'Hidden Patterns: {results["has_hidden_patterns"]}', fontsize=10)
    axes[2,2].text(0.1, 0.4, f'Spectral Peaks: {results["n_spectral_peaks"]}', fontsize=10)
    axes[2,2].text(0.1, 0.3, f'Clusters: {results["n_clusters"]}', fontsize=10)
    axes[2,2].text(0.1, 0.2, f'Significant: {results["significant_linear"]}', fontsize=10)
    axes[2,2].set_xlim(0, 1)
    axes[2,2].set_ylim(0, 1)
    axes[2,2].axis('off')
    
    plt.tight_layout()
    
    # Salva plot
    plot_filename = f'advanced_qg_analysis_{grb_name.lower()}.png'
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Advanced plot saved: {plot_filename}")

def analyze_all_anomalous_grbs():
    """
    Analizza tutti i GRB anomali per pattern QG nascosti
    """
    print("🚀 DEEP QG ANOMALY ANALYZER")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Lista dei file FITS disponibili
    fits_files = [
        'L251021105813F357373F65_PH00.fits',
        'L251021105813F357373F65_SC00.fits',
        'L251021105939F357373F58_PH00.fits',
        'L251021105939F357373F58_SC00.fits',
        'L251021110034F357373F27_PH00.fits',
        'L251021110034F357373F27_SC00.fits',
        'L251021110134F357373F33_PH00.fits',
        'L251021110134F357373F33_SC00.fits',
        'L251021110233F357373F36_PH00.fits',
        'L251021110233F357373F36_SC00.fits',
        'L251021110325F357373F43_PH00.fits',
        'L251021110325F357373F43_SC00.fits',
        'L251021110442F357373F27_PH00.fits',
        'L251021110442F357373F27_SC00.fits',
        'L251021110535F357373F42_PH00.fits',
        'L251021110535F357373F42_SC00.fits',
        'L251021110629F357373F55_PH00.fits',
        'L251021110629F357373F55_SC00.fits',
        'L251021110739F357373F39_PH00.fits',
        'L251021110739F357373F39_SC00.fits',
        'L251021110835F357373F04_SC00.fits',
        'L251021110941F357373F53_PH00.fits',
        'L251021110941F357373F53_SC00.fits',
        'L251021111027F357373F43_PH00.fits',
        'L251021111027F357373F43_SC00.fits'
    ]
    
    # Filtra solo file PH00 (events)
    event_files = [f for f in fits_files if '_PH00.fits' in f]
    
    # Crea directory per risultati
    os.makedirs('deep_qg_analysis', exist_ok=True)
    
    # Analizza ogni file
    all_results = {}
    
    for i, fits_file in enumerate(event_files, 1):
        grb_name = f"ANOMALOUS_GRB_{i:02d}"
        print(f"\n🔍 Analyzing {grb_name} ({fits_file})...")
        
        # Carica dati
        data = load_fermi_fits_data(fits_file)
        
        # Analizza pattern QG nascosti
        results = detect_hidden_qg_patterns(grb_name, data)
        
        if results:
            # Crea plot diagnostici avanzati
            create_advanced_diagnostic_plots(grb_name, data, results)
            
            # Salva risultati
            all_results[grb_name] = results
    
    # Salva tutti i risultati
    with open('deep_qg_analysis/advanced_analysis_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    # Crea riassunto
    print("\n" + "=" * 60)
    print("🎯 DEEP QG ANALYSIS SUMMARY")
    print("=" * 60)
    
    for grb_name, results in all_results.items():
        print(f"📊 {grb_name}:")
        print(f"   Photons: {results['n_photons']}")
        print(f"   Energy: {results['energy_range'][0]:.3f} - {results['energy_range'][1]:.3f} GeV")
        print(f"   Linear r: {results['pearson_r']:.4f}, σ: {results['pearson_sigma']:.2f}")
        print(f"   Log r: {results['log_pearson_r']:.4f}, σ: {results['log_pearson_sigma']:.2f}")
        print(f"   Best model: {results['best_model']}")
        print(f"   Hidden patterns: {results['has_hidden_patterns']}")
        print(f"   Spectral peaks: {results['n_spectral_peaks']}")
        print(f"   Clusters: {results['n_clusters']}")
        print(f"   Significant: {results['significant_linear']}")
        print()
    
    print("=" * 60)
    print("🎉 DEEP QG ANALYSIS COMPLETE!")
    print("📊 Check 'deep_qg_analysis/' directory for results")
    print("=" * 60)

if __name__ == "__main__":
    analyze_all_anomalous_grbs()
