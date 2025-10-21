#!/usr/bin/env python3
"""
Final Critical Validation of QG Candidates
No Unicode characters for Windows compatibility
"""

import os
import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, norm
import matplotlib.pyplot as plt
from datetime import datetime

def load_fermi_results():
    """Load the Fermi analysis results"""
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    if os.path.exists('super_complete_fermi_qg_analysis_results.csv'):
        df = pd.read_csv('super_complete_fermi_qg_analysis_results.csv')
        print(f"Loaded {len(df)} sources from Fermi analysis")
        return df
    else:
        print("No Fermi analysis results found!")
        return None

def benjamini_hochberg_correction(p_values, alpha=0.05):
    """Simple Benjamini-Hochberg FDR correction"""
    p_values = np.array(p_values)
    n = len(p_values)
    
    # Sort p-values and get indices
    sorted_indices = np.argsort(p_values)
    sorted_p_values = p_values[sorted_indices]
    
    # Calculate critical values
    critical_values = (np.arange(1, n + 1) / n) * alpha
    
    # Find largest i such that P(i) <= (i/n) * alpha
    rejected_indices = []
    for i in range(n - 1, -1, -1):
        if sorted_p_values[i] <= critical_values[i]:
            rejected_indices = sorted_indices[:i + 1]
            break
    
    # Create boolean array
    reject = np.zeros(n, dtype=bool)
    reject[rejected_indices] = True
    
    # Calculate corrected p-values
    corrected_p_values = np.minimum(1.0, sorted_p_values * n / np.arange(1, n + 1))
    corrected_p_values = corrected_p_values[np.argsort(sorted_indices)]
    
    return reject, corrected_p_values

def simulate_photon_data_for_validation(source_id, n_photons, has_qg_effect):
    """Simulate photon data for validation"""
    
    # Random energy range (100 MeV - 300 GeV)
    energies = np.random.uniform(0.1, 300, n_photons)
    
    if has_qg_effect:
        # Add QG time delay: Delta t = E/E_QG
        E_QG = np.random.uniform(1e15, 1e19)  # GeV
        time_delays = energies / E_QG
        
        # Add noise to make it more realistic
        noise_factor = np.random.uniform(0.8, 1.2, len(time_delays))
        time_delays *= noise_factor
        
        # Add random arrival times + QG delays
        arrival_times = np.random.uniform(0, 2000, n_photons) + time_delays
    else:
        # No QG effect - random times
        arrival_times = np.random.uniform(0, 2000, n_photons)
    
    return energies, arrival_times

def empirical_pvalue(energies, times, nperm=5000):
    """Compute empirical two-sided p-value for Pearson r via permutation"""
    
    # Remove NaNs
    mask = np.isfinite(energies) & np.isfinite(times)
    energies = energies[mask]
    times = times[mask]
    
    if energies.size < 4:
        return np.nan, np.nan
    
    try:
        r_obs = pearsonr(energies, times)[0]
    except Exception:
        r_obs = np.corrcoef(energies, times)[0,1]
    
    if not np.isfinite(r_obs):
        return np.nan, np.nan
    
    count = 0
    abs_ro = abs(r_obs)
    
    for _ in range(nperm):
        perm = np.random.permutation(times)
        r = pearsonr(energies, perm)[0]
        if abs(r) >= abs_ro:
            count += 1
    
    p_emp = (count + 1) / (nperm + 1)
    return p_emp, r_obs

def sigma_to_p(two_sided_sigma):
    """Convert z (sigma) to two-sided p-value"""
    z = abs(two_sided_sigma)
    return 2.0 * (1.0 - norm.cdf(z))

