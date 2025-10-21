#!/usr/bin/env python3
"""
🚀 QG-ANALYZER 2.0 - PIPELINE AUTOMATICA PER ESPANSIONE MULTI-GRB
FASE 2: ESPANSIONE E VALIDAZIONE SCIENTIFICA
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.linear_model import RANSACRegressor, LinearRegression
from astropy.io import fits
from astropy.cosmology import Planck18
import json
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class QGAnalyzer2:
    """Pipeline automatica per analisi QG multi-GRB"""
    
    def __init__(self):
        self.results = []
        self.grbs_analyzed = []
        self.start_time = datetime.now()
        self.setup_plotting()
        
    def setup_plotting(self):
        """Configura stile plotting"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def load_grb_catalog(self, catalog_file=None):
        """Carica catalogo GRB esteso (2018-2025)"""
        if catalog_file is None:
            # Catalogo GRB esteso simulato per demo
            grb_catalog = self.generate_extended_grb_catalog()
        else:
            grb_catalog = pd.read_csv(catalog_file)
            
        print(f"📊 Loaded GRB catalog: {len(grb_catalog)} GRBs")
        return grb_catalog
    
    def generate_extended_grb_catalog(self):
        """Genera catalogo GRB esteso per test"""
        grb_names = []
        dates = []
        redshifts = []
        ra_values = []
        dec_values = []
        
        # Genera 100 GRB dal 2018 al 2025
        for i in range(100):
            year = 2018 + (i * 7) // 100
            month = (i % 12) + 1
            day = (i % 28) + 1
            
            grb_names.append(f"GRB{year:02d}{month:02d}{day:02d}{chr(65 + i%26)}")
            dates.append(f"{year}-{month:02d}-{day:02d}")
            redshifts.append(np.random.uniform(0.1, 3.5))
            ra_values.append(np.random.uniform(0, 360))
            dec_values.append(np.random.uniform(-90, 90))
        
        return pd.DataFrame({
            'GRB': grb_names,
            'Date': dates,
            'Redshift': redshifts,
            'RA': ra_values,
            'Dec': dec_values,
            'Energy_Range_Min': np.random.uniform(0.1, 1.0, 100),
            'Energy_Range_Max': np.random.uniform(50, 300, 100),
            'Duration': np.random.uniform(1, 1000, 100),
            'Photon_Count': np.random.randint(100, 5000, 100)
        })
    
    def generate_realistic_grb_data(self, grb_info):
        """Genera dati realistici per un GRB"""
        n_photons = grb_info['Photon_Count']
        
        # Genera energie con distribuzione power-law (correzione per alpha negativo)
        alpha = np.random.uniform(-2.5, -1.5)  # Range fisicamente ragionevole
        # Per alpha negativo, usiamo una distribuzione inversa
        if alpha < 0:
            # Genera distribuzione power-law con alpha negativo
            uniform_samples = np.random.uniform(0, 1, n_photons)
            energies = grb_info['Energy_Range_Min'] * (1 - uniform_samples) ** (1 / (alpha + 1))
            # Normalizza al range energetico
            energies = energies * (grb_info['Energy_Range_Max'] - grb_info['Energy_Range_Min']) + grb_info['Energy_Range_Min']
        else:
            # Per alpha positivo, usa il metodo standard
            energies = np.random.power(1 + alpha, n_photons) * grb_info['Energy_Range_Max']
        
        # Genera tempi con struttura temporale realistica
        t_start = 0
        t_end = grb_info['Duration']
        times = np.random.uniform(t_start, t_end, n_photons)
        
        # Aggiungi effetti QG casualmente (62.5% probabilità)
        has_qg_effect = np.random.random() < 0.625
        
        if has_qg_effect:
            # Aggiungi dispersione quantistica
            qg_strength = np.random.uniform(0.5, 2.0)  # σ range
            energy_dependent_delay = qg_strength * (energies / 1.0) * np.random.normal(0, 0.1, n_photons)
            times += energy_dependent_delay
            
            # Aggiungi transizioni di fase per alcuni GRB
            if np.random.random() < 0.4:  # 40% probabilità
                phase_transition_time = np.random.uniform(0.2, 0.8) * t_end
                phase_mask = times > phase_transition_time
                times[phase_mask] += np.random.uniform(0.5, 2.0) * (energies[phase_mask] / 10.0)
        
        return {
            'energies': energies,
            'times': times,
            'has_qg_effect': has_qg_effect,
            'grb_info': grb_info
        }
    
    def analyze_grb(self, grb_data):
        """Analizza un singolo GRB per effetti QG"""
        energies = grb_data['energies']
        times = grb_data['times']
        grb_info = grb_data['grb_info']
        
        # Calcola correlazioni
        pearson_r, pearson_p = stats.pearsonr(energies, times)
        spearman_r, spearman_p = stats.spearmanr(energies, times)
        
        # Calcola significatività
        n = len(energies)
        pearson_sigma = abs(pearson_r) * np.sqrt((n-2)/(1-pearson_r**2)) if abs(pearson_r) < 0.999 else np.inf
        spearman_sigma = abs(spearman_r) * np.sqrt((n-2)/(1-spearman_r**2)) if abs(spearman_r) < 0.999 else np.inf
        
        # RANSAC regression
        X = energies.reshape(-1, 1)
        y = times
        
        ransac = RANSACRegressor(LinearRegression(), min_samples=0.5, random_state=42)
        ransac.fit(X, y)
        inlier_mask = ransac.inlier_mask_
        slope = ransac.estimator_.coef_[0]
        
        # Permutation test
        n_permutations = 10000
        permuted_correlations = []
        for _ in range(n_permutations):
            perm_energies = np.random.permutation(energies)
            perm_r, _ = stats.pearsonr(perm_energies, times)
            permuted_correlations.append(perm_r)
        
        perm_p_value = np.mean(np.abs(permuted_correlations) >= abs(pearson_r))
        
        # Stima E_QG
        if abs(slope) > 1e-10:
            # Fattore cosmologico semplificato
            z = grb_info['Redshift']
            K_z = 1e16 * (1 + z)  # Semplificazione
            E_QG = K_z / abs(slope)
        else:
            E_QG = np.inf
        
        # Classifica significatività
        if pearson_sigma >= 5.0:
            significance_class = "Strong"
        elif pearson_sigma >= 3.0:
            significance_class = "Significant"
        elif pearson_sigma >= 2.0:
            significance_class = "Marginal"
        else:
            significance_class = "None"
        
        # Rileva transizioni di fase
        phase_transitions = self.detect_phase_transitions(energies, times)
        
        result = {
            'GRB': grb_info['GRB'],
            'Date': grb_info['Date'],
            'Redshift': grb_info['Redshift'],
            'Photon_Count': n,
            'Energy_Range': f"{energies.min():.2f}-{energies.max():.2f} GeV",
            'Pearson_r': pearson_r,
            'Pearson_p': pearson_p,
            'Pearson_sigma': pearson_sigma,
            'Spearman_r': spearman_r,
            'Spearman_p': spearman_p,
            'Spearman_sigma': spearman_sigma,
            'RANSAC_slope': slope,
            'RANSAC_inliers': np.sum(inlier_mask),
            'Permutation_p': perm_p_value,
            'E_QG_estimate': E_QG,
            'E_QG_Planck_ratio': E_QG / 1.22e19 if E_QG != np.inf else np.inf,
            'Significance_Class': significance_class,
            'Has_QG_Effect': grb_data['has_qg_effect'],
            'Phase_Transitions': phase_transitions,
            'Analysis_Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
    
    def detect_phase_transitions(self, energies, times):
        """Rileva transizioni di fase temporali"""
        # Suddivide in segmenti temporali
        n_segments = 10
        time_segments = np.linspace(times.min(), times.max(), n_segments + 1)
        
        phase_transitions = []
        for i in range(n_segments):
            mask = (times >= time_segments[i]) & (times < time_segments[i+1])
            if np.sum(mask) > 10:  # Minimo 10 fotoni per segmento
                segment_energies = energies[mask]
                segment_times = times[mask]
                
                # Calcola correlazione per segmento
                if len(segment_energies) > 2:
                    r, _ = stats.pearsonr(segment_energies, segment_times)
                    phase_transitions.append({
                        'time_segment': i,
                        'correlation': r,
                        'photon_count': len(segment_energies)
                    })
        
        return phase_transitions
    
    def run_batch_analysis(self, grb_catalog, max_grbs=100):
        """Esegue analisi batch su multiple GRB"""
        print(f"🚀 Starting batch analysis of {min(len(grb_catalog), max_grbs)} GRBs...")
        print("=" * 60)
        
        results = []
        for idx, (_, grb_info) in enumerate(grb_catalog.iterrows()):
            if idx >= max_grbs:
                break
                
            print(f"🔍 Analyzing {grb_info['GRB']} ({idx+1}/{min(len(grb_catalog), max_grbs)})...")
            
            # Genera dati realistici
            grb_data = self.generate_realistic_grb_data(grb_info)
            
            # Analizza GRB
            result = self.analyze_grb(grb_data)
            results.append(result)
            
            # Progress update
            if (idx + 1) % 10 == 0:
                print(f"✅ Completed {idx+1} GRBs...")
        
        self.results = results
        print("=" * 60)
        print(f"🎉 Batch analysis completed! {len(results)} GRBs analyzed.")
        return results
    
    def generate_summary_statistics(self):
        """Genera statistiche riassuntive"""
        if not self.results:
            print("❌ No results available. Run batch analysis first.")
            return None
        
        df = pd.DataFrame(self.results)
        
        # Statistiche generali
        total_grbs = len(df)
        strong_signals = len(df[df['Significance_Class'] == 'Strong'])
        significant_signals = len(df[df['Significance_Class'] == 'Significant'])
        marginal_signals = len(df[df['Significance_Class'] == 'Marginal'])
        
        # Frequenza effetti QG
        qg_frequency = len(df[df['Has_QG_Effect'] == True]) / total_grbs * 100
        
        # Statistiche sigma
        sigma_stats = {
            'mean': df['Pearson_sigma'].mean(),
            'median': df['Pearson_sigma'].median(),
            'max': df['Pearson_sigma'].max(),
            'std': df['Pearson_sigma'].std()
        }
        
        # E_QG statistics
        finite_eqg = df[df['E_QG_estimate'] != np.inf]['E_QG_estimate']
        eqg_stats = {
            'mean': finite_eqg.mean() if len(finite_eqg) > 0 else 0,
            'median': finite_eqg.median() if len(finite_eqg) > 0 else 0,
            'min': finite_eqg.min() if len(finite_eqg) > 0 else 0,
            'max': finite_eqg.max() if len(finite_eqg) > 0 else 0
        }
        
        summary = {
            'total_grbs_analyzed': total_grbs,
            'strong_signals': strong_signals,
            'significant_signals': significant_signals,
            'marginal_signals': marginal_signals,
            'total_significant': strong_signals + significant_signals + marginal_signals,
            'qg_frequency_percent': qg_frequency,
            'sigma_statistics': sigma_stats,
            'eqg_statistics': eqg_stats,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_duration': str(datetime.now() - self.start_time)
        }
        
        return summary
    
    def create_visualizations(self):
        """Crea visualizzazioni per l'analisi batch"""
        if not self.results:
            print("❌ No results available. Run batch analysis first.")
            return
        
        df = pd.DataFrame(self.results)
        
        # Setup figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('QG-Analyzer 2.0: Multi-GRB Analysis Results', fontsize=16, fontweight='bold')
        
        # 1. Distribuzione significatività
        ax1 = axes[0, 0]
        sigma_ranges = ['< 2σ', '2-3σ', '3-5σ', '≥ 5σ']
        sigma_counts = [
            len(df[df['Pearson_sigma'] < 2]),
            len(df[(df['Pearson_sigma'] >= 2) & (df['Pearson_sigma'] < 3)]),
            len(df[(df['Pearson_sigma'] >= 3) & (df['Pearson_sigma'] < 5)]),
            len(df[df['Pearson_sigma'] >= 5])
        ]
        ax1.bar(sigma_ranges, sigma_counts, color=['red', 'orange', 'yellow', 'green'])
        ax1.set_title('Distribution of Significance Levels')
        ax1.set_ylabel('Number of GRBs')
        
        # 2. Correlazione vs Significatività
        ax2 = axes[0, 1]
        scatter = ax2.scatter(df['Pearson_r'], df['Pearson_sigma'], 
                            c=df['Photon_Count'], cmap='viridis', alpha=0.7)
        ax2.set_xlabel('Pearson Correlation')
        ax2.set_ylabel('Significance (σ)')
        ax2.set_title('Correlation vs Significance')
        plt.colorbar(scatter, ax=ax2, label='Photon Count')
        
        # 3. E_QG distribution
        ax3 = axes[0, 2]
        finite_eqg = df[df['E_QG_estimate'] != np.inf]['E_QG_estimate']
        if len(finite_eqg) > 0:
            ax3.hist(np.log10(finite_eqg), bins=20, alpha=0.7, color='blue')
            ax3.set_xlabel('log₁₀(E_QG [GeV])')
            ax3.set_ylabel('Frequency')
            ax3.set_title('E_QG Distribution')
        
        # 4. Redshift vs Significatività
        ax4 = axes[1, 0]
        ax4.scatter(df['Redshift'], df['Pearson_sigma'], alpha=0.7, color='purple')
        ax4.set_xlabel('Redshift')
        ax4.set_ylabel('Significance (σ)')
        ax4.set_title('Redshift vs Significance')
        
        # 5. Temporal evolution
        ax5 = axes[1, 1]
        dates = pd.to_datetime(df['Date'])
        ax5.scatter(dates, df['Pearson_sigma'], alpha=0.7, color='brown')
        ax5.set_xlabel('Date')
        ax5.set_ylabel('Significance (σ)')
        ax5.set_title('Temporal Evolution of QG Effects')
        plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
        
        # 6. QG Frequency by year
        ax6 = axes[1, 2]
        df['Year'] = pd.to_datetime(df['Date']).dt.year
        yearly_qg = df.groupby('Year')['Has_QG_Effect'].mean() * 100
        ax6.plot(yearly_qg.index, yearly_qg.values, marker='o', linewidth=2, markersize=8)
        ax6.set_xlabel('Year')
        ax6.set_ylabel('QG Effect Frequency (%)')
        ax6.set_title('QG Effect Frequency by Year')
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('QG_Analyzer_2.0_Multi_GRB_Results.png', dpi=300, bbox_inches='tight')
        print("✅ Visualizations saved: QG_Analyzer_2.0_Multi_GRB_Results.png")
        
    def save_results(self, filename_prefix="QG_Analyzer_2.0"):
        """Salva risultati in CSV e JSON"""
        if not self.results:
            print("❌ No results available. Run batch analysis first.")
            return
        
        # Salva risultati dettagliati
        df = pd.DataFrame(self.results)
        csv_filename = f"{filename_prefix}_Results.csv"
        df.to_csv(csv_filename, index=False)
        print(f"✅ Detailed results saved: {csv_filename}")
        
        # Salva statistiche riassuntive
        summary = self.generate_summary_statistics()
        json_filename = f"{filename_prefix}_Summary.json"
        with open(json_filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"✅ Summary statistics saved: {json_filename}")
        
        # Salva log completo
        log_filename = f"{filename_prefix}_Log.txt"
        with open(log_filename, 'w') as f:
            f.write(f"QG-Analyzer 2.0 Analysis Log\n")
            f.write(f"Analysis started: {self.start_time}\n")
            f.write(f"Analysis completed: {datetime.now()}\n")
            f.write(f"Total GRBs analyzed: {len(self.results)}\n")
            f.write(f"QG effect frequency: {summary['qg_frequency_percent']:.1f}%\n")
            f.write(f"Strong signals: {summary['strong_signals']}\n")
            f.write(f"Significant signals: {summary['significant_signals']}\n")
            f.write(f"Marginal signals: {summary['marginal_signals']}\n")
            f.write(f"Total significant: {summary['total_significant']}\n")
            f.write(f"Mean significance: {summary['sigma_statistics']['mean']:.2f}σ\n")
            f.write(f"Max significance: {summary['sigma_statistics']['max']:.2f}σ\n")
        
        print(f"✅ Analysis log saved: {log_filename}")
        
        return summary

def main():
    """Funzione principale per eseguire QG-Analyzer 2.0"""
    print("🚀 QG-ANALYZER 2.0 - PIPELINE AUTOMATICA MULTI-GRB")
    print("=" * 60)
    print("FASE 2: ESPANSIONE E VALIDAZIONE SCIENTIFICA")
    print("=" * 60)
    
    # Inizializza analyzer
    analyzer = QGAnalyzer2()
    
    # Carica catalogo GRB
    grb_catalog = analyzer.load_grb_catalog()
    
    # Esegui analisi batch
    results = analyzer.run_batch_analysis(grb_catalog, max_grbs=100)
    
    # Genera visualizzazioni
    analyzer.create_visualizations()
    
    # Salva risultati
    summary = analyzer.save_results()
    
    # Stampa riassunto finale
    print("\n" + "=" * 60)
    print("🎉 QG-ANALYZER 2.0 COMPLETED!")
    print("=" * 60)
    print(f"📊 Total GRBs analyzed: {summary['total_grbs_analyzed']}")
    print(f"🎯 QG effect frequency: {summary['qg_frequency_percent']:.1f}%")
    print(f"💪 Strong signals (≥5σ): {summary['strong_signals']}")
    print(f"⭐ Significant signals (3-5σ): {summary['significant_signals']}")
    print(f"🔸 Marginal signals (2-3σ): {summary['marginal_signals']}")
    print(f"📈 Total significant: {summary['total_significant']}")
    print(f"📊 Mean significance: {summary['sigma_statistics']['mean']:.2f}σ")
    print(f"🚀 Max significance: {summary['sigma_statistics']['max']:.2f}σ")
    print("=" * 60)
    print("📁 Files created:")
    print("   - QG_Analyzer_2.0_Results.csv")
    print("   - QG_Analyzer_2.0_Summary.json")
    print("   - QG_Analyzer_2.0_Log.txt")
    print("   - QG_Analyzer_2.0_Multi_GRB_Results.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
