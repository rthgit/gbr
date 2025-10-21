#!/usr/bin/env python3
"""
ADVANCED STATISTICAL VALIDATION
Validate QG effects using advanced statistical techniques
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path

def load_all_grb_data():
    """Load all GRB data"""
    print("LOADING ALL GRB DATA")
    print("=" * 50)
    
    grb_list = [
        'GRB090902B',
        'GRB130427A', 
        'GRB160625B',
        'GRB090926A',
        'GRB090510',
        'GRB080916C'
    ]
    
    grb_data = {}
    
    for grb in grb_list:
        csv_file = f"{grb}_PH00.csv"
        if Path(csv_file).exists():
            df = pd.read_csv(csv_file)
            grb_data[grb] = df
            print(f"✅ {grb}: {len(df)} photons")
        else:
            print(f"❌ {grb}: Data not found")
    
    return grb_data

def permutation_test(df, n_permutations=10000):
    """Perform permutation test for correlation significance"""
    print(f"Running permutation test with {n_permutations} iterations...")
    
    # Calculate observed correlation
    observed_corr, _ = stats.spearmanr(df['ENERGY'], df['TIME'])
    
    # Generate null distribution
    null_correlations = []
    for i in range(n_permutations):
        # Permute time while keeping energy fixed
        permuted_time = np.random.permutation(df['TIME'])
        perm_corr, _ = stats.spearmanr(df['ENERGY'], permuted_time)
        null_correlations.append(perm_corr)
    
    # Calculate p-value
    null_correlations = np.array(null_correlations)
    p_value = np.mean(np.abs(null_correlations) >= np.abs(observed_corr))
    
    # Calculate empirical sigma
    if p_value > 0:
        empirical_sigma = stats.norm.ppf(1 - p_value/2)
    else:
        empirical_sigma = np.inf
    
    return {
        'observed_correlation': observed_corr,
        'p_value': p_value,
        'empirical_sigma': empirical_sigma,
        'null_mean': np.mean(null_correlations),
        'null_std': np.std(null_correlations)
    }

def bootstrap_analysis(df, n_bootstrap=1000):
    """Perform bootstrap analysis for correlation confidence intervals"""
    print(f"Running bootstrap analysis with {n_bootstrap} iterations...")
    
    correlations = []
    n_samples = len(df)
    
    for i in range(n_bootstrap):
        # Bootstrap sample
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        bootstrap_df = df.iloc[indices]
        
        # Calculate correlation
        corr, _ = stats.spearmanr(bootstrap_df['ENERGY'], bootstrap_df['TIME'])
        correlations.append(corr)
    
    correlations = np.array(correlations)
    
    # Calculate confidence intervals
    ci_lower = np.percentile(correlations, 2.5)
    ci_upper = np.percentile(correlations, 97.5)
    
    return {
        'mean_correlation': np.mean(correlations),
        'std_correlation': np.std(correlations),
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'correlations': correlations
    }

def multiple_testing_correction(results):
    """Apply multiple testing correction (FDR)"""
    print("Applying multiple testing correction...")
    
    # Extract p-values
    p_values = [result['permutation']['p_value'] for result in results.values()]
    grb_names = list(results.keys())
    
    # Apply Benjamini-Hochberg correction
    from statsmodels.stats.multitest import multipletests
    rejected, p_corrected, alpha_sidak, alpha_bonferroni = multipletests(
        p_values, alpha=0.05, method='fdr_bh'
    )
    
    # Update results
    for i, grb in enumerate(grb_names):
        results[grb]['corrected'] = {
            'p_value_corrected': p_corrected[i],
            'rejected': rejected[i],
            'alpha_sidak': alpha_sidak,
            'alpha_bonferroni': alpha_bonferroni
        }
    
    return results

def analyze_grb_advanced(grb_name, df):
    """Perform advanced analysis on a GRB"""
    print(f"\n{'='*60}")
    print(f"ADVANCED ANALYSIS: {grb_name}")
    print(f"{'='*60}")
    
    print(f"Data: {len(df)} photons")
    print(f"Energy range: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
    
    # Basic correlation
    rho, p_basic = stats.spearmanr(df['ENERGY'], df['TIME'])
    print(f"Basic Spearman: ρ = {rho:.6f}, p = {p_basic:.2e}")
    
    # Permutation test
    perm_results = permutation_test(df)
    print(f"Permutation test: p = {perm_results['p_value']:.2e}, σ = {perm_results['empirical_sigma']:.2f}")
    
    # Bootstrap analysis
    bootstrap_results = bootstrap_analysis(df)
    print(f"Bootstrap: ρ = {bootstrap_results['mean_correlation']:.6f} ± {bootstrap_results['std_correlation']:.6f}")
    print(f"95% CI: [{bootstrap_results['ci_lower']:.6f}, {bootstrap_results['ci_upper']:.6f}]")
    
    return {
        'grb_name': grb_name,
        'n_photons': len(df),
        'basic': {'correlation': rho, 'p_value': p_basic},
        'permutation': perm_results,
        'bootstrap': bootstrap_results
    }

def main():
    """Main function"""
    print("ADVANCED STATISTICAL VALIDATION")
    print("=" * 80)
    
    # Load all GRB data
    grb_data = load_all_grb_data()
    
    if not grb_data:
        print("❌ No GRB data available!")
        return
    
    # Perform advanced analysis on each GRB
    results = {}
    
    for grb_name, df in grb_data.items():
        results[grb_name] = analyze_grb_advanced(grb_name, df)
    
    # Apply multiple testing correction
    results = multiple_testing_correction(results)
    
    # Save results
    with open('advanced_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Summary
    print(f"\n{'='*80}")
    print("ADVANCED VALIDATION SUMMARY")
    print(f"{'='*80}")
    
    print(f"📊 Results Summary:")
    for grb_name, result in results.items():
        perm_sigma = result['permutation']['empirical_sigma']
        corrected = result['corrected']
        
        status = "✅ SIGNIFICANT" if corrected['rejected'] else "❌ NOT SIGNIFICANT"
        
        print(f"  {grb_name}:")
        print(f"    Permutation σ: {perm_sigma:.2f}")
        print(f"    Corrected p: {corrected['p_value_corrected']:.2e}")
        print(f"    Status: {status}")
    
    # Count significant results
    significant_count = sum(1 for r in results.values() if r['corrected']['rejected'])
    total_count = len(results)
    
    print(f"\n🎯 Validation Results:")
    print(f"  Significant after correction: {significant_count}/{total_count}")
    print(f"  Success rate: {significant_count/total_count*100:.1f}%")
    
    print(f"\n📁 Files created:")
    print(f"  - advanced_validation_results.json")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
