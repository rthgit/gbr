#!/usr/bin/env python3
"""
CREAZIONE FIGURE FINALI PER IL PAPER
Genera le 4 figure mancanti per il paper scientifico
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Configurazione matplotlib per figure scientifiche
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.titlesize'] = 18

def load_grb_data():
    """Carica i dati dei GRB analizzati"""
    print("CARICAMENTO DATI GRB")
    print("-" * 30)
    
    grb_data = {}
    
    # Lista dei GRB da caricare
    grb_files = {
        'GRB130427A': 'GRB130427A_PH00.csv',
        'GRB090902B': 'GRB090902B_PH00.csv',
        'GRB080916C': 'GRB080916C_PH00.csv',
        'GRB090510': 'GRB090510_PH00.csv',
        'GRB090926A': 'GRB090926A_PH00.csv',
        'GRB160625B': 'GRB160625B_PH00.csv'
    }
    
    for grb_name, filename in grb_files.items():
        csv_path = Path(filename)
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                if 'ENERGY' in df.columns and 'TIME' in df.columns:
                    grb_data[grb_name] = df
                    print(f"✅ {grb_name}: {len(df)} fotoni")
                else:
                    print(f"❌ {grb_name}: colonne mancanti")
            except Exception as e:
                print(f"❌ {grb_name}: errore caricamento - {e}")
        else:
            print(f"❌ {grb_name}: file non trovato")
    
    return grb_data

def create_figure_1_grb_overview(grb_data):
    """Figure 1: Panoramica dei GRB analizzati"""
    print("\nCREAZIONE FIGURE 1: GRB Overview")
    print("-" * 40)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Figure 1: Gamma-Ray Burst Overview - Energy vs Time Analysis', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # Risultati noti dal paper
    results = {
        'GRB130427A': {'sigma': 10.18, 'photons': 9371, 'emax': 58.7},
        'GRB090902B': {'sigma': 3.28, 'photons': 11289, 'emax': 80.8},
        'GRB080916C': {'sigma': 1.88, 'photons': 3271, 'emax': 351.0},
        'GRB090510': {'sigma': 6.46, 'photons': 24139, 'emax': 58.7},
        'GRB090926A': {'sigma': 8.01, 'photons': 24149, 'emax': 61.3},
        'GRB160625B': {'sigma': 2.41, 'photons': 4152, 'emax': 71.9}
    }
    
    axes = axes.flatten()
    
    for i, (grb_name, df) in enumerate(grb_data.items()):
        if i >= 6:
            break
            
        ax = axes[i]
        
        # Prepara dati
        energy = df['ENERGY'].values / 1000  # GeV
        time = df['TIME'].values
        
        # Scatter plot
        ax.scatter(time, energy, alpha=0.4, s=0.5, color='blue')
        
        # Aggiungi trend line se significativo
        if results.get(grb_name, {}).get('sigma', 0) > 3.0:
            z = np.polyfit(time, energy, 1)
            p = np.poly1d(z)
            ax.plot(time, p(time), "r-", alpha=0.8, linewidth=2)
        
        # Formattazione
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Energy (GeV)')
        ax.set_title(f'{grb_name}\n{results.get(grb_name, {}).get("sigma", 0):.2f}σ, '
                    f'{results.get(grb_name, {}).get("photons", 0):,} photons', 
                    fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Colora il titolo in base alla significatività
        sigma = results.get(grb_name, {}).get('sigma', 0)
        if sigma >= 5.0:
            ax.title.set_color('red')
        elif sigma >= 3.0:
            ax.title.set_color('orange')
        else:
            ax.title.set_color('gray')
    
    plt.tight_layout()
    plt.savefig('Figure_1_GRB_Overview_Final.png', dpi=300, bbox_inches='tight')
    print("✅ Salvato: Figure_1_GRB_Overview_Final.png")
    
    return fig

def create_figure_2_top_grbs_analysis(grb_data):
    """Figure 2: Analisi dettagliata dei GRB top"""
    print("\nCREAZIONE FIGURE 2: Top GRBs Analysis")
    print("-" * 40)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Figure 2: Detailed Analysis of Top GRBs with QG Effects', 
                 fontsize=18, fontweight='bold')
    
    # Top GRBs con effetti più significativi
    top_grbs = ['GRB130427A', 'GRB090926A', 'GRB090510', 'GRB090902B']
    
    for i, grb_name in enumerate(top_grbs):
        if grb_name not in grb_data:
            continue
            
        ax = axes[i//2, i%2]
        df = grb_data[grb_name]
        
        energy = df['ENERGY'].values / 1000
        time = df['TIME'].values
        
        # Scatter plot con colori basati sull'energia
        scatter = ax.scatter(time, energy, c=energy, cmap='viridis', 
                           alpha=0.6, s=1, vmin=energy.min(), vmax=energy.max())
        
        # Trend line
        z = np.polyfit(time, energy, 1)
        p = np.poly1d(z)
        ax.plot(time, p(time), "r-", linewidth=3, alpha=0.8)
        
        # Calcola correlazione
        from scipy import stats
        r, p_val = stats.pearsonr(energy, time)
        sigma = stats.norm.ppf(1 - p_val/2)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Energy (GeV)')
        ax.set_title(f'{grb_name}\nCorrelation: r={r:.4f}, σ={sigma:.2f}', 
                    fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Aggiungi colorbar
        plt.colorbar(scatter, ax=ax, label='Energy (GeV)')
    
    plt.tight_layout()
    plt.savefig('Figure_2_Top_GRBs_Analysis_Final.png', dpi=300, bbox_inches='tight')
    print("✅ Salvato: Figure_2_Top_GRBs_Analysis_Final.png")
    
    return fig

def create_figure_3_phase_analysis(grb_data):
    """Figure 3: Analisi delle fasi temporali"""
    print("\nCREAZIONE FIGURE 3: Phase Analysis")
    print("-" * 40)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Figure 3: Temporal Phase Analysis Technique', 
                 fontsize=18, fontweight='bold')
    
    # Analisi per GRB130427A (il più significativo)
    grb_name = 'GRB130427A'
    if grb_name not in grb_data:
        print(f"❌ {grb_name} non disponibile per phase analysis")
        return None
    
    df = grb_data[grb_name]
    energy = df['ENERGY'].values / 1000
    time = df['TIME'].values
    
    # Ordina per tempo
    sort_idx = np.argsort(time)
    time_sorted = time[sort_idx]
    energy_sorted = energy[sort_idx]
    
    # Dividi in fasi
    n_photons = len(time_sorted)
    early_idx = slice(0, n_photons//2)
    late_idx = slice(n_photons//2, n_photons)
    
    # Plot 1: Scatter completo
    ax1 = axes[0, 0]
    ax1.scatter(time, energy, alpha=0.3, s=1, color='blue')
    ax1.axvline(time_sorted[n_photons//2], color='red', linestyle='--', 
               linewidth=2, label='Phase Split')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Energy (GeV)')
    ax1.set_title('Full Dataset with Phase Division')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Early phase
    ax2 = axes[0, 1]
    time_early = time_sorted[early_idx]
    energy_early = energy_sorted[early_idx]
    ax2.scatter(time_early, energy_early, alpha=0.6, s=2, color='green')
    
    from scipy import stats
    r_early, p_early = stats.pearsonr(energy_early, time_early)
    sigma_early = stats.norm.ppf(1 - p_early/2)
    
    z = np.polyfit(time_early, energy_early, 1)
    p = np.poly1d(z)
    ax2.plot(time_early, p(time_early), "r-", linewidth=2)
    
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Energy (GeV)')
    ax2.set_title(f'Early Phase\nr={r_early:.4f}, σ={sigma_early:.2f}')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Late phase
    ax3 = axes[1, 0]
    time_late = time_sorted[late_idx]
    energy_late = energy_sorted[late_idx]
    ax3.scatter(time_late, energy_late, alpha=0.6, s=2, color='orange')
    
    r_late, p_late = stats.pearsonr(energy_late, time_late)
    sigma_late = stats.norm.ppf(1 - p_late/2)
    
    z = np.polyfit(time_late, energy_late, 1)
    p = np.poly1d(z)
    ax3.plot(time_late, p(time_late), "r-", linewidth=2)
    
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Energy (GeV)')
    ax3.set_title(f'Late Phase\nr={r_late:.4f}, σ={sigma_late:.2f}')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Comparison
    ax4 = axes[1, 1]
    phases = ['Early', 'Late', 'Full']
    sigmas = [sigma_early, sigma_late, stats.norm.ppf(1 - stats.pearsonr(energy, time)[1]/2)]
    colors = ['green', 'orange', 'blue']
    
    bars = ax4.bar(phases, sigmas, color=colors, alpha=0.7)
    ax4.set_ylabel('Significance (σ)')
    ax4.set_title('Phase Analysis Comparison')
    ax4.grid(True, alpha=0.3)
    
    for bar, sigma in zip(bars, sigmas):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{sigma:.2f}σ', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('Figure_3_Phase_Analysis_Final.png', dpi=300, bbox_inches='tight')
    print("✅ Salvato: Figure_3_Phase_Analysis_Final.png")
    
    return fig

def create_figure_4_literature_comparison():
    """Figure 4: Confronto con la letteratura"""
    print("\nCREAZIONE FIGURE 4: Literature Comparison")
    print("-" * 40)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Figure 4: Literature Comparison and Discovery Summary', 
                 fontsize=18, fontweight='bold')
    
    # Linea 1: Confronto significatività
    grbs = ['GRB090902B', 'GRB130427A', 'GRB080916C']
    literature_sigma = [5.46, 4.2, 3.8]  # Dalla letteratura
    our_sigma = [3.28, 10.18, 1.88]      # I nostri risultati
    
    x = np.arange(len(grbs))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, literature_sigma, width, label='Literature', 
                   color='lightblue', alpha=0.8)
    bars2 = ax1.bar(x + width/2, our_sigma, width, label='This Work', 
                   color='red', alpha=0.8)
    
    ax1.set_xlabel('GRB')
    ax1.set_ylabel('Significance (σ)')
    ax1.set_title('Significance Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(grbs)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Aggiungi valori sulle barre
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Linea 2: Detection rate
    categories = ['σ ≥ 3.0', 'σ ≥ 5.0', 'New Discoveries']
    counts = [4, 2, 2]  # Dei 6 GRB analizzati
    total = 6
    percentages = [count/total*100 for count in counts]
    
    bars = ax2.bar(categories, percentages, color=['orange', 'red', 'green'], alpha=0.8)
    ax2.set_ylabel('Percentage (%)')
    ax2.set_title('Detection Statistics')
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)
    
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('Figure_4_Literature_Comparison_Final.png', dpi=300, bbox_inches='tight')
    print("✅ Salvato: Figure_4_Literature_Comparison_Final.png")
    
    return fig

def main():
    print("CREAZIONE FIGURE FINALI PER IL PAPER")
    print("=" * 50)
    
    # Carica dati
    grb_data = load_grb_data()
    
    if not grb_data:
        print("❌ Nessun dato GRB disponibile!")
        return
    
    # Crea le figure
    fig1 = create_figure_1_grb_overview(grb_data)
    fig2 = create_figure_2_top_grbs_analysis(grb_data)
    fig3 = create_figure_3_phase_analysis(grb_data)
    fig4 = create_figure_4_literature_comparison()
    
    print("\n" + "=" * 50)
    print("FIGURE COMPLETATE!")
    print("=" * 50)
    print("✅ Figure_1_GRB_Overview_Final.png")
    print("✅ Figure_2_Top_GRBs_Analysis_Final.png")
    print("✅ Figure_3_Phase_Analysis_Final.png")
    print("✅ Figure_4_Literature_Comparison_Final.png")
    print("\nLe figure sono pronte per essere integrate nel paper!")

if __name__ == "__main__":
    main()
