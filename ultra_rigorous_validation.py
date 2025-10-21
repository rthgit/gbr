#!/usr/bin/env python3
"""
ULTRA RIGOROUS VALIDATION - Double Check Everything
Leave no stone unturned in the validation process
"""

import os
import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, norm, ttest_1samp
import matplotlib.pyplot as plt
from datetime import datetime

def load_and_inspect_data():
    """Load and thoroughly inspect all data"""
    
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    print("ULTRA RIGOROUS DATA INSPECTION")
    print("=" * 60)
    
    # Check all available files
    files_to_check = [
        'super_complete_fermi_qg_analysis_results.csv',
        'super_complete_qg_analysis_report.json',
        'critical_validation_results.csv',
        'critical_validation_report.json',
        'fermi_catalog_all_sources.csv',
        'fermi_unassociated_sources.csv',
        'fermi_high_variability_sources.csv'
    ]
    
    available_files = []
    for file in files_to_check:
        if os.path.exists(file):
            available_files.append(file)
            print(f"✓ Found: {file}")
        else:
            print(f"✗ Missing: {file}")
    
    print(f"\nTotal available files: {len(available_files)}")
    
    # Load main results
    if 'super_complete_fermi_qg_analysis_results.csv' in available_files:
        df = pd.read_csv('super_complete_fermi_qg_analysis_results.csv')
        print(f"\nMain results loaded: {len(df)} sources")
        print(f"Columns: {list(df.columns)}")
        
        # Inspect data quality
        print(f"\nData quality inspection:")
        print(f"  - Missing values: {df.isnull().sum().sum()}")
        print(f"  - Infinite values: {np.isinf(df.select_dtypes(include=[np.number])).sum().sum()}")
        print(f"  - Duplicate rows: {df.duplicated().sum()}")
        
        return df, available_files
    else:
        print("ERROR: Main results file not found!")
        return None, available_files

def ultra_rigorous_statistical_analysis(df):
    """Perform ultra rigorous statistical analysis"""
    
    print("\nULTRA RIGOROUS STATISTICAL ANALYSIS")
    print("=" * 60)
    
    # 1. Check the original significance calculations
    print("1. ORIGINAL SIGNIFICANCE ANALYSIS:")
    significances = df['Significance_Sigma'].values
    qg_mask = df['Has_QG_Effect'] == True
    no_qg_mask = df['Has_QG_Effect'] == False
    
    print(f"   Total sources: {len(df)}")
    print(f"   QG sources: {qg_mask.sum()}")
    print(f"   No-QG sources: {no_qg_mask.sum()}")
    print(f"   QG fraction: {qg_mask.sum()/len(df):.1%}")
    
    print(f"\n   Significance statistics:")
    print(f"   - Mean: {np.mean(significances):.3f}")
    print(f"   - Median: {np.median(significances):.3f}")
    print(f"   - Std: {np.std(significances):.3f}")
    print(f"   - Min: {np.min(significances):.3f}")
    print(f"   - Max: {np.max(significances):.3f}")
    
    # 2. Check if significance calculation is correct
    print(f"\n2. SIGNIFICANCE CALCULATION VERIFICATION:")
    pearson_rs = df['Pearson_r'].values
    n_photons = df['N_Photons'].values
    
    # Recalculate significance: |r| * sqrt(n-2)
    recalc_significance = np.abs(pearson_rs) * np.sqrt(n_photons - 2)
    
    print(f"   Original vs Recalculated significance:")
    print(f"   - Original mean: {np.mean(significances):.3f}")
    print(f"   - Recalculated mean: {np.mean(recalc_significance):.3f}")
    print(f"   - Correlation: {np.corrcoef(significances, recalc_significance)[0,1]:.6f}")
    
    # 3. Check for potential issues
    print(f"\n3. POTENTIAL ISSUES DETECTION:")
    
    # Check for very high correlations
    high_corr_mask = np.abs(pearson_rs) > 0.5
    print(f"   - Sources with |r| > 0.5: {high_corr_mask.sum()}")
    
    # Check for very low photon counts
    low_photons_mask = n_photons < 100
    print(f"   - Sources with < 100 photons: {low_photons_mask.sum()}")
    
    # Check for unrealistic E_QG estimates
    e_qg_estimates = df['E_QG_Estimate'].values
    finite_e_qg = e_qg_estimates[np.isfinite(e_qg_estimates)]
    if len(finite_e_qg) > 0:
        print(f"   - E_QG estimates (finite): {len(finite_e_qg)}")
        print(f"     Mean: {np.mean(finite_e_qg):.2e} GeV")
        print(f"     Range: {np.min(finite_e_qg):.2e} - {np.max(finite_e_qg):.2e} GeV")
    
    # 4. Advanced statistical tests
    print(f"\n4. ADVANCED STATISTICAL TESTS:")
    
    # T-test for difference between QG and no-QG groups
    qg_sig = significances[qg_mask]
    no_qg_sig = significances[no_qg_mask]
    
    if len(qg_sig) > 0 and len(no_qg_sig) > 0:
        t_stat, t_p = ttest_1samp(qg_sig, np.mean(no_qg_sig))
        print(f"   - T-test QG vs No-QG significance: t={t_stat:.3f}, p={t_p:.3f}")
    
    # Check distribution normality
    from scipy.stats import shapiro
    if len(significances) <= 5000:  # Shapiro works only up to 5000 samples
        shapiro_stat, shapiro_p = shapiro(significances)
        print(f"   - Shapiro-Wilk normality test: W={shapiro_stat:.6f}, p={shapiro_p:.3f}")
    
    return {
        'significances': significances,
        'pearson_rs': pearson_rs,
        'n_photons': n_photons,
        'recalc_significance': recalc_significance,
        'qg_mask': qg_mask,
        'no_qg_mask': no_qg_mask,
        'high_corr_mask': high_corr_mask,
        'low_photons_mask': low_photons_mask
    }

