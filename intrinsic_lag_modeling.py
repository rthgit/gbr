#!/usr/bin/env python3
"""
FASE 2: MODELLAZIONE LAG INTRINSECI
===================================

Modellazione avanzata dei lag intrinseci astrofisici per separare
effetti QG da fenomeni astrofisici nei dati GRB.

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
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib per headless
import matplotlib
matplotlib.use('Agg')
plt.rcParams['figure.figsize'] = (14, 10)
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

def load_detailed_results():
    """Carica risultati della FASE 1"""
    try:
        with open('detailed_energy_analysis_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ File detailed_energy_analysis_results.json non trovato!")
        print("Esegui prima detailed_energy_analysis.py")
        return None

def model_intrinsic_lag_power_law(E, t0, alpha, beta):
    """Modello power-law per lag intrinseci: t = t0 + alpha * E^beta"""
    return t0 + alpha * np.power(E, beta)

def model_intrinsic_lag_broken_power_law(E, t0, alpha1, beta1, alpha2, beta2, E_break):
    """Modello broken power-law per lag intrinseci"""
    result = np.zeros_like(E)
    mask_low = E < E_break
    mask_high = E >= E_break
    
    result[mask_low] = t0 + alpha1 * np.power(E[mask_low], beta1)
    result[mask_high] = t0 + alpha1 * np.power(E_break, beta1) + alpha2 * np.power(E[mask_high], beta2)
    
    return result

def model_intrinsic_lag_exponential(E, t0, tau, E_scale):
    """Modello esponenziale per lag intrinseci: t = t0 + tau * exp(-E/E_scale)"""
    return t0 + tau * np.exp(-E / E_scale)

def model_intrinsic_lag_logarithmic(E, t0, alpha, E_ref):
    """Modello logaritmico per lag intrinseci: t = t0 + alpha * log(E/E_ref)"""
    return t0 + alpha * np.log(E / E_ref)

def fit_intrinsic_lag_models(times, energies):
    """Fit tutti i modelli di lag intrinseci"""
    models = {}
    
    # Modello 1: Power-law
    try:
        def power_law(E, t0, alpha, beta):
            return model_intrinsic_lag_power_law(E, t0, alpha, beta)
        
        # Valori iniziali ottimizzati
        p0 = [np.mean(times), -1.0, -0.5]
        bounds = ([times.min(), -100, -2], [times.max(), 100, 2])
        
        popt, pcov = curve_fit(power_law, energies, times, p0=p0, bounds=bounds, maxfev=2000)
        t0, alpha, beta = popt
        
        # Calcola goodness of fit
        times_pred = power_law(energies, t0, alpha, beta)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 3
        chi2_red = chi2 / dof
        
        # Correlazione
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['power_law'] = {
            't0': float(t0),
            'alpha': float(alpha),
            'beta': float(beta),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 3 + chi2),  # AIC = 2k + χ²
            'type': 'Power-law Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit power-law: {e}")
        models['power_law'] = None
    
    # Modello 2: Broken power-law
    try:
        def broken_power_law(E, t0, alpha1, beta1, alpha2, beta2, E_break):
            return model_intrinsic_lag_broken_power_law(E, t0, alpha1, beta1, alpha2, beta2, E_break)
        
        # Valori iniziali
        E_break_init = np.median(energies)
        p0 = [np.mean(times), -1.0, -0.5, -0.5, -0.3, E_break_init]
        bounds = ([times.min(), -50, -2, -50, -2, energies.min()], 
                 [times.max(), 50, 2, 50, 2, energies.max()])
        
        popt, pcov = curve_fit(broken_power_law, energies, times, p0=p0, bounds=bounds, maxfev=3000)
        t0, alpha1, beta1, alpha2, beta2, E_break = popt
        
        # Goodness of fit
        times_pred = broken_power_law(energies, t0, alpha1, beta1, alpha2, beta2, E_break)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 6
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['broken_power_law'] = {
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
            'type': 'Broken Power-law Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit broken power-law: {e}")
        models['broken_power_law'] = None
    
    # Modello 3: Esponenziale
    try:
        def exponential(E, t0, tau, E_scale):
            return model_intrinsic_lag_exponential(E, t0, tau, E_scale)
        
        p0 = [np.mean(times), 1.0, np.median(energies)]
        bounds = ([times.min(), 0, energies.min()], [times.max(), 100, energies.max()])
        
        popt, pcov = curve_fit(exponential, energies, times, p0=p0, bounds=bounds, maxfev=2000)
        t0, tau, E_scale = popt
        
        times_pred = exponential(energies, t0, tau, E_scale)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 3
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['exponential'] = {
            't0': float(t0),
            'tau': float(tau),
            'E_scale': float(E_scale),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 3 + chi2),
            'type': 'Exponential Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit exponential: {e}")
        models['exponential'] = None
    
    # Modello 4: Logaritmico
    try:
        def logarithmic(E, t0, alpha, E_ref):
            return model_intrinsic_lag_logarithmic(E, t0, alpha, E_ref)
        
        E_ref_init = np.median(energies)
        p0 = [np.mean(times), -1.0, E_ref_init]
        bounds = ([times.min(), -100, energies.min()], [times.max(), 100, energies.max()])
        
        popt, pcov = curve_fit(logarithmic, energies, times, p0=p0, bounds=bounds, maxfev=2000)
        t0, alpha, E_ref = popt
        
        times_pred = logarithmic(energies, t0, alpha, E_ref)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 3
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['logarithmic'] = {
            't0': float(t0),
            'alpha': float(alpha),
            'E_ref': float(E_ref),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 3 + chi2),
            'type': 'Logarithmic Lag'
        }
    except Exception as e:
        print(f"⚠️ Errore fit logarithmic: {e}")
        models['logarithmic'] = None
    
    return models

def select_best_model(models):
    """Seleziona il miglior modello basato su AIC"""
    valid_models = {k: v for k, v in models.items() if v is not None}
    
    if not valid_models:
        return None, None
    
    # Trova modello con AIC minimo
    best_model_name = min(valid_models.keys(), key=lambda x: valid_models[x]['aic'])
    best_model = valid_models[best_model_name]
    
    return best_model_name, best_model

def subtract_intrinsic_lag(times, energies, best_model_name, best_model_params):
    """Sottrae il lag intrinseco dai dati"""
    
    if best_model_name == 'power_law':
        predicted_times = model_intrinsic_lag_power_law(energies, 
                                                       best_model_params['t0'],
                                                       best_model_params['alpha'],
                                                       best_model_params['beta'])
    elif best_model_name == 'broken_power_law':
        predicted_times = model_intrinsic_lag_broken_power_law(energies,
                                                              best_model_params['t0'],
                                                              best_model_params['alpha1'],
                                                              best_model_params['beta1'],
                                                              best_model_params['alpha2'],
                                                              best_model_params['beta2'],
                                                              best_model_params['E_break'])
    elif best_model_name == 'exponential':
        predicted_times = model_intrinsic_lag_exponential(energies,
                                                         best_model_params['t0'],
                                                         best_model_params['tau'],
                                                         best_model_params['E_scale'])
    elif best_model_name == 'logarithmic':
        predicted_times = model_intrinsic_lag_logarithmic(energies,
                                                         best_model_params['t0'],
                                                         best_model_params['alpha'],
                                                         best_model_params['E_ref'])
    else:
        return times, None
    
    # Sottrai il lag intrinseco
    corrected_times = times - predicted_times + best_model_params['t0']
    
    return corrected_times, predicted_times

def create_lag_modeling_plots(grb_name, times, energies, models, best_model_name, best_model, corrected_times, predicted_times):
    """Crea grafici per la modellazione dei lag intrinseci"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'Modellazione Lag Intrinseci - {grb_name}', fontsize=16, fontweight='bold')
    
    # Plot 1: Dati originali
    ax1 = axes[0, 0]
    ax1.scatter(energies, times, alpha=0.6, s=20, c='blue', edgecolors='none')
    ax1.set_xlabel('Energia (GeV)')
    ax1.set_ylabel('Tempo relativo (s)')
    ax1.set_title('Dati Originali')
    ax1.set_xscale('log')
    
    # Plot 2: Modelli fit
    ax2 = axes[0, 1]
    ax2.scatter(energies, times, alpha=0.3, s=10, c='gray', label='Dati')
    
    # Plot tutti i modelli validi
    E_fit = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 100)
    colors = ['red', 'blue', 'green', 'orange']
    
    for i, (model_name, model) in enumerate(models.items()):
        if model is None:
            continue
            
        if model_name == 'power_law':
            t_fit = model_intrinsic_lag_power_law(E_fit, model['t0'], model['alpha'], model['beta'])
        elif model_name == 'broken_power_law':
            t_fit = model_intrinsic_lag_broken_power_law(E_fit, model['t0'], model['alpha1'], model['beta1'], 
                                                       model['alpha2'], model['beta2'], model['E_break'])
        elif model_name == 'exponential':
            t_fit = model_intrinsic_lag_exponential(E_fit, model['t0'], model['tau'], model['E_scale'])
        elif model_name == 'logarithmic':
            t_fit = model_intrinsic_lag_logarithmic(E_fit, model['t0'], model['alpha'], model['E_ref'])
        else:
            continue
        
        style = '-' if model_name == best_model_name else '--'
        width = 3 if model_name == best_model_name else 1
        ax2.plot(E_fit, t_fit, color=colors[i], linestyle=style, linewidth=width,
                label=f'{model["type"]} (AIC={model["aic"]:.1f})')
    
    ax2.set_xlabel('Energia (GeV)')
    ax2.set_ylabel('Tempo relativo (s)')
    ax2.set_title('Modelli Lag Intrinseci')
    ax2.set_xscale('log')
    ax2.legend()
    
    # Plot 3: Confronto modelli (AIC)
    ax3 = axes[0, 2]
    model_names = []
    aic_values = []
    colors_bar = []
    
    for model_name, model in models.items():
        if model is not None:
            model_names.append(model['type'])
            aic_values.append(model['aic'])
            colors_bar.append('red' if model_name == best_model_name else 'lightblue')
    
    if model_names:
        bars = ax3.bar(range(len(model_names)), aic_values, color=colors_bar, alpha=0.7)
        ax3.set_xticks(range(len(model_names)))
        ax3.set_xticklabels(model_names, rotation=45, ha='right')
        ax3.set_ylabel('AIC')
        ax3.set_title('Confronto Modelli (AIC)')
        
        # Evidenzia il migliore
        if best_model_name in models and models[best_model_name] is not None:
            best_idx = list(models.keys()).index(best_model_name)
            bars[best_idx].set_edgecolor('darkred')
            bars[best_idx].set_linewidth(3)
    
    # Plot 4: Dati corretti
    ax4 = axes[1, 0]
    ax4.scatter(energies, corrected_times, alpha=0.6, s=20, c='green', edgecolors='none')
    ax4.set_xlabel('Energia (GeV)')
    ax4.set_ylabel('Tempo corretto (s)')
    ax4.set_title('Dati dopo Sottrazione Lag')
    ax4.set_xscale('log')
    
    # Calcola correlazione corretta
    if len(corrected_times) > 2:
        correlation_corrected = np.corrcoef(energies, corrected_times)[0, 1]
        significance_corrected = abs(correlation_corrected) * np.sqrt(len(corrected_times) - 2) / np.sqrt(1 - correlation_corrected**2)
        ax4.text(0.05, 0.95, f'r = {correlation_corrected:.3f}\nσ = {significance_corrected:.2f}', 
                transform=ax4.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Plot 5: Residui
    ax5 = axes[1, 1]
    if predicted_times is not None:
        residuals = times - predicted_times
        ax5.scatter(energies, residuals, alpha=0.6, s=20, c='purple', edgecolors='none')
        ax5.axhline(0, color='black', linestyle='--', alpha=0.5)
        ax5.set_xlabel('Energia (GeV)')
        ax5.set_ylabel('Residui (s)')
        ax5.set_title('Residui del Fit')
        ax5.set_xscale('log')
        
        # Statistiche residui
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        ax5.text(0.05, 0.95, f'μ = {mean_residual:.3f}\nσ = {std_residual:.3f}', 
                transform=ax5.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Plot 6: Confronto prima/dopo
    ax6 = axes[1, 2]
    
    # Correlazione originale
    correlation_original = np.corrcoef(energies, times)[0, 1]
    significance_original = abs(correlation_original) * np.sqrt(len(times) - 2) / np.sqrt(1 - correlation_original**2)
    
    # Correlazione corretta
    if len(corrected_times) > 2:
        correlation_corrected = np.corrcoef(energies, corrected_times)[0, 1]
        significance_corrected = abs(correlation_corrected) * np.sqrt(len(corrected_times) - 2) / np.sqrt(1 - correlation_corrected**2)
        
        categories = ['Originale', 'Corretto']
        correlations = [correlation_original, correlation_corrected]
        significances = [significance_original, significance_corrected]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax6_twin = ax6.twinx()
        bars1 = ax6.bar(x - width/2, correlations, width, label='Correlazione', color='lightblue', alpha=0.7)
        bars2 = ax6_twin.bar(x + width/2, significances, width, label='Significatività', color='lightcoral', alpha=0.7)
        
        ax6.set_xlabel('Dataset')
        ax6.set_ylabel('Correlazione r', color='blue')
        ax6_twin.set_ylabel('Significatività σ', color='red')
        ax6.set_title('Confronto Prima/Dopo Correzione')
        ax6.set_xticks(x)
        ax6.set_xticklabels(categories)
        
        # Aggiungi valori sui bar
        for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
            height1 = bar1.get_height()
            height2 = bar2.get_height()
            ax6.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.01,
                    f'{height1:.3f}', ha='center', va='bottom', fontsize=8)
            ax6_twin.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.1,
                         f'{height2:.2f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'intrinsic_lag_modeling_{grb_name.lower()}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafici salvati: intrinsic_lag_modeling_{grb_name.lower()}.png")

def main():
    """Funzione principale per modellazione lag intrinseci"""
    
    print("="*70)
    print("FASE 2: MODELLAZIONE LAG INTRINSECI")
    print("Separazione effetti QG da fenomeni astrofisici")
    print("="*70)
    
    # Carica risultati FASE 1
    detailed_results = load_detailed_results()
    
    if detailed_results is None:
        return
    
    print(f"📊 Caricati risultati di {len(detailed_results)} GRB dalla FASE 1")
    
    # Configurazione GRB per caricamento dati originali
    grb_configs = {
        'GRB080916C': {'file': 'L251020154246F357373F64_EV00.fits', 'trigger': 243216266.0, 'z': 4.35},
        'GRB090902': {'file': 'L251020161615F357373F52_EV00.fits', 'trigger': 273581808.0, 'z': 1.822},
        'GRB090510': {'file': 'L251020161912F357373F19_EV00.fits', 'trigger': 263607281.0, 'z': 0.903},
        'GRB130427A': {'file': 'L251020164901F357373F96_EV00.fits', 'trigger': 388798843.0, 'z': 0.34}
    }
    
    all_results = []
    
    for result in detailed_results:
        grb_name = result['grb_name']
        
        if grb_name not in grb_configs:
            continue
            
        print(f"\n🔬 MODELLAZIONE LAG INTRINSECI: {grb_name}")
        print("-" * 50)
        
        # Carica dati originali
        config = grb_configs[grb_name]
        try:
            with fits.open(config['file']) as hdul:
                events_data = hdul['EVENTS'].data
                
                if events_data is None:
                    print(f"❌ Nessun dato in {config['file']}")
                    continue
                
                times = events_data['TIME'] - config['trigger']
                energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
                
                # Quality cuts - molto permissivi per GRB130427A
                if 'F357373F96' in config['file']:  # GRB130427A nuovo file
                    quality_cuts = (energies > 0.01) & (times >= -1000) & (times <= 10000)
                else:
                    quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
                times_filtered = times[quality_cuts]
                energies_filtered = energies[quality_cuts]
                
                if len(times_filtered) < 30:
                    print(f"❌ Dati insufficienti per {grb_name}")
                    continue
                
                print(f"  Fotoni: {len(times_filtered)}")
                print(f"  Range energia: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV")
                
        except Exception as e:
            print(f"❌ Errore caricamento {grb_name}: {e}")
            continue
        
        # Fit modelli lag intrinseci
        print(f"📈 Fit modelli lag intrinseci...")
        models = fit_intrinsic_lag_models(times_filtered, energies_filtered)
        
        # Seleziona miglior modello
        best_model_name, best_model = select_best_model(models)
        
        if best_model is None:
            print(f"❌ Nessun modello valido per {grb_name}")
            continue
        
        print(f"✅ Miglior modello: {best_model['type']} (AIC={best_model['aic']:.1f})")
        print(f"  Chi²/DOF: {best_model['chi2_red']:.2f}")
        print(f"  Correlazione: {best_model['correlation']:.3f}")
        
        # Sottrai lag intrinseco
        print(f"🔧 Sottrazione lag intrinseco...")
        corrected_times, predicted_times = subtract_intrinsic_lag(times_filtered, energies_filtered, 
                                                                best_model_name, best_model)
        
        # Calcola correlazione corretta
        if len(corrected_times) > 2:
            correlation_corrected = np.corrcoef(energies_filtered, corrected_times)[0, 1]
            significance_corrected = abs(correlation_corrected) * np.sqrt(len(corrected_times) - 2) / np.sqrt(1 - correlation_corrected**2)
            
            print(f"  Correlazione originale: {result['total_correlation']:.3f} ({result['total_significance']:.2f}σ)")
            print(f"  Correlazione corretta: {correlation_corrected:.3f} ({significance_corrected:.2f}σ)")
            
            # Calcola miglioramento
            improvement = result['total_significance'] - significance_corrected
            print(f"  Miglioramento: {improvement:.2f}σ")
        else:
            correlation_corrected = 0
            significance_corrected = 0
            improvement = 0
        
        # Crea grafici
        print(f"📊 Creazione grafici...")
        create_lag_modeling_plots(grb_name, times_filtered, energies_filtered, models, 
                                best_model_name, best_model, corrected_times, predicted_times)
        
        # Salva risultati
        lag_result = {
            'grb_name': grb_name,
            'n_photons': len(times_filtered),
            'energy_range': (float(energies_filtered.min()), float(energies_filtered.max())),
            'redshift': config['z'],
            'models_fit': {k: v is not None for k, v in models.items()},
            'best_model': {
                'name': best_model_name,
                'type': best_model['type'],
                'aic': best_model['aic'],
                'chi2_red': best_model['chi2_red'],
                'correlation': best_model['correlation'],
                'parameters': {k: v for k, v in best_model.items() if k not in ['type', 'aic', 'chi2', 'chi2_red', 'dof', 'correlation']}
            },
            'correlation_original': result['total_correlation'],
            'significance_original': result['total_significance'],
            'correlation_corrected': float(correlation_corrected),
            'significance_corrected': float(significance_corrected),
            'improvement_sigma': float(improvement),
            'models_detail': models
        }
        
        all_results.append(lag_result)
    
    # Salva risultati completi
    with open('intrinsic_lag_modeling_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=convert_numpy)
    
    # Riassunto finale
    print(f"\n🎯 RISULTATI FINALI FASE 2:")
    print(f"  GRB analizzati: {len(all_results)}")
    
    total_improvement = 0
    for result in all_results:
        print(f"  {result['grb_name']}: {result['significance_original']:.2f}σ → {result['significance_corrected']:.2f}σ "
              f"(Δ={result['improvement_sigma']:.2f}σ)")
        total_improvement += result['improvement_sigma']
    
    print(f"  Miglioramento totale: {total_improvement:.2f}σ")
    print(f"  Risultati salvati: intrinsic_lag_modeling_results.json")
    
    print("\n" + "="*70)
    print("FASE 2 COMPLETATA! Pronto per FASE 3!")
    print("="*70)

if __name__ == "__main__":
    main()