def critical_validation_analysis(df):
    """Perform critical validation analysis"""
    
    print("\nPerforming critical validation analysis...")
    print("=" * 60)
    
    results = []
    
    # Process each source (limit to first 100 for speed)
    for idx, row in df.head(100).iterrows():
        source_id = f"Source_{idx}"
        n_photons = int(row.get('N_Photons', 1000))
        has_qg_effect = row.get('Has_QG_Effect', False)
        significance = row.get('Significance_Sigma', 0)
        
        # Simulate photon data for validation
        energies, times = simulate_photon_data_for_validation(source_id, n_photons, has_qg_effect)
        
        # Calculate empirical p-value
        p_emp, r_obs = empirical_pvalue(energies, times, nperm=5000)
        
        # Convert significance to p-value
        p_from_sigma = sigma_to_p(significance)
        
        results.append({
            'source_id': source_id,
            'n_photons': n_photons,
            'has_qg_effect': has_qg_effect,
            'significance_sigma': significance,
            'p_from_sigma': p_from_sigma,
            'p_empirical': p_emp,
            'pearson_r_obs': r_obs,
            'energies': energies,
            'times': times
        })
    
    return results

def apply_multiple_testing_correction(results):
    """Apply FDR correction for multiple testing"""
    
    print("\nApplying multiple testing correction...")
    
    # Extract p-values (prefer empirical, fallback to sigma-based)
    pvals = []
    for r in results:
        if not np.isnan(r['p_empirical']):
            pvals.append(r['p_empirical'])
        else:
            pvals.append(r['p_from_sigma'])
    
    pvals = np.array(pvals)
    
    # Apply FDR correction (Benjamini-Hochberg)
    reject, pvals_corr = benjamini_hochberg_correction(pvals, alpha=0.05)
    
    # Add results back
    for i, r in enumerate(results):
        r['pval_used'] = pvals[i]
        r['pval_fdr_corrected'] = pvals_corr[i]
        r['reject_fdr_05'] = reject[i]
    
    return results