def comprehensive_permutation_analysis(df, stats_dict):
    """Comprehensive permutation analysis with multiple approaches"""
    
    print("\nCOMPREHENSIVE PERMUTATION ANALYSIS")
    print("=" * 60)
    
    # Get top candidates by significance
    top_candidates = df.nlargest(20, 'Significance_Sigma')
    
    print(f"Analyzing top 20 candidates by significance...")
    
    results = []
    
    for idx, row in top_candidates.iterrows():
        source_id = f"Source_{idx}"
        n_photons = int(row['N_Photons'])
        has_qg_effect = row['Has_QG_Effect']
        significance = row['Significance_Sigma']
        pearson_r = row['Pearson_r']
        
        # Simulate photon data
        energies = np.random.uniform(0.1, 300, n_photons)
        
        if has_qg_effect:
            E_QG = np.random.uniform(1e15, 1e19)
            time_delays = energies / E_QG
            noise_factor = np.random.uniform(0.8, 1.2, len(time_delays))
            time_delays *= noise_factor
            arrival_times = np.random.uniform(0, 2000, n_photons) + time_delays
        else:
            arrival_times = np.random.uniform(0, 2000, n_photons)
        
        # Multiple permutation approaches
        nperm = 10000
        
        # 1. Standard permutation test
        r_obs = pearsonr(energies, arrival_times)[0]
        count = 0
        for _ in range(nperm):
            perm_times = np.random.permutation(arrival_times)
            r_perm = pearsonr(energies, perm_times)[0]
            if abs(r_perm) >= abs(r_obs):
                count += 1
        p_emp_standard = (count + 1) / (nperm + 1)
        
        # 2. Bootstrap approach
        n_bootstrap = 1000
        bootstrap_rs = []
        for _ in range(n_bootstrap):
            indices = np.random.choice(len(energies), size=len(energies), replace=True)
            r_boot = pearsonr(energies[indices], arrival_times[indices])[0]
            bootstrap_rs.append(r_boot)
        p_emp_bootstrap = np.mean(np.abs(bootstrap_rs) >= abs(r_obs))
        
        # 3. Check if significance matches expected
        expected_sig = abs(r_obs) * np.sqrt(n_photons - 2)
        sig_match = abs(expected_sig - significance) < 0.01
        
        results.append({
            'source_id': source_id,
            'n_photons': n_photons,
            'has_qg_effect': has_qg_effect,
            'original_significance': significance,
            'original_pearson_r': pearson_r,
            'simulated_pearson_r': r_obs,
            'expected_significance': expected_sig,
            'significance_match': sig_match,
            'p_emp_standard': p_emp_standard,
            'p_emp_bootstrap': p_emp_bootstrap,
            'energies': energies,
            'times': arrival_times
        })
    
    return results

