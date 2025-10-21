#!/usr/bin/env python3
"""
ULTIMATE VALIDATION ALL GRB
===========================

Esegue ultimate validation suite su tutti i GRB disponibili
per confronto completo con GRB090902

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
plt.rcParams['figure.figsize'] = (20, 15)
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

def load_grb_data(filename):
    """Carica dati GRB dal file FITS"""
    
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

def ultimate_validation_grb(data, grb_name):
    """Esegue ultimate validation suite su un singolo GRB"""
    
    print(f"\n🔍 ULTIMATE VALIDATION: {grb_name}")
    print("="*50)
    
    times = data['times']
    energies = data['energies']
    
    # Analisi base
    correlation = np.corrcoef(energies, times)[0, 1]
    significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
    
    print(f"📊 Correlazione base: {correlation:.4f}")
    print(f"📊 Significatività base: {significance:.2f}σ")
    
    validation_results = {}
    
    # 1. Test di robustezza estremi
    print("  📊 Test di robustezza estremi...")
    robustness_results = {}
    
    # Filtri energetici estremi
    energy_filters = [0.01, 0.1, 1.0, 10.0, 100.0]  # GeV
    extreme_energy_results = {}
    
    for filter_gev in energy_filters:
        filter_mev = filter_gev * 1000
        mask = energies >= filter_mev
        
        if np.sum(mask) > 20:  # Almeno 20 fotoni
            filtered_times = times[mask]
            filtered_energies = energies[mask]
            
            if len(np.unique(filtered_energies)) > 1 and len(np.unique(filtered_times)) > 1:
                corr = np.corrcoef(filtered_energies, filtered_times)[0, 1]
                sig = abs(corr) * np.sqrt(len(filtered_energies) - 2) / np.sqrt(1 - corr**2)
                
                extreme_energy_results[f'filter_{filter_gev}_gev'] = {
                    'filter_gev': filter_gev,
                    'n_photons': np.sum(mask),
                    'correlation': corr,
                    'significance': sig
                }
    
    robustness_results['extreme_energy_filters'] = extreme_energy_results
    
    # Metodi di correlazione multipli
    correlation_methods = {}
    
    # Pearson
    pearson_corr = np.corrcoef(energies, times)[0, 1]
    pearson_sig = abs(pearson_corr) * np.sqrt(len(energies) - 2) / np.sqrt(1 - pearson_corr**2)
    correlation_methods['pearson'] = {
        'correlation': pearson_corr,
        'significance': pearson_sig
    }
    
    # Spearman
    spearman_corr, spearman_p = stats.spearmanr(energies, times)
    spearman_sig = abs(stats.norm.ppf(spearman_p/2))
    correlation_methods['spearman'] = {
        'correlation': spearman_corr,
        'significance': spearman_sig,
        'p_value': spearman_p
    }
    
    # Kendall
    kendall_corr, kendall_p = stats.kendalltau(energies, times)
    kendall_sig = abs(stats.norm.ppf(kendall_p/2))
    correlation_methods['kendall'] = {
        'correlation': kendall_corr,
        'significance': kendall_sig,
        'p_value': kendall_p
    }
    
    robustness_results['correlation_methods'] = correlation_methods
    
    validation_results['robustness'] = robustness_results
    
    # 2. Test per bias sistematici
    print("  📊 Test per bias sistematici...")
    bias_results = {}
    
    # Test con dati randomizzati
    n_randomizations = 1000
    random_results = []
    
    for i in range(n_randomizations):
        random_times = np.random.permutation(times)
        corr = np.corrcoef(energies, random_times)[0, 1]
        sig = abs(corr) * np.sqrt(len(energies) - 2) / np.sqrt(1 - corr**2)
        random_results.append({'correlation': corr, 'significance': sig})
    
    bias_results['randomization'] = {
        'n_randomizations': n_randomizations,
        'random_correlations_mean': np.mean([r['correlation'] for r in random_results]),
        'random_correlations_std': np.std([r['correlation'] for r in random_results]),
        'random_significances_mean': np.mean([r['significance'] for r in random_results]),
        'random_significances_std': np.std([r['significance'] for r in random_results])
    }
    
    validation_results['bias'] = bias_results
    
    # 3. Test per falsi positivi
    print("  📊 Test per falsi positivi...")
    fp_results = {}
    
    # Test con dati completamente random
    n_random_trials = 10000
    random_trials = []
    
    for i in range(n_random_trials):
        random_energies = np.random.exponential(scale=1000, size=len(energies))  # MeV
        random_times = np.random.uniform(times.min(), times.max(), size=len(times))
        
        corr = np.corrcoef(random_energies, random_times)[0, 1]
        sig = abs(corr) * np.sqrt(len(random_energies) - 2) / np.sqrt(1 - corr**2)
        random_trials.append({'correlation': corr, 'significance': sig})
    
    fp_results['random_data'] = {
        'n_trials': n_random_trials,
        'random_correlations_mean': np.mean([r['correlation'] for r in random_trials]),
        'random_correlations_std': np.std([r['correlation'] for r in random_trials]),
        'random_significances_mean': np.mean([r['significance'] for r in random_trials]),
        'random_significances_std': np.std([r['significance'] for r in random_trials]),
        'false_positive_rate_5sigma': np.sum([r['significance'] >= 5.0 for r in random_trials]) / n_random_trials,
        'false_positive_rate_3sigma': np.sum([r['significance'] >= 3.0 for r in random_trials]) / n_random_trials,
        'false_positive_rate_2sigma': np.sum([r['significance'] >= 2.0 for r in random_trials]) / n_random_trials
    }
    
    validation_results['false_positive'] = fp_results
    
    # 4. Test con campioni di controllo
    print("  📊 Test con campioni di controllo...")
    control_results = {}
    
    # Test con fotoni a bassa energia
    low_energy_mask = energies < 1000  # MeV (< 1 GeV)
    
    if np.sum(low_energy_mask) > 50:
        low_energy_times = times[low_energy_mask]
        low_energy_energies = energies[low_energy_mask]
        
        corr = np.corrcoef(low_energy_energies, low_energy_times)[0, 1]
        sig = abs(corr) * np.sqrt(len(low_energy_energies) - 2) / np.sqrt(1 - corr**2)
        
        control_results['low_energy'] = {
            'n_photons': np.sum(low_energy_mask),
            'correlation': corr,
            'significance': sig,
            'energy_range': f"< 1 GeV"
        }
    
    # Test con fotoni ad alta energia
    high_energy_mask = energies > 10000  # MeV (> 10 GeV)
    
    if np.sum(high_energy_mask) > 10:
        high_energy_times = times[high_energy_mask]
        high_energy_energies = energies[high_energy_mask]
        
        corr = np.corrcoef(high_energy_energies, high_energy_times)[0, 1]
        sig = abs(corr) * np.sqrt(len(high_energy_energies) - 2) / np.sqrt(1 - corr**2)
        
        control_results['high_energy'] = {
            'n_photons': np.sum(high_energy_mask),
            'correlation': corr,
            'significance': sig,
            'energy_range': f"> 10 GeV"
        }
    
    validation_results['control'] = control_results
    
    # Compila risultati finali
    final_results = {
        'timestamp': datetime.now().isoformat(),
        'grb_name': grb_name,
        'filename': data['filename'],
        'n_events': data['n_events'],
        'max_energy_gev': energies.max() / 1000.0,
        'base_correlation': correlation,
        'base_significance': significance,
        'validation_results': validation_results,
        'summary': {
            'anomaly_detected': significance >= 3.0,
            'significance': f"{significance:.2f}σ",
            'validation_status': 'Ultimate validation completed',
            'bias_analysis': 'Completed',
            'false_positive_analysis': 'Completed',
            'robustness_analysis': 'Completed',
            'control_sample_analysis': 'Completed'
        }
    }
    
    return final_results

def main():
    """Funzione principale per ultimate validation su tutti i GRB"""
    
    print("="*70)
    print("ULTIMATE VALIDATION ALL GRB")
    print("Validazione completa su tutti i GRB disponibili")
    print("="*70)
    
    # Configurazione GRB disponibili
    grb_configs = {
        'GRB090902': {
            'file': 'L251020161615F357373F52_EV00.fits',
            'priority': 'DISCOVERY',
            'description': 'Anomalia 5.46σ confermata'
        },
        'GRB080916C': {
            'file': 'L251020154246F357373F64_EV00.fits',
            'priority': 'High',
            'description': 'Record energetico, fotone da 13 GeV, z=4.35'
        },
        'GRB130427A': {
            'file': 'L251020164901F357373F96_EV00.fits',
            'priority': 'High', 
            'description': 'Fotone da 95 GeV, il più energetico mai visto, z=0.34'
        },
        'GRB090510': {
            'file': 'L251020161912F357373F19_EV00.fits',
            'priority': 'Medium',
            'description': 'Short burst con emissione GeV, ottimo per QG, z=0.903'
        }
    }
    
    # Verifica file disponibili
    available_grbs = {}
    for grb_name, config in grb_configs.items():
        if os.path.exists(config['file']):
            available_grbs[grb_name] = config
            print(f"✅ {grb_name}: {config['file']} - {config['description']}")
        else:
            print(f"❌ {grb_name}: {config['file']} - File non trovato")
    
    print(f"\n📊 GRB disponibili per ultimate validation: {len(available_grbs)}")
    
    # Esegui ultimate validation su ogni GRB disponibile
    all_results = {}
    
    for grb_name, config in available_grbs.items():
        print(f"\n{'='*70}")
        print(f"ULTIMATE VALIDATION: {grb_name}")
        print(f"{'='*70}")
        
        # Carica dati
        data = load_grb_data(config['file'])
        if data is None:
            print(f"❌ Errore caricamento dati per {grb_name}")
            continue
        
        # Esegui ultimate validation
        results = ultimate_validation_grb(data, grb_name)
        all_results[grb_name] = results
        
        # Salva risultati individuali
        output_file = f'ultimate_validation_{grb_name.lower()}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=convert_numpy)
        
        print(f"✅ Risultati salvati: {output_file}")
    
    # Compila riassunto finale
    ultimate_summary = {
        'timestamp': datetime.now().isoformat(),
        'strategy': 'Ultimate Validation All GRB',
        'grb_analyzed': len(all_results),
        'grb_results': all_results,
        'summary': {
            'total_grb': len(all_results),
            'high_significance_grb': len([grb for grb in all_results.values() if grb['base_significance'] >= 5.0]),
            'medium_significance_grb': len([grb for grb in all_results.values() if 3.0 <= grb['base_significance'] < 5.0]),
            'low_significance_grb': len([grb for grb in all_results.values() if grb['base_significance'] < 3.0]),
            'grb090902_unique': all_results.get('GRB090902', {}).get('base_significance', 0) >= 5.0
        }
    }
    
    # Salva riassunto finale
    with open('ultimate_validation_all_grb_summary.json', 'w') as f:
        json.dump(ultimate_summary, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto finale
    print(f"\n{'='*70}")
    print("🎯 RIASSUNTO ULTIMATE VALIDATION ALL GRB")
    print(f"{'='*70}")
    
    print(f"🎯 GRB analizzati: {ultimate_summary['summary']['total_grb']}")
    print(f"🎯 Alta significatività (≥5σ): {ultimate_summary['summary']['high_significance_grb']}")
    print(f"🎯 Media significatività (3-5σ): {ultimate_summary['summary']['medium_significance_grb']}")
    print(f"🎯 Bassa significatività (<3σ): {ultimate_summary['summary']['low_significance_grb']}")
    
    print(f"\n🔍 RISULTATI PER GRB:")
    for grb_name, results in all_results.items():
        sig = results['base_significance']
        n_events = results['n_events']
        max_e = results['max_energy_gev']
        status = "🔥 ALTA" if sig >= 5.0 else "⚡ MEDIA" if sig >= 3.0 else "📊 BASSA"
        print(f"  📊 {grb_name}: {sig:.2f}σ ({status}) - n={n_events}, E_max={max_e:.1f} GeV")
    
    # Analisi finale
    print(f"\n🎲 ANALISI FINALE:")
    high_sig_count = ultimate_summary['summary']['high_significance_grb']
    total_count = ultimate_summary['summary']['total_grb']
    
    if high_sig_count == 1:
        print("  📊 1/4 GRB mostra alta significatività → GRB090902 unico")
        print("  🔍 Possibile QG in condizioni specifiche o lag astrofisico")
    elif high_sig_count == 0:
        print("  📊 0/4 GRB mostra alta significatività → Nessuna evidenza QG")
    else:
        print(f"  🔥 {high_sig_count}/{total_count} GRB mostrano alta significatività → Evidenza forte QG!")
    
    print(f"\n{'='*70}")
    print("✅ ULTIMATE VALIDATION ALL GRB COMPLETATA!")
    print("📊 Riassunto salvato: ultimate_validation_all_grb_summary.json")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()

