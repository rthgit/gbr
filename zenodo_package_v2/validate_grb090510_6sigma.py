#!/usr/bin/env python3
"""
VALIDATE GRB090510 - 6.46 SIGMA EFFECT
Validate the 6.46 sigma effect in GRB090510 with advanced statistical techniques
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_grb090510_data():
    """Load GRB090510 data"""
    print("LOADING GRB090510 DATA")
    print("=" * 50)
    
    df = pd.read_csv('GRB090510_PH00.csv')
    print(f"✅ Loaded {len(df)} photons")
    print(f"Energy range: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
    print(f"Time range: {df['TIME'].min():.1f} - {df['TIME'].max():.1f} s")
    
    return df

def validate_6sigma_effect(df):
    """Validate the 6.46 sigma effect"""
    print("\nVALIDATING 6.46 SIGMA EFFECT")
    print("=" * 50)
    
    # Calculate phase analysis (early/late split)
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    split_idx = len(df_sorted) // 2
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    print(f"Phase analysis:")
    print(f"  Early phase: {len(early_df)} photons")
    print(f"  Late phase: {len(late_df)} photons")
    
    # Calculate correlations for each phase
    early_r, early_p = stats.pearsonr(early_df['ENERGY'], early_df['TIME'])
    late_r, late_p = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
    
    print(f"  Early phase: r = {early_r:.4f}, p = {early_p:.2e}")
    print(f"  Late phase: r = {late_r:.4f}, p = {late_p:.2e}")
    
    # Calculate sigma for late phase (the 6.46σ result)
    if late_p > 0:
        late_sigma = stats.norm.ppf(1 - late_p/2)
    else:
        late_sigma = float('inf')
    
    print(f"  Late phase sigma: {late_sigma:.2f}")
    
    return {
        'early': (early_r, early_p, len(early_df)),
        'late': (late_r, late_p, len(late_df), late_sigma)
    }

def perform_robustness_tests(df):
    """Perform robustness tests"""
    print("\nPERFORMING ROBUSTNESS TESTS")
    print("=" * 50)
    
    # Test 1: Bootstrap resampling
    print("Test 1: Bootstrap resampling...")
    n_bootstrap = 1000
    bootstrap_sigmas = []
    
    for i in range(n_bootstrap):
        # Resample with replacement
        boot_df = df.sample(n=len(df), replace=True)
        
        # Sort by time and split
        boot_sorted = boot_df.sort_values('TIME').reset_index(drop=True)
        split_idx = len(boot_sorted) // 2
        late_boot = boot_sorted.iloc[split_idx:]
        
        if len(late_boot) >= 3:
            _, boot_p = stats.pearsonr(late_boot['ENERGY'], late_boot['TIME'])
            if boot_p > 0:
                boot_sigma = stats.norm.ppf(1 - boot_p/2)
                bootstrap_sigmas.append(boot_sigma)
    
    bootstrap_mean = np.mean(bootstrap_sigmas)
    bootstrap_std = np.std(bootstrap_sigmas)
    
    print(f"  Bootstrap mean sigma: {bootstrap_mean:.2f} ± {bootstrap_std:.2f}")
    print(f"  Bootstrap samples: {len(bootstrap_sigmas)}")
    
    # Test 2: Different split ratios
    print("\nTest 2: Different split ratios...")
    split_ratios = [0.3, 0.4, 0.5, 0.6, 0.7]
    
    for ratio in split_ratios:
        df_sorted = df.sort_values('TIME').reset_index(drop=True)
        split_idx = int(len(df_sorted) * ratio)
        late_df = df_sorted.iloc[split_idx:]
        
        if len(late_df) >= 3:
            _, late_p = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
            if late_p > 0:
                late_sigma = stats.norm.ppf(1 - late_p/2)
                print(f"  Split {ratio:.1f}: σ = {late_sigma:.2f} ({len(late_df)} photons)")
    
    # Test 3: Energy threshold analysis
    print("\nTest 3: Energy threshold analysis...")
    energy_thresholds = [100, 200, 500, 1000, 2000]
    
    for threshold in energy_thresholds:
        high_energy_df = df[df['ENERGY'] >= threshold]
        if len(high_energy_df) >= 10:
            df_sorted = high_energy_df.sort_values('TIME').reset_index(drop=True)
            split_idx = len(df_sorted) // 2
            late_df = df_sorted.iloc[split_idx:]
            
            if len(late_df) >= 3:
                _, late_p = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
                if late_p > 0:
                    late_sigma = stats.norm.ppf(1 - late_p/2)
                    print(f"  E ≥ {threshold} GeV: σ = {late_sigma:.2f} ({len(late_df)} photons)")
    
    return {
        'bootstrap_mean': bootstrap_mean,
        'bootstrap_std': bootstrap_std,
        'bootstrap_samples': len(bootstrap_sigmas)
    }

def analyze_energy_time_patterns(df):
    """Analyze energy-time patterns"""
    print("\nANALYZING ENERGY-TIME PATTERNS")
    print("=" * 50)
    
    # Sort by time
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    
    # Calculate rolling correlations
    window_size = 1000
    rolling_correlations = []
    
    for i in range(0, len(df_sorted) - window_size, window_size):
        window_df = df_sorted.iloc[i:i+window_size]
        if len(window_df) >= 10:
            r, p = stats.pearsonr(window_df['ENERGY'], window_df['TIME'])
            rolling_correlations.append(r)
    
    if rolling_correlations:
        print(f"Rolling correlations (window={window_size}):")
        print(f"  Mean: {np.mean(rolling_correlations):.4f}")
        print(f"  Std: {np.std(rolling_correlations):.4f}")
        print(f"  Min: {np.min(rolling_correlations):.4f}")
        print(f"  Max: {np.max(rolling_correlations):.4f}")
    
    # Analyze time evolution
    print(f"\nTime evolution analysis:")
    
    # Split into 10 time bins
    n_bins = 10
    bin_size = len(df_sorted) // n_bins
    
    for i in range(n_bins):
        start_idx = i * bin_size
        end_idx = (i + 1) * bin_size if i < n_bins - 1 else len(df_sorted)
        bin_df = df_sorted.iloc[start_idx:end_idx]
        
        if len(bin_df) >= 10:
            r, p = stats.pearsonr(bin_df['ENERGY'], bin_df['TIME'])
            if p > 0:
                sigma = stats.norm.ppf(1 - p/2)
                print(f"  Bin {i+1}: r = {r:.4f}, σ = {sigma:.2f} ({len(bin_df)} photons)")
    
    return rolling_correlations

def create_validation_visualizations(df):
    """Create validation visualizations"""
    print("\nCREATING VALIDATION VISUALIZATIONS")
    print("=" * 50)
    
    # Set up the plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('GRB090510 - 6.46σ Validation', fontsize=16, fontweight='bold')
    
    # 1. Energy vs Time scatter plot
    axes[0,0].scatter(df['TIME'], df['ENERGY'], alpha=0.6, s=1)
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Energy (GeV)')
    axes[0,0].set_title('Energy vs Time')
    axes[0,0].set_yscale('log')
    
    # 2. Phase analysis plot
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    split_idx = len(df_sorted) // 2
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    axes[0,1].scatter(early_df['TIME'], early_df['ENERGY'], alpha=0.6, s=1, label='Early Phase', color='blue')
    axes[0,1].scatter(late_df['TIME'], late_df['ENERGY'], alpha=0.6, s=1, label='Late Phase', color='red')
    axes[0,1].set_xlabel('Time (s)')
    axes[0,1].set_ylabel('Energy (GeV)')
    axes[0,1].set_title('Phase Analysis')
    axes[0,1].set_yscale('log')
    axes[0,1].legend()
    
    # 3. Energy distribution
    axes[1,0].hist(df['ENERGY'], bins=50, alpha=0.7, edgecolor='black')
    axes[1,0].set_xlabel('Energy (GeV)')
    axes[1,0].set_ylabel('Count')
    axes[1,0].set_title('Energy Distribution')
    axes[1,0].set_xscale('log')
    
    # 4. Time distribution
    axes[1,1].hist(df['TIME'], bins=50, alpha=0.7, edgecolor='black')
    axes[1,1].set_xlabel('Time (s)')
    axes[1,1].set_ylabel('Count')
    axes[1,1].set_title('Time Distribution')
    
    plt.tight_layout()
    plt.savefig('GRB090510_validation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: GRB090510_validation.png")

def main():
    """Main function"""
    print("VALIDATE GRB090510 - 6.46 SIGMA EFFECT")
    print("=" * 80)
    
    # Load data
    df = load_grb090510_data()
    
    # Validate 6.46 sigma effect
    phase_results = validate_6sigma_effect(df)
    
    # Perform robustness tests
    robustness_results = perform_robustness_tests(df)
    
    # Analyze patterns
    rolling_correlations = analyze_energy_time_patterns(df)
    
    # Create visualizations
    create_validation_visualizations(df)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - GRB090510 VALIDATION")
    print("=" * 80)
    
    print(f"📊 Original Results:")
    print(f"  Late phase sigma: {phase_results['late'][3]:.2f}")
    print(f"  Late phase correlation: {phase_results['late'][0]:.4f}")
    print(f"  Late phase photons: {phase_results['late'][2]:,}")
    
    print(f"\n🔍 Robustness Tests:")
    print(f"  Bootstrap mean: {robustness_results['bootstrap_mean']:.2f} ± {robustness_results['bootstrap_std']:.2f}")
    print(f"  Bootstrap samples: {robustness_results['bootstrap_samples']}")
    
    print(f"\n🎯 Validation Status:")
    if robustness_results['bootstrap_mean'] > 5.0:
        print("  ✅ EFFECT VALIDATED - Bootstrap confirms high significance")
    elif robustness_results['bootstrap_mean'] > 3.0:
        print("  ⚠️ EFFECT PARTIALLY VALIDATED - Bootstrap shows moderate significance")
    else:
        print("  ❌ EFFECT NOT VALIDATED - Bootstrap shows low significance")
    
    print(f"\n📁 Files created:")
    print(f"  - GRB090510_validation.png")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
