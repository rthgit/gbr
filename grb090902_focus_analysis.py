#!/usr/bin/env python3
"""
FASE 5: ANALISI DETTAGLIATA GRB090902
=====================================

Analisi dettagliata specifica per GRB090902 per verificare se il residuo
3.32σ è effetto QG reale o bias sistematico.

Autore: Christian Quintino De Luca (RTH Italia)
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from astropy.io import fits
from datetime import datetime
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit, minimize
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib per headless
import matplotlib
matplotlib.use('Agg')
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 10

def convert_numpy(obj):
    """Converte tipi NumPy in tipi Python standard per JSON"""
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                        np.int16, np.int32, np.int64, np.uint8,
                        np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def load_grb090902_data():
    """Carica dati specifici GRB090902"""
    try:
        with fits.open('L251020161615F357373F52_EV00.fits') as hdul:
            events_data = hdul['EVENTS'].data
            
            if events_data is None:
                print("❌ Nessun dato in GRB090902")
                return None
            
            times = events_data['TIME'] - 273581808.0  # Trigger time
            energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
            
            # Quality cuts - GRB090902 usa filtri normali
            quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
            
            times_filtered = times[quality_cuts]
            energies_filtered = energies[quality_cuts]
            
            print(f"📊 GRB090902: {len(times_filtered)} fotoni")
            print(f"  Range energia: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV")
            print(f"  Range tempo: {times_filtered.min():.1f} - {times_filtered.max():.1f} s")
            
            return {
                'times': times_filtered,
                'energies': energies_filtered,
                'n_photons': len(times_filtered),
                'energy_range': (energies_filtered.min(), energies_filtered.max()),
                'time_range': (times_filtered.min(), times_filtered.max()),
                'redshift': 1.822
            }
            
    except Exception as e:
        print(f"❌ Errore caricamento GRB090902: {e}")
        return None

def analyze_temporal_structure(times, energies):
    """Analizza struttura temporale dettagliata"""
    print("🔍 Analisi struttura temporale...")
    
    # Dividi in bande temporali
    time_bins = np.linspace(times.min(), times.max(), 11)  # 10 bande temporali
    temporal_results = []
    
    for i in range(len(time_bins) - 1):
        mask = (times >= time_bins[i]) & (times < time_bins[i + 1])
        if np.sum(mask) > 20:  # Almeno 20 fotoni per banda
            times_band = times[mask]
            energies_band = energies[mask]
            
            # Calcola correlazione per questa banda temporale
            if len(times_band) > 2:
                correlation = np.corrcoef(energies_band, times_band)[0, 1]
                if not np.isnan(correlation):
                    significance = abs(correlation) * np.sqrt(len(times_band) - 2) / np.sqrt(1 - correlation**2)
                    
                    temporal_results.append({
                        'time_start': time_bins[i],
                        'time_end': time_bins[i + 1],
                        'time_center': (time_bins[i] + time_bins[i + 1]) / 2,
                        'n_photons': len(times_band),
                        'correlation': correlation,
                        'significance': significance,
                        'energy_mean': np.mean(energies_band),
                        'time_mean': np.mean(times_band)
                    })
    
    return temporal_results

def analyze_energy_structure(times, energies):
    """Analizza struttura energetica dettagliata"""
    print("🔍 Analisi struttura energetica...")
    
    # Dividi in bande energetiche logaritmiche
    energy_bins = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 16)  # 15 bande energetiche
    energy_results = []
    
    for i in range(len(energy_bins) - 1):
        mask = (energies >= energy_bins[i]) & (energies < energy_bins[i + 1])
        if np.sum(mask) > 20:  # Almeno 20 fotoni per banda
            times_band = times[mask]
            energies_band = energies[mask]
            
            # Calcola correlazione per questa banda energetica
            if len(times_band) > 2:
                correlation = np.corrcoef(energies_band, times_band)[0, 1]
                if not np.isnan(correlation):
                    significance = abs(correlation) * np.sqrt(len(times_band) - 2) / np.sqrt(1 - correlation**2)
                    
                    energy_results.append({
                        'energy_start': energy_bins[i],
                        'energy_end': energy_bins[i + 1],
                        'energy_center': np.sqrt(energy_bins[i] * energy_bins[i + 1]),  # Geometric mean
                        'n_photons': len(times_band),
                        'correlation': correlation,
                        'significance': significance,
                        'energy_mean': np.mean(energies_band),
                        'time_mean': np.mean(times_band)
                    })
    
    return energy_results

def test_advanced_qg_models(times, energies):
    """Test modelli QG avanzati specifici"""
    print("🔍 Test modelli QG avanzati...")
    
    # Calcola distanza di luminosità
    z = 1.822
    H0 = 70.0  # km/s/Mpc
    c_km_s = 3e5  # km/s
    d_L = (c_km_s / H0) * z * (1 + z)  # Mpc
    
    qg_models = {}
    
    # Modello 1: QG con dipendenza temporale
    try:
        def qg_temporal(E, t, t0, E_QG, alpha):
            """QG con dipendenza temporale: t = t0 + (d_L/c) * (E/E_QG) * (1 + alpha * t)"""
            c = 3e8  # m/s
            return t0 + (d_L * 3.086e22 / c) * (E / E_QG) * (1 + alpha * t)
        
        def qg_temporal_fit(E, t0, E_QG, alpha):
            return qg_temporal(E, times, t0, E_QG, alpha)
        
        p0 = [np.mean(times), 1e19, 0.01]
        bounds = ([times.min(), 1e15, -0.1], [times.max(), 1e25, 0.1])
        
        popt, pcov = curve_fit(qg_temporal_fit, energies, times, p0=p0, bounds=bounds, maxfev=3000)
        t0, E_QG, alpha = popt
        
        times_pred = qg_temporal_fit(energies, t0, E_QG, alpha)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 3
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        qg_models['qg_temporal'] = {
            't0': float(t0),
            'E_QG': float(E_QG),
            'alpha': float(alpha),
            'd_L': float(d_L),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 3 + chi2),
            'type': 'QG with Temporal Dependence'
        }
    except Exception as e:
        print(f"⚠️ Errore fit QG temporal: {e}")
        qg_models['qg_temporal'] = None
    
    # Modello 2: QG con dipendenza energetica non-lineare
    try:
        def qg_nonlinear(E, t0, E_QG, beta):
            """QG non-lineare: t = t0 + (d_L/c) * (E/E_QG)^beta"""
            c = 3e8  # m/s
            return t0 + (d_L * 3.086e22 / c) * np.power(E / E_QG, beta)
        
        p0 = [np.mean(times), 1e19, 1.5]
        bounds = ([times.min(), 1e15, 0.5], [times.max(), 1e25, 3.0])
        
        popt, pcov = curve_fit(qg_nonlinear, energies, times, p0=p0, bounds=bounds, maxfev=3000)
        t0, E_QG, beta = popt
        
        times_pred = qg_nonlinear(energies, t0, E_QG, beta)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 3
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        qg_models['qg_nonlinear'] = {
            't0': float(t0),
            'E_QG': float(E_QG),
            'beta': float(beta),
            'd_L': float(d_L),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 3 + chi2),
            'type': 'QG with Nonlinear Energy Dependence'
        }
    except Exception as e:
        print(f"⚠️ Errore fit QG nonlinear: {e}")
        qg_models['qg_nonlinear'] = None
    
    # Modello 3: QG con break energetico
    try:
        def qg_break(E, t0, E_QG1, E_QG2, E_break):
            """QG con break energetico: due scale QG diverse"""
            c = 3e8  # m/s
            result = np.zeros_like(E)
            mask_low = E < E_break
            mask_high = E >= E_break
            
            result[mask_low] = t0 + (d_L * 3.086e22 / c) * (E[mask_low] / E_QG1)
            result[mask_high] = t0 + (d_L * 3.086e22 / c) * (E_break / E_QG1) + (d_L * 3.086e22 / c) * (E[mask_high] / E_QG2)
            
            return result
        
        E_break_init = np.median(energies)
        p0 = [np.mean(times), 1e19, 1e19, E_break_init]
        bounds = ([times.min(), 1e15, 1e15, energies.min()], [times.max(), 1e25, 1e25, energies.max()])
        
        popt, pcov = curve_fit(qg_break, energies, times, p0=p0, bounds=bounds, maxfev=3000)
        t0, E_QG1, E_QG2, E_break = popt
        
        times_pred = qg_break(energies, t0, E_QG1, E_QG2, E_break)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 4
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        qg_models['qg_break'] = {
            't0': float(t0),
            'E_QG1': float(E_QG1),
            'E_QG2': float(E_QG2),
            'E_break': float(E_break),
            'd_L': float(d_L),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 4 + chi2),
            'type': 'QG with Energy Break'
        }
    except Exception as e:
        print(f"⚠️ Errore fit QG break: {e}")
        qg_models['qg_break'] = None
    
    return qg_models

def machine_learning_analysis(times, energies):
    """Analisi con machine learning"""
    print("🔍 Analisi machine learning...")
    
    ml_results = {}
    
    # Prepara dati
    X = np.column_stack([energies, np.log10(energies), np.power(energies, 0.5)])
    y = times
    
    # 1. Random Forest
    try:
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        scores = cross_val_score(rf, X, y, cv=5, scoring='neg_mean_squared_error')
        
        ml_results['random_forest'] = {
            'scores': scores.tolist(),
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'feature_importance': rf.fit(X, y).feature_importances_.tolist()
        }
    except Exception as e:
        print(f"⚠️ Errore Random Forest: {e}")
        ml_results['random_forest'] = None
    
    # 2. Regressione polinomiale avanzata
    try:
        poly = PolynomialFeatures(degree=3)
        X_poly = poly.fit_transform(X)
        
        lr_poly = LinearRegression()
        scores_poly = cross_val_score(lr_poly, X_poly, y, cv=5, scoring='neg_mean_squared_error')
        
        ml_results['polynomial_degree3'] = {
            'scores': scores_poly.tolist(),
            'mean_score': float(np.mean(scores_poly)),
            'std_score': float(np.std(scores_poly))
        }
    except Exception as e:
        print(f"⚠️ Errore regressione polinomiale: {e}")
        ml_results['polynomial_degree3'] = None
    
    return ml_results

def create_grb090902_focus_plots(grb_name, times, energies, temporal_results, energy_results, qg_models, ml_results):
    """Crea grafici dettagliati per GRB090902"""
    
    fig, axes = plt.subplots(4, 4, figsize=(24, 20))
    fig.suptitle(f'Analisi Dettagliata GRB090902 - Focus 3.32σ Residuo', fontsize=18, fontweight='bold')
    
    # Plot 1: Distribuzione temporale
    ax1 = axes[0, 0]
    ax1.scatter(times, energies, alpha=0.6, s=20, c='blue', edgecolors='none')
    ax1.set_xlabel('Tempo relativo (s)')
    ax1.set_ylabel('Energia (GeV)')
    ax1.set_title('Distribuzione Tempo-Energia')
    ax1.set_yscale('log')
    
    # Plot 2: Correlazione per banda temporale
    ax2 = axes[0, 1]
    if temporal_results:
        time_centers = [r['time_center'] for r in temporal_results]
        correlations = [r['correlation'] for r in temporal_results]
        significances = [r['significance'] for r in temporal_results]
        
        colors = ['red' if s > 2 else 'orange' if s > 1 else 'green' for s in significances]
        ax2.scatter(time_centers, correlations, c=colors, s=100, alpha=0.7)
        ax2.axhline(0, color='black', linestyle='-', alpha=0.5)
        ax2.set_xlabel('Tempo centro banda (s)')
        ax2.set_ylabel('Correlazione r')
        ax2.set_title('Correlazione per Banda Temporale')
    
    # Plot 3: Significatività per banda temporale
    ax3 = axes[0, 2]
    if temporal_results:
        ax3.bar(range(len(significances)), significances, color=colors, alpha=0.7)
        ax3.axhline(2, color='red', linestyle='--', label='2σ')
        ax3.axhline(3, color='darkred', linestyle='--', label='3σ')
        ax3.set_xlabel('Banda Temporale')
        ax3.set_ylabel('Significatività (σ)')
        ax3.set_title('Significatività per Banda Temporale')
        ax3.legend()
    
    # Plot 4: Correlazione per banda energetica
    ax4 = axes[0, 3]
    if energy_results:
        energy_centers = [r['energy_center'] for r in energy_results]
        correlations_energy = [r['correlation'] for r in energy_results]
        significances_energy = [r['significance'] for r in energy_results]
        
        colors_energy = ['red' if s > 2 else 'orange' if s > 1 else 'green' for s in significances_energy]
        ax4.scatter(energy_centers, correlations_energy, c=colors_energy, s=100, alpha=0.7)
        ax4.axhline(0, color='black', linestyle='-', alpha=0.5)
        ax4.set_xlabel('Energia centro banda (GeV)')
        ax4.set_ylabel('Correlazione r')
        ax4.set_title('Correlazione per Banda Energetica')
        ax4.set_xscale('log')
    
    # Plot 5-7: Modelli QG avanzati
    plot_idx = 4
    colors_qg = ['red', 'blue', 'green']
    
    for model_name, model in qg_models.items():
        if model is None or plot_idx >= 8:
            continue
            
        row = plot_idx // 4
        col = plot_idx % 4
        ax = axes[row, col]
        
        # Plot dati e modello
        ax.scatter(energies, times, alpha=0.3, s=10, c='gray', label='Dati')
        
        # Plot modello
        E_fit = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 100)
        
        if model_name == 'qg_temporal':
            t_fit = model['t0'] + (model['d_L'] * 3.086e22 / 3e8) * (E_fit / model['E_QG']) * (1 + model['alpha'] * np.mean(times))
        elif model_name == 'qg_nonlinear':
            t_fit = model['t0'] + (model['d_L'] * 3.086e22 / 3e8) * np.power(E_fit / model['E_QG'], model['beta'])
        elif model_name == 'qg_break':
            t_fit = np.zeros_like(E_fit)
            mask_low = E_fit < model['E_break']
            mask_high = E_fit >= model['E_break']
            t_fit[mask_low] = model['t0'] + (model['d_L'] * 3.086e22 / 3e8) * (E_fit[mask_low] / model['E_QG1'])
            t_fit[mask_high] = model['t0'] + (model['d_L'] * 3.086e22 / 3e8) * (model['E_break'] / model['E_QG1']) + (model['d_L'] * 3.086e22 / 3e8) * (E_fit[mask_high] / model['E_QG2'])
        else:
            continue
        
        ax.plot(E_fit, t_fit, color=colors_qg[plot_idx-4], linewidth=3,
                label=f'{model["type"]} (AIC={model["aic"]:.1f})')
        
        ax.set_xlabel('Energia (GeV)')
        ax.set_ylabel('Tempo relativo (s)')
        ax.set_title(f'{model["type"]}')
        ax.set_xscale('log')
        ax.legend()
        
        plot_idx += 1
    
    # Plot 8: Confronto AIC modelli QG
    ax8 = axes[1, 3]
    model_names = []
    aic_values = []
    
    for model_name, model in qg_models.items():
        if model is not None:
            model_names.append(model['type'])
            aic_values.append(model['aic'])
    
    if model_names:
        bars = ax8.bar(range(len(model_names)), aic_values, color='lightblue', alpha=0.7)
        ax8.set_xticks(range(len(model_names)))
        ax8.set_xticklabels(model_names, rotation=45, ha='right')
        ax8.set_ylabel('AIC')
        ax8.set_title('Confronto Modelli QG (AIC)')
        
        # Evidenzia il migliore
        best_idx = np.argmin(aic_values)
        bars[best_idx].set_edgecolor('darkblue')
        bars[best_idx].set_linewidth(3)
    
    # Plot 9-12: Analisi machine learning
    plot_idx = 8
    ml_plots = ['random_forest', 'polynomial_degree3']
    
    for ml_name in ml_plots:
        if ml_name in ml_results and ml_results[ml_name] is not None:
            row = plot_idx // 4
            col = plot_idx % 4
            ax = axes[row, col]
            
            scores = ml_results[ml_name]['scores']
            ax.bar(range(len(scores)), scores, color='lightgreen', alpha=0.7)
            ax.axhline(ml_results[ml_name]['mean_score'], color='green', 
                      linestyle='--', label=f'Media: {ml_results[ml_name]["mean_score"]:.3f}')
            ax.set_xlabel('Fold CV')
            ax.set_ylabel('Score (MSE)')
            ax.set_title(f'Cross-Validation - {ml_name}')
            ax.legend()
            
            plot_idx += 1
    
    # Plot 13: Riassunto risultati
    ax13 = axes[3, 0]
    ax13.axis('off')
    
    # Calcola statistiche principali
    correlation_total = np.corrcoef(energies, times)[0, 1]
    significance_total = abs(correlation_total) * np.sqrt(len(times) - 2) / np.sqrt(1 - correlation_total**2)
    
    summary_text = f"""