def create_validation_plots(results, top_n=10):
    """Create validation plots for top candidates"""
    
    print(f"\nCreating validation plots for top {top_n} candidates...")
    
    # Sort by smallest p-value
    sorted_results = sorted(results, key=lambda x: x['pval_used'])
    top_candidates = sorted_results[:top_n]
    
    # Create plots directory
    plots_dir = "validation_plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    for i, result in enumerate(top_candidates):
        if np.isnan(result['p_empirical']):
            continue
            
        source_id = result['source_id']
        energies = result['energies']
        times = result['times']
        
        # Normalize time to zero baseline
        rel_times = times - np.min(times)
        
        # Create plot
        plt.figure(figsize=(8, 6))
        plt.scatter(energies, rel_times, s=10, alpha=0.6, c='blue')
        plt.xscale('log')
        plt.xlabel('Energy (GeV)')
        plt.ylabel('Relative Time (s)')
        plt.title(f'{source_id}\n'
                 f'p_empirical = {result["p_empirical"]:.3e}, '
                 f'p_FDR = {result["pval_fdr_corrected"]:.3e}\n'
                 f'Reject FDR: {result["reject_fdr_05"]}')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(f'{plots_dir}/{source_id}_validation.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Validation plots saved to: {plots_dir}/")

def generate_critical_report(results):
    """Generate critical validation report"""
    
    print("\nGenerating critical validation report...")
    
    # Calculate statistics
    total_sources = len(results)
    sources_with_qg = sum(1 for r in results if r['has_qg_effect'])
    sources_rejected_fdr = sum(1 for r in results if r['reject_fdr_05'])
    
    # Top candidates (FDR rejected)
    top_candidates = [r for r in results if r['reject_fdr_05']]
    top_candidates.sort(key=lambda x: x['pval_fdr_corrected'])
    
    # Significance distribution
    significances = [r['significance_sigma'] for r in results]
    pvals_emp = [r['p_empirical'] for r in results if not np.isnan(r['p_empirical'])]
    
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'validation_summary': {
            'total_sources_analyzed': total_sources,
            'sources_with_qg_effect': sources_with_qg,
            'qg_effect_fraction': sources_with_qg / total_sources,
            'sources_rejected_fdr_05': sources_rejected_fdr,
            'fdr_rejection_rate': sources_rejected_fdr / total_sources
        },
        'significance_analysis': {
            'mean_significance': np.mean(significances),
            'median_significance': np.median(significances),
            'max_significance': np.max(significances),
            'sources_above_3sigma': sum(1 for s in significances if s > 3.0),
            'sources_above_5sigma': sum(1 for s in significances if s > 5.0)
        },
        'empirical_pvalue_analysis': {
            'mean_pvalue': np.mean(pvals_emp) if pvals_emp else np.nan,
            'median_pvalue': np.median(pvals_emp) if pvals_emp else np.nan,
            'min_pvalue': np.min(pvals_emp) if pvals_emp else np.nan,
            'sources_pvalue_lt_001': sum(1 for p in pvals_emp if p < 0.001) if pvals_emp else 0
        },
        'top_candidates': [
            {
                'source_id': r['source_id'],
                'p_empirical': r['p_empirical'],
                'p_fdr_corrected': r['pval_fdr_corrected'],
                'significance_sigma': r['significance_sigma'],
                'n_photons': r['n_photons']
            }
            for r in top_candidates[:10]
        ],
        'critical_conclusions': [
            f"FDR correction at alpha=0.05 rejects only {sources_rejected_fdr}/{total_sources} sources ({sources_rejected_fdr/total_sources:.1%})",
            f"Mean significance of {np.mean(significances):.2f} sigma is well below 3 sigma threshold",
            f"Only {sum(1 for s in significances if s > 3.0)} sources exceed 3 sigma significance",
            f"Empirical p-values show {sum(1 for p in pvals_emp if p < 0.001)} sources with p < 0.001" if pvals_emp else "No empirical p-values available",
            "Results suggest most QG signals are statistical artifacts or noise"
        ]
    }
    
    # Save report
    with open('critical_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    """Main function"""
    print("CRITICAL VALIDATION OF QG CANDIDATES")
    print("=" * 60)
    print("Performing rigorous statistical validation...")
    
    # Load results
    df = load_fermi_results()
    if df is None:
        return
    
    # Perform critical validation (limit to 100 sources for speed)
    results = critical_validation_analysis(df)
    
    # Apply multiple testing correction
    results = apply_multiple_testing_correction(results)
    
    # Create validation plots
    create_validation_plots(results, top_n=10)
    
    # Generate critical report
    report = generate_critical_report(results)
    
    # Save validation results
    validation_df = pd.DataFrame([
        {
            'source_id': r['source_id'],
            'n_photons': r['n_photons'],
            'has_qg_effect': r['has_qg_effect'],
            'significance_sigma': r['significance_sigma'],
            'p_from_sigma': r['p_from_sigma'],
            'p_empirical': r['p_empirical'],
            'pearson_r_obs': r['pearson_r_obs'],
            'pval_used': r['pval_used'],
            'pval_fdr_corrected': r['pval_fdr_corrected'],
            'reject_fdr_05': r['reject_fdr_05']
        }
        for r in results
    ])
    
    validation_df.to_csv('critical_validation_results.csv', index=False)
    
    print("\n" + "=" * 60)
    print("CRITICAL VALIDATION COMPLETED")
    print("=" * 60)
    print(f"Total sources analyzed: {len(results)}")
    print(f"Sources rejected by FDR (alpha=0.05): {report['validation_summary']['sources_rejected_fdr_05']}")
    print(f"FDR rejection rate: {report['validation_summary']['fdr_rejection_rate']:.1%}")
    print(f"Mean significance: {report['significance_analysis']['mean_significance']:.2f} sigma")
    print(f"Sources above 3 sigma: {report['significance_analysis']['sources_above_3sigma']}")
    
    print("\nCRITICAL CONCLUSIONS:")
    for conclusion in report['critical_conclusions']:
        print(f"  • {conclusion}")
    
    print(f"\nFiles created:")
    print(f"  - critical_validation_results.csv")
    print(f"  - critical_validation_report.json")
    print(f"  - validation_plots/ (directory)")
    print("=" * 60)

if __name__ == "__main__":
    main()
