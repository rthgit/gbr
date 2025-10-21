#!/usr/bin/env python3
"""
FASE 3: RICERCA RESIDUI QG
===========================

Ricerca di effetti QG residui dopo sottrazione lag intrinseci
astrofisici nei dati GRB corretti.

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
plt.rcParams['figure.figsize'] = (16, 12)
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

def load_lag_modeling_results():
    """Carica risultati della FASE 2"""
    try:
        with open('intrinsic_lag_modeling_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ File intrinsic_lag_modeling_results.json non trovato!")
        print("Esegui prima intrinsic_lag_modeling.py")
        return None

def model_qg_linear(E, t0, E_QG, d_L):
    """Modello QG lineare: t = t0 + (d_L / c) * (E / E_QG)"""
    c = 3e8  # m/s
    return t0 + (d_L * 3.086e22 / c) * (E / E_QG)  # d_L in Mpc, E in GeV

def model_qg_quadratic(E, t0, E_QG, d_L):
    """Modello QG quadratico: t = t0 + (d_L / c) * (E / E_QG)^2"""
    c = 3e8  # m/s
    return t0 + (d_L * 3.086e22 / c) * ((E / E_QG) ** 2)

def fit_qg_models(times, energies, redshift):
    """Fit modelli QG sui dati corretti"""
    
    # Calcola distanza di luminosità
    H0 = 70.0  # km/s/Mpc
    c_km_s = 3e5  # km/s
    d_L = (c_km_s / H0) * redshift * (1 + redshift)  # Mpc
    
    models = {}
    
    # Modello 1: QG Lineare
    try:
        def qg_linear(E, t0, E_QG):
            return model_qg_linear(E, t0, E_QG, d_L)
        
        # Valori iniziali
        p0 = [np.mean(times), 1e19]  # E_QG iniziale vicino a Planck
        bounds = ([times.min(), 1e15], [times.max(), 1e25])
        
        popt, pcov = curve_fit(qg_linear, energies, times, p0=p0, bounds=bounds, maxfev=2000)
        t0, E_QG = popt
        
        # Goodness of fit
        times_pred = qg_linear(energies, t0, E_QG)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 2
        chi2_red = chi2 / dof
        
        # Correlazione
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['qg_linear'] = {
            't0': float(t0),
            'E_QG': float(E_QG),
            'd_L': float(d_L),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 2 + chi2),
            'type': 'QG Linear'
        }
    except Exception as e:
        print(f"⚠️ Errore fit QG linear: {e}")
        models['qg_linear'] = None
    
    # Modello 2: QG Quadratico
    try:
        def qg_quadratic(E, t0, E_QG):
            return model_qg_quadratic(E, t0, E_QG, d_L)
        
        # Valori iniziali
        p0 = [np.mean(times), 1e19]
        bounds = ([times.min(), 1e15], [times.max(), 1e25])
        
        popt, pcov = curve_fit(qg_quadratic, energies, times, p0=p0, bounds=bounds, maxfev=2000)
        t0, E_QG = popt
        
        times_pred = qg_quadratic(energies, t0, E_QG)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 2
        chi2_red = chi2 / dof
        
        correlation = np.corrcoef(times, times_pred)[0, 1]
        
        models['qg_quadratic'] = {
            't0': float(t0),
            'E_QG': float(E_QG),
            'd_L': float(d_L),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 2 + chi2),
            'type': 'QG Quadratic'
        }
    except Exception as e:
        print(f"⚠️ Errore fit QG quadratic: {e}")
        models['qg_quadratic'] = None
    
    # Modello 3: Nessun QG (costante)
    try:
        t0_constant = np.mean(times)
        times_pred = np.full_like(times, t0_constant)
        residuals = times - times_pred
        chi2 = np.sum((residuals / np.std(residuals))**2)
        dof = len(times) - 1
        chi2_red = chi2 / dof
        correlation = 0.0
        
        models['no_qg'] = {
            't0': float(t0_constant),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'dof': int(dof),
            'correlation': float(correlation),
            'aic': float(2 * 1 + chi2),
            'type': 'No QG (Constant)'
        }
    except Exception as e:
        print(f"⚠️ Errore fit no QG: {e}")
        models['no_qg'] = None
    
    return models

def calculate_qg_limits(times, energies, redshift, confidence_level=0.95):
    """Calcola limiti su E_QG usando likelihood ratio test"""
    
    # Calcola distanza di luminosità
    H0 = 70.0
    c_km_s = 3e5
    d_L = (c_km_s / H0) * redshift * (1 + redshift)
    
    # Fit modello senza QG
    t0_constant = np.mean(times)
    chi2_no_qg = np.sum(((times - t0_constant) / np.std(times))**2)
    
    # Test diversi valori di E_QG
    E_QG_values = np.logspace(15, 25, 100)  # GeV
    chi2_values = []
    
    for E_QG in E_QG_values:
        try:
            def qg_model(E, t0):
                return model_qg_linear(E, t0, E_QG, d_L)
            
            p0 = [np.mean(times)]
            bounds = ([times.min()], [times.max()])
            popt, _ = curve_fit(qg_model, energies, times, p0=p0, bounds=bounds, maxfev=1000)
            
            times_pred = qg_model(energies, popt[0])
            chi2 = np.sum(((times - times_pred) / np.std(times))**2)
            chi2_values.append(chi2)
            
        except:
            chi2_values.append(np.inf)
    
    chi2_values = np.array(chi2_values)
    
    # Trova limite di confidenza
    delta_chi2 = chi2_values - chi2_no_qg
    alpha = 1 - confidence_level
    
    # Trova E_QG limite
    limit_mask = delta_chi2 <= stats.chi2.ppf(1 - alpha, df=1)
    if np.any(limit_mask):
        E_QG_limit = np.max(E_QG_values[limit_mask])
    else:
        E_QG_limit = E_QG_values[0]
    
    return {
        'E_QG_limit': float(E_QG_limit),
        'confidence_level': confidence_level,
        'E_QG_values': E_QG_values.tolist(),
        'delta_chi2_values': delta_chi2.tolist()
    }

def create_qg_residual_plots(grb_name, times_original, times_corrected, energies, models, qg_limits, redshift):
    """Crea grafici per la ricerca residui QG"""
    
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle(f'Ricerca Residui QG - {grb_name}', fontsize=16, fontweight='bold')
    
    # Plot 1: Dati originali vs corretti
    ax1 = axes[0, 0]
    ax1.scatter(energies, times_original, alpha=0.4, s=15, c='red', label='Originali', edgecolors='none')
    ax1.scatter(energies, times_corrected, alpha=0.6, s=15, c='blue', label='Corretti', edgecolors='none')
    ax1.set_xlabel('Energia (GeV)')
    ax1.set_ylabel('Tempo relativo (s)')
    ax1.set_title('Confronto Dati Originali vs Corretti')
    ax1.set_xscale('log')
    ax1.legend()
    
    # Plot 2: Modelli QG fit
    ax2 = axes[0, 1]
    ax2.scatter(energies, times_corrected, alpha=0.4, s=10, c='gray', label='Dati corretti')
    
    E_fit = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 100)
    colors = ['red', 'blue', 'green']
    
    for i, (model_name, model) in enumerate(models.items()):
        if model is None:
            continue
            
        if model_name == 'qg_linear':
            t_fit = model_qg_linear(E_fit, model['t0'], model['E_QG'], model['d_L'])
        elif model_name == 'qg_quadratic':
            t_fit = model_qg_quadratic(E_fit, model['t0'], model['E_QG'], model['d_L'])
        elif model_name == 'no_qg':
            t_fit = np.full_like(E_fit, model['t0'])
        else:
            continue
        
        ax2.plot(E_fit, t_fit, color=colors[i], linewidth=2,
                label=f'{model["type"]} (AIC={model["aic"]:.1f})')
    
    ax2.set_xlabel('Energia (GeV)')
    ax2.set_ylabel('Tempo corretto (s)')
    ax2.set_title('Modelli QG sui Dati Corretti')
    ax2.set_xscale('log')
    ax2.legend()
    
    # Plot 3: Confronto AIC
    ax3 = axes[0, 2]
    model_names = []
    aic_values = []
    colors_bar = []
    
    for model_name, model in models.items():
        if model is not None:
            model_names.append(model['type'])
            aic_values.append(model['aic'])
            colors_bar.append('lightgreen' if model_name == 'no_qg' else 'lightblue')
    
    if model_names:
        bars = ax3.bar(range(len(model_names)), aic_values, color=colors_bar, alpha=0.7)
        ax3.set_xticks(range(len(model_names)))
        ax3.set_xticklabels(model_names, rotation=45, ha='right')
        ax3.set_ylabel('AIC')
        ax3.set_title('Confronto Modelli QG (AIC)')
        
        # Evidenzia il migliore
        best_idx = np.argmin(aic_values)
        bars[best_idx].set_edgecolor('darkgreen')
        bars[best_idx].set_linewidth(3)
    
    # Plot 4: Limiti E_QG
    ax4 = axes[1, 0]
    E_QG_values = np.array(qg_limits['E_QG_values'])
    delta_chi2 = np.array(qg_limits['delta_chi2_values'])
    
    ax4.plot(E_QG_values, delta_chi2, 'b-', linewidth=2)
    ax4.axhline(stats.chi2.ppf(0.95, df=1), color='red', linestyle='--', 
               label=f'95% CL (Δχ²={stats.chi2.ppf(0.95, df=1):.2f})')
    ax4.axvline(qg_limits['E_QG_limit'], color='red', linestyle=':', 
               label=f'E_QG > {qg_limits["E_QG_limit"]:.2e} GeV')
    
    ax4.set_xlabel('E_QG (GeV)')
    ax4.set_ylabel('Δχ²')
    ax4.set_title('Limiti su E_QG (95% CL)')
    ax4.set_xscale('log')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Residui QG
    ax5 = axes[1, 1]
    if models['no_qg'] is not None:
        t0_constant = models['no_qg']['t0']
        residuals = times_corrected - t0_constant
        ax5.scatter(energies, residuals, alpha=0.6, s=20, c='purple', edgecolors='none')
        ax5.axhline(0, color='black', linestyle='--', alpha=0.5)
        ax5.set_xlabel('Energia (GeV)')
        ax5.set_ylabel('Residui (s)')
        ax5.set_title('Residui QG')
        ax5.set_xscale('log')
        
        # Statistiche residui
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        ax5.text(0.05, 0.95, f'μ = {mean_residual:.3f}\nσ = {std_residual:.3f}', 
                transform=ax5.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Plot 6: Correlazione energia-tempo
    ax6 = axes[1, 2]
    
    # Correlazione originale e corretta
    corr_original = np.corrcoef(energies, times_original)[0, 1]
    sig_original = abs(corr_original) * np.sqrt(len(energies) - 2) / np.sqrt(1 - corr_original**2)
    
    corr_corrected = np.corrcoef(energies, times_corrected)[0, 1]
    sig_corrected = abs(corr_corrected) * np.sqrt(len(energies) - 2) / np.sqrt(1 - corr_corrected**2)
    
    categories = ['Originale', 'Corretto']
    correlations = [corr_original, corr_corrected]
    significances = [sig_original, sig_corrected]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax6_twin = ax6.twinx()
    bars1 = ax6.bar(x - width/2, correlations, width, label='Correlazione', color='lightblue', alpha=0.7)
    bars2 = ax6_twin.bar(x + width/2, significances, width, label='Significatività', color='lightcoral', alpha=0.7)
    
    ax6.set_xlabel('Dataset')
    ax6.set_ylabel('Correlazione r', color='blue')
    ax6_twin.set_ylabel('Significatività σ', color='red')
    ax6.set_title('Confronto Correlazioni')
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
    
    # Plot 7: Distribuzione residui
    ax7 = axes[2, 0]
    if models['no_qg'] is not None:
        t0_constant = models['no_qg']['t0']
        residuals = times_corrected - t0_constant
        ax7.hist(residuals, bins=30, alpha=0.7, color='purple', density=True)
        ax7.axvline(0, color='black', linestyle='--', alpha=0.5)
        ax7.set_xlabel('Residui (s)')
        ax7.set_ylabel('Densità')
        ax7.set_title('Distribuzione Residui')
        
        # Test normalità
        _, p_value = stats.normaltest(residuals)
        ax7.text(0.05, 0.95, f'Test normalità:\np = {p_value:.3f}', 
                transform=ax7.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Plot 8: Energia vs tempo (log scale)
    ax8 = axes[2, 1]
    ax8.scatter(energies, times_corrected, alpha=0.6, s=20, c='blue', edgecolors='none')
    ax8.set_xlabel('Energia (GeV)')
    ax8.set_ylabel('Tempo corretto (s)')
    ax8.set_title('Dati Corretti (Log Scale)')
    ax8.set_xscale('log')
    
    # Plot 9: Riassunto risultati
    ax9 = axes[2, 2]
    ax9.axis('off')
    
    # Testo riassuntivo
    summary_text = f"""
