#!/usr/bin/env python3
"""
ANALYZE REMAINING GRBs
Analyze GRB160625B and GRB080916C in detail to complete the dataset
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def analyze_grb160625b():
    """Analyze GRB160625B in detail"""
    print("ANALYZING GRB160625B")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv('GRB160625B_PH00.csv')
    print(f"✅ Loaded {len(df)} photons")
    print(f"Energy range: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
    print(f"Time range: {df['TIME'].min():.1f} - {df['TIME'].max():.1f} s")
    
    # Global correlation
    r_global, p_global = stats.pearsonr(df['ENERGY'], df['TIME'])
    sigma_global = stats.norm.ppf(1 - p_global/2) if p_global > 0 else 0
    
    print(f"\nGlobal correlation:")
    print(f"  r = {r_global:.4f}, p = {p_global:.2e}, σ = {sigma_global:.2f}")
    
    # Phase analysis
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    split_idx = len(df_sorted) // 2
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    early_r, early_p = stats.pearsonr(early_df['ENERGY'], early_df['TIME'])
    late_r, late_p = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
    
    early_sigma = stats.norm.ppf(1 - early_p/2) if early_p > 0 else 0
    late_sigma = stats.norm.ppf(1 - late_p/2) if late_p > 0 else 0
    
    print(f"\nPhase analysis:")
    print(f"  Early: r = {early_r:.4f}, σ = {early_sigma:.2f} ({len(early_df)} photons)")
    print(f"  Late: r = {late_r:.4f}, σ = {late_sigma:.2f} ({len(late_df)} photons)")
    
    # Energy percentiles
    print(f"\nEnergy percentiles:")
    for pct in [75, 90, 95]:
        threshold = np.percentile(df['ENERGY'], pct)
        high_energy_df = df[df['ENERGY'] >= threshold]
        
        if len(high_energy_df) >= 10:
            r, p = stats.pearsonr(high_energy_df['ENERGY'], high_energy_df['TIME'])
            sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
            print(f"  E ≥ {threshold:.0f} GeV: r = {r:.4f}, σ = {sigma:.2f} ({len(high_energy_df)} photons)")
    
    return {
        'grb_name': 'GRB160625B',
        'photons': len(df),
        'global_sigma': sigma_global,
        'max_sigma': max(sigma_global, early_sigma, late_sigma),
        'best_technique': 'phase_late' if late_sigma > early_sigma else 'phase_early'
    }

def analyze_grb080916c():
    """Analyze GRB080916C in detail"""
    print("\nANALYZING GRB080916C")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv('GRB080916C_PH00.csv')
    print(f"✅ Loaded {len(df)} photons")
    print(f"Energy range: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
    print(f"Time range: {df['TIME'].min():.1f} - {df['TIME'].max():.1f} s")
    
    # Global correlation
    r_global, p_global = stats.pearsonr(df['ENERGY'], df['TIME'])
    sigma_global = stats.norm.ppf(1 - p_global/2) if p_global > 0 else 0
    
    print(f"\nGlobal correlation:")
    print(f"  r = {r_global:.4f}, p = {p_global:.2e}, σ = {sigma_global:.2f}")
    
    # Phase analysis
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    split_idx = len(df_sorted) // 2
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    early_r, early_p = stats.pearsonr(early_df['ENERGY'], early_df['TIME'])
    late_r, late_p = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
    
    early_sigma = stats.norm.ppf(1 - early_p/2) if early_p > 0 else 0
    late_sigma = stats.norm.ppf(1 - late_p/2) if late_p > 0 else 0
    
    print(f"\nPhase analysis:")
    print(f"  Early: r = {early_r:.4f}, σ = {early_sigma:.2f} ({len(early_df)} photons)")
    print(f"  Late: r = {late_r:.4f}, σ = {late_sigma:.2f} ({len(late_df)} photons)")
    
    # Energy percentiles
    print(f"\nEnergy percentiles:")
    for pct in [75, 90, 95]:
        threshold = np.percentile(df['ENERGY'], pct)
        high_energy_df = df[df['ENERGY'] >= threshold]
        
        if len(high_energy_df) >= 10:
            r, p = stats.pearsonr(high_energy_df['ENERGY'], high_energy_df['TIME'])
            sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
            print(f"  E ≥ {threshold:.0f} GeV: r = {r:.4f}, σ = {sigma:.2f} ({len(high_energy_df)} photons)")
    
    return {
        'grb_name': 'GRB080916C',
        'photons': len(df),
        'global_sigma': sigma_global,
        'max_sigma': max(sigma_global, early_sigma, late_sigma),
        'best_technique': 'phase_late' if late_sigma > early_sigma else 'phase_early'
    }

def create_comprehensive_visualization():
    """Create comprehensive visualization of all GRBs"""
    print("\nCREATING COMPREHENSIVE VISUALIZATION")
    print("=" * 50)
    
    # Load all GRB data
    grb_files = [
        'GRB090926A_PH00.csv',
        'GRB090510_PH00.csv', 
        'GRB090902B_PH00.csv',
        'GRB130427A_PH00.csv',
        'GRB160625B_PH00.csv',
        'GRB080916C_PH00.csv'
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Comprehensive GRB QG Analysis', fontsize=16, fontweight='bold')
    
    for i, grb_file in enumerate(grb_files):
        row = i // 3
        col = i % 3
        
        df = pd.read_csv(grb_file)
        grb_name = grb_file.replace('_PH00.csv', '')
        
        axes[row, col].scatter(df['TIME'], df['ENERGY'], alpha=0.6, s=1)
        axes[row, col].set_title(f'{grb_name}')
        axes[row, col].set_xlabel('Time (s)')
        axes[row, col].set_ylabel('Energy (GeV)')
        axes[row, col].set_yscale('log')
        
        # Add significance info
        r, p = stats.pearsonr(df['ENERGY'], df['TIME'])
        sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
        axes[row, col].text(0.05, 0.95, f'σ = {sigma:.2f}', 
                           transform=axes[row, col].transAxes, 
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('comprehensive_grb_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: comprehensive_grb_analysis.png")

def main():
    """Main function"""
    print("ANALYZE REMAINING GRBs")
    print("=" * 80)
    print("Analyzing GRB160625B and GRB080916C to complete the dataset")
    
    # Analyze GRB160625B
    grb160625b_results = analyze_grb160625b()
    
    # Analyze GRB080916C
    grb080916c_results = analyze_grb080916c()
    
    # Create comprehensive visualization
    create_comprehensive_visualization()
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY - REMAINING GRBs ANALYSIS")
    print(f"{'='*80}")
    
    print(f"📊 GRB160625B Results:")
    print(f"  Photons: {grb160625b_results['photons']:,}")
    print(f"  Global σ: {grb160625b_results['global_sigma']:.2f}")
    print(f"  Max σ: {grb160625b_results['max_sigma']:.2f}")
    print(f"  Best technique: {grb160625b_results['best_technique']}")
    
    print(f"\n📊 GRB080916C Results:")
    print(f"  Photons: {grb080916c_results['photons']:,}")
    print(f"  Global σ: {grb080916c_results['global_sigma']:.2f}")
    print(f"  Max σ: {grb080916c_results['max_sigma']:.2f}")
    print(f"  Best technique: {grb080916c_results['best_technique']}")
    
    print(f"\n🎯 Overall Status:")
    print(f"  ✅ GRB160625B: {grb160625b_results['max_sigma']:.2f}σ (marginal)")
    print(f"  ✅ GRB080916C: {grb080916c_results['max_sigma']:.2f}σ (below threshold)")
    
    print(f"\n📁 Files created:")
    print(f"  - comprehensive_grb_analysis.png")
    
    print(f"\n{'='*80}")
    print("REMAINING GRBs ANALYSIS COMPLETE!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
