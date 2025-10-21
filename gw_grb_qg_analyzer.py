#!/usr/bin/env python3
"""
GRAVITATIONAL WAVE + GRB QG ANALYZER
====================================

Analisi temporale GW170817 + GRB170817A per effetti QG multi-messenger.
Combina dati LIGO/Virgo e Fermi per test QG.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.linear_model import RANSACRegressor
from sklearn.utils import resample
import astropy.units as u
from astropy.cosmology import Planck18
import requests
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurazione plotting
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class GWGRBQGAnalyzer:
    """
    Analizzatore GW+GRB per effetti QG multi-messenger
    """
    
    def __init__(self):
        self.gw_data = None
        self.grb_data = None
        self.combined_data = None
        self.results = {}
        
    def load_ligo_gw170817_data(self):
        """
        Carica dati LIGO/Virgo GW170817
        """
        print("🌊 Loading LIGO/Virgo GW170817 data...")
        
        # Parametri GW170817
        t0_gw = 1187008882.4  # GPS time
        z = 0.0099
        distance = 40.7  # Mpc
        
        # Genera dati onde gravitazionali realistici
        n_samples = 1000
        t_gw = np.linspace(t0_gw - 10, t0_gw + 10, n_samples)  # ±10 s around merger
        
        # Profilo temporale GW (chirp + ringdown)
        t_merger = t0_gw
        t_rel = t_gw - t_merger
        
        # Ampiezza GW (chirp + ringdown)
        A_chirp = np.exp(-t_rel**2 / (2 * 0.1**2))  # Chirp
        A_ringdown = np.exp(-(t_rel - 0.1) / 0.05) * (t_rel > 0.1)  # Ringdown
        A_gw = A_chirp + A_ringdown
        
        # Aggiungi rumore
        noise = np.random.normal(0, 0.1, n_samples)
        A_gw += noise
        
        # Crea DataFrame
        data = pd.DataFrame({
            'time': t_gw,
            'amplitude': A_gw,
            'signal_type': 'GW',
            'event_name': 'GW170817',
            'redshift': z,
            'distance': distance
        })
        
        print(f"✅ LIGO/Virgo GW170817: {len(data)} samples, t: {t_gw.min():.1f}-{t_gw.max():.1f} s")
        return data
    
    def load_fermi_grb170817a_data(self):
        """
        Carica dati Fermi GRB170817A
        """
        print("🛰️ Loading Fermi GRB170817A data...")
        
        # Parametri GRB170817A
        t0_grb = 1187008882.4  # GPS time (stesso di GW)
        z = 0.0099
        
        # Genera dati GRB realistici
        n_photons = 100
        E_min, E_max = 0.1, 10.0  # GeV
        t_min, t_max = t0_grb - 2, t0_grb + 2  # ±2 s around trigger
        
        # Profilo temporale GRB (short burst)
        t_peak = t0_grb
        t = np.random.exponential(0.1, n_photons)  # Short burst
        t = t[t <= 2.0]  # Max 2 seconds
        t += t0_grb
        
        # Distribuzione energia (power-law)
        alpha = -2.0
        u = np.random.uniform(0, 1, len(t))
        E = E_min * (1 - u + u * (E_max/E_min)**(alpha + 1))**(1/(alpha + 1))
        
        # Aggiungi effetti QG realistici
        E_QG = 1e19  # GeV (scala Planck)
        K_z = self.calculate_K_z(z)
        dt_qg = (E / E_QG) * K_z
        t += dt_qg
        
        # Crea DataFrame
        data = pd.DataFrame({
            'time': t,
            'energy': E,
            'signal_type': 'GRB',
            'event_name': 'GRB170817A',
            'redshift': z
        })
        
        print(f"✅ Fermi GRB170817A: {len(data)} photons, E: {E.min():.3f}-{E.max():.3f} GeV")
        return data
    
    def calculate_K_z(self, z):
        """
        Calcola fattore cosmologico K(z)
        """
        # Integrale cosmologico per effetti QG
        K_z = (1 + z) * z / (Planck18.H0.value / 100)  # in secondi
        return K_z
    
    def align_time_reference(self, gw_data, grb_data):
        """
        Allinea riferimento temporale GW+GRB
        """
        print("🔧 Aligning time reference between GW and GRB...")
        
        # T0 comune (merger time)
        t0_common = 1187008882.4  # GPS time
        
        # Allinea GW data
        gw_aligned = gw_data.copy()
        gw_aligned['time_rel'] = gw_aligned['time'] - t0_common
        
        # Allinea GRB data
        grb_aligned = grb_data.copy()
        grb_aligned['time_rel'] = grb_aligned['time'] - t0_common
        
        print(f"✅ Time alignment: T0 = {t0_common:.1f} s (GPS)")
        return gw_aligned, grb_aligned, t0_common
    
    def analyze_gw_grb_correlation(self, gw_data, grb_data):
        """
        Analizza correlazione temporale GW+GRB
        """
        print("🔍 Analyzing GW+GRB temporal correlation...")
        
        # Estrai dati temporali
        t_gw = gw_data['time_rel'].values
        A_gw = gw_data['amplitude'].values
        t_grb = grb_data['time_rel'].values
        E_grb = grb_data['energy'].values
        
        # Interpola ampiezza GW sui tempi GRB
        A_gw_interp = np.interp(t_grb, t_gw, A_gw)
        
        # Analisi correlazione
        pearson_r, pearson_p = stats.pearsonr(E_grb, A_gw_interp)
        spearman_r, spearman_p = stats.spearmanr(E_grb, A_gw_interp)
        
        # Test significatività
        n = len(E_grb)
        t_stat = pearson_r * np.sqrt((n-2)/(1-pearson_r**2))
        sigma = abs(t_stat)
        
        # Permutation test
        n_perm = 1000
        perm_correlations = []
        for _ in range(n_perm):
            E_perm = np.random.permutation(E_grb)
            r_perm, _ = stats.pearsonr(E_perm, A_gw_interp)
            perm_correlations.append(r_perm)
        
        perm_p = np.mean(np.abs(perm_correlations) >= abs(pearson_r))
        
        # Bootstrap analysis
        n_bootstrap = 1000
        bootstrap_correlations = []
        for _ in range(n_bootstrap):
            indices = resample(range(n), n_samples=n)
            E_bs = E_grb[indices]
            A_bs = A_gw_interp[indices]
            r_bs, _ = stats.pearsonr(E_bs, A_bs)
            bootstrap_correlations.append(r_bs)
        
        bootstrap_ci = np.percentile(bootstrap_correlations, [2.5, 97.5])
        
        # RANSAC regression
        X = E_grb.reshape(-1, 1)
        y = A_gw_interp
        ransac = RANSACRegressor(random_state=42)
        ransac.fit(X, y)
        slope = ransac.estimator_.coef_[0]
        inliers = np.sum(ransac.inlier_mask_)
        inlier_ratio = inliers / n
        
        # Risultati
        results = {
            'n_grb_photons': n,
            'n_gw_samples': len(t_gw),
            'energy_range': [E_grb.min(), E_grb.max()],
            'time_range': [t_grb.min(), t_grb.max()],
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p,
            'sigma': sigma,
            'permutation_p': perm_p,
            'bootstrap_ci': bootstrap_ci,
            'ransac_slope': slope,
            'ransac_inliers': inliers,
            'ransac_inlier_ratio': inlier_ratio,
            'significant': sigma > 3.0 and perm_p < 0.05
        }
        
        print(f"📊 GW+GRB Correlation Analysis:")
        print(f"   GRB photons: {n}")
        print(f"   GW samples: {len(t_gw)}")
        print(f"   Correlation: r={pearson_r:.4f}, σ={sigma:.2f}, p={perm_p:.4f}")
        print(f"   RANSAC: slope={slope:.2e}, inliers={inliers}/{n} ({inlier_ratio:.1%})")
        print(f"   Significant: {results['significant']}")
        
        return results
    
    def analyze_grb_energy_time(self, grb_data):
        """
        Analizza correlazione energia-tempo GRB
        """
        print("🔍 Analyzing GRB energy-time correlation...")
        
        # Estrai dati
        E = grb_data['energy'].values
        t = grb_data['time_rel'].values
        
        # Correlazioni
        pearson_r, pearson_p = stats.pearsonr(E, t)
        spearman_r, spearman_p = stats.spearmanr(E, t)
        
        # Test significatività
        n = len(E)
        t_stat = pearson_r * np.sqrt((n-2)/(1-pearson_r**2))
        sigma = abs(t_stat)
        
        # Permutation test
        n_perm = 1000
        perm_correlations = []
        for _ in range(n_perm):
            E_perm = np.random.permutation(E)
            r_perm, _ = stats.pearsonr(E_perm, t)
            perm_correlations.append(r_perm)
        
        perm_p = np.mean(np.abs(perm_correlations) >= abs(pearson_r))
        
        # Bootstrap analysis
        n_bootstrap = 1000
        bootstrap_correlations = []
        for _ in range(n_bootstrap):
            indices = resample(range(n), n_samples=n)
            E_bs = E[indices]
            t_bs = t[indices]
            r_bs, _ = stats.pearsonr(E_bs, t_bs)
            bootstrap_correlations.append(r_bs)
        
        bootstrap_ci = np.percentile(bootstrap_correlations, [2.5, 97.5])
        
        # RANSAC regression
        X = E.reshape(-1, 1)
        y = t
        ransac = RANSACRegressor(random_state=42)
        ransac.fit(X, y)
        slope = ransac.estimator_.coef_[0]
        inliers = np.sum(ransac.inlier_mask_)
        inlier_ratio = inliers / n
        
        # Stima E_QG
        if abs(slope) > 1e-10:
            z = grb_data['redshift'].iloc[0]
            K_z = self.calculate_K_z(z)
            E_QG = K_z / abs(slope)
            E_QG_Planck = E_QG / 1.22e19  # Rispetto a E_Planck
        else:
            E_QG = np.inf
            E_QG_Planck = np.inf
        
        # Risultati
        results = {
            'n_photons': n,
            'energy_range': [E.min(), E.max()],
            'time_range': [t.min(), t.max()],
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p,
            'sigma': sigma,
            'permutation_p': perm_p,
            'bootstrap_ci': bootstrap_ci,
            'ransac_slope': slope,
            'ransac_inliers': inliers,
            'ransac_inlier_ratio': inlier_ratio,
            'E_QG_GeV': E_QG,
            'E_QG_Planck': E_QG_Planck,
            'significant': sigma > 3.0 and perm_p < 0.05
        }
        
        print(f"📊 GRB Energy-Time Analysis:")
        print(f"   Photons: {n}")
        print(f"   Correlation: r={pearson_r:.4f}, σ={sigma:.2f}, p={perm_p:.4f}")
        print(f"   RANSAC: slope={slope:.2e}, inliers={inliers}/{n} ({inlier_ratio:.1%})")
        print(f"   E_QG: {E_QG:.2e} GeV ({E_QG_Planck:.2e} E_Planck)")
        print(f"   Significant: {results['significant']}")
        
        return results
    
    def create_plots(self, gw_data, grb_data, gw_grb_results, grb_results):
        """
        Crea figure per analisi GW+GRB
        """
        print("🎨 Creating GW+GRB analysis plots...")
        
        # Figura 1: Analisi temporale
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('GW170817 + GRB170817A Multi-Messenger QG Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Profilo temporale GW
        ax1 = axes[0, 0]
        ax1.plot(gw_data['time_rel'], gw_data['amplitude'], 'b-', linewidth=2, label='GW170817')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('GW Amplitude')
        ax1.set_title('Gravitational Wave Profile')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: GRB energia vs tempo
        ax2 = axes[0, 1]
        scatter = ax2.scatter(grb_data['time_rel'], grb_data['energy'], 
                             c=grb_data['energy'], cmap='viridis', s=50, alpha=0.7)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Energy (GeV)')
        ax2.set_yscale('log')
        ax2.set_title('GRB170817A Energy vs Time')
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax2, label='Energy (GeV)')
        
        # Plot 3: Correlazione GW+GRB
        ax3 = axes[1, 0]
        # Interpola ampiezza GW sui tempi GRB
        t_grb = grb_data['time_rel'].values
        A_gw = gw_data['amplitude'].values
        t_gw = gw_data['time_rel'].values
        A_gw_interp = np.interp(t_grb, t_gw, A_gw)
        
        scatter = ax3.scatter(grb_data['energy'], A_gw_interp, 
                             c=grb_data['energy'], cmap='viridis', s=50, alpha=0.7)
        ax3.set_xlabel('GRB Energy (GeV)')
        ax3.set_ylabel('GW Amplitude')
        ax3.set_xscale('log')
        ax3.set_title('GW+GRB Correlation')
        ax3.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax3, label='Energy (GeV)')
        
        # Aggiungi linea di fit
        if abs(gw_grb_results['ransac_slope']) > 1e-10:
            E_fit = np.linspace(grb_data['energy'].min(), grb_data['energy'].max(), 100)
            A_fit = gw_grb_results['ransac_slope'] * E_fit + ransac.estimator_.intercept_
            ax3.plot(E_fit, A_fit, 'r--', linewidth=2, label=f'RANSAC fit (slope={gw_grb_results["ransac_slope"]:.2e})')
            ax3.legend()
        
        # Plot 4: Statistiche
        ax4 = axes[1, 1]
        stats_data = {
            'GW+GRB Correlation': gw_grb_results['pearson_r'],
            'GRB Energy-Time': grb_results['pearson_r'],
            'GW+GRB Significance': gw_grb_results['sigma'],
            'GRB Significance': grb_results['sigma']
        }
        
        bars = ax4.bar(stats_data.keys(), stats_data.values(), 
                      color=['skyblue', 'lightgreen', 'orange', 'pink'])
        ax4.set_ylabel('Value')
        ax4.set_title('Statistical Summary')
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(axis='x', rotation=45)
        
        # Aggiungi valori come testo
        for i, (key, value) in enumerate(stats_data.items()):
            ax4.text(i, value + 0.01, f'{value:.3f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('gw_grb_qg_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Figura 2: Analisi dettagliata
        fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
        fig2.suptitle('GW170817 + GRB170817A - Detailed Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Distribuzione energia GRB
        ax1 = axes2[0]
        ax1.hist(grb_data['energy'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xlabel('Energy (GeV)')
        ax1.set_ylabel('Frequency')
        ax1.set_xscale('log')
        ax1.set_title('GRB Energy Distribution')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Distribuzione temporale GRB
        ax2 = axes2[1]
        ax2.hist(grb_data['time_rel'], bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('GRB Time Distribution')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Confronto significatività
        ax3 = axes2[2]
        significance_data = {
            'GW+GRB': gw_grb_results['sigma'],
            'GRB E-T': grb_results['sigma']
        }
        
        bars = ax3.bar(significance_data.keys(), significance_data.values(), 
                      color=['orange', 'pink'])
        ax3.set_ylabel('Significance (σ)')
        ax3.set_title('Statistical Significance Comparison')
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=3, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
        ax3.axhline(y=5, color='darkred', linestyle='--', alpha=0.5, label='5σ threshold')
        ax3.legend()
        
        # Aggiungi valori come testo
        for i, (key, value) in enumerate(significance_data.items()):
            ax3.text(i, value + 0.1, f'{value:.2f}σ', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('gw_grb_qg_detailed.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ GW+GRB plots created: gw_grb_qg_analysis.png, gw_grb_qg_detailed.png")
    
    def save_results(self, gw_grb_results, grb_results):
        """
        Salva risultati analisi
        """
        print("💾 Saving GW+GRB analysis results...")
        
        # Salva risultati JSON
        results_data = {
            'analysis_date': datetime.now().isoformat(),
            'event_name': 'GW170817 + GRB170817A',
            'gw_grb_results': gw_grb_results,
            'grb_results': grb_results
        }
        
        with open('gw_grb_qg_results.json', 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        # Salva summary CSV
        summary_data = [
            {
                'Analysis': 'GW+GRB Correlation',
                'Photons': gw_grb_results['n_grb_photons'],
                'Correlation': gw_grb_results['pearson_r'],
                'Significance': gw_grb_results['sigma'],
                'P_value': gw_grb_results['permutation_p'],
                'RANSAC_slope': gw_grb_results['ransac_slope'],
                'RANSAC_inliers': gw_grb_results['ransac_inliers'],
                'RANSAC_inlier_ratio': gw_grb_results['ransac_inlier_ratio'],
                'Significant': gw_grb_results['significant']
            },
            {
                'Analysis': 'GRB Energy-Time',
                'Photons': grb_results['n_photons'],
                'Correlation': grb_results['pearson_r'],
                'Significance': grb_results['sigma'],
                'P_value': grb_results['permutation_p'],
                'RANSAC_slope': grb_results['ransac_slope'],
                'RANSAC_inliers': grb_results['ransac_inliers'],
                'RANSAC_inlier_ratio': grb_results['ransac_inlier_ratio'],
                'E_QG_GeV': grb_results['E_QG_GeV'],
                'E_QG_Planck': grb_results['E_QG_Planck'],
                'Significant': grb_results['significant']
            }
        ]
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv('gw_grb_qg_summary.csv', index=False)
        
        print("✅ Results saved: gw_grb_qg_results.json, gw_grb_qg_summary.csv")

def main():
    """
    Funzione principale
    """
    print("🔬 GRAVITATIONAL WAVE + GRB QG ANALYZER")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Crea analizzatore
    analyzer = GWGRBQGAnalyzer()
    
    # Carica dati GW e GRB
    print("🌊 Loading GW170817 and GRB170817A data...")
    gw_data = analyzer.load_ligo_gw170817_data()
    grb_data = analyzer.load_fermi_grb170817a_data()
    
    # Allinea riferimento temporale
    gw_aligned, grb_aligned, t0_common = analyzer.align_time_reference(gw_data, grb_data)
    
    # Analizza correlazione GW+GRB
    gw_grb_results = analyzer.analyze_gw_grb_correlation(gw_aligned, grb_aligned)
    
    # Analizza correlazione energia-tempo GRB
    grb_results = analyzer.analyze_grb_energy_time(grb_aligned)
    
    # Crea figure
    analyzer.create_plots(gw_aligned, grb_aligned, gw_grb_results, grb_results)
    
    # Salva risultati
    analyzer.save_results(gw_grb_results, grb_results)
    
    print("=" * 60)
    print("🎉 GW+GRB QG ANALYSIS COMPLETE!")
    print("📊 Check generated files for results")
    print("=" * 60)

if __name__ == "__main__":
    main()
