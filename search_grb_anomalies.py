#!/usr/bin/env python3
"""
RICERCA GRB CON ANOMALIE
========================

Ricerca sistematica di GRB con anomalie significative:
- GRB080916C, GRB130427A, GRB190114C, GRB221009A
- Analisi con metodologie semplici e robuste
- Identificazione anomalie reali vs bias

Autore: Christian Quintino De Luca (RTH Italia)
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)
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

def generate_grb_data(grb_name, n_photons=None, has_qg=False, qg_strength=0.001):
    """Genera dati realistici per GRB specifici"""
    
    # Parametri GRB specifici
    grb_params = {
        'GRB080916C': {
            'redshift': 4.35,
            'max_energy': 13.2,  # GeV
            'duration': 63.0,    # s
            'n_photons': n_photons or 516,
            'energy_range': (0.1, 27.4),
            'time_range': (0, 3000),
            'energy_distribution': 'lognormal',
            'energy_params': (0.5, 1.2)
        },
        'GRB130427A': {
            'redshift': 0.34,
            'max_energy': 95.0,  # GeV
            'duration': 162.0,   # s
            'n_photons': n_photons or 548,
            'energy_range': (0.1, 2.1),
            'time_range': (0, 2000),
            'energy_distribution': 'lognormal',
            'energy_params': (0.3, 1.0)
        },
        'GRB190114C': {
            'redshift': 0.424,
            'max_energy': 1.0,   # TeV = 1000 GeV
            'duration': 116.0,   # s
            'n_photons': n_photons or 150,
            'energy_range': (0.1, 1000.0),
            'time_range': (0, 1500),
            'energy_distribution': 'lognormal',
            'energy_params': (1.5, 1.0)
        },
        'GRB221009A': {
            'redshift': 0.151,
            'max_energy': 18.0,  # GeV
            'duration': 327.0,   # s
            'n_photons': n_photons or 2000,
            'energy_range': (0.1, 18.0),
            'time_range': (0, 4000),
            'energy_distribution': 'lognormal',
            'energy_params': (0.8, 1.1)
        }
    }
    
    if grb_name not in grb_params:
        raise ValueError(f"GRB {grb_name} non supportato")
    
    params = grb_params[grb_name]
    np.random.seed(hash(grb_name) % 2**32)
    
    # Genera energie
    if params['energy_distribution'] == 'lognormal':
        energies = np.random.lognormal(params['energy_params'][0], params['energy_params'][1], params['n_photons'])
    
    energies = np.clip(energies, params['energy_range'][0], params['energy_range'][1])
    
    # Genera tempi
    times = np.random.exponential(params['duration'] * 2, params['n_photons'])
    times = np.clip(times, params['time_range'][0], params['time_range'][1])
    
    # Lag intrinseci specifici per GRB
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(params['n_photons'])
    times += intrinsic_lag
    
    # Effetti QG se richiesti
    if has_qg:
        qg_delay = qg_strength * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    # Rumore
    times += 0.1 * np.random.randn(params['n_photons'])
    
    return energies, times, params

def simple_robust_analysis(energies, times, grb_name):
    """Analisi semplice e robusta per detection QG"""
    
    if len(energies) < 10:
        return None
    
    # Metodo 1: Correlazione diretta (più robusto)
    correlation = np.corrcoef(energies, times)[0, 1]
    significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
    
    # Metodo 2: Fit lineare semplice
    slope, intercept = np.polyfit(energies, times, 1)
    
    # Metodo 3: Test di permutazione (robustezza)
    n_permutations = 100
    permuted_significances = []
    
    for _ in range(n_permutations):
        permuted_times = np.random.permutation(times)
        perm_corr = np.corrcoef(energies, permuted_times)[0, 1]
        perm_sig = abs(perm_corr) * np.sqrt(len(energies) - 2) / np.sqrt(1 - perm_corr**2)
        permuted_significances.append(perm_sig)
    
    p_value = np.sum(np.array(permuted_significances) >= significance) / n_permutations
    
    # Metodo 4: Analisi per bin energetici
    n_bins = min(5, len(energies) // 50)
    if n_bins > 1:
        energy_bins = np.linspace(energies.min(), energies.max(), n_bins + 1)
        bin_correlations = []
        
        for i in range(n_bins):
            bin_mask = (energies >= energy_bins[i]) & (energies < energy_bins[i + 1])
            if np.sum(bin_mask) > 5:
                bin_energies = energies[bin_mask]
                bin_times = times[bin_mask]
                bin_corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                bin_correlations.append(bin_corr)
        
        avg_bin_corr = np.mean(bin_correlations) if bin_correlations else 0
        bin_significance = abs(avg_bin_corr) * np.sqrt(len(energies) - 2) / np.sqrt(1 - avg_bin_corr**2)
    else:
        bin_significance = significance
    
    return {
        'grb_name': grb_name,
        'n_photons': len(energies),
        'energy_range': [float(energies.min()), float(energies.max())],
        'time_range': [float(times.min()), float(times.max())],
        'direct_correlation': correlation,
        'direct_significance': significance,
        'linear_slope': slope,
        'linear_intercept': intercept,
        'p_value': p_value,
        'bin_correlation': avg_bin_corr if n_bins > 1 else correlation,
        'bin_significance': bin_significance,
        'n_energy_bins': n_bins,
        'permuted_significances_mean': np.mean(permuted_significances),
        'permuted_significances_std': np.std(permuted_significances)
    }

def search_grb_anomalies():
    """Ricerca sistematica di GRB con anomalie"""
    
    print("🔍 Ricerca GRB con Anomalie...")
    
    # GRB da analizzare
    grb_list = ['GRB080916C', 'GRB130427A', 'GRB190114C', 'GRB221009A']
    
    results = {}
    anomalies_found = []
    
    for grb_name in grb_list:
        print(f"  🔍 Analizzando {grb_name}...")
        
        # Test con dati null (nessun QG)
        energies_null, times_null, params = generate_grb_data(grb_name, has_qg=False)
        result_null = simple_robust_analysis(energies_null, times_null, grb_name)
        
        # Test con QG iniettato
        energies_qg, times_qg, _ = generate_grb_data(grb_name, has_qg=True, qg_strength=0.001)
        result_qg = simple_robust_analysis(energies_qg, times_qg, grb_name)
        
        # Test con QG forte
        energies_qg_strong, times_qg_strong, _ = generate_grb_data(grb_name, has_qg=True, qg_strength=0.005)
        result_qg_strong = simple_robust_analysis(energies_qg_strong, times_qg_strong, grb_name)
        
        results[grb_name] = {
            'parameters': params,
            'null_data': result_null,
            'qg_data': result_qg,
            'qg_strong_data': result_qg_strong
        }
        
        # Identifica anomalie
        if result_null:
            if result_null['direct_significance'] > 3.0:
                anomalies_found.append({
                    'grb_name': grb_name,
                    'type': 'High Significance Null',
                    'significance': result_null['direct_significance'],
                    'p_value': result_null['p_value']
                })
            
            if result_null['p_value'] < 0.01:
                anomalies_found.append({
                    'grb_name': grb_name,
                    'type': 'Low P-Value',
                    'significance': result_null['direct_significance'],
                    'p_value': result_null['p_value']
                })
        
        # Test robustezza QG detection
        if result_null and result_qg:
            qg_detection_improvement = result_qg['direct_significance'] - result_null['direct_significance']
            if qg_detection_improvement < 0:
                anomalies_found.append({
                    'grb_name': grb_name,
                    'type': 'QG Detection Failure',
                    'improvement': qg_detection_improvement,
                    'null_sig': result_null['direct_significance'],
                    'qg_sig': result_qg['direct_significance']
                })
    
    return results, anomalies_found

def create_grb_anomaly_plots(results, anomalies_found):
    """Crea grafici per ricerca GRB anomalie"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('GRB Anomaly Search Results', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Significatività per GRB
    grb_names = list(results.keys())
    null_significances = []
    qg_significances = []
    qg_strong_significances = []
    
    for grb_name in grb_names:
        if results[grb_name]['null_data']:
            null_significances.append(results[grb_name]['null_data']['direct_significance'])
        else:
            null_significances.append(0)
            
        if results[grb_name]['qg_data']:
            qg_significances.append(results[grb_name]['qg_data']['direct_significance'])
        else:
            qg_significances.append(0)
            
        if results[grb_name]['qg_strong_data']:
            qg_strong_significances.append(results[grb_name]['qg_strong_data']['direct_significance'])
        else:
            qg_strong_significances.append(0)
    
    x = np.arange(len(grb_names))
    width = 0.25
    
    bars1 = ax1.bar(x - width, null_significances, width, 
                   label='Null Data', color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x, qg_significances, width,
                   label='QG Data', color='#3498db', alpha=0.8)
    bars3 = ax1.bar(x + width, qg_strong_significances, width,
                   label='QG Strong', color='#9b59b6', alpha=0.8)
    
    ax1.set_xlabel('GRB', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax1.set_title('Significance by GRB', fontsize=16, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(grb_names, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=3.0, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
    ax1.legend()
    
    # Plot 2: P-Values per GRB
    p_values = []
    for grb_name in grb_names:
        if results[grb_name]['null_data']:
            p_values.append(results[grb_name]['null_data']['p_value'])
        else:
            p_values.append(1.0)
    
    bars = ax2.bar(grb_names, p_values, color='#f39c12', alpha=0.8)
    ax2.set_xlabel('GRB', fontsize=14, fontweight='bold')
    ax2.set_ylabel('P-Value', fontsize=14, fontweight='bold')
    ax2.set_title('P-Values by GRB', fontsize=16, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0.01, color='red', linestyle='--', alpha=0.5, label='p=0.01')
    ax2.axhline(y=0.05, color='orange', linestyle='--', alpha=0.5, label='p=0.05')
    ax2.legend()
    ax2.set_yscale('log')
    
    # Plot 3: QG Detection Performance
    qg_improvements = []
    for grb_name in grb_names:
        if results[grb_name]['null_data'] and results[grb_name]['qg_data']:
            improvement = results[grb_name]['qg_data']['direct_significance'] - results[grb_name]['null_data']['direct_significance']
            qg_improvements.append(improvement)
        else:
            qg_improvements.append(0)
    
    bars = ax3.bar(grb_names, qg_improvements, color='#27ae60', alpha=0.8)
    ax3.set_xlabel('GRB', fontsize=14, fontweight='bold')
    ax3.set_ylabel('QG Detection Improvement (σ)', fontsize=14, fontweight='bold')
    ax3.set_title('QG Detection Performance', fontsize=16, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='red', linestyle='-', alpha=0.5)
    
    # Plot 4: Anomalies Summary
    anomaly_types = {}
    for anomaly in anomalies_found:
        anomaly_type = anomaly['type']
        if anomaly_type not in anomaly_types:
            anomaly_types[anomaly_type] = 0
        anomaly_types[anomaly_type] += 1
    
    if anomaly_types:
        bars = ax4.bar(anomaly_types.keys(), anomaly_types.values(), 
                       color=['#e74c3c', '#3498db', '#f39c12', '#9b59b6'], alpha=0.8)
        ax4.set_xlabel('Anomaly Type', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Count', fontsize=14, fontweight='bold')
        ax4.set_title('Anomalies Found', fontsize=16, fontweight='bold')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No Anomalies Found', transform=ax4.transAxes, 
                ha='center', va='center', fontsize=16, fontweight='bold')
        ax4.set_title('Anomalies Found', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('grb_anomaly_search_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici ricerca GRB anomalie creati: grb_anomaly_search_results.png")

def main():
    """Funzione principale per ricerca GRB anomalie"""
    
    print("="*70)
    print("RICERCA GRB CON ANOMALIE")
    print("Ricerca sistematica di GRB con anomalie significative")
    print("="*70)
    
    # Ricerca GRB anomalie
    print("\n🔍 Ricerca GRB con Anomalie...")
    results, anomalies_found = search_grb_anomalies()
    
    # Crea grafici
    print("\n📊 Creazione grafici ricerca GRB anomalie...")
    create_grb_anomaly_plots(results, anomalies_found)
    
    # Compila risultati
    search_results = {
        'timestamp': datetime.now().isoformat(),
        'grb_analyzed': list(results.keys()),
        'results': results,
        'anomalies_found': anomalies_found,
        'summary': {
            'total_grb': len(results),
            'total_anomalies': len(anomalies_found),
            'anomaly_rate': len(anomalies_found) / len(results),
            'high_significance_grb': sum(1 for r in results.values() if r['null_data'] and r['null_data']['direct_significance'] > 3.0),
            'low_p_value_grb': sum(1 for r in results.values() if r['null_data'] and r['null_data']['p_value'] < 0.01)
        }
    }
    
    # Salva risultati
    with open('grb_anomaly_search_results.json', 'w') as f:
        json.dump(search_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI RICERCA GRB ANOMALIE")
    print("="*70)
    
    print(f"🎯 GRB Analizzati: {search_results['summary']['total_grb']}")
    print(f"🎯 Anomalie Trovate: {search_results['summary']['total_anomalies']}")
    print(f"🎯 Tasso Anomalie: {search_results['summary']['anomaly_rate']:.1%}")
    print(f"🎯 GRB Alta Significatività: {search_results['summary']['high_significance_grb']}")
    print(f"🎯 GRB P-Value Basso: {search_results['summary']['low_p_value_grb']}")
    
    print(f"\n🔍 Risultati per GRB:")
    for grb_name, result in results.items():
        if result['null_data']:
            sig = result['null_data']['direct_significance']
            p_val = result['null_data']['p_value']
            print(f"  {grb_name}: {sig:.2f}σ (p={p_val:.3f})")
    
    if anomalies_found:
        print(f"\n🚨 Anomalie Trovate:")
        for anomaly in anomalies_found:
            print(f"  {anomaly['grb_name']}: {anomaly['type']} - {anomaly.get('significance', anomaly.get('improvement', 'N/A'))}")
    else:
        print(f"\n✅ Nessuna Anomalia Significativa Trovata")
    
    print("\n" + "="*70)
    print("✅ Ricerca GRB anomalie completata!")
    print("📊 Risultati salvati: grb_anomaly_search_results.json")
    print("📈 Grafici salvati: grb_anomaly_search_results.png")
    print("="*70)

if __name__ == "__main__":
    main()
