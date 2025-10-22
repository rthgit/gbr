#!/usr/bin/env python3
"""
DEEP ANALYSIS GRB090926A - INFINITE EFFECT
Analyze the infinite sigma effect in GRB090926A in detail
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_grb090926a_data():
    """Load GRB090926A data"""
    print("LOADING GRB090926A DATA")
    print("=" * 50)
    
    df = pd.read_csv('GRB090926A_PH00.csv')
    print(f"✅ Loaded {len(df)} photons")
    print(f"Energy range: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
    print(f"Time range: {df['TIME'].min():.1f} - {df['TIME'].max():.1f} s")
    
    return df

def analyze_infinite_effect(df):
    """Analyze the infinite sigma effect"""
    print("\nANALYZING INFINITE SIGMA EFFECT")
    print("=" * 50)
    
    # Calculate Spearman correlation
    rho, p_value = stats.spearmanr(df['ENERGY'], df['TIME'])
    
    print(f"Spearman correlation: ρ = {rho:.6f}")
    print(f"P-value: {p_value:.2e}")
    
    # Check if p-value is exactly 0 (causing infinite sigma)
    if p_value == 0:
        print("⚠️ P-value is exactly 0 - this causes infinite sigma!")
        print("This suggests a perfect or near-perfect correlation")
        
        # Check for perfect correlation
        if abs(rho) == 1.0:
            print("🎯 PERFECT CORRELATION DETECTED!")
            print("This is extremely rare and suggests:")
            print("1. Possible data artifact")
            print("2. Perfect QG effect")
            print("3. Systematic error")
        else:
            print(f"Near-perfect correlation: |ρ| = {abs(rho):.6f}")
    
    # Calculate sigma manually with small epsilon
    epsilon = 1e-15
    p_value_corrected = max(p_value, epsilon)
    sigma_corrected = stats.norm.ppf(1 - p_value_corrected/2)
    
    print(f"Corrected sigma: {sigma_corrected:.2f}")
    
    return rho, p_value, sigma_corrected

def check_data_quality(df):
    """Check data quality for artifacts"""
    print("\nCHECKING DATA QUALITY")
    print("=" * 50)
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"Duplicate photons: {duplicates}")
    
    # Check for constant values
    energy_constant = df['ENERGY'].nunique() == 1
    time_constant = df['TIME'].nunique() == 1
    
    print(f"Constant energy: {energy_constant}")
    print(f"Constant time: {time_constant}")
    
    # Check for linear relationship
    energy_sorted = df.sort_values('ENERGY')
    time_sorted = df.sort_values('TIME')
    
    energy_order = energy_sorted['ENERGY'].values
    time_order = time_sorted['TIME'].values
    
    # Check if energy and time have same order
    energy_time_correlation = np.corrcoef(energy_order, time_order)[0,1]
    print(f"Energy-time order correlation: {energy_time_correlation:.6f}")
    
    # Check for systematic patterns
    print(f"Energy variance: {df['ENERGY'].var():.2e}")
    print(f"Time variance: {df['TIME'].var():.2e}")
    
    return {
        'duplicates': duplicates,
        'energy_constant': energy_constant,
        'time_constant': time_constant,
        'order_correlation': energy_time_correlation
    }

def analyze_energy_time_relationship(df):
    """Analyze the energy-time relationship in detail"""
    print("\nANALYZING ENERGY-TIME RELATIONSHIP")
    print("=" * 50)
    
    # Calculate various correlation measures
    pearson_r, pearson_p = stats.pearsonr(df['ENERGY'], df['TIME'])
    spearman_rho, spearman_p = stats.spearmanr(df['ENERGY'], df['TIME'])
    kendall_tau, kendall_p = stats.kendalltau(df['ENERGY'], df['TIME'])
    
    print(f"Pearson correlation: r = {pearson_r:.6f}, p = {pearson_p:.2e}")
    print(f"Spearman correlation: ρ = {spearman_rho:.6f}, p = {spearman_p:.2e}")
    print(f"Kendall correlation: τ = {kendall_tau:.6f}, p = {kendall_p:.2e}")
    
    # Analyze correlation strength
    if abs(spearman_rho) > 0.9:
        print("🎯 VERY STRONG CORRELATION!")
    elif abs(spearman_rho) > 0.7:
        print("🔥 STRONG CORRELATION!")
    elif abs(spearman_rho) > 0.5:
        print("📊 MODERATE CORRELATION")
    else:
        print("📉 WEAK CORRELATION")
    
    return {
        'pearson': (pearson_r, pearson_p),
        'spearman': (spearman_rho, spearman_p),
        'kendall': (kendall_tau, kendall_p)
    }

def analyze_energy_distribution(df):
    """Analyze energy distribution"""
    print("\nANALYZING ENERGY DISTRIBUTION")
    print("=" * 50)
    
    energy = df['ENERGY']
    
    print(f"Energy statistics:")
    print(f"  Mean: {energy.mean():.2f} GeV")
    print(f"  Median: {energy.median():.2f} GeV")
    print(f"  Std: {energy.std():.2f} GeV")
    print(f"  Min: {energy.min():.2f} GeV")
    print(f"  Max: {energy.max():.2f} GeV")
    
    # Check for power-law distribution
    log_energy = np.log10(energy)
    log_energy_mean = log_energy.mean()
    log_energy_std = log_energy.std()
    
    print(f"Log-energy statistics:")
    print(f"  Mean: {log_energy_mean:.2f}")
    print(f"  Std: {log_energy_std:.2f}")
    
    # Check for energy clustering
    energy_unique = energy.nunique()
    energy_total = len(energy)
    energy_diversity = energy_unique / energy_total
    
    print(f"Energy diversity: {energy_diversity:.4f} ({energy_unique}/{energy_total})")
    
    return {
        'mean': energy.mean(),
        'std': energy.std(),
        'diversity': energy_diversity
    }

def analyze_time_distribution(df):
    """Analyze time distribution"""
    print("\nANALYZING TIME DISTRIBUTION")
    print("=" * 50)
    
    time = df['TIME']
    
    print(f"Time statistics:")
    print(f"  Mean: {time.mean():.1f} s")
    print(f"  Median: {time.median():.1f} s")
    print(f"  Std: {time.std():.1f} s")
    print(f"  Min: {time.min():.1f} s")
    print(f"  Max: {time.max():.1f} s")
    
    # Check for time clustering
    time_unique = time.nunique()
    time_total = len(time)
    time_diversity = time_unique / time_total
    
    print(f"Time diversity: {time_diversity:.4f} ({time_unique}/{time_total})")
    
    # Check for temporal patterns
    time_sorted = df.sort_values('TIME')
    time_diffs = time_sorted['TIME'].diff().dropna()
    
    print(f"Time differences:")
    print(f"  Mean: {time_diffs.mean():.2f} s")
    print(f"  Std: {time_diffs.std():.2f} s")
    print(f"  Min: {time_diffs.min():.2f} s")
    print(f"  Max: {time_diffs.max():.2f} s")
    
    return {
        'mean': time.mean(),
        'std': time.std(),
        'diversity': time_diversity
    }

def create_visualizations(df):
    """Create visualizations for GRB090926A"""
    print("\nCREATING VISUALIZATIONS")
    print("=" * 50)
    
    # Set up the plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('GRB090926A - Deep Analysis', fontsize=16, fontweight='bold')
    
    # 1. Energy vs Time scatter plot
    axes[0,0].scatter(df['TIME'], df['ENERGY'], alpha=0.6, s=1)
    axes[0,0].set_xlabel('Time (s)')
    axes[0,0].set_ylabel('Energy (GeV)')
    axes[0,0].set_title('Energy vs Time')
    axes[0,0].set_yscale('log')
    
    # 2. Energy distribution
    axes[0,1].hist(df['ENERGY'], bins=50, alpha=0.7, edgecolor='black')
    axes[0,1].set_xlabel('Energy (GeV)')
    axes[0,1].set_ylabel('Count')
    axes[0,1].set_title('Energy Distribution')
    axes[0,1].set_xscale('log')
    
    # 3. Time distribution
    axes[1,0].hist(df['TIME'], bins=50, alpha=0.7, edgecolor='black')
    axes[1,0].set_xlabel('Time (s)')
    axes[1,0].set_ylabel('Count')
    axes[1,0].set_title('Time Distribution')
    
    # 4. Correlation plot
    axes[1,1].scatter(df['ENERGY'], df['TIME'], alpha=0.6, s=1)
    axes[1,1].set_xlabel('Energy (GeV)')
    axes[1,1].set_ylabel('Time (s)')
    axes[1,1].set_title('Correlation Plot')
    axes[1,1].set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('GRB090926A_deep_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: GRB090926A_deep_analysis.png")

def main():
    """Main function"""
    print("DEEP ANALYSIS GRB090926A - INFINITE EFFECT")
    print("=" * 80)
    
    # Load data
    df = load_grb090926a_data()
    
    # Analyze infinite effect
    rho, p_value, sigma_corrected = analyze_infinite_effect(df)
    
    # Check data quality
    quality_check = check_data_quality(df)
    
    # Analyze energy-time relationship
    correlations = analyze_energy_time_relationship(df)
    
    # Analyze distributions
    energy_stats = analyze_energy_distribution(df)
    time_stats = analyze_time_distribution(df)
    
    # Create visualizations
    create_visualizations(df)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - GRB090926A ANALYSIS")
    print("=" * 80)
    
    print(f"📊 Data Quality:")
    print(f"  Photons: {len(df):,}")
    print(f"  Duplicates: {quality_check['duplicates']}")
    print(f"  Energy diversity: {energy_stats['diversity']:.4f}")
    print(f"  Time diversity: {time_stats['diversity']:.4f}")
    
    print(f"\n🔍 Correlations:")
    print(f"  Spearman ρ: {correlations['spearman'][0]:.6f}")
    print(f"  P-value: {correlations['spearman'][1]:.2e}")
    print(f"  Corrected σ: {sigma_corrected:.2f}")
    
    print(f"\n🎯 Interpretation:")
    if abs(correlations['spearman'][0]) > 0.9:
        print("  VERY STRONG correlation detected!")
        print("  This suggests a significant QG effect or data artifact")
    elif abs(correlations['spearman'][0]) > 0.7:
        print("  STRONG correlation detected!")
        print("  This suggests a QG effect")
    else:
        print("  Moderate correlation detected")
    
    if correlations['spearman'][1] == 0:
        print("  ⚠️ Perfect correlation (p=0) - investigate further!")
    
    print(f"\n📁 Files created:")
    print(f"  - GRB090926A_deep_analysis.png")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