RISULTATI QG - {grb_name}

📊 Statistiche:
• Fotoni: {len(energies):,}
• Redshift: z = {redshift:.2f}
• d_L: {qg_limits.get('d_L', 0):.1f} Mpc

🎯 Limiti QG:
• E_QG > {qg_limits['E_QG_limit']:.2e} GeV
• Confidenza: {qg_limits['confidence_level']*100:.0f}%

📈 Correlazioni:
• Originale: r = {corr_original:.3f} ({sig_original:.2f}σ)
• Corretta: r = {corr_corrected:.3f} ({sig_corrected:.2f}σ)
• Miglioramento: {sig_original - sig_corrected:.2f}σ

🔬 Interpretazione:
"""
    
    if sig_corrected < 2:
        summary_text += "✅ NESSUNA EVIDENZA QG"
    elif sig_corrected < 3:
        summary_text += "⚠️ CORRELAZIONE DEBOLE"
    else:
        summary_text += "🚨 CORRELAZIONE SIGNIFICATIVA"
    
    ax9.text(0.05, 0.95, summary_text, transform=ax9.transAxes, 
            verticalalignment='top', fontfamily='monospace', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'qg_residual_search_{grb_name.lower()}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafici salvati: qg_residual_search_{grb_name.lower()}.png")

def main():
    """Funzione principale per ricerca residui QG"""
    
    print("="*70)
    print("FASE 3: RICERCA RESIDUI QG")
    print("Analisi effetti QG dopo sottrazione lag intrinseci")
    print("="*70)
    
    # Carica risultati FASE 2
    lag_results = load_lag_modeling_results()
    
    if lag_results is None:
        return
    
    print(f"📊 Caricati risultati di {len(lag_results)} GRB dalla FASE 2")
    
    # Configurazione GRB per caricamento dati originali
    grb_configs = {
        'GRB080916C': {'file': 'L251020154246F357373F64_EV00.fits', 'trigger': 243216266.0, 'z': 4.35},
        'GRB090902': {'file': 'L251020161615F357373F52_EV00.fits', 'trigger': 273581808.0, 'z': 1.822},
        'GRB090510': {'file': 'L251020161912F357373F19_EV00.fits', 'trigger': 263607281.0, 'z': 0.903},
        'GRB130427A': {'file': 'L251020164901F357373F96_EV00.fits', 'trigger': 388798843.0, 'z': 0.34}
    }
    
    all_results = []
    
    for result in lag_results:
        grb_name = result['grb_name']
        
        if grb_name not in grb_configs:
            continue
            
        print(f"\n🔬 RICERCA RESIDUI QG: {grb_name}")
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
                times_original_filtered = times_original[quality_cuts]
                energies_filtered = energies[quality_cuts]
                
                if len(times_original_filtered) < 30:
                    print(f"❌ Dati insufficienti per {grb_name}")
                    continue
                
                print(f"  Fotoni: {len(times_original_filtered)}")
                print(f"  Range energia: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV")
                print(f"  Redshift: z = {config['z']}")
                
        except Exception as e:
            print(f"❌ Errore caricamento {grb_name}: {e}")
            continue
        
        # Ricostruisci tempi corretti usando il modello migliore
        best_model = result['best_model']
        best_model_name = best_model['name']
        best_model_params = best_model['parameters']
        
        # Applica correzione lag intrinseco
        if best_model_name == 'power_law':
            from intrinsic_lag_modeling import model_intrinsic_lag_power_law
            predicted_times = model_intrinsic_lag_power_law(energies_filtered, 
                                                          best_model_params['t0'],
                                                          best_model_params['alpha'],
                                                          best_model_params['beta'])
        elif best_model_name == 'logarithmic':
            from intrinsic_lag_modeling import model_intrinsic_lag_logarithmic
            predicted_times = model_intrinsic_lag_logarithmic(energies_filtered,
                                                            best_model_params['t0'],
                                                            best_model_params['alpha'],
                                                            best_model_params['E_ref'])
        else:
            print(f"❌ Modello {best_model_name} non supportato")
            continue
        
        # Sottrai lag intrinseco
        times_corrected = times_original_filtered - predicted_times + best_model_params['t0']
        
        print(f"  Correlazione originale: {result['correlation_original']:.3f} ({result['significance_original']:.2f}σ)")
        print(f"  Correlazione corretta: {result['correlation_corrected']:.3f} ({result['significance_corrected']:.2f}σ)")
        
        # Fit modelli QG sui dati corretti
        print(f"📈 Fit modelli QG...")
        qg_models = fit_qg_models(times_corrected, energies_filtered, config['z'])
        
        # Calcola limiti su E_QG
        print(f"🎯 Calcolo limiti E_QG...")
        qg_limits = calculate_qg_limits(times_corrected, energies_filtered, config['z'])
        
        print(f"✅ Limite E_QG: > {qg_limits['E_QG_limit']:.2e} GeV (95% CL)")
        
        # Crea grafici
        print(f"📊 Creazione grafici...")
        create_qg_residual_plots(grb_name, times_original_filtered, times_corrected, 
                               energies_filtered, qg_models, qg_limits, config['z'])
        
        # Salva risultati
        qg_result = {
            'grb_name': grb_name,
            'n_photons': len(times_original_filtered),
            'energy_range': (float(energies_filtered.min()), float(energies_filtered.max())),
            'redshift': config['z'],
            'correlation_original': result['correlation_original'],
            'significance_original': result['significance_original'],
            'correlation_corrected': result['correlation_corrected'],
            'significance_corrected': result['significance_corrected'],
            'improvement_sigma': result['improvement_sigma'],
            'qg_models': {k: v for k, v in qg_models.items() if v is not None},
            'qg_limits': qg_limits,
            'best_intrinsic_model': best_model
        }
        
        all_results.append(qg_result)
    
    # Salva risultati completi
    with open('qg_residual_search_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=convert_numpy)
    
    # Riassunto finale
    print(f"\n🎯 RISULTATI FINALI FASE 3:")
    print(f"  GRB analizzati: {len(all_results)}")
    
    combined_limit = 0
    for result in all_results:
        limit = result['qg_limits']['E_QG_limit']
        combined_limit = max(combined_limit, limit)
        print(f"  {result['grb_name']}: E_QG > {limit:.2e} GeV")
        print(f"    Correlazione: {result['significance_original']:.2f}σ → {result['significance_corrected']:.2f}σ")
    
    print(f"\n🚀 LIMITE COMBINATO: E_QG > {combined_limit:.2e} GeV")
    
    # Interpretazione finale
    max_significance = max(result['significance_corrected'] for result in all_results)
    if max_significance < 2:
        interpretation = "✅ NESSUNA EVIDENZA QG - RISULTATO CONSISTENTE CON LETTERATURA!"
    elif max_significance < 3:
        interpretation = "⚠️ CORRELAZIONE DEBOLE - ULTERIORI ANALISI NECESSARIE"
    else:
        interpretation = "🚨 CORRELAZIONE SIGNIFICATIVA - POSSIBILE EVIDENZA QG!"
    
    print(f"\n🔬 INTERPRETAZIONE FINALE: {interpretation}")
    print(f"  Significatività massima residua: {max_significance:.2f}σ")
    
    print("\n" + "="*70)
    print("FASE 3 COMPLETATA! ANALISI COMPLETA FINITA!")
    print("="*70)

if __name__ == "__main__":
    main()
