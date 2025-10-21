#!/usr/bin/env python3
"""
FASE 4: ANALISI AVANZATA DEI LAG
================================

Analisi avanzata dei lag intrinseci per verificare se il residuo 3.32σ
è effetto QG reale o bias sistematico non modellato.

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
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib per headless
import matplotlib
matplotlib.use('Agg')
plt.rcParams['figure.figsize'] = (18, 14)
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

def load_qg_residual_results():
    """Carica risultati della FASE 3"""
    try:
        with open('qg_residual_search_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ File qg_residual_search_results.json non trovato!")
        print("Esegui prima qg_residual_search.py")
        return None

def model_temporal_evolving_lag(times, energies, t0, alpha, beta, gamma):
    """Modello lag che evolve nel tempo: t = t0 + alpha * E^beta * (1 + gamma * t)"""
    return t0 + alpha * np.power(energies, beta) * (1 + gamma * times)

def model_multi_component_lag(times, energies, t0, alpha1, beta1, alpha2, beta2, E_break):
    """Modello lag multi-componente: due processi astrofisici"""
    result = np.zeros_like(times)
    mask_low = energies < E_break
    mask_high = energies >= E_break
    
    result[mask_low] = t0 + alpha1 * np.power(energies[mask_low], beta1)
    result[mask_high] = t0 + alpha1 * np.power(E_break, beta1) + alpha2 * np.power(energies[mask_high], beta2)
    
    return result

def model_nonlinear_energy_lag(times, energies, t0, alpha, beta, gamma):
    """Modello lag non-lineare in energia: t = t0 + alpha * E^beta * (1 + gamma * E^2)"""
    return t0 + alpha * np.power(energies, beta) * (1 + gamma * np.power(energies, 2))

def model_temporal_band_lag(times, energies, t0, alpha, beta, t_break, alpha2, beta2):
    """Modello lag con break temporale: due fasi temporali"""
    result = np.zeros_like(times)
    mask_early = times < t_break
    mask_late = times >= t_break
    
    result[mask_early] = t0 + alpha * np.power(energies[mask_early], beta)
    result[mask_late] = t0 + alpha * np.power(energies[mask_late], beta) + alpha2 * np.power(energies[mask_late], beta2)
    
    return result

def fit_advanced_lag_models(times, energies):
    """Fit modelli lag avanzati"""
    models = {}
    
    # Modello 1: Lag che evolve nel tempo
    try:
        def temporal_evolving(E, t0, alpha, beta, gamma):
            return model_temporal_evolving_lag(times, E, t0, alpha, beta, gamma)
        
        p0 = [np.mean(times), -1.0, -0.5, 0.01]
        bounds = ([times.min(), -100, -2, -0.1], [times.max(), 100, 2, 0.1])
        
        popt, pcov = curve_fit(temporal_evolving, energies, times, p0=p0, bounds=bounds, maxfev=3000)
        t0, alpha, beta, gamma = popt
        
        times_pred = temporal_evolving(energies, t0, alpha, beta, gamma)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 4
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['temporal_evolving'] = {
            't0': float(t0),
            'alpha': float(alpha),
            'beta': float(beta),
            'gamma': float(gamma),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 4 + chi2),
            'type': 'Temporal Evolving Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit temporal evolving: {e}")
        models['temporal_evolving'] = None
    
    # Modello 2: Lag multi-componente
    try:
        def multi_component(E, t0, alpha1, beta1, alpha2, beta2, E_break):
            return model_multi_component_lag(times, E, t0, alpha1, beta1, alpha2, beta2, E_break)
        
        E_break_init = np.median(energies)
        p0 = [np.mean(times), -1.0, -0.5, -0.5, -0.3, E_break_init]
        bounds = ([times.min(), -50, -2, -50, -2, energies.min()], 
                 [times.max(), 50, 2, 50, 2, energies.max()])
        
        popt, pcov = curve_fit(multi_component, energies, times, p0=p0, bounds=bounds, maxfev=4000)
        t0, alpha1, beta1, alpha2, beta2, E_break = popt
        
        times_pred = multi_component(energies, t0, alpha1, beta1, alpha2, beta2, E_break)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 6
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['multi_component'] = {
            't0': float(t0),
            'alpha1': float(alpha1),
            'beta1': float(beta1),
            'alpha2': float(alpha2),
            'beta2': float(beta2),
            'E_break': float(E_break),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 6 + chi2),
            'type': 'Multi-Component Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit multi-component: {e}")
        models['multi_component'] = None
    
    # Modello 3: Lag non-lineare in energia
    try:
        def nonlinear_energy(E, t0, alpha, beta, gamma):
            return model_nonlinear_energy_lag(times, E, t0, alpha, beta, gamma)
        
        p0 = [np.mean(times), -1.0, -0.5, 0.001]
        bounds = ([times.min(), -100, -2, -0.01], [times.max(), 100, 2, 0.01])
        
        popt, pcov = curve_fit(nonlinear_energy, energies, times, p0=p0, bounds=bounds, maxfev=3000)
        t0, alpha, beta, gamma = popt
        
        times_pred = nonlinear_energy(energies, t0, alpha, beta, gamma)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 4
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['nonlinear_energy'] = {
            't0': float(t0),
            'alpha': float(alpha),
            'beta': float(beta),
            'gamma': float(gamma),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 4 + chi2),
            'type': 'Nonlinear Energy Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit nonlinear energy: {e}")
        models['nonlinear_energy'] = None
    
    # Modello 4: Lag con break temporale
    try:
        def temporal_band(E, t0, alpha, beta, t_break, alpha2, beta2):
            return model_temporal_band_lag(times, E, t0, alpha, beta, t_break, alpha2, beta2)
        
        t_break_init = np.median(times)
        p0 = [np.mean(times), -1.0, -0.5, t_break_init, -0.5, -0.3]
        bounds = ([times.min(), -50, -2, times.min(), -50, -2], 
                 [times.max(), 50, 2, times.max(), 50, 2])
        
        popt, pcov = curve_fit(temporal_band, energies, times, p0=p0, bounds=bounds, maxfev=4000)
        t0, alpha, beta, t_break, alpha2, beta2 = popt
        
        times_pred = temporal_band(energies, t0, alpha, beta, t_break, alpha2, beta2)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 6
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['temporal_band'] = {
            't0': float(t0),
            'alpha': float(alpha),
            'beta': float(beta),
            't_break': float(t_break),
            'alpha2': float(alpha2),
            'beta2': float(beta2),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 6 + chi2),
            'type': 'Temporal Band Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit temporal band: {e}")
        models['temporal_band'] = None
    
    return models

def analyze_systematic_effects(times, energies):
    """Analizza effetti sistematici"""
    systematic_results = {}
    
    # 1. Effetto selezione fotoni
    print("🔍 Analisi selezione fotoni...")
    
    # Testa diverse soglie energetiche
    energy_thresholds = [0.05, 0.1, 0.2, 0.5, 1.0]
    correlations_energy = []
    
    for threshold in energy_thresholds:
        mask = energies > threshold
        if np.sum(mask) > 50:
            corr = np.corrcoef(energies[mask], times[mask])[0, 1]
            correlations_energy.append(corr)
        else:
            correlations_energy.append(np.nan)
    
    systematic_results['energy_threshold'] = {
        'thresholds': energy_thresholds,
        'correlations': correlations_energy
    }
    
    # 2. Effetto finestra temporale
    print("🔍 Analisi finestra temporale...")
    
    time_windows = [500, 1000, 1500, 2000, 2500]
    correlations_time = []
    
    for window in time_windows:
        mask = times <= window
        if np.sum(mask) > 50:
            corr = np.corrcoef(energies[mask], times[mask])[0, 1]
            correlations_time.append(corr)
        else:
            correlations_time.append(np.nan)
    
    systematic_results['time_window'] = {
        'windows': time_windows,
        'correlations': correlations_time
    }
    
    # 3. Effetto binning energetico
    print("🔍 Analisi binning energetico...")
    
    n_bins_options = [5, 10, 15, 20, 25]
    correlations_binning = []
    
    for n_bins in n_bins_options:
        try:
            # Crea bins energetici
            percentiles = np.linspace(0, 100, n_bins + 1)
            bin_edges = np.percentile(energies, percentiles)
            bin_edges = np.unique(bin_edges)
            
            correlations_bin = []
            for i in range(len(bin_edges) - 1):
                mask = (energies >= bin_edges[i]) & (energies < bin_edges[i + 1])
                if np.sum(mask) > 10:
                    corr = np.corrcoef(energies[mask], times[mask])[0, 1]
                    if not np.isnan(corr):
                        correlations_bin.append(corr)
            
            if correlations_bin:
                correlations_binning.append(np.mean(correlations_bin))
            else:
                correlations_binning.append(np.nan)
        except:
            correlations_binning.append(np.nan)
    
    systematic_results['binning'] = {
        'n_bins': n_bins_options,
        'correlations': correlations_binning
    }
    
    return systematic_results

def cross_validation_analysis(times, energies):
    """Analisi cross-validation"""
    cv_results = {}
    
    # 1. Cross-validation con regressione lineare
    print("🔍 Cross-validation lineare...")
    
    try:
        X = energies.reshape(-1, 1)
        y = times
        
        # Regressione lineare
        lr = LinearRegression()
        scores = cross_val_score(lr, X, y, cv=5, scoring='neg_mean_squared_error')
        cv_results['linear_regression'] = {
            'scores': scores.tolist(),
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores))
        }
    except Exception as e:
        print(f"⚠️ Errore cross-validation lineare: {e}")
        cv_results['linear_regression'] = None
    
    # 2. Cross-validation con regressione polinomiale
    print("🔍 Cross-validation polinomiale...")
    
    try:
        X = energies.reshape(-1, 1)
        y = times
        
        # Regressione polinomiale grado 2
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        
        lr_poly = LinearRegression()
        scores_poly = cross_val_score(lr_poly, X_poly, y, cv=5, scoring='neg_mean_squared_error')
        cv_results['polynomial_regression'] = {
            'scores': scores_poly.tolist(),
            'mean_score': float(np.mean(scores_poly)),
            'std_score': float(np.std(scores_poly))
        }
    except Exception as e:
        print(f"⚠️ Errore cross-validation polinomiale: {e}")
        cv_results['polynomial_regression'] = None
    
    return cv_results

def create_advanced_analysis_plots(grb_name, times, energies, advanced_models, systematic_results, cv_results):
    """Crea grafici per analisi avanzata"""
    
    fig, axes = plt.subplots(3, 4, figsize=(24, 18))
    fig.suptitle(f'Analisi Avanzata Lag - {grb_name}', fontsize=16, fontweight='bold')
    
    # Plot 1: Modelli avanzati
    ax1 = axes[0, 0]
    ax1.scatter(energies, times, alpha=0.3, s=10, c='gray', label='Dati')
    
    E_fit = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 100)
    colors = ['red', 'blue', 'green', 'orange']
    
    for i, (model_name, model) in enumerate(advanced_models.items()):
        if model is None:
            continue
            
        if model_name == 'temporal_evolving':
            t_fit = model_temporal_evolving_lag(np.full_like(E_fit, np.mean(times)), E_fit, 
                                               model['t0'], model['alpha'], model['beta'], model['gamma'])
        elif model_name == 'multi_component':
            t_fit = model_multi_component_lag(np.full_like(E_fit, np.mean(times)), E_fit,
                                            model['t0'], model['alpha1'], model['beta1'], 
                                            model['alpha2'], model['beta2'], model['E_break'])
        elif model_name == 'nonlinear_energy':
            t_fit = model_nonlinear_energy_lag(np.full_like(E_fit, np.mean(times)), E_fit,
                                             model['t0'], model['alpha'], model['beta'], model['gamma'])
        elif model_name == 'temporal_band':
            t_fit = model_temporal_band_lag(np.full_like(E_fit, np.mean(times)), E_fit,
                                          model['t0'], model['alpha'], model['beta'], 
                                          model['t_break'], model['alpha2'], model['beta2'])
        else:
            continue
        
        ax1.plot(E_fit, t_fit, color=colors[i], linewidth=2,
                label=f'{model["type"]} (AIC={model["aic"]:.1f})')
    
    ax1.set_xlabel('Energia (GeV)')
    ax1.set_ylabel('Tempo relativo (s)')
    ax1.set_title('Modelli Lag Avanzati')
    ax1.set_xscale('log')
    ax1.legend()
    
    # Plot 2: Confronto AIC
    ax2 = axes[0, 1]
    model_names = []
    aic_values = []
    
    for model_name, model in advanced_models.items():
        if model is not None:
            model_names.append(model['type'])
            aic_values.append(model['aic'])
    
    if model_names:
        bars = ax2.bar(range(len(model_names)), aic_values, color='lightblue', alpha=0.7)
        ax2.set_xticks(range(len(model_names)))
        ax2.set_xticklabels(model_names, rotation=45, ha='right')
        ax2.set_ylabel('AIC')
        ax2.set_title('Confronto Modelli Avanzati (AIC)')
        
        # Evidenzia il migliore
        best_idx = np.argmin(aic_values)
        bars[best_idx].set_edgecolor('darkblue')
        bars[best_idx].set_linewidth(3)
    
    # Plot 3: Effetti sistematici - soglia energetica
    ax3 = axes[0, 2]
    if 'energy_threshold' in systematic_results:
        thresholds = systematic_results['energy_threshold']['thresholds']
        correlations = systematic_results['energy_threshold']['correlations']
        valid_mask = ~np.isnan(correlations)
        
        ax3.plot(np.array(thresholds)[valid_mask], np.array(correlations)[valid_mask], 
                'bo-', linewidth=2, markersize=8)
        ax3.set_xlabel('Soglia Energetica (GeV)')
        ax3.set_ylabel('Correlazione')
        ax3.set_title('Effetto Selezione Fotoni')
        ax3.set_xscale('log')
        ax3.grid(True, alpha=0.3)
    
    # Plot 4: Effetti sistematici - finestra temporale
    ax4 = axes[0, 3]
    if 'time_window' in systematic_results:
        windows = systematic_results['time_window']['windows']
        correlations = systematic_results['time_window']['correlations']
        valid_mask = ~np.isnan(correlations)
        
        ax4.plot(np.array(windows)[valid_mask], np.array(correlations)[valid_mask], 
                'ro-', linewidth=2, markersize=8)
        ax4.set_xlabel('Finestra Temporale (s)')
        ax4.set_ylabel('Correlazione')
        ax4.set_title('Effetto Finestra Temporale')
        ax4.grid(True, alpha=0.3)
    
    # Plot 5: Effetti sistematici - binning
    ax5 = axes[1, 0]
    if 'binning' in systematic_results:
        n_bins = systematic_results['binning']['n_bins']
        correlations = systematic_results['binning']['correlations']
        valid_mask = ~np.isnan(correlations)
        
        ax5.plot(np.array(n_bins)[valid_mask], np.array(correlations)[valid_mask], 
                'go-', linewidth=2, markersize=8)
        ax5.set_xlabel('Numero Bins Energetici')
        ax5.set_ylabel('Correlazione Media')
        ax5.set_title('Effetto Binning Energetico')
        ax5.grid(True, alpha=0.3)
    
    # Plot 6: Cross-validation lineare
    ax6 = axes[1, 1]
    if cv_results['linear_regression'] is not None:
        scores = cv_results['linear_regression']['scores']
        ax6.bar(range(len(scores)), scores, color='lightcoral', alpha=0.7)
        ax6.axhline(cv_results['linear_regression']['mean_score'], color='red', 
                   linestyle='--', label=f'Media: {cv_results["linear_regression"]["mean_score"]:.3f}')
        ax6.set_xlabel('Fold CV')
        ax6.set_ylabel('Score (MSE)')
        ax6.set_title('Cross-Validation Lineare')
        ax6.legend()
    
    # Plot 7: Cross-validation polinomiale
    ax7 = axes[1, 2]
    if cv_results['polynomial_regression'] is not None:
        scores = cv_results['polynomial_regression']['scores']
        ax7.bar(range(len(scores)), scores, color='lightgreen', alpha=0.7)
        ax7.axhline(cv_results['polynomial_regression']['mean_score'], color='green', 
                   linestyle='--', label=f'Media: {cv_results["polynomial_regression"]["mean_score"]:.3f}')
        ax7.set_xlabel('Fold CV')
        ax7.set_ylabel('Score (MSE)')
        ax7.set_title('Cross-Validation Polinomiale')
        ax7.legend()
    
    # Plot 8: Confronto modelli semplici vs avanzati
    ax8 = axes[1, 3]
    # Qui potresti confrontare con modelli semplici della FASE 2
    ax8.text(0.5, 0.5, 'Confronto\nModelli\nSemplici vs\nAvanzati', 
            ha='center', va='center', transform=ax8.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    ax8.set_title('Confronto Metodologie')
    
    # Plot 9-12: Analisi residui per ogni modello avanzato
    plot_idx = 8
    for model_name, model in advanced_models.items():
        if model is None or plot_idx >= 12:
            continue
            
        row = plot_idx // 4
        col = plot_idx % 4
        ax = axes[row, col]
        
        if model_name == 'temporal_evolving':
            times_pred = model_temporal_evolving_lag(times, energies, 
                                                   model['t0'], model['alpha'], model['beta'], model['gamma'])
        elif model_name == 'multi_component':
            times_pred = model_multi_component_lag(times, energies,
                                                 model['t0'], model['alpha1'], model['beta1'], 
                                                 model['alpha2'], model['beta2'], model['E_break'])
        elif model_name == 'nonlinear_energy':
            times_pred = model_nonlinear_energy_lag(times, energies,
                                                  model['t0'], model['alpha'], model['beta'], model['gamma'])
        elif model_name == 'temporal_band':
            times_pred = model_temporal_band_lag(times, energies,
                                               model['t0'], model['alpha'], model['beta'], 
                                               model['t_break'], model['alpha2'], model['beta2'])
        else:
            continue
        
        residuals = times - times_pred
        ax.scatter(energies, residuals, alpha=0.6, s=20, c='purple', edgecolors='none')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel('Energia (GeV)')
        ax.set_ylabel('Residui (s)')
        ax.set_title(f'Residui - {model["type"]}')
        ax.set_xscale('log')
        
        # Statistiche residui
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        ax.text(0.05, 0.95, f'μ = {mean_residual:.3f}\nσ = {std_residual:.3f}', 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plot_idx += 1
    
    plt.tight_layout()
    plt.savefig(f'advanced_lag_analysis_{grb_name.lower()}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafici salvati: advanced_lag_analysis_{grb_name.lower()}.png")

def main():
    """Funzione principale per analisi avanzata lag"""
    
    print("="*70)
    print("FASE 4: ANALISI AVANZATA DEI LAG")
    print("Verifica se il residuo 3.32σ è QG reale o bias sistematico")
    print("="*70)
    
    # Carica risultati FASE 3
    qg_results = load_qg_residual_results()
    
    if qg_results is None:
        return
    
    print(f"📊 Caricati risultati di {len(qg_results)} GRB dalla FASE 3")
    
    # Configurazione GRB per caricamento dati originali
    grb_configs = {
        'GRB080916C': {'file': 'L251020154246F357373F64_EV00.fits', 'trigger': 243216266.0, 'z': 4.35},
        'GRB090902': {'file': 'L251020161615F357373F52_EV00.fits', 'trigger': 273581808.0, 'z': 1.822},
        'GRB090510': {'file': 'L251020161912F357373F19_EV00.fits', 'trigger': 263607281.0, 'z': 0.903},
        'GRB130427A': {'file': 'L251020164901F357373F96_EV00.fits', 'trigger': 388798843.0, 'z': 0.34}
    }
    
    all_results = []
    
    for result in qg_results:
        grb_name = result['grb_name']
        
        if grb_name not in grb_configs:
            continue
            
        print(f"\n🔬 ANALISI AVANZATA LAG: {grb_name}")
        print("-" * 50)
        
        # Carica dati originali
        config = grb_configs[grb_name]
        try:
            with fits.open(config['file']) as hdul:
                events_data = hdul['EVENTS'].data
                
                if events_data is None:
                    print(f"❌ Nessun dato in {config['file']}")
                    continue
                
                times_original = events_data['TIME'] - config['trigger']
                energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
                
                # Quality cuts - molto permissivi per GRB130427A
                if 'F357373F96' in config['file']:  # GRB130427A nuovo file
                    quality_cuts = (energies > 0.01) & (times_original >= -1000) & (times_original <= 10000)
                else:
                    quality_cuts = (energies > 0.1) & (times_original >= 0) & (times_original <= 2500)
                times_filtered = times_original[quality_cuts]
                energies_filtered = energies[quality_cuts]
                
                if len(times_filtered) < 30:
                    print(f"❌ Dati insufficienti per {grb_name}")
                    continue
                
                print(f"  Fotoni: {len(times_filtered)}")
                print(f"  Range energia: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV")
                
        except Exception as e:
            print(f"❌ Errore caricamento {grb_name}: {e}")
            continue
        
        # Fit modelli lag avanzati
        print(f"📈 Fit modelli lag avanzati...")
        advanced_models = fit_advanced_lag_models(times_filtered, energies_filtered)
        
        # Analizza effetti sistematici
        print(f"🔍 Analisi effetti sistematici...")
        systematic_results = analyze_systematic_effects(times_filtered, energies_filtered)
        
        # Cross-validation
        print(f"🔍 Cross-validation...")
        cv_results = cross_validation_analysis(times_filtered, energies_filtered)
        
        # Crea grafici
        print(f"📊 Creazione grafici...")
        create_advanced_analysis_plots(grb_name, times_filtered, energies_filtered, 
                                     advanced_models, systematic_results, cv_results)
        
        # Salva risultati
        advanced_result = {
            'grb_name': grb_name,
            'n_photons': len(times_filtered),
            'energy_range': (float(energies_filtered.min()), float(energies_filtered.max())),
            'redshift': config['z'],
            'residual_significance': result['significance_corrected'],
            'advanced_models': {k: v for k, v in advanced_models.items() if v is not None},
            'systematic_results': systematic_results,
            'cv_results': cv_results
        }
        
        all_results.append(advanced_result)
    
    # Salva risultati completi
    with open('advanced_lag_analysis_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=convert_numpy)
    
    # Riassunto finale
    print(f"\n🎯 RISULTATI FINALI FASE 4:")
    print(f"  GRB analizzati: {len(all_results)}")
    
    for result in all_results:
        print(f"  {result['grb_name']}: Residuo {result['residual_significance']:.2f}σ")
        if result['advanced_models']:
            best_model = min(result['advanced_models'].items(), key=lambda x: x[1]['aic'])
            print(f"    Miglior modello: {best_model[1]['type']} (AIC={best_model[1]['aic']:.1f})")
    
    print("\n" + "="*70)
    print("FASE 4 COMPLETATA! Pronto per analisi finale!")
    print("="*70)

if __name__ == "__main__":
    main()