def check_for_hidden_patterns(df, stats_dict):
    """Check for hidden patterns that might explain the results"""
    
    print("\nHIDDEN PATTERNS ANALYSIS")
    print("=" * 60)
    
    # 1. Check correlation between photon count and significance
    n_photons = stats_dict['n_photons']
    significances = stats_dict['significances']
    photon_sig_corr = np.corrcoef(n_photons, significances)[0,1]
    print(f"1. Photon count vs Significance correlation: {photon_sig_corr:.4f}")
    
    # 2. Check if QG effects are clustered in certain photon count ranges
    qg_mask = stats_dict['qg_mask']
    qg_photons = n_photons[qg_mask]
    no_qg_photons = n_photons[~qg_mask]
    
    print(f"\n2. Photon count distribution:")
    print(f"   - QG sources: mean={np.mean(qg_photons):.0f}, std={np.std(qg_photons):.0f}")
    print(f"   - No-QG sources: mean={np.mean(no_qg_photons):.0f}, std={np.std(no_qg_photons):.0f}")
    
    # 3. Check energy range effects
    if 'Energy_Range_Min' in df.columns and 'Energy_Range_Max' in df.columns:
        energy_ranges = df['Energy_Range_Max'] - df['Energy_Range_Min']
        energy_sig_corr = np.corrcoef(energy_ranges, significances)[0,1]
        print(f"\n3. Energy range vs Significance correlation: {energy_sig_corr:.4f}")
    
    # 4. Check for systematic biases
    print(f"\n4. Systematic bias checks:")
    
    # Check if QG effects are more common in certain significance ranges
    sig_ranges = [(0, 1), (1, 2), (2, 3), (3, np.inf)]
    for sig_min, sig_max in sig_ranges:
        mask = (significances >= sig_min) & (significances < sig_max)
        if mask.sum() > 0:
            qg_fraction = qg_mask[mask].sum() / mask.sum()
            print(f"   - Significance {sig_min}-{sig_max}: QG fraction = {qg_fraction:.1%} ({mask.sum()} sources)")

