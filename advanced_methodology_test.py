#!/usr/bin/env python3
"""
TEST METODOLOGIA AVANZATA
=========================

Test con dati realistici più complessi:
- GRB con burst multipli (multi-pulse)
- GRB con evoluzione temporale (temporal evolution)
- GRB con spettro complesso (complex spectrum)
- GRB con effetti strumentali (instrumental effects)

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

def generate_multi_pulse_grb(n_photons=5000, n_pulses=3, has_qg=True):
    """Genera GRB con burst multipli"""
    
    np.random.seed(42)
    
    # Parametri per ogni pulse
    pulse_centers = np.linspace(0, 2000, n_pulses)
    pulse_widths = np.random.uniform(100, 300, n_pulses)
    pulse_amplitudes = np.random.uniform(0.5, 2.0, n_pulses)
    
    all_energies = []
    all_times = []
    
    for i, (center, width, amplitude) in enumerate(zip(pulse_centers, pulse_widths, pulse_amplitudes)):
        # Fotoni per questo pulse
        n_pulse_photons = int(n_photons / n_pulses * amplitude)
        
        # Energia per questo pulse
        pulse_energies = np.random.lognormal(0.5 + i*0.2, 1.0, n_pulse_photons)
        pulse_energies = np.clip(pulse_energies, 0.1, 50.0)
        
        # Tempo per questo pulse
        pulse_times = np.random.normal(center, width, n_pulse_photons)
        pulse_times = np.clip(pulse_times, 0, 3000)
        
        # Lag intrinseci specifici per pulse
        intrinsic_lag = 0.1 * np.power(pulse_energies, -0.3) + 0.05 * np.random.randn(n_pulse_photons)
        pulse_times += intrinsic_lag
        
        # Effetti QG se richiesti
        if has_qg:
            qg_delay = 0.001 * (pulse_energies / 10.0) * (1 + 0.1 * pulse_times / 1000)
            pulse_times += qg_delay
        
        all_energies.extend(pulse_energies)
        all_times.extend(pulse_times)
    
    return np.array(all_energies), np.array(all_times), n_pulses

def generate_temporal_evolution_grb(n_photons=5000, has_qg=True):
    """Genera GRB con evoluzione temporale"""
    
    np.random.seed(43)
    
    # Evoluzione temporale dell'energia
    times = np.sort(np.random.exponential(500, n_photons))
    
    # Energia evolve nel tempo
    energy_evolution = 1.0 + 0.5 * np.exp(-times / 1000) + 0.3 * np.sin(times / 200)
    energies = np.random.lognormal(np.log(energy_evolution), 0.8, n_photons)
    energies = np.clip(energies, 0.1, 80.0)
    
    # Lag intrinseci evolutivi
    intrinsic_lag = 0.1 * np.power(energies, -0.3) * (1 + 0.2 * times / 1000)
    times += intrinsic_lag
    
    # Effetti QG se richiesti
    if has_qg:
        qg_delay = 0.001 * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    return energies, times

def generate_complex_spectrum_grb(n_photons=5000, has_qg=True):
    """Genera GRB con spettro complesso"""
    
    np.random.seed(44)
    
    # Spettro complesso con multiple componenti
    times = np.random.exponential(500, n_photons)
    
    # Componente 1: Bassa energia
    low_energy_mask = np.random.random(n_photons) < 0.6
    low_energies = np.random.lognormal(0.2, 0.8, np.sum(low_energy_mask))
    
    # Componente 2: Alta energia
    high_energy_mask = ~low_energy_mask
    high_energies = np.random.lognormal(1.5, 1.0, np.sum(high_energy_mask))
    
    energies = np.zeros(n_photons)
    energies[low_energy_mask] = low_energies
    energies[high_energy_mask] = high_energies
    energies = np.clip(energies, 0.1, 100.0)
    
    # Lag intrinseci complessi
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # Effetti QG se richiesti
    if has_qg:
        qg_delay = 0.001 * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    return energies, times

def generate_instrumental_effects_grb(n_photons=5000, has_qg=True):
    """Genera GRB con effetti strumentali"""
    
    np.random.seed(45)
    
    # Dati base
    energies = np.random.lognormal(0.5, 1.2, n_photons)
    energies = np.clip(energies, 0.1, 80.0)
    times = np.random.exponential(500, n_photons)
    
    # Effetti strumentali
    # 1. Dead time
    dead_time_mask = np.random.random(n_photons) < 0.1
    times[dead_time_mask] += np.random.uniform(0, 0.1, np.sum(dead_time_mask))
    
    # 2. Background
    background_mask = np.random.random(n_photons) < 0.05
    energies[background_mask] *= np.random.uniform(0.5, 1.5, np.sum(background_mask))
    
    # 3. Calibrazione
    calibration_error = 1.0 + 0.02 * np.random.randn(n_photons)
    energies *= calibration_error
    
    # Lag intrinseci
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # Effetti QG se richiesti
    if has_qg:
        qg_delay = 0.001 * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    return energies, times

def advanced_qg_analysis(energies, times, method_name):
    """Analisi QG avanzata per dati complessi"""
    
    if len(energies) < 10:
        return None
    
    # Metodo 1: Correlazione diretta
    correlation = np.corrcoef(energies, times)[0, 1]
    significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
    
    # Metodo 2: Fit lineare
    slope, intercept = np.polyfit(energies, times, 1)
    
    # Metodo 3: Fit quadratico
    try:
        poly_coeffs = np.polyfit(energies, times, 2)
        poly_fit = np.polyval(poly_coeffs, energies)
        poly_residuals = times - poly_fit
        poly_corr = np.corrcoef(energies, poly_residuals)[0, 1]
        poly_sig = abs(poly_corr) * np.sqrt(len(energies) - 3) / np.sqrt(1 - poly_corr**2)
    except:
        poly_sig = 0
    
    # Metodo 4: Analisi per bin energetici
    n_bins = min(10, len(energies) // 50)
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
    else:
        avg_bin_corr = correlation
    
    return {
        'method': method_name,
        'n_photons': len(energies),
        'energy_range': [float(energies.min()), float(energies.max())],
        'time_range': [float(times.min()), float(times.max())],
        'direct_correlation': correlation,
        'direct_significance': significance,
        'linear_slope': slope,
        'quadratic_significance': poly_sig,
        'bin_average_correlation': avg_bin_corr,
        'n_energy_bins': n_bins
    }

def test_advanced_methodologies():
    """Test tutte le metodologie avanzate"""
    
    print("🔬 Test Metodologie Avanzate...")
    
    methodologies = {
        'Multi-Pulse GRB': generate_multi_pulse_grb,
        'Temporal Evolution GRB': generate_temporal_evolution_grb,
        'Complex Spectrum GRB': generate_complex_spectrum_grb,
        'Instrumental Effects GRB': generate_instrumental_effects_grb
    }
    
    results = {}
    
    for method_name, generator_func in methodologies.items():
        print(f"  🔬 Testando {method_name}...")
        
        # Test con QG
        if method_name == 'Multi-Pulse GRB':
            energies_qg, times_qg, _ = generator_func(has_qg=True)
        else:
            energies_qg, times_qg = generator_func(has_qg=True)
        result_qg = advanced_qg_analysis(energies_qg, times_qg, f"{method_name}_with_QG")
        
        # Test senza QG
        if method_name == 'Multi-Pulse GRB':
            energies_no_qg, times_no_qg, _ = generator_func(has_qg=False)
        else:
            energies_no_qg, times_no_qg = generator_func(has_qg=False)
        result_no_qg = advanced_qg_analysis(energies_no_qg, times_no_qg, f"{method_name}_without_QG")
        
        results[method_name] = {
            'with_qg': result_qg,
            'without_qg': result_no_qg
        }
    
    return results

def create_advanced_methodology_plots(results):
    """Crea grafici per metodologie avanzate"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Advanced Methodology Test Results', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Significatività per Metodologia
    methods = list(results.keys())
    significances_with_qg = []
    significances_without_qg = []
    
    for method in methods:
        if results[method]['with_qg']:
            significances_with_qg.append(results[method]['with_qg']['direct_significance'])
        else:
            significances_with_qg.append(0)
            
        if results[method]['without_qg']:
            significances_without_qg.append(results[method]['without_qg']['direct_significance'])
        else:
            significances_without_qg.append(0)
    
    x = np.arange(len(methods))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, significances_with_qg, width, 
                   label='With QG', color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, significances_without_qg, width,
                   label='Without QG', color='#3498db', alpha=0.8)
    
    ax1.set_xlabel('Methodology', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax1.set_title('Significance by Methodology', fontsize=16, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Correlazioni per Metodologia
    correlations_with_qg = []
    correlations_without_qg = []
    
    for method in methods:
        if results[method]['with_qg']:
            correlations_with_qg.append(results[method]['with_qg']['direct_correlation'])
        else:
            correlations_with_qg.append(0)
            
        if results[method]['without_qg']:
            correlations_without_qg.append(results[method]['without_qg']['direct_correlation'])
        else:
            correlations_without_qg.append(0)
    
    bars1 = ax2.bar(x - width/2, correlations_with_qg, width,
                   label='With QG', color='#e74c3c', alpha=0.8)
    bars2 = ax2.bar(x + width/2, correlations_without_qg, width,
                   label='Without QG', color='#3498db', alpha=0.8)
    
    ax2.set_xlabel('Methodology', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Correlation', fontsize=14, fontweight='bold')
    ax2.set_title('Correlation by Methodology', fontsize=16, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Numero Fotoni per Metodologia
    photons_with_qg = []
    photons_without_qg = []
    
    for method in methods:
        if results[method]['with_qg']:
            photons_with_qg.append(results[method]['with_qg']['n_photons'])
        else:
            photons_with_qg.append(0)
            
        if results[method]['without_qg']:
            photons_without_qg.append(results[method]['without_qg']['n_photons'])
        else:
            photons_without_qg.append(0)
    
    bars1 = ax3.bar(x - width/2, photons_with_qg, width,
                   label='With QG', color='#e74c3c', alpha=0.8)
    bars2 = ax3.bar(x + width/2, photons_without_qg, width,
                   label='Without QG', color='#3498db', alpha=0.8)
    
    ax3.set_xlabel('Methodology', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Number of Photons', fontsize=14, fontweight='bold')
    ax3.set_title('Photon Count by Methodology', fontsize=16, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(methods, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Riepilogo Performance
    performance_metrics = []
    for method in methods:
        if results[method]['with_qg'] and results[method]['without_qg']:
            qg_sig = results[method]['with_qg']['direct_significance']
            no_qg_sig = results[method]['without_qg']['direct_significance']
            performance = qg_sig - no_qg_sig
            performance_metrics.append(performance)
        else:
            performance_metrics.append(0)
    
    bars = ax4.bar(methods, performance_metrics, color='#f39c12', alpha=0.8)
    ax4.set_xlabel('Methodology', fontsize=14, fontweight='bold')
    ax4.set_ylabel('QG Detection Performance (σ)', fontsize=14, fontweight='bold')
    ax4.set_title('QG Detection Performance', fontsize=16, fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # Aggiungi valori sui bar
    for bar, perf in zip(bars, performance_metrics):
        ax4.text(bar.get_x() + bar.get_width()/2, perf + 0.01,
                f'{perf:.2f}σ', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('advanced_methodology_test_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici metodologie avanzate creati: advanced_methodology_test_results.png")

def main():
    """Funzione principale per test metodologie avanzate"""
    
    print("="*70)
    print("TEST METODOLOGIA AVANZATA")
    print("Dati realistici complessi e metodologie innovative")
    print("="*70)
    
    # Test metodologie avanzate
    print("\n🔬 Test Metodologie Avanzate...")
    results = test_advanced_methodologies()
    
    # Crea grafici
    print("\n📊 Creazione grafici metodologie avanzate...")
    create_advanced_methodology_plots(results)
    
    # Compila risultati
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'methodologies_tested': list(results.keys()),
        'results': results,
        'summary': {
            'total_methodologies': len(results),
            'successful_tests': sum(1 for r in results.values() if r['with_qg'] and r['without_qg']),
            'avg_significance_with_qg': np.mean([r['with_qg']['direct_significance'] for r in results.values() if r['with_qg']]),
            'avg_significance_without_qg': np.mean([r['without_qg']['direct_significance'] for r in results.values() if r['without_qg']])
        }
    }
    
    # Salva risultati
    with open('advanced_methodology_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI TEST METODOLOGIA AVANZATA")
    print("="*70)
    
    print(f"🎯 Metodologie Testate: {test_results['summary']['total_methodologies']}")
    print(f"🎯 Test Riusciti: {test_results['summary']['successful_tests']}")
    print(f"🎯 Significatività Media con QG: {test_results['summary']['avg_significance_with_qg']:.2f}σ")
    print(f"🎯 Significatività Media senza QG: {test_results['summary']['avg_significance_without_qg']:.2f}σ")
    
    print(f"\n🔬 Risultati per Metodologia:")
    for method_name, method_results in results.items():
        if method_results['with_qg'] and method_results['without_qg']:
            qg_sig = method_results['with_qg']['direct_significance']
            no_qg_sig = method_results['without_qg']['direct_significance']
            performance = qg_sig - no_qg_sig
            print(f"  {method_name}: {performance:.2f}σ performance")
    
    print("\n" + "="*70)
    print("✅ Test metodologia avanzata completato!")
    print("📊 Risultati salvati: advanced_methodology_test_results.json")
    print("📈 Grafici salvati: advanced_methodology_test_results.png")
    print("="*70)

if __name__ == "__main__":
    main()