ANALISI DETTAGLIATA GRB090902

📊 Statistiche Principali:
• Fotoni: {len(times):,}
• Range energia: {energies.min():.3f} - {energies.max():.1f} GeV
• Range tempo: {times.min():.1f} - {times.max():.1f} s
• Redshift: z = 1.822

🎯 Correlazione Totale:
• r = {correlation_total:.3f}
• σ = {significance_total:.2f}

🔬 Analisi Temporale:
• Bande temporali: {len(temporal_results)}
• Max significatività: {max([r['significance'] for r in temporal_results]) if temporal_results else 0:.2f}σ

📈 Analisi Energetica:
• Bande energetiche: {len(energy_results)}
• Max significatività: {max([r['significance'] for r in energy_results]) if energy_results else 0:.2f}σ

🚨 Modelli QG Avanzati:
• Modelli testati: {sum(1 for m in qg_models.values() if m is not None)}
• Miglior modello: {min(qg_models.items(), key=lambda x: x[1]['aic'] if x[1] else float('inf'))[1]['type'] if any(m for m in qg_models.values() if m) else 'N/A'}

🔍 Interpretazione:
"""
    
    if significance_total > 3:
        summary_text += "🚨 CORRELAZIONE MOLTO SIGNIFICATIVA!"
    elif significance_total > 2:
        summary_text += "⚠️ CORRELAZIONE SIGNIFICATIVA"
    else:
        summary_text += "✅ CORRELAZIONE NON SIGNIFICATIVA"
    
    ax13.text(0.05, 0.95, summary_text, transform=ax13.transAxes, 
             verticalalignment='top', fontfamily='monospace', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Plot 14-16: Analisi aggiuntive
    # Plot 14: Distribuzione energetica
    ax14 = axes[3, 1]
    hist, bin_edges = np.histogram(energies, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    ax14.step(bin_centers, hist, where='mid', linewidth=2, color='green')
    ax14.set_xlabel('Energia (GeV)')
    ax14.set_ylabel('Numero fotoni')
    ax14.set_title('Distribuzione Energetica')
    ax14.set_xscale('log')
    
    # Plot 15: Distribuzione temporale
    ax15 = axes[3, 2]
    hist, bin_edges = np.histogram(times, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    ax15.step(bin_centers, hist, where='mid', linewidth=2, color='purple')
    ax15.set_xlabel('Tempo relativo (s)')
    ax15.set_ylabel('Numero fotoni')
    ax15.set_title('Distribuzione Temporale')
    
    # Plot 16: Scatter plot colorato per significatività
    ax16 = axes[3, 3]
    
    # Calcola significatività locale
    window_size = 200  # fotoni per finestra
    significances_local = []
    
    for i in range(0, len(times), window_size):
        end_idx = min(i + window_size, len(times))
        if end_idx - i > 10:
            times_local = times[i:end_idx]
            energies_local = energies[i:end_idx]
            if len(times_local) > 2:
                corr_local = np.corrcoef(energies_local, times_local)[0, 1]
                if not np.isnan(corr_local):
                    sig_local = abs(corr_local) * np.sqrt(len(times_local) - 2) / np.sqrt(1 - corr_local**2)
                    significances_local.extend([sig_local] * (end_idx - i))
                else:
                    significances_local.extend([0] * (end_idx - i))
            else:
                significances_local.extend([0] * (end_idx - i))
        else:
            significances_local.extend([0] * (end_idx - i))
    
    # Aggiungi zeri per i fotoni rimanenti
    while len(significances_local) < len(times):
        significances_local.append(0)
    
    significances_local = np.array(significances_local[:len(times)])
    
    # Colora per significatività locale
    colors_local = plt.cm.RdYlBu_r(significances_local / np.max(significances_local) if np.max(significances_local) > 0 else 0)
    
    ax16.scatter(times, energies, c=colors_local, s=20, alpha=0.6, edgecolors='none')
    ax16.set_xlabel('Tempo relativo (s)')
    ax16.set_ylabel('Energia (GeV)')
    ax16.set_title('Significatività Locale')
    ax16.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('grb090902_focus_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici salvati: grb090902_focus_analysis.png")

def main():
    """Funzione principale per analisi dettagliata GRB090902"""
    
    print("="*70)
    print("FASE 5: ANALISI DETTAGLIATA GRB090902")
    print("Focus su residuo 3.32σ - Verifica QG vs bias sistematico")
    print("="*70)
    
    # Carica dati GRB090902
    data = load_grb090902_data()
    
    if data is None:
        return
    
    times = data['times']
    energies = data['energies']
    
    print(f"📊 Dati caricati: {len(times)} fotoni")
    
    # Analisi struttura temporale
    temporal_results = analyze_temporal_structure(times, energies)
    print(f"✅ Analisi temporale: {len(temporal_results)} bande")
    
    # Analisi struttura energetica
    energy_results = analyze_energy_structure(times, energies)
    print(f"✅ Analisi energetica: {len(energy_results)} bande")
    
    # Test modelli QG avanzati
    qg_models = test_advanced_qg_models(times, energies)
    print(f"✅ Modelli QG testati: {sum(1 for m in qg_models.values() if m is not None)}")
    
    # Analisi machine learning
    ml_results = machine_learning_analysis(times, energies)
    print(f"✅ Analisi ML completata")
    
    # Crea grafici
    create_grb090902_focus_plots('GRB090902', times, energies, temporal_results, 
                               energy_results, qg_models, ml_results)
    
    # Salva risultati
    results = {
        'grb_name': 'GRB090902',
        'n_photons': len(times),
        'energy_range': data['energy_range'],
        'time_range': data['time_range'],
        'redshift': data['redshift'],
        'total_correlation': float(np.corrcoef(energies, times)[0, 1]),
        'total_significance': float(abs(np.corrcoef(energies, times)[0, 1]) * np.sqrt(len(times) - 2) / np.sqrt(1 - np.corrcoef(energies, times)[0, 1]**2)),
        'temporal_analysis': temporal_results,
        'energy_analysis': energy_results,
        'qg_models': {k: v for k, v in qg_models.items() if v is not None},
        'ml_results': ml_results
    }
    
    with open('grb090902_focus_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=convert_numpy)
    
    # Riassunto finale
    print(f"\n🎯 RISULTATI FINALI GRB090902:")
    print(f"  Fotoni analizzati: {len(times):,}")
    print(f"  Correlazione totale: {results['total_correlation']:.3f} ({results['total_significance']:.2f}σ)")
    print(f"  Bande temporali: {len(temporal_results)}")
    print(f"  Bande energetiche: {len(energy_results)}")
    print(f"  Modelli QG testati: {sum(1 for m in qg_models.values() if m is not None)}")
    
    if qg_models:
        best_model = min(qg_models.items(), key=lambda x: x[1]['aic'] if x[1] else float('inf'))
        if best_model[1]:
            print(f"  Miglior modello QG: {best_model[1]['type']} (AIC={best_model[1]['aic']:.1f})")
    
    print("\n" + "="*70)
    print("FASE 5 COMPLETATA! Pronto per interpretazione finale!")
    print("="*70)

if __name__ == "__main__":
    main()
