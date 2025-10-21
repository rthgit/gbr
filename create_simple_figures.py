#!/usr/bin/env python3
"""
CREATE SIMPLE FIGURES
Create simple scientific figures for the paper
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def create_figure_1():
    """Create Figure 1: GRB Overview"""
    print("Creating Figure 1: GRB Overview")
    
    # GRB data
    grbs = ['090926A', '090510', '090902B', '130427A', '160625B', '080916C']
    sigmas = [8.01, 6.46, 3.28, 3.24, 2.41, 1.66]
    photons = [24149, 24139, 11289, 706, 4152, 3271]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Figure 1: Quantum Gravity Effects in GRBs', fontsize=14, fontweight='bold')
    
    # Significance bar chart
    colors = ['red' if s >= 5.0 else 'orange' if s >= 3.0 else 'blue' for s in sigmas]
    bars = ax1.bar(grbs, sigmas, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Significance (σ)')
    ax1.set_title('(a) QG Effect Significance')
    ax1.axhline(y=3.0, color='orange', linestyle='--', alpha=0.7)
    ax1.axhline(y=5.0, color='red', linestyle='--', alpha=0.7)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, sigma in zip(bars, sigmas):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{sigma:.2f}σ', ha='center', va='bottom', fontweight='bold')
    
    # Photons vs Significance
    ax2.scatter(photons, sigmas, s=100, c=colors, alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Number of Photons')
    ax2.set_ylabel('Significance (σ)')
    ax2.set_title('(b) Photons vs Significance')
    ax2.set_xscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Add GRB labels
    for i, grb in enumerate(grbs):
        ax2.annotate(grb, (photons[i], sigmas[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('Figure_1_GRB_Overview.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved: Figure_1_GRB_Overview.png")

def create_figure_2():
    """Create Figure 2: Top GRBs Analysis"""
    print("Creating Figure 2: Top GRBs Analysis")
    
    # Load data for top 2 GRBs
    df1 = pd.read_csv('GRB090926A_PH00.csv')
    df2 = pd.read_csv('GRB090510_PH00.csv')
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Figure 2: Detailed Analysis of Top QG GRBs', fontsize=14, fontweight='bold')
    
    # GRB090926A
    ax1.scatter(df1['TIME'], df1['ENERGY'], alpha=0.6, s=1, c='red')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Energy (GeV)')
    ax1.set_title('(a) GRB090926A: 8.01σ Effect')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # GRB090510
    ax2.scatter(df2['TIME'], df2['ENERGY'], alpha=0.6, s=1, c='orange')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Energy (GeV)')
    ax2.set_title('(b) GRB090510: 6.46σ Effect')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Energy distributions
    ax3.hist(df1['ENERGY'], bins=50, alpha=0.7, color='red', label='GRB090926A', density=True)
    ax3.hist(df2['ENERGY'], bins=50, alpha=0.7, color='orange', label='GRB090510', density=True)
    ax3.set_xlabel('Energy (GeV)')
    ax3.set_ylabel('Density')
    ax3.set_title('(c) Energy Distributions')
    ax3.set_xscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Detection rate pie chart
    above_3sigma = 4
    below_3sigma = 2
    
    ax4.pie([above_3sigma, below_3sigma], labels=[f'σ ≥ 3.0\n({above_3sigma} GRBs)', 
                                                   f'σ < 3.0\n({below_3sigma} GRBs)'], 
            colors=['orange', 'lightblue'], autopct='%1.1f%%', startangle=90)
    ax4.set_title('(d) QG Detection Rate')
    
    plt.tight_layout()
    plt.savefig('Figure_2_Top_GRBs_Analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved: Figure_2_Top_GRBs_Analysis.png")

def create_figure_3():
    """Create Figure 3: Phase Analysis"""
    print("Creating Figure 3: Phase Analysis")
    
    # Use GRB090510 as example
    df = pd.read_csv('GRB090510_PH00.csv')
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Figure 3: Phase Analysis Technique', fontsize=14, fontweight='bold')
    
    # Full dataset
    ax1.scatter(df['TIME'], df['ENERGY'], alpha=0.6, s=1, c='gray')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Energy (GeV)')
    ax1.set_title('(a) Full Dataset')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Sort by time and split
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    split_idx = len(df_sorted) // 2
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    # Early phase
    ax2.scatter(early_df['TIME'], early_df['ENERGY'], alpha=0.6, s=1, c='blue')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Energy (GeV)')
    ax2.set_title('(b) Early Phase')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Late phase
    ax3.scatter(late_df['TIME'], late_df['ENERGY'], alpha=0.6, s=1, c='red')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Energy (GeV)')
    ax3.set_title('(c) Late Phase')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    
    # Phase comparison
    phases = ['Full', 'Early', 'Late']
    # Calculate sigmas
    r_full, p_full = stats.pearsonr(df['ENERGY'], df['TIME'])
    r_early, p_early = stats.pearsonr(early_df['ENERGY'], early_df['TIME'])
    r_late, p_late = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
    
    sigmas = [
        stats.norm.ppf(1 - p_full/2) if p_full > 0 else 0,
        stats.norm.ppf(1 - p_early/2) if p_early > 0 else 0,
        stats.norm.ppf(1 - p_late/2) if p_late > 0 else 0
    ]
    
    colors = ['gray', 'blue', 'red']
    bars = ax4.bar(phases, sigmas, color=colors, alpha=0.7, edgecolor='black')
    ax4.set_ylabel('Significance (σ)')
    ax4.set_title('(d) Phase Comparison')
    ax4.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, sigma in zip(bars, sigmas):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{sigma:.2f}σ', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('Figure_3_Phase_Analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Saved: Figure_3_Phase_Analysis.png")

def main():
    """Main function"""
    print("CREATE SIMPLE FIGURES")
    print("=" * 60)
    
    create_figure_1()
    create_figure_2()
    create_figure_3()
    
    print("\n" + "=" * 60)
    print("ALL FIGURES CREATED!")
    print("=" * 60)
    
    print("📊 Figures created:")
    print("  - Figure_1_GRB_Overview.png")
    print("  - Figure_2_Top_GRBs_Analysis.png")
    print("  - Figure_3_Phase_Analysis.png")
    
    print("\n🎯 Ready for paper integration!")

if __name__ == "__main__":
    main()
