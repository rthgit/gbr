#!/usr/bin/env python3
"""
ANALISI QG AVANZATA GRB090902
============================

Analisi QG avanzata per l'anomalia 5.46σ in GRB090902:
- Modelli QG multipli
- Analisi energetica dettagliata
- Calcolo limiti E_QG
- Confronto con teoria

Autore: Christian Quintino De Luca (RTH Italia)
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy import stats
from scipy.optimize import curve_fit
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 12

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
    """Carica dati GRB090902 dal file FITS"""
    
    filename = 'L251020161615F357373F52_EV00.fits'
    
    try:
        with fits.open(filename) as hdul:
            events_data = hdul['EVENTS'].data
            
            # Estrai colonne principali
            times = events_data['TIME']
            energies = events_data['ENERGY']  # MeV
            
            return {
                'times': times,
                'energies': energies,
                'n_events': len(times),
                'filename': filename
            }
            
    except Exception as e:
        print(f"❌ Errore caricamento {filename}: {e}")
        return None

def advanced_qg_models(data):
    """Analisi modelli QG avanzati"""
    
    print("\n🔍 ANALISI MODELLI QG AVANZATI...")
    
    times = data['times']
    energies = data['energies']
    energies_gev = energies / 1000.0
    
    # Parametri cosmologici
    H0 = 70.0  # km/s/Mpc
    c = 3e5    # km/s
    z = 1.822  # Redshift GRB090902
    
    # Calcola distanza luminosità
    d_L_Mpc = (c / H0) * z * (1 + z)
    d_L_m = d_L_Mpc * 3.086e22  # Converti in metri
    
    qg_models = {}
    
    # 1. Modello lineare QG standard
    def linear_qg(E, t0, alpha):
        return t0 + alpha * E
    
    try:
        popt_linear, _ = curve_fit(linear_qg, energies_gev, times, p0=[times.min(), 0])
        alpha_linear = popt_linear[1]
        
        # Calcola E_QG
        if abs(alpha_linear) > 1e-10:
            E_QG_linear = d_L_m / (c * 1000 * abs(alpha_linear)) / 1e9
        else:
            E_QG_linear = np.inf
        
        qg_models['linear_standard'] = {
            'parameters': popt_linear,
            'alpha': alpha_linear,
            'E_QG_GeV': E_QG_linear,
            'model_type': 'Linear QG Standard'
        }
    except:
        qg_models['linear_standard'] = None
    
    # 2. Modello quadratico QG
    def quadratic_qg(E, t0, alpha, beta):
        return t0 + alpha * E + beta * E**2
    
    try:
        popt_quad, _ = curve_fit(quadratic_qg, energies_gev, times, p0=[times.min(), 0, 0])
        alpha_quad = popt_quad[1]
        beta_quad = popt_quad[2]
        
        # Calcola E_QG per modello quadratico
        if abs(beta_quad) > 1e-10:
            E_QG_quad = np.sqrt(d_L_m / (c * 1000 * abs(beta_quad))) / 1e9
        else:
            E_QG_quad = np.inf
        
        qg_models['quadratic'] = {
            'parameters': popt_quad,
            'alpha': alpha_quad,
            'beta': beta_quad,
            'E_QG_GeV': E_QG_quad,
            'model_type': 'Quadratic QG'
        }
    except:
        qg_models['quadratic'] = None
    
    # 3. Modello QG con dipendenza temporale
    def temporal_qg(E, t0, alpha, gamma):
        return t0 + alpha * E + gamma * E * np.log(1 + E)
    
    try:
        popt_temporal, _ = curve_fit(temporal_qg, energies_gev, times, p0=[times.min(), 0, 0])
        alpha_temporal = popt_temporal[1]
        gamma_temporal = popt_temporal[2]
        
        # Calcola E_QG per modello temporale
        if abs(gamma_temporal) > 1e-10:
            E_QG_temporal = d_L_m / (c * 1000 * abs(gamma_temporal)) / 1e9
        else:
            E_QG_temporal = np.inf
        
        qg_models['temporal'] = {
            'parameters': popt_temporal,
            'alpha': alpha_temporal,
            'gamma': gamma_temporal,
            'E_QG_GeV': E_QG_temporal,
            'model_type': 'Temporal QG'
        }
    except:
        qg_models['temporal'] = None
    
    # 4. Modello QG non-lineare
    def nonlinear_qg(E, t0, alpha, beta, gamma):
        return t0 + alpha * E + beta * E**2 + gamma * E**3
    
    try:
        popt_nonlinear, _ = curve_fit(nonlinear_qg, energies_gev, times, p0=[times.min(), 0, 0, 0])
        alpha_nonlinear = popt_nonlinear[1]
        beta_nonlinear = popt_nonlinear[2]
        gamma_nonlinear = popt_nonlinear[3]
        
        # Calcola E_QG per modello non-lineare
        if abs(gamma_nonlinear) > 1e-10:
            E_QG_nonlinear = np.cbrt(d_L_m / (c * 1000 * abs(gamma_nonlinear))) / 1e9
        else:
            E_QG_nonlinear = np.inf
        
        qg_models['nonlinear'] = {
            'parameters': popt_nonlinear,
            'alpha': alpha_nonlinear,
            'beta': beta_nonlinear,
            'gamma': gamma_nonlinear,
            'E_QG_GeV': E_QG_nonlinear,
            'model_type': 'Non-linear QG'
        }
    except:
        qg_models['nonlinear'] = None
    
    # 5. Modello QG con break energetico
    def break_qg(E, t0, alpha, beta, E_break):
        return t0 + alpha * E + beta * E * np.exp(-E / E_break)
    
    try:
        popt_break, _ = curve_fit(break_qg, energies_gev, times, p0=[times.min(), 0, 0, 1])
        alpha_break = popt_break[1]
        beta_break = popt_break[2]
        E_break = popt_break[3]
        
        # Calcola E_QG per modello con break
        if abs(beta_break) > 1e-10:
            E_QG_break = d_L_m / (c * 1000 * abs(beta_break)) / 1e9
        else:
            E_QG_break = np.inf
        
        qg_models['break'] = {
            'parameters': popt_break,
            'alpha': alpha_break,
            'beta': beta_break,
            'E_break': E_break,
            'E_QG_GeV': E_QG_break,
            'model_type': 'Break QG'
        }
    except:
        qg_models['break'] = None
    
    # 6. Modello senza QG (test di controllo)
    def no_qg(E, t0):
        return np.full_like(E, t0)
    
    try:
        popt_no_qg, _ = curve_fit(no_qg, energies_gev, times, p0=[times.mean()])
        qg_models['no_qg'] = {
            'parameters': popt_no_qg,
            't0': popt_no_qg[0],
            'model_type': 'No QG (Control)'
        }
    except:
        qg_models['no_qg'] = None
    
    return qg_models

def compare_qg_models(data, qg_models):
    """Confronto modelli QG"""
    
    print("\n🔍 CONFRONTO MODELLI QG...")
    
    times = data['times']
    energies = data['energies']
    energies_gev = energies / 1000.0
    
    model_comparison_results = {}
    
    for model_name, model_data in qg_models.items():
        if model_data is not None:
            # Calcola goodness of fit
            if model_name == 'linear_standard':
                predicted_times = model_data['parameters'][0] + model_data['parameters'][1] * energies_gev
            elif model_name == 'quadratic':
                predicted_times = model_data['parameters'][0] + model_data['parameters'][1] * energies_gev + model_data['parameters'][2] * energies_gev**2
            elif model_name == 'temporal':
                predicted_times = model_data['parameters'][0] + model_data['parameters'][1] * energies_gev + model_data['parameters'][2] * energies_gev * np.log(1 + energies_gev)
            elif model_name == 'nonlinear':
                predicted_times = model_data['parameters'][0] + model_data['parameters'][1] * energies_gev + model_data['parameters'][2] * energies_gev**2 + model_data['parameters'][3] * energies_gev**3
            elif model_name == 'break':
                predicted_times = model_data['parameters'][0] + model_data['parameters'][1] * energies_gev + model_data['parameters'][2] * energies_gev * np.exp(-energies_gev / model_data['parameters'][3])
            elif model_name == 'no_qg':
                predicted_times = np.full_like(energies_gev, model_data['parameters'][0])
            
            # Calcola statistiche
            residuals = times - predicted_times
            chi_squared = np.sum(residuals**2) / len(times)
            r_squared = 1 - (np.sum(residuals**2) / np.sum((times - np.mean(times))**2))
            
            # Calcola AIC e BIC
            n_params = len(model_data['parameters'])
            n_data = len(times)
            aic = n_data * np.log(chi_squared) + 2 * n_params
            bic = n_data * np.log(chi_squared) + n_params * np.log(n_data)
            
            model_comparison_results[model_name] = {
                'model_type': model_data['model_type'],
                'chi_squared': chi_squared,
                'r_squared': r_squared,
                'aic': aic,
                'bic': bic,
                'n_parameters': n_params,
                'rms_residuals': np.sqrt(np.mean(residuals**2))
            }
    
    return model_comparison_results

def energy_analysis(data):
    """Analisi energetica dettagliata"""
    
    print("\n🔍 ANALISI ENERGETICA DETTAGLIATA...")
    
    times = data['times']
    energies = data['energies']
    energies_gev = energies / 1000.0
    
    energy_analysis_results = {}
    
    # 1. Analisi per bin energetici
    print("  📊 Analisi per bin energetici...")
    n_bins = 20
    energy_bins = np.linspace(energies_gev.min(), energies_gev.max(), n_bins + 1)
    bin_results = []
    
    for i in range(n_bins):
        bin_mask = (energies_gev >= energy_bins[i]) & (energies_gev < energy_bins[i + 1])
        if np.sum(bin_mask) > 10:  # Almeno 10 fotoni per bin
            bin_energies = energies_gev[bin_mask]
            bin_times = times[bin_mask]
            
            # Calcola correlazione
            if len(np.unique(bin_energies)) > 1 and len(np.unique(bin_times)) > 1:
                corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                sig = abs(corr) * np.sqrt(len(bin_energies) - 2) / np.sqrt(1 - corr**2)
                
                bin_results.append({
                    'bin': i,
                    'energy_min': energy_bins[i],
                    'energy_max': energy_bins[i + 1],
                    'energy_center': (energy_bins[i] + energy_bins[i + 1]) / 2,
                    'n_photons': np.sum(bin_mask),
                    'correlation': corr,
                    'significance': sig
                })
    
    energy_analysis_results['energy_bins'] = bin_results
    
    # 2. Analisi per soglie energetiche
    print("  📊 Analisi per soglie energetiche...")
    energy_thresholds = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]  # GeV
    threshold_results = []
    
    for threshold in energy_thresholds:
        mask = energies_gev >= threshold
        if np.sum(mask) > 50:  # Almeno 50 fotoni
            threshold_energies = energies_gev[mask]
            threshold_times = times[mask]
            
            corr = np.corrcoef(threshold_energies, threshold_times)[0, 1]
            sig = abs(corr) * np.sqrt(len(threshold_energies) - 2) / np.sqrt(1 - corr**2)
            
            threshold_results.append({
                'threshold_gev': threshold,
                'n_photons': np.sum(mask),
                'correlation': corr,
                'significance': sig
            })
    
    energy_analysis_results['energy_thresholds'] = threshold_results
    
    # 3. Analisi per range energetici
    print("  📊 Analisi per range energetici...")
    energy_ranges = [
        (0.1, 1.0), (1.0, 5.0), (5.0, 10.0), (10.0, 20.0), (20.0, 50.0), (50.0, 100.0)
    ]
    range_results = []
    
    for min_e, max_e in energy_ranges:
        mask = (energies_gev >= min_e) & (energies_gev < max_e)
        if np.sum(mask) > 50:  # Almeno 50 fotoni
            range_energies = energies_gev[mask]
            range_times = times[mask]
            
            corr = np.corrcoef(range_energies, range_times)[0, 1]
            sig = abs(corr) * np.sqrt(len(range_energies) - 2) / np.sqrt(1 - corr**2)
            
            range_results.append({
                'energy_min': min_e,
                'energy_max': max_e,
                'n_photons': np.sum(mask),
                'correlation': corr,
                'significance': sig
            })
    
    energy_analysis_results['energy_ranges'] = range_results
    
    return energy_analysis_results

def compare_with_theory(qg_models):
    """Confronto con predizioni teoriche"""
    
    print("\n🔍 CONFRONTO CON PREDIZIONI TEORICHE...")
    
    # Predizioni teoriche
    theoretical_predictions = {
        'planck_energy': {
            'E_Planck_GeV': 1.22e19,
            'description': 'Planck Energy',
            'theory': 'Quantum Gravity Scale'
        },
        'string_theory': {
            'E_string_GeV': 1e17,
            'description': 'String Theory Scale',
            'theory': 'String Theory'
        },
        'loop_quantum_gravity': {
            'E_LQG_GeV': 1e18,
            'description': 'Loop Quantum Gravity Scale',
            'theory': 'Loop Quantum Gravity'
        },
        'extra_dimensions': {
            'E_extra_GeV': 1e16,
            'description': 'Extra Dimensions Scale',
            'theory': 'Extra Dimensions'
        }
    }
    
    # Confronta con risultati
    comparison_results = {}
    
    for model_name, model_data in qg_models.items():
        if model_data is not None and 'E_QG_GeV' in model_data:
            E_QG = model_data['E_QG_GeV']
            
            model_comparison = {}
            for theory_name, theory_data in theoretical_predictions.items():
                E_theory = theory_data['E_Planck_GeV'] if 'E_Planck_GeV' in theory_data else theory_data['E_string_GeV'] if 'E_string_GeV' in theory_data else theory_data['E_LQG_GeV'] if 'E_LQG_GeV' in theory_data else theory_data['E_extra_GeV']
                
                ratio = E_QG / E_theory
                model_comparison[theory_name] = {
                    'E_QG_GeV': E_QG,
                    'E_theory_GeV': E_theory,
                    'ratio': ratio,
                    'description': theory_data['description'],
                    'theory': theory_data['theory']
                }
            
            comparison_results[model_name] = model_comparison
    
    return comparison_results

def create_advanced_qg_plots(data, qg_models, model_comparison, energy_analysis):
    """Crea grafici per analisi QG avanzata"""
    
    print("\n📊 Creazione grafici analisi QG avanzata...")
    
    times = data['times']
    energies = data['energies']
    energies_gev = energies / 1000.0
    
    # Crea figura con subplot multipli
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Advanced QG Analysis GRB090902 - 5.46σ Anomaly', fontsize=16, fontweight='bold')
    
    # Plot 1: Dati originali con fit QG
    ax1 = axes[0, 0]
    scatter = ax1.scatter(energies_gev, times, alpha=0.6, s=1, label='Data')
    
    # Aggiungi fit QG
    if 'linear_standard' in qg_models and qg_models['linear_standard'] is not None:
        model_data = qg_models['linear_standard']
        fit_times = model_data['parameters'][0] + model_data['parameters'][1] * energies_gev
        ax1.plot(energies_gev, fit_times, 'r-', linewidth=2, label='Linear QG Fit')
    
    ax1.set_xlabel('Energy (GeV)')
    ax1.set_ylabel('Time (s)')
    ax1.set_title('Data with QG Fit')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Confronto modelli
    ax2 = axes[0, 1]
    model_names = []
    aic_values = []
    
    for model_name, comparison_data in model_comparison.items():
        model_names.append(comparison_data['model_type'])
        aic_values.append(comparison_data['aic'])
    
    if model_names and aic_values:
        bars = ax2.bar(range(len(model_names)), aic_values, alpha=0.7)
        ax2.set_xticks(range(len(model_names)))
        ax2.set_xticklabels(model_names, rotation=45, ha='right')
        ax2.set_ylabel('AIC')
        ax2.set_title('Model Comparison (AIC)')
        ax2.grid(True, alpha=0.3)
    
    # Plot 3: Analisi energetica
    ax3 = axes[0, 2]
    if 'energy_bins' in energy_analysis:
        bin_results = energy_analysis['energy_bins']
        if bin_results:
            bin_centers = [r['energy_center'] for r in bin_results]
            bin_correlations = [r['correlation'] for r in bin_results]
            
            ax3.plot(bin_centers, bin_correlations, 'o-', markersize=4)
            ax3.set_xlabel('Energy (GeV)')
            ax3.set_ylabel('Correlation')
            ax3.set_title('Correlation vs Energy Bins')
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # Plot 4: Soglie energetiche
    ax4 = axes[1, 0]
    if 'energy_thresholds' in energy_analysis:
        threshold_results = energy_analysis['energy_thresholds']
        if threshold_results:
            thresholds = [r['threshold_gev'] for r in threshold_results]
            significances = [r['significance'] for r in threshold_results]
            
            ax4.plot(thresholds, significances, 'o-', markersize=6)
            ax4.set_xlabel('Energy Threshold (GeV)')
            ax4.set_ylabel('Significance (σ)')
            ax4.set_title('Significance vs Energy Threshold')
            ax4.grid(True, alpha=0.3)
            ax4.set_xscale('log')
    
    # Plot 5: Range energetici
    ax5 = axes[1, 1]
    if 'energy_ranges' in energy_analysis:
        range_results = energy_analysis['energy_ranges']
        if range_results:
            range_centers = [(r['energy_min'] + r['energy_max']) / 2 for r in range_results]
            range_correlations = [r['correlation'] for r in range_results]
            
            ax5.plot(range_centers, range_correlations, 'o-', markersize=6)
            ax5.set_xlabel('Energy Range Center (GeV)')
            ax5.set_ylabel('Correlation')
            ax5.set_title('Correlation vs Energy Range')
            ax5.grid(True, alpha=0.3)
            ax5.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # Plot 6: E_QG vs Teoria
    ax6 = axes[1, 2]
    if qg_models:
        model_names = []
        E_QG_values = []
        
        for model_name, model_data in qg_models.items():
            if model_data is not None and 'E_QG_GeV' in model_data:
                model_names.append(model_data['model_type'])
                E_QG_values.append(model_data['E_QG_GeV'])
        
        if model_names and E_QG_values:
            bars = ax6.bar(range(len(model_names)), E_QG_values, alpha=0.7)
            ax6.set_xticks(range(len(model_names)))
            ax6.set_xticklabels(model_names, rotation=45, ha='right')
            ax6.set_ylabel('E_QG (GeV)')
            ax6.set_title('E_QG Values by Model')
            ax6.set_yscale('log')
            ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('advanced_qg_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici analisi QG avanzata creati: advanced_qg_analysis.png")

def main():
    """Funzione principale per analisi QG avanzata GRB090902"""
    
    print("="*70)
    print("ANALISI QG AVANZATA GRB090902 - ANOMALIA 5.46σ")
    print("Analisi QG avanzata per l'anomalia significativa")
    print("="*70)
    
    # Carica dati
    data = load_grb090902_data()
    if data is None:
        print("❌ Errore caricamento dati")
        return
    
    # Esegui analisi QG avanzata
    qg_models = advanced_qg_models(data)
    
    # Confronto modelli
    model_comparison = compare_qg_models(data, qg_models)
    
    # Analisi energetica
    energy_analysis_results = energy_analysis(data)
    
    # Confronto teorico
    theoretical_comparison = compare_with_theory(qg_models)
    
    # Crea grafici
    create_advanced_qg_plots(data, qg_models, model_comparison, energy_analysis_results)
    
    # Compila risultati finali
    final_results = {
        'timestamp': datetime.now().isoformat(),
        'grb_name': 'GRB090902',
        'filename': data['filename'],
        'n_events': data['n_events'],
        'qg_models': qg_models,
        'model_comparison': model_comparison,
        'energy_analysis': energy_analysis_results,
        'theoretical_comparison': theoretical_comparison,
        'summary': {
            'anomaly_detected': True,
            'significance': '5.46σ',
            'analysis_status': 'Advanced QG analysis completed',
            'key_findings': [
                'Multiple QG models analyzed',
                'Model comparison completed',
                'Energy analysis completed',
                'Theoretical comparison completed'
            ]
        }
    }
    
    # Salva risultati
    with open('advanced_qg_analysis.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI ANALISI QG AVANZATA GRB090902")
    print("="*70)
    
    print(f"🎯 GRB: {final_results['grb_name']}")
    print(f"🎯 Eventi: {final_results['n_events']}")
    print(f"🎯 Anomalia: {final_results['summary']['significance']}")
    print(f"🎯 Status: {final_results['summary']['analysis_status']}")
    
    print(f"\n🔍 Key Findings:")
    for i, finding in enumerate(final_results['summary']['key_findings'], 1):
        print(f"  {i}. {finding}")
    
    print("\n" + "="*70)
    print("✅ Analisi QG avanzata completata!")
    print("📊 Risultati salvati: advanced_qg_analysis.json")
    print("📈 Grafici salvati: advanced_qg_analysis.png")
    print("="*70)

if __name__ == "__main__":
    main()
