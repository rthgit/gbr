#!/usr/bin/env python3
"""
VALIDAZIONE ROBUSTA 10.18σ GRB130427A
Permutation test rigoroso per il segnale più forte
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from tqdm import tqdm
import json
from pathlib import Path

def load_grb130427a_data():
    """Carica i dati di GRB130427A"""
    print("CARICAMENTO DATI GRB130427A")
    print("-" * 40)
    
    # Cerca il file CSV corretto
    csv_files = list(Path('.').glob('**/*GRB130427A*.csv'))
    
    if not csv_files:
        print("❌ File GRB130427A non trovato!")
        return None
    
    csv_file = csv_files[0]
    print(f"📁 Caricando: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Caricati {len(df)} fotoni")
        
        if 'ENERGY' not in df.columns or 'TIME' not in df.columns:
            print("❌ Colonne ENERGY/TIME non trovate!")
            return None
        
        energy = df['ENERGY'].values / 1000  # Converti in GeV
        time = df['TIME'].values
        
        print(f"📊 Energia: {energy.min():.3f} - {energy.max():.3f} GeV")
        print(f"📊 Tempo: {time.min():.0f} - {time.max():.0f} s")
        
        return df, energy, time
        
    except Exception as e:
        print(f"❌ Errore caricamento: {e}")
        return None

def permutation_test(energy, time, n_perm=100000):
    """Permutation test rigoroso"""
    print(f"\nPERMUTATION TEST ({n_perm:,} permutazioni)")
    print("-" * 40)
    
    # Correlazione osservata
    r_obs, p_obs = stats.pearsonr(energy, time)
    print(f"📊 Correlazione osservata: r = {r_obs:.6f}")
    print(f"📊 P-value osservato: p = {p_obs:.2e}")
    
    # Permutation test
    print("🔄 Eseguendo permutazioni...")
    r_perm = np.zeros(n_perm)
    
    for i in tqdm(range(n_perm)):
        time_shuffled = np.random.permutation(time)
        r_perm[i], _ = stats.pearsonr(energy, time_shuffled)
    
    # Calcola p-value empirico
    p_empirical = np.sum(np.abs(r_perm) >= np.abs(r_obs)) / n_perm
    
    # Calcola significatività
    if p_empirical == 0:
        sigma_empirical = stats.norm.ppf(1 - 1/(2*n_perm))
        print(f"🎯 σ > {sigma_empirical:.2f} (nessuna permutazione ha superato)")
    else:
        sigma_empirical = stats.norm.ppf(1 - p_empirical/2)
        print(f"🎯 σ = {sigma_empirical:.2f}")
    
    print(f"📊 P-value empirico: {p_empirical:.2e}")
    
    return r_obs, p_obs, r_perm, p_empirical, sigma_empirical

def bootstrap_analysis(energy, time, n_bootstrap=10000):
    """Bootstrap analysis per intervalli di confidenza"""
    print(f"\nBOOTSTRAP ANALYSIS ({n_bootstrap:,} campioni)")
    print("-" * 40)
    
    r_bootstrap = np.zeros(n_bootstrap)
    n_samples = len(energy)
    
    print("🔄 Eseguendo bootstrap...")
    for i in tqdm(range(n_bootstrap)):
        # Resample con replacement
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        energy_boot = energy[indices]
        time_boot = time[indices]
        
        r_bootstrap[i], _ = stats.pearsonr(energy_boot, time_boot)
    
    # Calcola intervalli di confidenza
    ci_95 = np.percentile(r_bootstrap, [2.5, 97.5])
    ci_99 = np.percentile(r_bootstrap, [0.5, 99.5])
    
    print(f"📊 Bootstrap mean: {np.mean(r_bootstrap):.6f}")
    print(f"📊 Bootstrap std: {np.std(r_bootstrap):.6f}")
    print(f"📊 95% CI: [{ci_95[0]:.6f}, {ci_95[1]:.6f}]")
    print(f"📊 99% CI: [{ci_99[0]:.6f}, {ci_99[1]:.6f}]")
    
    return r_bootstrap, ci_95, ci_99

def phase_analysis(energy, time):
    """Analisi delle fasi temporali"""
    print("\nPHASE ANALYSIS")
    print("-" * 40)
    
    # Ordina per tempo
    sort_idx = np.argsort(time)
    time_sorted = time[sort_idx]
    energy_sorted = energy[sort_idx]
    
    # Dividi in fasi
    n_photons = len(time_sorted)
    early_idx = slice(0, n_photons//2)
    late_idx = slice(n_photons//2, n_photons)
    
    # Early phase
    energy_early = energy_sorted[early_idx]
    time_early = time_sorted[early_idx]
    r_early, p_early = stats.pearsonr(energy_early, time_early)
    sigma_early = stats.norm.ppf(1 - p_early/2)
    
    # Late phase
    energy_late = energy_sorted[late_idx]
    time_late = time_sorted[late_idx]
    r_late, p_late = stats.pearsonr(energy_late, time_late)
    sigma_late = stats.norm.ppf(1 - p_late/2)
    
    print(f"📊 Early phase: r = {r_early:.6f}, σ = {sigma_early:.2f}")
    print(f"📊 Late phase: r = {r_late:.6f}, σ = {sigma_late:.2f}")
    
    return {
        'early': {'r': r_early, 'p': p_early, 'sigma': sigma_early},
        'late': {'r': r_late, 'p': p_late, 'sigma': sigma_late}
    }

def create_validation_plots(energy, time, r_obs, r_perm, r_bootstrap, phase_results):
    """Crea i grafici di validazione"""
    print("\nCREAZIONE GRAFICI")
    print("-" * 40)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('GRB130427A - Validazione Segnale 10.18σ', fontsize=16, fontweight='bold')
    
    # Plot 1: Energy vs Time scatter
    ax1 = axes[0, 0]
    ax1.scatter(time, energy, alpha=0.3, s=1, color='blue')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Energy (GeV)')
    ax1.set_title(f'Energy vs Time (r = {r_obs:.4f})')
    ax1.grid(True, alpha=0.3)
    
    # Aggiungi trend line
    z = np.polyfit(time, energy, 1)
    p = np.poly1d(z)
    ax1.plot(time, p(time), "r--", alpha=0.8, linewidth=2)
    
    # Plot 2: Permutation distribution
    ax2 = axes[0, 1]
    ax2.hist(r_perm, bins=100, alpha=0.7, color='gray', density=True)
    ax2.axvline(r_obs, color='red', linestyle='--', linewidth=2, label=f'Observed: {r_obs:.4f}')
    ax2.axvline(-r_obs, color='red', linestyle='--', linewidth=2, alpha=0.5)
    ax2.set_xlabel('Correlation Coefficient')
    ax2.set_ylabel('Density')
    ax2.set_title('Permutation Test Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Bootstrap distribution
    ax3 = axes[1, 0]
    ax3.hist(r_bootstrap, bins=100, alpha=0.7, color='green', density=True)
    ax3.axvline(r_obs, color='red', linestyle='--', linewidth=2, label=f'Observed: {r_obs:.4f}')
    ci_95 = np.percentile(r_bootstrap, [2.5, 97.5])
    ax3.axvline(ci_95[0], color='orange', linestyle=':', alpha=0.7)
    ax3.axvline(ci_95[1], color='orange', linestyle=':', alpha=0.7)
    ax3.set_xlabel('Correlation Coefficient')
    ax3.set_ylabel('Density')
    ax3.set_title('Bootstrap Distribution (95% CI)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Phase comparison
    ax4 = axes[1, 1]
    phases = ['Early', 'Late']
    sigmas = [phase_results['early']['sigma'], phase_results['late']['sigma']]
    colors = ['blue', 'red']
    
    bars = ax4.bar(phases, sigmas, color=colors, alpha=0.7)
    ax4.set_ylabel('Significance (σ)')
    ax4.set_title('Phase Analysis Comparison')
    ax4.grid(True, alpha=0.3)
    
    # Aggiungi valori sulle barre
    for bar, sigma in zip(bars, sigmas):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{sigma:.2f}σ', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('GRB130427A_10sigma_validation.png', dpi=300, bbox_inches='tight')
    print("✅ Salvato: GRB130427A_10sigma_validation.png")
    
    return fig

def main():
    print("VALIDAZIONE ROBUSTA 10.18σ GRB130427A")
    print("=" * 50)
    
    # Carica dati
    data = load_grb130427a_data()
    if data is None:
        return
    
    df, energy, time = data
    
    # Permutation test
    r_obs, p_obs, r_perm, p_empirical, sigma_empirical = permutation_test(energy, time)
    
    # Bootstrap analysis
    r_bootstrap, ci_95, ci_99 = bootstrap_analysis(energy, time)
    
    # Phase analysis
    phase_results = phase_analysis(energy, time)
    
    # Crea grafici
    fig = create_validation_plots(energy, time, r_obs, r_perm, r_bootstrap, phase_results)
    
    # Salva risultati
    results = {
        'grb': 'GRB130427A',
        'n_photons': len(energy),
        'energy_range': [float(energy.min()), float(energy.max())],
        'time_range': [float(time.min()), float(time.max())],
        'observed_correlation': float(r_obs),
        'observed_pvalue': float(p_obs),
        'empirical_pvalue': float(p_empirical),
        'empirical_sigma': float(sigma_empirical),
        'bootstrap_mean': float(np.mean(r_bootstrap)),
        'bootstrap_std': float(np.std(r_bootstrap)),
        'bootstrap_ci_95': [float(ci_95[0]), float(ci_95[1])],
        'bootstrap_ci_99': [float(ci_99[0]), float(ci_99[1])],
        'phase_analysis': phase_results,
        'validation_status': 'VALIDATED' if sigma_empirical > 5.0 else 'MARGINAL'
    }
    
    with open('GRB130427A_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 50)
    print("RISULTATI VALIDAZIONE:")
    print("=" * 50)
    print(f"🎯 Segnale osservato: {r_obs:.6f}")
    print(f"🎯 Significatività empirica: {sigma_empirical:.2f}σ")
    print(f"🎯 P-value empirico: {p_empirical:.2e}")
    print(f"🎯 Status: {results['validation_status']}")
    print(f"📁 Risultati salvati: GRB130427A_validation_results.json")
    print(f"📁 Grafici salvati: GRB130427A_10sigma_validation.png")

if __name__ == "__main__":
    main()

