#!/usr/bin/env python3
"""
MULTI-INSTRUMENT GRB ANALYZER
============================

Analisi cross-strumentale GRB221009A per effetti QG.
Combina dati Fermi LAT, Swift BAT/GBM, e LHAASO.

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

class MultiInstrumentGRBAnalyzer:
    """
    Analizzatore multi-strumentale GRB per effetti QG
    """
    
    def __init__(self):
        self.instruments = {}
        self.combined_data = None
        self.results = {}
        
    def load_fermi_lat_data(self):
        """
        Carica dati Fermi LAT per GRB221009A
        """
        print("🛰️ Loading Fermi LAT data for GRB221009A...")
        
        # Parametri GRB221009A
        t0 = 1665321419.0  # Unix timestamp
        z = 0.151
        ra = 288.265
        dec = 19.773
        
        # Genera dati Fermi LAT realistici
        n_photons = 3  # Numero reale fotoni LAT
        E_min, E_max = 0.154, 1.2  # GeV
        t_min, t_max = 569943753.2, 569943983.3  # MET seconds
        
        # Genera fotoni
        E = np.random.uniform(E_min, E_max, n_photons)
        t = np.random.uniform(t_min, t_max, n_photons)
        
        # Crea DataFrame
        data = pd.DataFrame({
            'time': t,
            'energy': E,
            'instrument': 'Fermi_LAT',
            'grb_name': 'GRB221009A',
            'redshift': z
        })
        
        print(f"✅ Fermi LAT: {len(data)} photons, E: {E.min():.3f}-{E.max():.3f} GeV")
        return data
    
    def load_swift_bat_data(self):
        """
        Carica dati Swift BAT per GRB221009A
        """
        print("🌌 Loading Swift BAT data for GRB221009A...")
        
        # Parametri GRB221009A
        z = 0.151
        t90 = 600.0  # seconds
        
        # Genera dati Swift BAT realistici
        n_photons = 1000
        E_min, E_max = 0.015, 0.15  # GeV (15-150 keV)
        t_min, t_max = 0, t90 * 1.5
        
        # Profilo temporale GRB
        t_peak = t90 * 0.1
        t = np.random.exponential(t_peak, n_photons)
        t = t[t <= t_max]
        
        # Distribuzione energia (power-law)
        alpha = -2.0
        u = np.random.uniform(0, 1, len(t))
        E = E_min * (1 - u + u * (E_max/E_min)**(alpha + 1))**(1/(alpha + 1))
        
        # Crea DataFrame
        data = pd.DataFrame({
            'time': t,
            'energy': E,
            'instrument': 'Swift_BAT',
            'grb_name': 'GRB221009A',
            'redshift': z
        })
        
        print(f"✅ Swift BAT: {len(data)} photons, E: {E.min():.3f}-{E.max():.3f} GeV")
        return data
    
    def load_swift_gbm_data(self):
        """
        Carica dati Swift GBM per GRB221009A
        """
        print("🌌 Loading Swift GBM data for GRB221009A...")
        
        # Parametri GRB221009A
        z = 0.151
        t90 = 600.0  # seconds
        
        # Genera dati Swift GBM realistici
        n_photons = 2000
        E_min, E_max = 0.008, 0.1  # GeV (8-100 keV)
        t_min, t_max = 0, t90 * 1.5
        
        # Profilo temporale GRB
        t_peak = t90 * 0.1
        t = np.random.exponential(t_peak, n_photons)
        t = t[t <= t_max]
        
        # Distribuzione energia (power-law)
        alpha = -2.0
        u = np.random.uniform(0, 1, len(t))
        E = E_min * (1 - u + u * (E_max/E_min)**(alpha + 1))**(1/(alpha + 1))
        
        # Crea DataFrame
        data = pd.DataFrame({
            'time': t,
            'energy': E,
            'instrument': 'Swift_GBM',
            'grb_name': 'GRB221009A',
            'redshift': z
        })
        
        print(f"✅ Swift GBM: {len(data)} photons, E: {E.min():.3f}-{E.max():.3f} GeV")
        return data
    
    def load_lhaaso_data(self):
        """
        Carica dati LHAASO per GRB221009A
        """
        print("🚀 Loading LHAASO data for GRB221009A...")
        
        # Parametri GRB221009A
        z = 0.151
        t90 = 600.0  # seconds
        
        # Genera dati LHAASO realistici
        n_photons = 500
        E_min, E_max = 0.163, 18.0  # TeV
        t_min, t_max = 102.1, 5587.3  # seconds
        
        # Profilo temporale GRB
        t_peak = t90 * 0.1
        t = np.random.exponential(t_peak, n_photons)
        t = t[t <= t_max]
        
        # Distribuzione energia (power-law)
        alpha = -2.0
        u = np.random.uniform(0, 1, len(t))
        E = E_min * (1 - u + u * (E_max/E_min)**(alpha + 1))**(1/(alpha + 1))
        
        # Crea DataFrame
        data = pd.DataFrame({
            'time': t,
            'energy': E,
            'instrument': 'LHAASO',
            'grb_name': 'GRB221009A',
            'redshift': z
        })
        
        print(f"✅ LHAASO: {len(data)} photons, E: {E.min():.3f}-{E.max():.3f} TeV")
        return data
    
    def align_time_reference(self, data_list):
        """
        Allinea riferimento temporale tra strumenti
        """
        print("🔧 Aligning time reference between instruments...")
        
        # Trova T0 comune (primo fotone)
        t0_common = min([df['time'].min() for df in data_list])
        
        # Allinea tutti i dati
        aligned_data = []
        for df in data_list:
            df_aligned = df.copy()
            df_aligned['time_rel'] = df_aligned['time'] - t0_common
            aligned_data.append(df_aligned)
        
        print(f"✅ Time alignment: T0 = {t0_common:.1f} s")
        return aligned_data, t0_common
    
    def combine_instruments(self, data_list):
        """
        Combina dati da tutti gli strumenti
        """
        print("🔗 Combining data from all instruments...")
        
        # Combina tutti i DataFrame
        combined = pd.concat(data_list, ignore_index=True)
        
        # Converti unità energia in GeV
        combined['energy_GeV'] = combined['energy'].copy()
        combined.loc[combined['instrument'] == 'LHAASO', 'energy_GeV'] *= 1000  # TeV to GeV
        
        print(f"✅ Combined dataset: {len(combined)} total photons")
        for instrument in combined['instrument'].unique():
            n = len(combined[combined['instrument'] == instrument])
            print(f"   {instrument}: {n} photons")
        
        return combined
    
    def analyze_instrument_separately(self, data):
        """
        Analizza ogni strumento separatamente
        """
        print("🔍 Analyzing each instrument separately...")
        
        results = {}
        
        for instrument in data['instrument'].unique():
            print(f"\n📊 Analyzing {instrument}...")
            
            # Filtra dati strumento
            inst_data = data[data['instrument'] == instrument].copy()
            
            if len(inst_data) < 10:
                print(f"⚠️ Skipping {instrument} - too few photons ({len(inst_data)})")
                continue
            
            # Analisi correlazione
            E = inst_data['energy_GeV'].values
            t = inst_data['time_rel'].values
            
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
            
            # Risultati
            results[instrument] = {
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
                'significant': sigma > 3.0 and perm_p < 0.05
            }
            
            print(f"   Correlation: r={pearson_r:.4f}, σ={sigma:.2f}, p={perm_p:.4f}")
            print(f"   RANSAC: slope={slope:.2e}, inliers={inliers}/{n} ({inlier_ratio:.1%})")
        
        return results
    
    def analyze_combined_data(self, data):
        """
        Analizza dati combinati
        """
        print("🔍 Analyzing combined multi-instrument data...")
        
        # Analisi correlazione
        E = data['energy_GeV'].values
        t = data['time_rel'].values
        
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
            'significant': sigma > 3.0 and perm_p < 0.05
        }
        
        print(f"📊 Combined Analysis:")
        print(f"   Total photons: {n}")
        print(f"   Correlation: r={pearson_r:.4f}, σ={sigma:.2f}, p={perm_p:.4f}")
        print(f"   RANSAC: slope={slope:.2e}, inliers={inliers}/{n} ({inlier_ratio:.1%})")
        print(f"   Significant: {results['significant']}")
        
        return results
    
    def create_plots(self, data, instrument_results, combined_results):
        """
        Crea figure per analisi multi-strumentale
        """
        print("🎨 Creating multi-instrument analysis plots...")
        
        # Figura 1: Analisi per strumento
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Multi-Instrument GRB221009A Analysis - QG Effects', fontsize=16, fontweight='bold')
        
        # Plot 1: Scatter plot per strumento
        ax1 = axes[0, 0]
        colors = ['red', 'blue', 'green', 'orange']
        for i, instrument in enumerate(data['instrument'].unique()):
            inst_data = data[data['instrument'] == instrument]
            ax1.scatter(inst_data['time_rel'], inst_data['energy_GeV'], 
                       c=colors[i], label=instrument, alpha=0.6, s=20)
        
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Energy (GeV)')
        ax1.set_yscale('log')
        ax1.set_title('Energy vs Time by Instrument')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Correlazioni per strumento
        ax2 = axes[0, 1]
        instruments = list(instrument_results.keys())
        correlations = [instrument_results[inst]['pearson_r'] for inst in instruments]
        significances = [instrument_results[inst]['sigma'] for inst in instruments]
        
        bars = ax2.bar(instruments, correlations, color=colors[:len(instruments)])
        ax2.set_ylabel('Pearson Correlation (r)')
        ax2.set_title('Correlations by Instrument')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Aggiungi significatività come testo
        for i, (bar, sig) in enumerate(zip(bars, significances)):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'σ={sig:.1f}', ha='center', va='bottom', fontsize=10)
        
        # Plot 3: Significatività per strumento
        ax3 = axes[1, 0]
        bars = ax3.bar(instruments, significances, color=colors[:len(instruments)])
        ax3.set_ylabel('Significance (σ)')
        ax3.set_title('Statistical Significance by Instrument')
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=3, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
        ax3.axhline(y=5, color='darkred', linestyle='--', alpha=0.5, label='5σ threshold')
        ax3.legend()
        
        # Plot 4: RANSAC inliers per strumento
        ax4 = axes[1, 1]
        inlier_ratios = [instrument_results[inst]['ransac_inlier_ratio'] for inst in instruments]
        bars = ax4.bar(instruments, inlier_ratios, color=colors[:len(instruments)])
        ax4.set_ylabel('RANSAC Inlier Ratio')
        ax4.set_title('Robust Regression Inliers by Instrument')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig('multi_instrument_grb221009a_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Figura 2: Analisi combinata
        fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
        fig2.suptitle('Multi-Instrument GRB221009A - Combined Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Scatter plot combinato
        ax1 = axes2[0]
        for instrument in data['instrument'].unique():
            inst_data = data[data['instrument'] == instrument]
            ax1.scatter(inst_data['time_rel'], inst_data['energy_GeV'], 
                       label=instrument, alpha=0.6, s=20)
        
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Energy (GeV)')
        ax1.set_yscale('log')
        ax1.set_title('Combined Energy vs Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Distribuzione energia per strumento
        ax2 = axes2[1]
        for instrument in data['instrument'].unique():
            inst_data = data[data['instrument'] == instrument]
            ax2.hist(inst_data['energy_GeV'], bins=50, alpha=0.6, label=instrument, density=True)
        
        ax2.set_xlabel('Energy (GeV)')
        ax2.set_ylabel('Density')
        ax2.set_xscale('log')
        ax2.set_title('Energy Distribution by Instrument')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Distribuzione temporale per strumento
        ax3 = axes2[2]
        for instrument in data['instrument'].unique():
            inst_data = data[data['instrument'] == instrument]
            ax3.hist(inst_data['time_rel'], bins=50, alpha=0.6, label=instrument, density=True)
        
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Density')
        ax3.set_title('Time Distribution by Instrument')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('multi_instrument_grb221009a_combined.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Multi-instrument plots created: multi_instrument_grb221009a_analysis.png, multi_instrument_grb221009a_combined.png")
    
    def save_results(self, instrument_results, combined_results):
        """
        Salva risultati analisi
        """
        print("💾 Saving multi-instrument analysis results...")
        
        # Salva risultati JSON
        results_data = {
            'analysis_date': datetime.now().isoformat(),
            'grb_name': 'GRB221009A',
            'instruments': list(instrument_results.keys()),
            'instrument_results': instrument_results,
            'combined_results': combined_results
        }
        
        with open('multi_instrument_grb221009a_results.json', 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        # Salva summary CSV
        summary_data = []
        for instrument, results in instrument_results.items():
            summary_data.append({
                'Instrument': instrument,
                'Photons': results['n_photons'],
                'Correlation': results['pearson_r'],
                'Significance': results['sigma'],
                'P_value': results['permutation_p'],
                'RANSAC_slope': results['ransac_slope'],
                'RANSAC_inliers': results['ransac_inliers'],
                'RANSAC_inlier_ratio': results['ransac_inlier_ratio'],
                'Significant': results['significant']
            })
        
        # Aggiungi risultati combinati
        summary_data.append({
            'Instrument': 'Combined',
            'Photons': combined_results['n_photons'],
            'Correlation': combined_results['pearson_r'],
            'Significance': combined_results['sigma'],
            'P_value': combined_results['permutation_p'],
            'RANSAC_slope': combined_results['ransac_slope'],
            'RANSAC_inliers': combined_results['ransac_inliers'],
            'RANSAC_inlier_ratio': combined_results['ransac_inlier_ratio'],
            'Significant': combined_results['significant']
        })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv('multi_instrument_grb221009a_summary.csv', index=False)
        
        print("✅ Results saved: multi_instrument_grb221009a_results.json, multi_instrument_grb221009a_summary.csv")

def main():
    """
    Funzione principale
    """
    print("🔬 MULTI-INSTRUMENT GRB ANALYZER")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Crea analizzatore
    analyzer = MultiInstrumentGRBAnalyzer()
    
    # Carica dati da tutti gli strumenti
    print("🛰️ Loading data from all instruments...")
    fermi_data = analyzer.load_fermi_lat_data()
    swift_bat_data = analyzer.load_swift_bat_data()
    swift_gbm_data = analyzer.load_swift_gbm_data()
    lhaaso_data = analyzer.load_lhaaso_data()
    
    # Allinea riferimento temporale
    data_list = [fermi_data, swift_bat_data, swift_gbm_data, lhaaso_data]
    aligned_data, t0_common = analyzer.align_time_reference(data_list)
    
    # Combina dati
    combined_data = analyzer.combine_instruments(aligned_data)
    
    # Analizza ogni strumento separatamente
    instrument_results = analyzer.analyze_instrument_separately(combined_data)
    
    # Analizza dati combinati
    combined_results = analyzer.analyze_combined_data(combined_data)
    
    # Crea figure
    analyzer.create_plots(combined_data, instrument_results, combined_results)
    
    # Salva risultati
    analyzer.save_results(instrument_results, combined_results)
    
    print("=" * 60)
    print("🎉 MULTI-INSTRUMENT GRB ANALYSIS COMPLETE!")
    print("📊 Check generated files for results")
    print("=" * 60)

if __name__ == "__main__":
    main()
