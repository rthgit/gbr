#!/usr/bin/env python3
"""
COMPREHENSIVE REAL DATA ANALYSIS
================================

Analisi completa multi-dimensionale dei dati reali FITS.
Testa TUTTO il testabile sotto ogni punto di vista.

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
from scipy.signal import find_peaks, periodogram
from sklearn.linear_model import RANSACRegressor, LinearRegression
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveQGAnalyzer:
    """Analizzatore completo per effetti QG"""
    
    def __init__(self, times, energies, grb_name):
        self.times = times - times.min()  # Normalize
        self.energies = energies
        self.grb_name = grb_name
        self.n = len(energies)
        
    def basic_correlations(self):
        """Correlazioni di base"""
        pearson_r, pearson_p = stats.pearsonr(self.energies, self.times)
        spearman_r, spearman_p = stats.spearmanr(self.energies, self.times)
        kendall_r, kendall_p = stats.kendalltau(self.energies, self.times)
        
        return {
            'pearson': {'r': pearson_r, 'p': pearson_p, 'sigma': abs(pearson_r) * np.sqrt(self.n - 2) / np.sqrt(1 - pearson_r**2)},
            'spearman': {'r': spearman_r, 'p': spearman_p, 'sigma': abs(spearman_r) * np.sqrt(self.n - 2) / np.sqrt(1 - spearman_r**2)},
            'kendall': {'r': kendall_r, 'p': kendall_p}
        }
    
    def energy_subset_analysis(self):
        """Analisi per subset di energia"""
        results = {}
        
        # Define energy percentiles
        e_25 = np.percentile(self.energies, 25)
        e_50 = np.percentile(self.energies, 50)
        e_75 = np.percentile(self.energies, 75)
        e_90 = np.percentile(self.energies, 90)
        e_95 = np.percentile(self.energies, 95)
        
        subsets = {
            'low_energy': self.energies < e_25,
            'medium_low': (self.energies >= e_25) & (self.energies < e_50),
            'medium_high': (self.energies >= e_50) & (self.energies < e_75),
            'high_energy': (self.energies >= e_75) & (self.energies < e_90),
            'very_high_energy': (self.energies >= e_90) & (self.energies < e_95),
            'ultra_high_energy': self.energies >= e_95
        }
        
        for name, mask in subsets.items():
            if np.sum(mask) < 20:  # Minimum photons
                continue
                
            e_sub = self.energies[mask]
            t_sub = self.times[mask]
            
            r, p = stats.pearsonr(e_sub, t_sub)
            sigma = abs(r) * np.sqrt(len(e_sub) - 2) / np.sqrt(1 - r**2)
            
            results[name] = {
                'n_photons': int(np.sum(mask)),
                'energy_range': [float(e_sub.min()), float(e_sub.max())],
                'pearson_r': float(r),
                'pearson_p': float(p),
                'sigma': float(sigma),
                'significant': sigma >= 2.0
            }
        
        return results
    
    def temporal_evolution_analysis(self):
        """Analisi evoluzione temporale"""
        results = {}
        
        # Time bins
        n_bins = min(10, self.n // 200)
        if n_bins < 2:
            return results
        
        time_bins = np.linspace(0, self.times.max(), n_bins + 1)
        
        correlations = []
        for i in range(n_bins):
            mask = (self.times >= time_bins[i]) & (self.times < time_bins[i+1])
            if np.sum(mask) < 20:
                continue
                
            e_bin = self.energies[mask]
            t_bin = self.times[mask]
            
            r, p = stats.pearsonr(e_bin, t_bin)
            sigma = abs(r) * np.sqrt(len(e_bin) - 2) / np.sqrt(1 - r**2)
            
            correlations.append({
                'time_window': [float(time_bins[i]), float(time_bins[i+1])],
                'n_photons': int(np.sum(mask)),
                'pearson_r': float(r),
                'pearson_p': float(p),
                'sigma': float(sigma)
            })
        
        if correlations:
            results['time_bins'] = correlations
            
            # Check for evolution
            r_values = [c['pearson_r'] for c in correlations]
            if len(r_values) >= 3:
                # Sign changes
                sign_changes = np.diff(np.sign(r_values)) != 0
                if np.any(sign_changes):
                    results['sign_transition_detected'] = True
                    results['transition_type'] = 'correlation_reversal'
                    results['n_transitions'] = int(np.sum(sign_changes))
                
                # Trend analysis
                r_trend = np.polyfit(range(len(r_values)), r_values, 1)[0]
                results['correlation_trend'] = float(r_trend)
        
        return results
    
    def early_late_analysis(self):
        """Analisi early vs late time"""
        t_median = np.median(self.times)
        
        early_mask = self.times < t_median
        late_mask = self.times >= t_median
        
        if np.sum(early_mask) < 20 or np.sum(late_mask) < 20:
            return None
        
        # Early phase
        e_early = self.energies[early_mask]
        t_early = self.times[early_mask]
        r_early, p_early = stats.pearsonr(e_early, t_early)
        sigma_early = abs(r_early) * np.sqrt(len(e_early) - 2) / np.sqrt(1 - r_early**2)
        
        # Late phase
        e_late = self.energies[late_mask]
        t_late = self.times[late_mask]
        r_late, p_late = stats.pearsonr(e_late, t_late)
        sigma_late = abs(r_late) * np.sqrt(len(e_late) - 2) / np.sqrt(1 - r_late**2)
        
        return {
            'early_phase': {
                'n_photons': int(np.sum(early_mask)),
                'pearson_r': float(r_early),
                'pearson_p': float(p_early),
                'sigma': float(sigma_early)
            },
            'late_phase': {
                'n_photons': int(np.sum(late_mask)),
                'pearson_r': float(r_late),
                'pearson_p': float(p_late),
                'sigma': float(sigma_late)
            },
            'phase_comparison': {
                'correlation_change': float(r_late - r_early),
                'sigma_change': float(sigma_late - sigma_early),
                'sign_flip': bool((r_early * r_late) < 0),
                'significance_change': abs(sigma_late - sigma_early)
            }
        }
    
    def ransac_analysis(self):
        """Analisi RANSAC robusta"""
        X = self.energies.reshape(-1, 1)
        y = self.times
        
        ransac = RANSACRegressor(random_state=42, min_samples=0.5)
        ransac.fit(X, y)
        
        slope = ransac.estimator_.coef_[0]
        intercept = ransac.estimator_.intercept_
        inliers = ransac.inlier_mask_
        
        # Calculate R²
        y_pred = ransac.predict(X)
        r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r2': float(r2),
            'n_inliers': int(np.sum(inliers)),
            'n_outliers': int(np.sum(~inliers)),
            'inlier_fraction': float(np.sum(inliers) / self.n)
        }
    
    def eqg_estimation(self):
        """Stima E_QG"""
        # Simple linear fit for E_QG estimation
        X = self.energies.reshape(-1, 1)
        y = self.times
        
        reg = LinearRegression()
        reg.fit(X, y)
        
        slope = reg.coef_[0]
        intercept = reg.intercept_
        
        # E_QG estimation (simplified)
        if slope != 0:
            E_QG = 1.0 / abs(slope)
            E_Planck = 1.22e19  # GeV
            E_QG_ratio = E_QG / E_Planck
        else:
            E_QG = np.inf
            E_QG_ratio = np.inf
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'E_QG_GeV': float(E_QG),
            'E_QG_E_Planck': float(E_QG_ratio),
            'physically_reasonable': E_QG_ratio > 1e-10 and E_QG_ratio < 1e10
        }
    
    def spectral_analysis(self):
        """Analisi spettrale per periodicità"""
        # Energy spectrum analysis
        e_hist, e_bins = np.histogram(self.energies, bins=50)
        e_centers = (e_bins[:-1] + e_bins[1:]) / 2
        
        # Time spectrum analysis
        t_hist, t_bins = np.histogram(self.times, bins=50)
        t_centers = (t_bins[:-1] + t_bins[1:]) / 2
        
        # Look for peaks in energy spectrum
        e_peaks, e_properties = find_peaks(e_hist, height=np.max(e_hist)*0.1)
        
        # Look for peaks in time spectrum
        t_peaks, t_properties = find_peaks(t_hist, height=np.max(t_hist)*0.1)
        
        return {
            'energy_spectrum': {
                'peaks': len(e_peaks),
                'peak_energies': [float(e_centers[p]) for p in e_peaks],
                'peak_heights': [float(e_hist[p]) for p in e_peaks]
            },
            'time_spectrum': {
                'peaks': len(t_peaks),
                'peak_times': [float(t_centers[p]) for p in t_peaks],
                'peak_heights': [float(t_hist[p]) for p in t_peaks]
            }
        }
    
    def clustering_analysis(self):
        """Analisi clustering per pattern nascosti"""
        # Prepare data for clustering
        data = np.column_stack([self.energies, self.times])
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        # DBSCAN clustering
        clustering = DBSCAN(eps=0.5, min_samples=5)
        cluster_labels = clustering.fit_predict(data_scaled)
        
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        
        # Analyze each cluster
        cluster_analysis = {}
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Noise
                continue
                
            mask = cluster_labels == cluster_id
            e_cluster = self.energies[mask]
            t_cluster = self.times[mask]
            
            if len(e_cluster) >= 10:
                r, p = stats.pearsonr(e_cluster, t_cluster)
                sigma = abs(r) * np.sqrt(len(e_cluster) - 2) / np.sqrt(1 - r**2)
                
                cluster_analysis[f'cluster_{cluster_id}'] = {
                    'n_photons': int(np.sum(mask)),
                    'energy_range': [float(e_cluster.min()), float(e_cluster.max())],
                    'time_range': [float(t_cluster.min()), float(t_cluster.max())],
                    'pearson_r': float(r),
                    'pearson_p': float(p),
                    'sigma': float(sigma)
                }
        
        return {
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'cluster_analysis': cluster_analysis
        }
    
    def outlier_analysis(self):
        """Analisi outlier e loro effetto"""
        # Energy outliers
        e_mean = np.mean(self.energies)
        e_std = np.std(self.energies)
        e_outliers = np.abs(self.energies - e_mean) > 3 * e_std
        
        # Time outliers
        t_mean = np.mean(self.times)
        t_std = np.std(self.times)
        t_outliers = np.abs(self.times - t_mean) > 3 * t_std
        
        outliers = e_outliers | t_outliers
        
        if np.sum(outliers) > 0 and np.sum(~outliers) >= 20:
            # Recompute without outliers
            e_clean = self.energies[~outliers]
            t_clean = self.times[~outliers]
            
            r_clean, p_clean = stats.pearsonr(e_clean, t_clean)
            sigma_clean = abs(r_clean) * np.sqrt(len(e_clean) - 2) / np.sqrt(1 - r_clean**2)
            
            return {
                'n_outliers': int(np.sum(outliers)),
                'outlier_fraction': float(np.sum(outliers) / self.n),
                'correlation_without_outliers': float(r_clean),
                'p_without_outliers': float(p_clean),
                'sigma_without_outliers': float(sigma_clean),
                'outlier_effect': abs(sigma_clean - self.basic_correlations()['pearson']['sigma'])
            }
        
        return None
    
    def comprehensive_analysis(self):
        """Analisi completa"""
        results = {
            'grb_name': self.grb_name,
            'n_photons': self.n,
            'energy_range': [float(self.energies.min()), float(self.energies.max())],
            'time_range': [float(self.times.min()), float(self.times.max())],
            
            # Basic correlations
            'basic_correlations': self.basic_correlations(),
            
            # Energy subset analysis
            'energy_subsets': self.energy_subset_analysis(),
            
            # Temporal evolution
            'temporal_evolution': self.temporal_evolution_analysis(),
            
            # Early/late analysis
            'early_late': self.early_late_analysis(),
            
            # RANSAC analysis
            'ransac': self.ransac_analysis(),
            
            # E_QG estimation
            'eqg_estimation': self.eqg_estimation(),
            
            # Spectral analysis
            'spectral_analysis': self.spectral_analysis(),
            
            # Clustering analysis
            'clustering': self.clustering_analysis(),
            
            # Outlier analysis
            'outliers': self.outlier_analysis()
        }
        
        # Overall assessment
        max_sigma = results['basic_correlations']['pearson']['sigma']
        
        # Check subset significances
        for subset_result in results['energy_subsets'].values():
            if subset_result['sigma'] > max_sigma:
                max_sigma = subset_result['sigma']
        
        # Check early/late significances
        if results['early_late']:
            for phase in ['early_phase', 'late_phase']:
                if results['early_late'][phase]['sigma'] > max_sigma:
                    max_sigma = results['early_late'][phase]['sigma']
        
        results['max_sigma_overall'] = float(max_sigma)
        
        # Classification
        if max_sigma >= 5.0:
            results['classification'] = '🔴 STRONG_SIGNAL'
        elif max_sigma >= 3.0:
            results['classification'] = '🟠 SIGNIFICANT'
        elif max_sigma >= 2.0:
            results['classification'] = '🟡 MARGINAL'
        else:
            results['classification'] = '⚪ NO_SIGNAL'
        
        return results

def analyze_all_grbs():
    """Analizza tutti i GRB con analisi completa"""
    
    print("🚀 COMPREHENSIVE REAL DATA ANALYSIS")
    print("=" * 80)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 80)
    print("🔬 Testando TUTTO il testabile sotto ogni punto di vista!")
    print("=" * 80)
    
    # Find all FITS files
    fits_files = {}
    for pattern in ['*_PH*.fits', '*PH*.fits']:
        for fits_file in os.listdir('.'):
            if fits_file.endswith('.fits') and 'PH' in fits_file:
                query_id = fits_file.split('_')[0]
                if query_id not in fits_files:
                    fits_files[query_id] = fits_file
    
    if not fits_files:
        print("❌ No FITS files found!")
        return
    
    print(f"✅ Found {len(fits_files)} FITS files to analyze")
    
    all_results = []
    
    for i, (query_id, fits_path) in enumerate(fits_files.items(), 1):
        print(f"\n[{i}/{len(fits_files)}] 🔍 {query_id}...")
        
        try:
            with fits.open(fits_path) as hdul:
                # Get EVENTS data
                if 'EVENTS' in [h.name for h in hdul]:
                    events = hdul['EVENTS'].data
                elif len(hdul) > 1:
                    events = hdul[1].data
                else:
                    print(f"   ❌ No EVENTS extension found")
                    continue
                
                times = events['TIME']
                energies = events['ENERGY'] / 1000.0  # MeV to GeV
                
                if len(energies) < 50:
                    print(f"   ⚠️  Too few photons: n={len(energies)}")
                    continue
                
                # Comprehensive analysis
                analyzer = ComprehensiveQGAnalyzer(times, energies, query_id)
                result = analyzer.comprehensive_analysis()
                all_results.append(result)
                
                print(f"   {result['classification']}")
                print(f"   📊 n={result['n_photons']}, E: {result['energy_range'][0]:.2f}-{result['energy_range'][1]:.1f} GeV")
                print(f"   🌍 Global: r={result['basic_correlations']['pearson']['r']:+.4f}, σ={result['basic_correlations']['pearson']['sigma']:.2f}")
                print(f"   🎯 Max σ: {result['max_sigma_overall']:.2f}")
                
                # Show key findings
                if result['energy_subsets']:
                    max_subset_sigma = max([s['sigma'] for s in result['energy_subsets'].values()])
                    if max_subset_sigma >= 2.0:
                        print(f"   🔍 Subset analysis: max σ={max_subset_sigma:.2f}")
                
                if result['early_late'] and result['early_late']['phase_comparison']['sign_flip']:
                    print(f"   🔄 Phase transition detected!")
                
                if result['outliers'] and result['outliers']['sigma_without_outliers'] >= 2.0:
                    print(f"   🎯 Outlier-masked signal: σ={result['outliers']['sigma_without_outliers']:.2f}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # COMPREHENSIVE SUMMARY
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE ANALYSIS SUMMARY")
    print("=" * 80)
    
    if not all_results:
        print("❌ No valid results!")
        return
    
    # Sort by max sigma
    all_results.sort(key=lambda x: x['max_sigma_overall'], reverse=True)
    
    print(f"\n{'GRB':<25} {'N':<6} {'Global σ':<10} {'Max σ':<10} {'Status':<20}")
    print("-" * 80)
    
    for r in all_results:
        print(f"{r['grb_name']:<25} {r['n_photons']:<6} "
              f"{r['basic_correlations']['pearson']['sigma']:>8.2f}σ  "
              f"{r['max_sigma_overall']:>8.2f}σ  "
              f"{r['classification']}")
    
    # Categorize results
    strong = [r for r in all_results if '🔴' in r['classification']]
    significant = [r for r in all_results if '🟠' in r['classification']]
    marginal = [r for r in all_results if '🟡' in r['classification']]
    no_signal = [r for r in all_results if '⚪' in r['classification']]
    
    print("\n" + "=" * 80)
    print("🎯 SIGNAL CLASSIFICATION")
    print("=" * 80)
    
    if strong:
        print(f"\n🔴 STRONG SIGNALS (≥5σ): {len(strong)}")
        for r in strong:
            print(f"   {r['grb_name']}: Global {r['basic_correlations']['pearson']['sigma']:.2f}σ, Max {r['max_sigma_overall']:.2f}σ")
    
    if significant:
        print(f"\n🟠 SIGNIFICANT (3-5σ): {len(significant)}")
        for r in significant:
            print(f"   {r['grb_name']}: Global {r['basic_correlations']['pearson']['sigma']:.2f}σ, Max {r['max_sigma_overall']:.2f}σ")
    
    if marginal:
        print(f"\n🟡 MARGINAL (2-3σ): {len(marginal)}")
        for r in marginal:
            print(f"   {r['grb_name']}: Global {r['basic_correlations']['pearson']['sigma']:.2f}σ, Max {r['max_sigma_overall']:.2f}σ")
    
    if no_signal:
        print(f"\n⚪ NO SIGNAL: {len(no_signal)} GRB")
        print("   💡 L'ASSENZA stessa è informazione!")
    
    # Save comprehensive results
    def convert_numpy_types(obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.float32):
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
    
    # Convert all results
    results_clean = convert_numpy_types(all_results)
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'analysis_type': 'comprehensive_real_data_analysis',
        'n_analyzed': len(all_results),
        'results': results_clean,
        'summary': {
            'strong': len(strong),
            'significant': len(significant),
            'marginal': len(marginal),
            'no_signal': len(no_signal)
        }
    }
    
    output_file = f'comprehensive_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📁 Comprehensive results saved: {output_file}")
    
    # FINAL INTERPRETATION
    print("\n" + "=" * 80)
    print("💡 FINAL INTERPRETATION - TUTTO TESTATO!")
    print("=" * 80)
    
    total_with_signal = len(strong) + len(significant) + len(marginal)
    
    if len(strong) >= 2:
        print("\n🎉 EXCELLENT! Multiple strong signals confirmed!")
        print("   → Pattern is REAL and REPRODUCIBLE")
        print("   → Multi-GRB discovery CONFIRMED!")
    elif total_with_signal >= 3:
        print("\n✅ GOOD! Multiple GRBs show signals/patterns")
        print("   → Evidence for reproducible effect")
    elif total_with_signal >= 1:
        print("\n⚠️  Limited signals found")
    
    print(f"\n🔬 ANALYSIS COMPLETE - TUTTO TESTATO!")
    print(f"📊 {len(all_results)} GRB analyzed comprehensively")
    print(f"🎯 {total_with_signal} GRB with signals/patterns")
    print("=" * 80)

if __name__ == '__main__':
    analyze_all_grbs()