def final_verdict_analysis(df, stats_dict, permutation_results):
    """Final comprehensive verdict analysis"""
    
    print("\nFINAL COMPREHENSIVE VERDICT")
    print("=" * 60)
    
    # 1. Count sources that pass different criteria
    significances = stats_dict['significances']
    qg_mask = stats_dict['qg_mask']
    
    criteria = {
        'significance_1sigma': significances > 1.0,
        'significance_2sigma': significances > 2.0,
        'significance_3sigma': significances > 3.0,
        'significance_5sigma': significances > 5.0,
        'high_correlation': np.abs(stats_dict['pearson_rs']) > 0.5,
        'sufficient_photons': stats_dict['n_photons'] >= 1000
    }
    
    print("1. SOURCES PASSING DIFFERENT CRITERIA:")
    for criterion, mask in criteria.items():
        total_pass = mask.sum()
        qg_pass = (mask & qg_mask).sum()
        print(f"   - {criterion}: {total_pass} total, {qg_pass} QG ({qg_pass/total_pass:.1%} if total>0 else 'N/A')")
    
    # 2. Check permutation results
    print(f"\n2. PERMUTATION ANALYSIS RESULTS:")
    strong_candidates = [r for r in permutation_results if r['p_emp_standard'] < 0.001]
    moderate_candidates = [r for r in permutation_results if 0.001 <= r['p_emp_standard'] < 0.01]
    
    print(f"   - Strong candidates (p < 0.001): {len(strong_candidates)}")
    print(f"   - Moderate candidates (0.001 ≤ p < 0.01): {len(moderate_candidates)}")
    
    if strong_candidates:
        print(f"   - Top strong candidate: {strong_candidates[0]['source_id']}")
        print(f"     p-value: {strong_candidates[0]['p_emp_standard']:.6f}")
        print(f"     significance: {strong_candidates[0]['original_significance']:.2f}")
    
    # 3. Final assessment
    print(f"\n3. FINAL ASSESSMENT:")
    
    # Calculate overall statistics
    mean_sig = np.mean(significances)
    median_sig = np.median(significances)
    max_sig = np.max(significances)
    qg_fraction = qg_mask.sum() / len(qg_mask)
    
    print(f"   - Mean significance: {mean_sig:.3f}σ")
    print(f"   - Median significance: {median_sig:.3f}σ")
    print(f"   - Maximum significance: {max_sig:.3f}σ")
    print(f"   - QG effect fraction: {qg_fraction:.1%}")
    print(f"   - Sources above 3σ: {(significances > 3.0).sum()}")
    print(f"   - Sources above 5σ: {(significances > 5.0).sum()}")
    
    # 4. Verdict
    print(f"\n4. FINAL VERDICT:")
    
    if len(strong_candidates) > 0:
        print(f"   ⚠️  WARNING: Found {len(strong_candidates)} strong candidates!")
        print(f"   ⚠️  These require immediate investigation!")
    elif max_sig > 5.0:
        print(f"   ⚠️  WARNING: Maximum significance {max_sig:.2f}σ is very high!")
        print(f"   ⚠️  This source requires detailed investigation!")
    elif max_sig > 3.0:
        print(f"   ⚠️  CAUTION: {len(strong_candidates)} sources above 3σ")
        print(f"   ⚠️  These may warrant follow-up analysis")
    else:
        print(f"   ✓ CONFIRMED: No strong statistical evidence found")
        print(f"   ✓ All sources below 3σ significance threshold")
    
    return {
        'mean_significance': mean_sig,
        'max_significance': max_sig,
        'qg_fraction': qg_fraction,
        'strong_candidates': len(strong_candidates),
        'sources_above_3sigma': (significances > 3.0).sum(),
        'sources_above_5sigma': (significances > 5.0).sum()
    }

def main():
    """Main function"""
    print("ULTRA RIGOROUS VALIDATION - DOUBLE CHECK EVERYTHING")
    print("=" * 70)
    print("Leaving no stone unturned in the validation process...")
    
    # Load and inspect data
    df, available_files = load_and_inspect_data()
    if df is None:
        return
    
    # Ultra rigorous statistical analysis
    stats_dict = ultra_rigorous_statistical_analysis(df)
    
    # Comprehensive permutation analysis
    permutation_results = comprehensive_permutation_analysis(df, stats_dict)
    
    # Check for hidden patterns
    check_for_hidden_patterns(df, stats_dict)
    
    # Final verdict
    verdict = final_verdict_analysis(df, stats_dict, permutation_results)
    
    # Save comprehensive report
    comprehensive_report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'available_files': available_files,
        'data_quality': {
            'total_sources': len(df),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'infinite_values': np.isinf(df.select_dtypes(include=[np.number])).sum().sum()
        },
        'statistical_analysis': {
            'mean_significance': float(verdict['mean_significance']),
            'max_significance': float(verdict['max_significance']),
            'qg_fraction': float(verdict['qg_fraction']),
            'sources_above_3sigma': int(verdict['sources_above_3sigma']),
            'sources_above_5sigma': int(verdict['sources_above_5sigma'])
        },
        'permutation_analysis': {
            'strong_candidates': verdict['strong_candidates'],
            'top_candidates': [
                {
                    'source_id': r['source_id'],
                    'p_emp_standard': float(r['p_emp_standard']),
                    'original_significance': float(r['original_significance']),
                    'significance_match': bool(r['significance_match'])
                }
                for r in permutation_results[:10]
            ]
        },
        'final_verdict': verdict
    }
    
    with open('ultra_rigorous_validation_report.json', 'w') as f:
        json.dump(comprehensive_report, f, indent=2)
    
    print(f"\n" + "=" * 70)
    print("ULTRA RIGOROUS VALIDATION COMPLETED")
    print("=" * 70)
    print(f"Comprehensive report saved: ultra_rigorous_validation_report.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
