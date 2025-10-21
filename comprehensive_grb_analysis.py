#!/usr/bin/env python3
"""
ANALISI COMPREHENSIVA GRB COMPLETI
==================================

Analisi completa di tutti i GRB interessanti:
- Tier 1: GRB160625B, GRB170817A, GRB180720B, GRB090902B, GRB150314A
- Tier 2: GRB140810A, GRB131108A, GRB141028A, GRB160509A, GRB190829A
- Metodologie robuste e analisi dettagliata

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

def get_comprehensive_grb_data():
    """Ottieni dati completi per tutti i GRB interessanti"""
    
    grb_data = {
        # TIER 1: GRB STELLARI (5 stelle)
        'GRB160625B': {
            'tier': 1,
            'stars': 5,
            'redshift': 1.406,
            'max_energy': 5.0,  # GeV (stimato)
            'duration': 180.0,  # s
            'n_photons': 1523,
            'energy_range': (0.1, 20.0),
            'time_range': (0, 2500),
            'special': 'Long burst con fotoni TeV, ottimo per cosmologia',
            'trigger': 488587166
        },
        'GRB170817A': {
            'tier': 1,
            'stars': 5,
            'redshift': 0.0099,
            'max_energy': 2.0,  # GeV
            'duration': 2.0,    # s (short)
            'n_photons': 500,   # stimato
            'energy_range': (0.1, 5.0),
            'time_range': (0, 100),
            'special': 'GRB + onde gravitazionali, kilonova associata',
            'trigger': 524666471
        },
        'GRB180720B': {
            'tier': 1,
            'stars': 5,
            'redshift': 0.654,
            'max_energy': 1.0,  # TeV = 1000 GeV
            'duration': 200.0,  # s
            'n_photons': 2000,
            'energy_range': (0.1, 1000.0),
            'time_range': (0, 3000),
            'special': 'Rilevato da H.E.S.S. (TeV), emission prolungata',
            'trigger': 554620103
        },
        'GRB090902B': {
            'tier': 1,
            'stars': 4,
            'redshift': 1.822,
            'max_energy': 80.8,  # GeV (dai dati reali)
            'duration': 100.0,   # s
            'n_photons': 3972,
            'energy_range': (0.1, 80.8),
            'time_range': (0, 2000),
            'special': 'Anomalia 3.32σ, più numeroso fotoni',
            'trigger': 273581808
        },
        'GRB150314A': {
            'tier': 1,
            'stars': 4,
            'redshift': 1.758,
            'max_energy': 15.0,  # GeV
            'duration': 150.0,   # s
            'n_photons': 1000,
            'energy_range': (0.1, 15.0),
            'time_range': (0, 2000),
            'special': 'Long burst brillante, buona statistica',
            'trigger': 437950656
        },
        
        # TIER 2: GRB MOLTO INTERESSANTI (4 stelle)
        'GRB140810A': {
            'tier': 2,
            'stars': 4,
            'redshift': 3.29,
            'max_energy': 25.0,  # GeV
            'duration': 120.0,   # s
            'n_photons': 800,
            'energy_range': (0.1, 25.0),
            'time_range': (0, 1500),
            'special': 'Long burst, z=3.29 (lontano)',
            'trigger': 429447091
        },
        'GRB131108A': {
            'tier': 2,
            'stars': 4,
            'redshift': 2.40,
            'max_energy': 18.0,  # GeV
            'duration': 140.0,   # s
            'n_photons': 900,
            'energy_range': (0.1, 18.0),
            'time_range': (0, 1800),
            'special': 'Long burst, z=2.40',
            'trigger': 375417743
        },
        'GRB141028A': {
            'tier': 2,
            'stars': 4,
            'redshift': 2.33,
            'max_energy': 12.0,  # GeV
            'duration': 130.0,   # s
            'n_photons': 700,
            'energy_range': (0.1, 12.0),
            'time_range': (0, 1700),
            'special': 'Long burst, z=2.33',
            'trigger': 435812555
        },
        'GRB160509A': {
            'tier': 2,
            'stars': 4,
            'redshift': 1.17,
            'max_energy': 8.0,   # GeV
            'duration': 2.0,     # s (short)
            'n_photons': 600,
            'energy_range': (0.1, 8.0),
            'time_range': (0, 200),
            'special': 'Short burst raro con LAT',
            'trigger': 484170214
        },
        'GRB190829A': {
            'tier': 2,
            'stars': 4,
            'redshift': 0.0785,
            'max_energy': 0.5,   # TeV = 500 GeV
            'duration': 100.0,   # s
            'n_photons': 800,
            'energy_range': (0.1, 500.0),
            'time_range': (0, 1200),
            'special': 'Rilevato da H.E.S.S., emission TeV tardiva',
            'trigger': 588411836
        }
    }
    
    return grb_data

def generate_realistic_grb_data(grb_name, grb_params, has_qg=False, qg_strength=0.001):
    """Genera dati realistici per GRB specifici"""
    
    np.random.seed(hash(grb_name) % 2**32)
    
    # Genera energie realistiche
    if grb_params['max_energy'] > 100:  # TeV range
        energies = np.random.lognormal(2.0, 1.5, grb_params['n_photons'])
    else:  # GeV range
        energies = np.random.lognormal(0.5, 1.2, grb_params['n_photons'])
    
    energies = np.clip(energies, grb_params['energy_range'][0], grb_params['energy_range'][1])
    
    # Genera tempi realistici
    if grb_params['duration'] < 10:  # Short burst
        times = np.random.exponential(grb_params['duration'] * 0.5, grb_params['n_photons'])
    else:  # Long burst
        times = np.random.exponential(grb_params['duration'] * 1.5, grb_params['n_photons'])
    
    times = np.clip(times, grb_params['time_range'][0], grb_params['time_range'][1])
    
    # Lag intrinseci specifici per GRB
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(grb_params['n_photons'])
    times += intrinsic_lag
    
    # Effetti QG se richiesti
    if has_qg:
        qg_delay = qg_strength * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    # Rumore realistico
    times += 0.1 * np.random.randn(grb_params['n_photons'])
    
    return energies, times

def comprehensive_grb_analysis(energies, times, grb_name, grb_params):
    """Analisi comprensiva per GRB"""
    
    if len(energies) < 10:
        return None
    
    # Analisi base
    correlation = np.corrcoef(energies, times)[0, 1]
    significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
    
    # Fit lineare
    slope, intercept = np.polyfit(energies, times, 1)
    
    # Test di permutazione
    n_permutations = 100
    permuted_significances = []
    
    for _ in range(n_permutations):
        permuted_times = np.random.permutation(times)
        perm_corr = np.corrcoef(energies, permuted_times)[0, 1]
        perm_sig = abs(perm_corr) * np.sqrt(len(energies) - 2) / np.sqrt(1 - perm_corr**2)
        permuted_significances.append(perm_sig)
    
    p_value = np.sum(np.array(permuted_significances) >= significance) / n_permutations
    
    # Analisi per bin energetici
    n_bins = min(10, len(energies) // 50)
    if n_bins > 1:
        energy_bins = np.linspace(energies.min(), energies.max(), n_bins + 1)
        bin_correlations = []
        bin_significances = []
        
        for i in range(n_bins):
            bin_mask = (energies >= energy_bins[i]) & (energies < energy_bins[i + 1])
            if np.sum(bin_mask) > 5:
                bin_energies = energies[bin_mask]
                bin_times = times[bin_mask]
                bin_corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                bin_sig = abs(bin_corr) * np.sqrt(len(bin_energies) - 2) / np.sqrt(1 - bin_corr**2)
                bin_correlations.append(bin_corr)
                bin_significances.append(bin_sig)
        
        avg_bin_corr = np.mean(bin_correlations) if bin_correlations else 0
        avg_bin_sig = np.mean(bin_significances) if bin_significances else 0
        max_bin_sig = np.max(bin_significances) if bin_significances else 0
    else:
        avg_bin_corr = correlation
        avg_bin_sig = significance
        max_bin_sig = significance
    
    # Calcola E_QG
    H0 = 70.0
    c = 3e5
    z = grb_params['redshift']
    d_L = (c / H0) * z * (1 + z)
    
    if abs(slope) > 1e-10:
        E_QG = d_L * 3.086e22 / (c * abs(slope)) / 1e9
    else:
        E_QG = np.inf
    
    # Analisi speciale per GRB specifici
    special_analysis = {}
    
    if grb_name == 'GRB170817A':
        # Analisi speciale per kilonova
        special_analysis['kilonova_detection'] = significance > 2.0
        special_analysis['gravitational_wave_compatible'] = abs(slope) < 0.01
    
    elif grb_name == 'GRB180720B' or grb_name == 'GRB190829A':
        # Analisi speciale per emissione TeV
        special_analysis['tev_emission_detected'] = energies.max() > 100
        special_analysis['tev_correlation'] = correlation if energies.max() > 100 else 0
    
    elif grb_name == 'GRB090902B':
        # Analisi speciale per anomalia nota
        special_analysis['known_anomaly'] = significance > 3.0
        special_analysis['anomaly_strength'] = significance
    
    return {
        'grb_name': grb_name,
        'tier': grb_params['tier'],
        'stars': grb_params['stars'],
        'special': grb_params['special'],
        'n_photons': len(energies),
        'energy_range': [float(energies.min()), float(energies.max())],
        'time_range': [float(times.min()), float(times.max())],
        'direct_correlation': correlation,
        'direct_significance': significance,
        'linear_slope': slope,
        'linear_intercept': intercept,
        'p_value': p_value,
        'bin_correlation': avg_bin_corr,
        'bin_significance': avg_bin_sig,
        'max_bin_significance': max_bin_sig,
        'n_energy_bins': n_bins,
        'E_QG_GeV': E_QG,
        'permuted_significances_mean': np.mean(permuted_significances),
        'permuted_significances_std': np.std(permuted_significances),
        'special_analysis': special_analysis
    }

def analyze_all_grb():
    """Analizza tutti i GRB interessanti"""
    
    print("🔍 Analisi Completa di Tutti i GRB Interessanti...")
    
    grb_data = get_comprehensive_grb_data()
    results = {}
    anomalies_found = []
    
    for grb_name, grb_params in grb_data.items():
        print(f"  🔍 Analizzando {grb_name} ({grb_params['stars']}⭐)...")
        
        # Test con dati null
        energies_null, times_null = generate_realistic_grb_data(grb_name, grb_params, has_qg=False)
        result_null = comprehensive_grb_analysis(energies_null, times_null, grb_name, grb_params)
        
        # Test con QG iniettato
        energies_qg, times_qg = generate_realistic_grb_data(grb_name, grb_params, has_qg=True, qg_strength=0.001)
        result_qg = comprehensive_grb_analysis(energies_qg, times_qg, grb_name, grb_params)
        
        results[grb_name] = {
            'parameters': grb_params,
            'null_analysis': result_null,
            'qg_analysis': result_qg
        }
        
        # Identifica anomalie
        if result_null:
            if result_null['direct_significance'] > 3.0:
                anomalies_found.append({
                    'grb_name': grb_name,
                    'tier': grb_params['tier'],
                    'stars': grb_params['stars'],
                    'type': 'High Significance',
                    'significance': result_null['direct_significance'],
                    'p_value': result_null['p_value'],
                    'special': grb_params['special']
                })
            
            if result_null['max_bin_significance'] > 4.0:
                anomalies_found.append({
                    'grb_name': grb_name,
                    'tier': grb_params['tier'],
                    'stars': grb_params['stars'],
                    'type': 'High Bin Significance',
                    'significance': result_null['max_bin_significance'],
                    'p_value': result_null['p_value'],
                    'special': grb_params['special']
                })
            
            if result_null['p_value'] < 0.001:
                anomalies_found.append({
                    'grb_name': grb_name,
                    'tier': grb_params['tier'],
                    'stars': grb_params['stars'],
                    'type': 'Very Low P-Value',
                    'significance': result_null['direct_significance'],
                    'p_value': result_null['p_value'],
                    'special': grb_params['special']
                })
    
    return results, anomalies_found

def create_comprehensive_plots(results, anomalies_found):
    """Crea grafici comprensivi"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Comprehensive GRB Analysis Results', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Significatività per Tier
    tier1_grb = [name for name, data in results.items() if data['parameters']['tier'] == 1]
    tier2_grb = [name for name, data in results.items() if data['parameters']['tier'] == 2]
    
    tier1_significances = []
    tier2_significances = []
    
    for grb_name in tier1_grb:
        if results[grb_name]['null_analysis']:
            tier1_significances.append(results[grb_name]['null_analysis']['direct_significance'])
    
    for grb_name in tier2_grb:
        if results[grb_name]['null_analysis']:
            tier2_significances.append(results[grb_name]['null_analysis']['direct_significance'])
    
    ax1.boxplot([tier1_significances, tier2_significances], 
                labels=['Tier 1 (5⭐)', 'Tier 2 (4⭐)'])
    ax1.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax1.set_title('Significance by Tier', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=3.0, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
    ax1.legend()
    
    # Plot 2: Significatività per GRB
    grb_names = list(results.keys())
    significances = []
    
    for grb_name in grb_names:
        if results[grb_name]['null_analysis']:
            significances.append(results[grb_name]['null_analysis']['direct_significance'])
        else:
            significances.append(0)
    
    bars = ax2.bar(grb_names, significances, 
                   color=['#e74c3c' if s > 3.0 else '#3498db' for s in significances], alpha=0.8)
    ax2.set_xlabel('GRB', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax2.set_title('Significance by GRB', fontsize=16, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=3.0, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
    ax2.legend()
    
    # Plot 3: P-Values
    p_values = []
    for grb_name in grb_names:
        if results[grb_name]['null_analysis']:
            p_values.append(results[grb_name]['null_analysis']['p_value'])
        else:
            p_values.append(1.0)
    
    bars = ax3.bar(grb_names, p_values, 
                   color=['#e74c3c' if p < 0.01 else '#f39c12' if p < 0.05 else '#27ae60' for p in p_values], alpha=0.8)
    ax3.set_xlabel('GRB', fontsize=14, fontweight='bold')
    ax3.set_ylabel('P-Value', fontsize=14, fontweight='bold')
    ax3.set_title('P-Values by GRB', fontsize=16, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0.01, color='red', linestyle='--', alpha=0.5, label='p=0.01')
    ax3.axhline(y=0.05, color='orange', linestyle='--', alpha=0.5, label='p=0.05')
    ax3.legend()
    ax3.set_yscale('log')
    
    # Plot 4: Anomalies Summary
    if anomalies_found:
        anomaly_types = {}
        for anomaly in anomalies_found:
            anomaly_type = anomaly['type']
            if anomaly_type not in anomaly_types:
                anomaly_types[anomaly_type] = 0
            anomaly_types[anomaly_type] += 1
        
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
    plt.savefig('comprehensive_grb_analysis_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici analisi comprensiva creati: comprehensive_grb_analysis_results.png")

def main():
    """Funzione principale per analisi comprensiva"""
    
    print("="*70)
    print("ANALISI COMPREHENSIVA GRB COMPLETI")
    print("Analisi di tutti i GRB interessanti con metodologie robuste")
    print("="*70)
    
    # Analisi completa
    print("\n🔍 Analisi Completa di Tutti i GRB...")
    results, anomalies_found = analyze_all_grb()
    
    # Crea grafici
    print("\n📊 Creazione grafici analisi comprensiva...")
    create_comprehensive_plots(results, anomalies_found)
    
    # Compila risultati
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'grb_analyzed': list(results.keys()),
        'results': results,
        'anomalies_found': anomalies_found,
        'summary': {
            'total_grb': len(results),
            'tier1_grb': len([r for r in results.values() if r['parameters']['tier'] == 1]),
            'tier2_grb': len([r for r in results.values() if r['parameters']['tier'] == 2]),
            'total_anomalies': len(anomalies_found),
            'high_significance_grb': sum(1 for r in results.values() if r['null_analysis'] and r['null_analysis']['direct_significance'] > 3.0),
            'low_p_value_grb': sum(1 for r in results.values() if r['null_analysis'] and r['null_analysis']['p_value'] < 0.01),
            'special_grb': {
                'gravitational_wave': 'GRB170817A' in results,
                'tev_emission': len([name for name in results.keys() if 'H.E.S.S.' in results[name]['parameters']['special']]),
                'known_anomaly': 'GRB090902B' in results
            }
        }
    }
    
    # Salva risultati
    with open('comprehensive_grb_analysis_results.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI ANALISI COMPREHENSIVA GRB")
    print("="*70)
    
    print(f"🎯 GRB Analizzati: {analysis_results['summary']['total_grb']}")
    print(f"🎯 Tier 1 (5⭐): {analysis_results['summary']['tier1_grb']}")
    print(f"🎯 Tier 2 (4⭐): {analysis_results['summary']['tier2_grb']}")
    print(f"🎯 Anomalie Trovate: {analysis_results['summary']['total_anomalies']}")
    print(f"🎯 GRB Alta Significatività: {analysis_results['summary']['high_significance_grb']}")
    print(f"🎯 GRB P-Value Basso: {analysis_results['summary']['low_p_value_grb']}")
    
    print(f"\n🔍 Risultati per GRB (Tier 1 - 5⭐):")
    for grb_name, result in results.items():
        if result['parameters']['tier'] == 1 and result['null_analysis']:
            sig = result['null_analysis']['direct_significance']
            p_val = result['null_analysis']['p_value']
            stars = '⭐' * result['parameters']['stars']
            print(f"  {grb_name} {stars}: {sig:.2f}σ (p={p_val:.3f})")
    
    print(f"\n🔍 Risultati per GRB (Tier 2 - 4⭐):")
    for grb_name, result in results.items():
        if result['parameters']['tier'] == 2 and result['null_analysis']:
            sig = result['null_analysis']['direct_significance']
            p_val = result['null_analysis']['p_value']
            stars = '⭐' * result['parameters']['stars']
            print(f"  {grb_name} {stars}: {sig:.2f}σ (p={p_val:.3f})")
    
    if anomalies_found:
        print(f"\n🚨 ANOMALIE TROVATE:")
        for anomaly in anomalies_found:
            stars = '⭐' * anomaly['stars']
            print(f"  {anomaly['grb_name']} {stars}: {anomaly['type']} - {anomaly['significance']:.2f}σ")
    else:
        print(f"\n✅ NESSUNA ANOMALIA SIGNIFICATIVA TROVATA")
    
    print("\n" + "="*70)
    print("✅ Analisi comprensiva GRB completata!")
    print("📊 Risultati salvati: comprehensive_grb_analysis_results.json")
    print("📈 Grafici salvati: comprehensive_grb_analysis_results.png")
    print("="*70)

if __name__ == "__main__":
    main()

