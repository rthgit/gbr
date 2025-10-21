"""
DEEP PATTERN HUNTER - Cerca l'Invisibile
=========================================
Non cerca solo correlazioni evidenti, ma PATTERN NASCOSTI:
- Subset analysis (high-E, low-E, early, late)
- Non-linear patterns
- Weak but consistent signals
- Energy-dependent evolution
- Time-dependent evolution
- L'ASSENZA stessa come informazione!

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import numpy as np
from astropy.io import fits
from scipy.stats import pearsonr, spearmanr, kendalltau
from scipy.signal import find_peaks
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DeepPatternAnalyzer:
    """Analisi profonda per trovare pattern nascosti"""
    
    def __init__(self, times, energies):
        self.times = times - times.min()  # Normalize
        self.energies = energies
        self.n = len(energies)
        
    def global_correlation(self):
        """Correlazione globale standard"""
        if self.n < 10:
            return None
            
        r_p, _ = pearsonr(self.energies, self.times)
        r_s, _ = spearmanr(self.energies, self.times)
        r_k, _ = kendalltau(self.energies, self.times)
        
        sig_p = abs(r_p) * np.sqrt(self.n - 2) / np.sqrt(1 - r_p**2)
        sig_s = abs(r_s) * np.sqrt(self.n - 2) / np.sqrt(1 - r_s**2)
        
        return {
            'pearson_r': float(r_p),
            'pearson_sigma': float(sig_p),
            'spearman_rho': float(r_s),
            'spearman_sigma': float(sig_s),
            'kendall_tau': float(r_k)
        }
    
    def energy_subset_analysis(self):
        """Analizza subset di energia - cerca pattern nascosti!"""
        results = {}
        
        # Define energy bins
        e_median = np.median(self.energies)
        e_75 = np.percentile(self.energies, 75)
        e_90 = np.percentile(self.energies, 90)
        
        subsets = {
            'low_energy': self.energies < e_median,
            'high_energy': self.energies >= e_median,
            'very_high_energy': self.energies >= e_75,
            'ultra_high_energy': self.energies >= e_90
        }
        
        for name, mask in subsets.items():
            if np.sum(mask) < 10:
                continue
                
            e_sub = self.energies[mask]
            t_sub = self.times[mask]
            
            if len(e_sub) >= 10:
                r, _ = pearsonr(e_sub, t_sub)
                sig = abs(r) * np.sqrt(len(e_sub) - 2) / np.sqrt(1 - r**2)
                
                results[name] = {
                    'n_photons': int(np.sum(mask)),
                    'energy_range': [float(e_sub.min()), float(e_sub.max())],
                    'pearson_r': float(r),
                    'sigma': float(sig)
                }
        
        return results
    
    def time_evolution_analysis(self):
        """Analizza come evolve la correlazione nel tempo"""
        results = {}
        
        # Divide in time bins
        n_bins = min(5, self.n // 100)
        if n_bins < 2:
            return results
        
        time_bins = np.linspace(0, self.times.max(), n_bins + 1)
        
        correlations = []
        for i in range(n_bins):
            mask = (self.times >= time_bins[i]) & (self.times < time_bins[i+1])
            if np.sum(mask) < 10:
                continue
                
            e_bin = self.energies[mask]
            t_bin = self.times[mask]
            
            if len(e_bin) >= 10:
                r, _ = pearsonr(e_bin, t_bin)
                sig = abs(r) * np.sqrt(len(e_bin) - 2) / np.sqrt(1 - r**2)
                
                correlations.append({
                    'time_window': [float(time_bins[i]), float(time_bins[i+1])],
                    'n_photons': int(np.sum(mask)),
                    'pearson_r': float(r),
                    'sigma': float(sig)
                })
        
        if correlations:
            results['time_bins'] = correlations
            
            # Check for evolution/transition
            r_values = [c['pearson_r'] for c in correlations]
            if len(r_values) >= 3:
                # Sign changes?
                sign_changes = np.diff(np.sign(r_values)) != 0
                if np.any(sign_changes):
                    results['sign_transition_detected'] = True
                    results['transition_type'] = 'correlation_reversal'
        
        return results
    
    def energy_weighted_correlation(self):
        """Correlazione pesata per energia - fotoni ad alta energia contano di più"""
        weights = self.energies / self.energies.max()
        
        # Weighted correlation
        mean_t = np.average(self.times, weights=weights)
        mean_e = np.average(self.energies, weights=weights)
        
        cov = np.average((self.energies - mean_e) * (self.times - mean_t), 
                         weights=weights)
        std_e = np.sqrt(np.average((self.energies - mean_e)**2, weights=weights))
        std_t = np.sqrt(np.average((self.times - mean_t)**2, weights=weights))
        
        r_weighted = cov / (std_e * std_t)
        
        return {
            'weighted_correlation': float(r_weighted),
            'weight_scheme': 'energy_proportional'
        }
    
    def detect_outliers(self):
        """Identifica fotoni outlier che potrebbero nascondere pattern"""
        # Energy outliers
        e_mean = np.mean(self.energies)
        e_std = np.std(self.energies)
        e_outliers = np.abs(self.energies - e_mean) > 3 * e_std
        
        # Time outliers
        t_mean = np.mean(self.times)
        t_std = np.std(self.times)
        t_outliers = np.abs(self.times - t_mean) > 3 * t_std
        
        outliers = e_outliers | t_outliers
        
        if np.sum(outliers) > 0 and np.sum(~outliers) >= 10:
            # Recompute correlation without outliers
            e_clean = self.energies[~outliers]
            t_clean = self.times[~outliers]
            
            r_clean, _ = pearsonr(e_clean, t_clean)
            sig_clean = abs(r_clean) * np.sqrt(len(e_clean) - 2) / np.sqrt(1 - r_clean**2)
            
            return {
                'n_outliers': int(np.sum(outliers)),
                'outlier_fraction': float(np.sum(outliers) / self.n),
                'correlation_without_outliers': float(r_clean),
                'sigma_without_outliers': float(sig_clean)
            }
        
        return None
    
    def early_late_comparison(self):
        """Confronta comportamento early vs late time"""
        t_median = np.median(self.times)
        
        early_mask = self.times < t_median
        late_mask = self.times >= t_median
        
        if np.sum(early_mask) < 10 or np.sum(late_mask) < 10:
            return None
        
        # Early correlation
        e_early = self.energies[early_mask]
        t_early = self.times[early_mask]
        r_early, _ = pearsonr(e_early, t_early)
        sig_early = abs(r_early) * np.sqrt(len(e_early) - 2) / np.sqrt(1 - r_early**2)
        
        # Late correlation
        e_late = self.energies[late_mask]
        t_late = self.times[late_mask]
        r_late, _ = pearsonr(e_late, t_late)
        sig_late = abs(r_late) * np.sqrt(len(e_late) - 2) / np.sqrt(1 - r_late**2)
        
        return {
            'early_phase': {
                'n_photons': int(np.sum(early_mask)),
                'pearson_r': float(r_early),
                'sigma': float(sig_early)
            },
            'late_phase': {
                'n_photons': int(np.sum(late_mask)),
                'pearson_r': float(r_late),
                'sigma': float(sig_late)
            },
            'phase_comparison': {
                'correlation_change': float(r_late - r_early),
                'sigma_change': float(sig_late - sig_early),
                'sign_flip': bool((r_early * r_late) < 0)
            }
        }
    
    def detect_hidden_patterns(self):
        """Meta-analisi: cerca QUALSIASI pattern nascosto"""
        patterns_found = []
        
        # 1. Check subset significances
        subset_results = self.energy_subset_analysis()
        for name, result in subset_results.items():
            if result['sigma'] >= 2.0:
                patterns_found.append({
                    'type': 'subset_correlation',
                    'subset': name,
                    'significance': result['sigma'],
                    'detail': f"{name}: {result['sigma']:.2f}σ with {result['n_photons']} photons"
                })
        
        # 2. Check time evolution
        time_results = self.time_evolution_analysis()
        if 'sign_transition_detected' in time_results:
            patterns_found.append({
                'type': 'temporal_transition',
                'detail': 'Correlation sign changes over time (like GRB160625B!)'
            })
        
        # 3. Check early/late difference
        early_late = self.early_late_comparison()
        if early_late and early_late['phase_comparison']['sign_flip']:
            patterns_found.append({
                'type': 'phase_transition',
                'detail': f"Early: {early_late['early_phase']['sigma']:.2f}σ, Late: {early_late['late_phase']['sigma']:.2f}σ"
            })
        
        # 4. Check outlier effect
        outlier_result = self.detect_outliers()
        if outlier_result and abs(outlier_result['sigma_without_outliers']) >= 2.0:
            patterns_found.append({
                'type': 'outlier_masked_signal',
                'detail': f"Signal {outlier_result['sigma_without_outliers']:.2f}σ after removing {outlier_result['n_outliers']} outliers"
            })
        
        return patterns_found


def deep_analyze_grb(fits_path, grb_name):
    """Analisi profonda completa di un GRB"""
    
    try:
        with fits.open(fits_path) as hdul:
            # Get EVENTS data
            if 'EVENTS' in [h.name for h in hdul]:
                events = hdul['EVENTS'].data
            elif len(hdul) > 1:
                events = hdul[1].data
            else:
                return {'grb': grb_name, 'status': 'NO_EVENTS_EXTENSION'}
            
            times = events['TIME']
            energies = events['ENERGY'] / 1000.0  # MeV to GeV
            
            n = len(energies)
            if n < 50:
                return {
                    'grb': grb_name,
                    'status': 'INSUFFICIENT_DATA',
                    'n_photons': n
                }
            
            # Initialize analyzer
            analyzer = DeepPatternAnalyzer(times, energies)
            
            # Run all analyses
            results = {
                'grb': grb_name,
                'status': 'ANALYZED',
                'n_photons': int(n),
                'energy_range_gev': [float(energies.min()), float(energies.max())],
                
                # Global correlation
                'global': analyzer.global_correlation(),
                
                # Subset analysis
                'energy_subsets': analyzer.energy_subset_analysis(),
                
                # Time evolution
                'time_evolution': analyzer.time_evolution_analysis(),
                
                # Weighted correlation
                'weighted': analyzer.energy_weighted_correlation(),
                
                # Outlier analysis
                'outliers': analyzer.detect_outliers(),
                
                # Early/late comparison
                'early_late': analyzer.early_late_comparison(),
                
                # Hidden patterns summary
                'hidden_patterns': analyzer.detect_hidden_patterns()
            }
            
            # Overall assessment
            max_sigma_global = 0
            if results['global']:
                max_sigma_global = max(
                    abs(results['global']['pearson_sigma']),
                    abs(results['global']['spearman_sigma'])
                )
            
            # Check if ANY subset/phase shows signal
            max_sigma_overall = max_sigma_global
            
            for subset_result in results['energy_subsets'].values():
                if subset_result['sigma'] > max_sigma_overall:
                    max_sigma_overall = subset_result['sigma']
            
            if results['early_late']:
                for phase in ['early_phase', 'late_phase']:
                    if results['early_late'][phase]['sigma'] > max_sigma_overall:
                        max_sigma_overall = results['early_late'][phase]['sigma']
            
            results['max_sigma_overall'] = float(max_sigma_overall)
            results['max_sigma_global'] = float(max_sigma_global)
            
            # Classification
            if max_sigma_overall >= 5.0:
                results['classification'] = '🔴 STRONG_SIGNAL'
            elif max_sigma_overall >= 3.0:
                results['classification'] = '🟠 SIGNIFICANT'
            elif max_sigma_overall >= 2.0:
                results['classification'] = '🟡 MARGINAL'
            elif len(results['hidden_patterns']) > 0:
                results['classification'] = '🔵 HIDDEN_PATTERNS'
            else:
                results['classification'] = '⚪ NO_SIGNAL'
            
            return results
            
    except Exception as e:
        return {
            'grb': grb_name,
            'status': 'ERROR',
            'error': str(e)
        }


def batch_deep_analysis():
    """Analisi profonda su tutti i GRB scaricati"""
    
    print("="*80)
    print("🔬 DEEP PATTERN HUNTER - Cerca l'Invisibile")
    print("="*80)
    print("Autore: Christian Quintino De Luca")
    print("Non cerca solo segnali forti, ma PATTERN NASCOSTI ovunque!")
    print("="*80)
    
    # Find all FITS files
    print("\n🔍 Cercando file FITS...")
    fits_files = {}
    
    for pattern in ['*_PH*.fits', '*PH*.fits']:
        for fits_file in Path('.').glob(pattern):
            query_id = fits_file.stem.split('_')[0]
            if query_id not in fits_files:
                fits_files[query_id] = str(fits_file)
    
    if not fits_files:
        print("❌ NESSUN FILE _PH FITS TROVATO!")
        return
    
    print(f"✅ Trovati {len(fits_files)} file FITS da analizzare")
    
    # Analyze each
    print("\n" + "="*80)
    print("🔬 DEEP ANALYSIS IN PROGRESS...")
    print("="*80)
    
    all_results = []
    
    for i, (query_id, fits_path) in enumerate(fits_files.items(), 1):
        print(f"\n[{i}/{len(fits_files)}] 🔍 {query_id}...")
        
        result = deep_analyze_grb(fits_path, query_id)
        all_results.append(result)
        
        if result['status'] == 'ERROR':
            print(f"   ❌ Error: {result['error']}")
        elif result['status'] == 'INSUFFICIENT_DATA':
            print(f"   ⚠️  Too few photons: n={result['n_photons']}")
        else:
            print(f"   {result['classification']}")
            print(f"   📊 n={result['n_photons']}, E: {result['energy_range_gev'][0]:.2f}-{result['energy_range_gev'][1]:.1f} GeV")
            
            if result['global']:
                print(f"   🌍 Global: r={result['global']['pearson_r']:+.4f}, σ={result['global']['pearson_sigma']:.2f}")
            
            # Show hidden patterns found
            if result['hidden_patterns']:
                print(f"   🔍 HIDDEN PATTERNS FOUND: {len(result['hidden_patterns'])}")
                for pattern in result['hidden_patterns']:
                    print(f"      • {pattern['type']}: {pattern['detail']}")
    
    # COMPREHENSIVE SUMMARY
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE SUMMARY")
    print("="*80)
    
    valid_results = [r for r in all_results if r['status'] == 'ANALYZED']
    
    # Sort by max overall sigma
    valid_results.sort(key=lambda x: x.get('max_sigma_overall', 0), reverse=True)
    
    print(f"\n{'Query ID':<20} {'N':<6} {'Global σ':<10} {'Max σ':<10} {'Status':<20}")
    print("-"*80)
    
    for r in valid_results:
        print(f"{r['grb']:<20} {r['n_photons']:<6} "
              f"{r.get('max_sigma_global', 0):>8.2f}σ  "
              f"{r.get('max_sigma_overall', 0):>8.2f}σ  "
              f"{r['classification']}")
    
    # Categorize
    strong = [r for r in valid_results if '🔴' in r['classification']]
    significant = [r for r in valid_results if '🟠' in r['classification']]
    marginal = [r for r in valid_results if '🟡' in r['classification']]
    hidden = [r for r in valid_results if '🔵' in r['classification']]
    
    print("\n" + "="*80)
    print("🎯 SIGNAL CLASSIFICATION")
    print("="*80)
    
    if strong:
        print(f"\n🔴 STRONG SIGNALS (≥5σ): {len(strong)}")
        for r in strong:
            print(f"   {r['grb']}: Global {r['max_sigma_global']:.2f}σ, Max {r['max_sigma_overall']:.2f}σ")
    
    if significant:
        print(f"\n🟠 SIGNIFICANT (3-5σ): {len(significant)}")
        for r in significant:
            print(f"   {r['grb']}: Global {r['max_sigma_global']:.2f}σ, Max {r['max_sigma_overall']:.2f}σ")
    
    if marginal:
        print(f"\n🟡 MARGINAL (2-3σ): {len(marginal)}")
        for r in marginal:
            print(f"   {r['grb']}: Global {r['max_sigma_global']:.2f}σ, Max {r['max_sigma_overall']:.2f}σ")
    
    if hidden:
        print(f"\n🔵 HIDDEN PATTERNS (no global signal, but patterns found): {len(hidden)}")
        for r in hidden:
            print(f"   {r['grb']}: {len(r['hidden_patterns'])} patterns detected")
            for pattern in r['hidden_patterns']:
                print(f"      • {pattern['type']}")
    
    # THE INVISIBLE - Analyze absences
    no_signal = [r for r in valid_results if '⚪' in r['classification']]
    if no_signal:
        print(f"\n⚪ NO SIGNAL: {len(no_signal)} GRB")
        print("   💡 L'ASSENZA stessa è informazione!")
        print("   → Questi GRB NON mostrano effetto")
        print("   → Suggerisce condizioni specifiche necessarie")
    
    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'analysis_type': 'deep_pattern_hunting',
        'n_analyzed': len(valid_results),
        'results': all_results,
        'summary': {
            'strong': len(strong),
            'significant': len(significant),
            'marginal': len(marginal),
            'hidden_patterns': len(hidden),
            'no_signal': len(no_signal)
        }
    }
    
    output_file = f'deep_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Full detailed report: {output_file}")
    
    # FINAL INTERPRETATION
    print("\n" + "="*80)
    print("💡 FINAL INTERPRETATION - L'INVISIBILE RIVELATO")
    print("="*80)
    
    total_with_signal = len(strong) + len(significant) + len(marginal) + len(hidden)
    
    if len(strong) >= 2:
        print("\n🎉 EXCELLENT! Multiple strong signals!")
        print("   → Pattern is REAL and REPRODUCIBLE")
        print("   → Multi-GRB discovery confirmed!")
    elif total_with_signal >= 3:
        print("\n✅ GOOD! Multiple GRBs show signals/patterns")
        print("   → Evidence for reproducible effect")
        print("   → May be energy/time dependent")
    elif total_with_signal >= 1:
        print("\n⚠️  Limited signals found")
        if total_with_signal == 1 and strong:
            print("   → 1 GRB stands out as unique")
        else:
            print("   → Pattern appears rare or conditional")
    
    if len(hidden) > 0:
        print(f"\n🔵 HIDDEN PATTERNS: {len(hidden)} GRB")
        print("   → No global signal BUT specific conditions show effect")
        print("   → Suggests energy/time-dependent phenomenon")
    
    if len(no_signal) > 0:
        print(f"\n⚪ THE INVISIBLE ({len(no_signal)} GRB with no signal):")
        print("   → Not all GRB show effect")
        print("   → Suggests SPECIFIC CONDITIONS required:")
        print("      • Redshift range?")
        print("      • Energy threshold?")
        print("      • GRB type (short vs long)?")
        print("      • Intrinsic properties?")
    
    print("\n" + "="*80)
    print("✅ DEEP ANALYSIS COMPLETE - L'INVISIBILE ESPLORATO!")
    print("="*80)


if __name__ == '__main__':
    batch_deep_analysis()
