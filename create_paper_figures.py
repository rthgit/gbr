#!/usr/bin/env python3
"""
CREATE PAPER FIGURES
Create high-quality scientific figures for the Quantum Gravity GRB paper
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
from pathlib import Path

# Set style for scientific figures
plt.style.use('default')
sns.set_palette("husl")

def create_figure_1_overview():
    """Create Figure 1: Overview of all GRB results"""
    print("Creating Figure 1: GRB Overview")
    
    # Load results
    with open('comprehensive_qg_report.json', 'r') as f:
        results = json.load(f)
    
    grb_data = results['grb_results']
    
    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Figure 1: Quantum Gravity Effects in Gamma-Ray Bursts', fontsize=16, fontweight='bold')
    
    # 1. Significance vs GRB
    grb_names = [grb['grb_name'] for grb in grb_data]
    significances = [grb['significance'] for grb in grb_data]
    photons = [grb['photons'] for grb in grb_data]
    
    colors = ['red' if sig >= 5.0 else 'orange' if sig >= 3.0 else 'blue' for sig in significances]
    
    bars = ax1.bar(range(len(grb_names)), significances, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('GRB')
    ax1.set_ylabel('Significance (σ)')
    ax1.set_title('(a) QG Effect Significance')
    ax1.set_xticks(range(len(grb_names)))
    ax1.set_xticklabels([name.replace('GRB', '') for name in grb_names], rotation=45)
    ax1.axhline(y=3.0, color='orange', linestyle='--', alpha=0.7, label='3σ threshold')
    ax1.axhline(y=5.0, color='red', linestyle='--', alpha=0.7, label='5σ threshold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, sig) in enumerate(zip(bars, significances)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{sig:.2f}σ', ha='center', va='bottom', fontweight='bold')
    
    # 2. Photons vs Significance
    ax2.scatter(photons, significances, s=100, c=colors, alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Number of Photons')
    ax2.set_ylabel('Significance (σ)')
    ax2.set_title('(b) Photons vs Significance')
    ax2.set_xscale('log')
    ax2.axhline(y=3.0, color='orange', linestyle='--', alpha=0.7)
    ax2.axhline(y=5.0, color='red', linestyle='--', alpha=0.7)
    ax2.grid(True, alpha=0.3)
    
    # Add GRB labels
    for i, name in enumerate(grb_names):
        ax2.annotate(name.replace('GRB', ''), (photons[i], significances[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 3. Energy vs Time scatter for top GRB
    top_grb = max(grb_data, key=lambda x: x['significance'])
    df = pd.read_csv(f"{top_grb['grb_name']}_PH00.csv")
    
    ax3.scatter(df['TIME'], df['ENERGY'], alpha=0.6, s=1, c='blue')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Energy (GeV)')
    ax3.set_title(f'(c) {top_grb["grb_name"]} Energy vs Time')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    
    # 4. Detection rate pie chart
    above_3sigma = len([g for g in grb_data if g['significance'] >= 3.0])
    below_3sigma = len(grb_data) - above_3sigma
    
    ax4.pie([above_3sigma, below_3sigma], labels=[f'σ ≥ 3.0\n({above_3sigma} GRBs)', 
                                                   f'σ < 3.0\n({below_3sigma} GRBs)'], 
            colors=['orange', 'lightblue'], autopct='%1.1f%%', startangle=90)
    ax4.set_title('(d) QG Detection Rate')
    
    plt.tight_layout()
    plt.savefig('Figure_1_GRB_Overview.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: Figure_1_GRB_Overview.png")

def create_figure_2_top_grbs():
    """Create Figure 2: Detailed analysis of top GRBs"""
    print("Creating Figure 2: Top GRBs Analysis")
    
    # Load data for top 2 GRBs
    grb1_data = pd.read_csv('GRB090926A_PH00.csv')
    grb2_data = pd.read_csv('GRB090510_PH00.csv')
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Figure 2: Detailed Analysis of Top QG GRBs', fontsize=16, fontweight='bold')
    
    # GRB090926A Energy vs Time
    ax1.scatter(grb1_data['TIME'], grb1_data['ENERGY'], alpha=0.6, s=1, c='red')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Energy (GeV)')
    ax1.set_title('(a) GRB090926A: 8.01σ Effect')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Add correlation info
    r, p = stats.pearsonr(grb1_data['ENERGY'], grb1_data['TIME'])
    sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
    ax1.text(0.05, 0.95, f'r = {r:.4f}\nσ = {sigma:.2f}', 
             transform=ax1.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # GRB090510 Energy vs Time
    ax2.scatter(grb2_data['TIME'], grb2_data['ENERGY'], alpha=0.6, s=1, c='orange')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Energy (GeV)')
    ax2.set_title('(b) GRB090510: 6.46σ Effect')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Add correlation info
    r, p = stats.pearsonr(grb2_data['ENERGY'], grb2_data['TIME'])
    sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
    ax2.text(0.05, 0.95, f'r = {r:.4f}\nσ = {sigma:.2f}', 
             transform=ax2.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Energy distributions
    ax3.hist(grb1_data['ENERGY'], bins=50, alpha=0.7, color='red', label='GRB090926A', density=True)
    ax3.hist(grb2_data['ENERGY'], bins=50, alpha=0.7, color='orange', label='GRB090510', density=True)
    ax3.set_xlabel('Energy (GeV)')
    ax3.set_ylabel('Density')
    ax3.set_title('(c) Energy Distributions')
    ax3.set_xscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Time distributions
    ax4.hist(grb1_data['TIME'], bins=50, alpha=0.7, color='red', label='GRB090926A', density=True)
    ax4.hist(grb2_data['TIME'], bins=50, alpha=0.7, color='orange', label='GRB090510', density=True)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Density')
    ax4.set_title('(d) Time Distributions')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('Figure_2_Top_GRBs_Analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: Figure_2_Top_GRBs_Analysis.png")

def create_figure_3_phase_analysis():
    """Create Figure 3: Phase analysis demonstration"""
    print("Creating Figure 3: Phase Analysis")
    
    # Use GRB090510 as example (6.46σ effect)
    df = pd.read_csv('GRB090510_PH00.csv')
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Figure 3: Phase Analysis Technique', fontsize=16, fontweight='bold')
    
    # Sort by time and split
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    split_idx = len(df_sorted) // 2
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    # Full dataset
    ax1.scatter(df['TIME'], df['ENERGY'], alpha=0.6, s=1, c='gray')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Energy (GeV)')
    ax1.set_title('(a) Full Dataset')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    r, p = stats.pearsonr(df['ENERGY'], df['TIME'])
    sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
    ax1.text(0.05, 0.95, f'Global: σ = {sigma:.2f}', 
             transform=ax1.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Early phase
    ax2.scatter(early_df['TIME'], early_df['ENERGY'], alpha=0.6, s=1, c='blue')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Energy (GeV)')
    ax2.set_title('(b) Early Phase')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    r, p = stats.pearsonr(early_df['ENERGY'], early_df['TIME'])
    sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
    ax2.text(0.05, 0.95, f'Early: σ = {sigma:.2f}', 
             transform=ax2.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Late phase
    ax3.scatter(late_df['TIME'], late_df['ENERGY'], alpha=0.6, s=1, c='red')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Energy (GeV)')
    ax3.set_title('(c) Late Phase')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    
    r, p = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
    sigma = stats.norm.ppf(1 - p/2) if p > 0 else 0
    ax3.text(0.05, 0.95, f'Late: σ = {sigma:.2f}', 
             transform=ax3.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Comparison
    phases = ['Full', 'Early', 'Late']
    sigmas = [
        stats.norm.ppf(1 - stats.pearsonr(df['ENERGY'], df['TIME'])[1]/2),
        stats.norm.ppf(1 - stats.pearsonr(early_df['ENERGY'], early_df['TIME'])[1]/2),
        stats.norm.ppf(1 - stats.pearsonr(late_df['ENERGY'], late_df['TIME'])[1]/2)
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

def create_figure_4_literature_comparison():
    """Create Figure 4: Literature comparison"""
    print("Creating Figure 4: Literature Comparison")
    
    # Load literature comparison data
    with open('literature_comparison_report.json', 'r') as f:
        lit_data = json.load(f)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Figure 4: Literature Comparison and Validation', fontsize=16, fontweight='bold')
    
    # Our results vs Literature
    grb_names = []
    our_sigmas = []
    lit_sigmas = []
    colors = []
    
    for grb, our_data in lit_data['our_results'].items():
        if grb in lit_data['literature']:
            lit_info = lit_data['literature'][grb]
            if lit_info['significance'] is not None:
                grb_names.append(grb.replace('GRB', ''))
                our_sigmas.append(our_data['significance'])
                lit_sigmas.append(lit_info['significance'])
                
                # Color based on agreement
                diff = abs(our_data['significance'] - lit_info['significance'])
                if diff < 1.0:
                    colors.append('green')
                elif diff < 2.0:
                    colors.append('orange')
                else:
                    colors.append('red')
    
    # Scatter plot
    ax1.scatter(our_sigmas, lit_sigmas, c=colors, s=100, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Our Results (σ)')
    ax1.set_ylabel('Literature (σ)')
    ax1.set_title('(a) Our Results vs Literature')
    ax1.grid(True, alpha=0.3)
    
    # Add diagonal line
    min_val = min(min(our_sigmas), min(lit_sigmas))
    max_val = max(max(our_sigmas), max(lit_sigmas))
    ax1.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect agreement')
    
    # Add GRB labels
    for i, name in enumerate(grb_names):
        ax1.annotate(name, (our_sigmas[i], lit_sigmas[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.legend()
    
    # Agreement summary
    agreements = ['Good\n(<1σ)', 'Moderate\n(1-2σ)', 'Poor\n(>2σ)']
    counts = [colors.count('green'), colors.count('orange'), colors.count('red')]
    colors_pie = ['green', 'orange', 'red']
    
    ax2.pie(counts, labels=agreements, colors=colors_pie, autopct='%1.0f%%', startangle=90)
    ax2.set_title('(b) Agreement Distribution')
    
    plt.tight_layout()
    plt.savefig('Figure_4_Literature_Comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: Figure_4_Literature_Comparison.png")

def create_figure_5_methodology():
    """Create Figure 5: Methodology overview"""
    print("Creating Figure 5: Methodology Overview")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Figure 5: Analysis Methodology', fontsize=16, fontweight='bold')
    
    # 1. Data flow diagram
    ax1.text(0.5, 0.9, 'Fermi LAT Data', ha='center', va='center', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightblue'))
    ax1.text(0.5, 0.7, '↓', ha='center', va='center', fontsize=20)
    ax1.text(0.5, 0.6, 'Data Processing', ha='center', va='center', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax1.text(0.5, 0.4, '↓', ha='center', va='center', fontsize=20)
    ax1.text(0.5, 0.3, 'Multi-Technique Analysis', ha='center', va='center', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightyellow'))
    ax1.text(0.5, 0.1, '↓', ha='center', va='center', fontsize=20)
    ax1.text(0.5, 0.0, 'QG Detection', ha='center', va='center', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightcoral'))
    ax1.set_xlim(0, 1)
    ax1.set_ylim(-0.1, 1)
    ax1.set_title('(a) Analysis Pipeline')
    ax1.axis('off')
    
    # 2. Techniques used
    techniques = ['Global\nCorrelation', 'Phase\nAnalysis', 'Energy\nPercentiles', 'Bootstrap\nValidation']
    usage = [6, 6, 6, 2]  # How many GRBs used each technique
    
    bars = ax2.bar(techniques, usage, color=['blue', 'green', 'orange', 'red'], alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Number of GRBs')
    ax2.set_title('(b) Techniques Applied')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, usage):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(val), ha='center', va='bottom', fontweight='bold')
    
    # 3. Statistical significance distribution
    with open('comprehensive_qg_report.json', 'r') as f:
        results = json.load(f)
    
    sigmas = [grb['significance'] for grb in results['grb_results']]
    
    ax3.hist(sigmas, bins=6, alpha=0.7, color='purple', edgecolor='black')
    ax3.axvline(x=3.0, color='orange', linestyle='--', alpha=0.7, label='3σ threshold')
    ax3.axvline(x=5.0, color='red', linestyle='--', alpha=0.7, label='5σ threshold')
    ax3.set_xlabel('Significance (σ)')
    ax3.set_ylabel('Number of GRBs')
    ax3.set_title('(c) Significance Distribution')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Detection summary
    above_3sigma = len([s for s in sigmas if s >= 3.0])
    above_5sigma = len([s for s in sigmas if s >= 5.0])
    below_3sigma = len(sigmas) - above_3sigma
    
    categories = ['σ ≥ 5.0', '3.0 ≤ σ < 5.0', 'σ < 3.0']
    counts = [above_5sigma, above_3sigma - above_5sigma, below_3sigma]
    colors = ['red', 'orange', 'lightblue']
    
    ax4.pie(counts, labels=categories, colors=colors, autopct='%1.1f%%', startangle=90)
    ax4.set_title('(d) Detection Summary')
    
    plt.tight_layout()
    plt.savefig('Figure_5_Methodology.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: Figure_5_Methodology.png")

def main():
    """Main function"""
    print("CREATE PAPER FIGURES")
    print("=" * 80)
    print("Creating high-quality scientific figures for the Quantum Gravity GRB paper")
    
    # Create all figures
    create_figure_1_overview()
    create_figure_2_top_grbs()
    create_figure_3_phase_analysis()
    create_figure_4_literature_comparison()
    create_figure_5_methodology()
    
    print(f"\n{'='*80}")
    print("ALL FIGURES CREATED!")
    print(f"{'='*80}")
    
    print("📊 Figures created:")
    print("  - Figure_1_GRB_Overview.png")
    print("  - Figure_2_Top_GRBs_Analysis.png")
    print("  - Figure_3_Phase_Analysis.png")
    print("  - Figure_4_Literature_Comparison.png")
    print("  - Figure_5_Methodology.png")
    
    print(f"\n🎯 Figure descriptions:")
    print("  Figure 1: Overview of all GRB results and detection rates")
    print("  Figure 2: Detailed analysis of top QG GRBs (8.01σ and 6.46σ)")
    print("  Figure 3: Phase analysis technique demonstration")
    print("  Figure 4: Literature comparison and validation")
    print("  Figure 5: Methodology overview and statistical summary")
    
    print(f"\n📁 Ready for paper integration!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
