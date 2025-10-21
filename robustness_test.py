#!/usr/bin/env python3
"""
TEST ROBUSTEZZA METODOLOGICA
============================

Test robustezza della metodologia QG:
- Variazione parametri cosmologici
- Variazione modelli lag intrinseci
- Variazione soglie detection
- Variazione filtri dati

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

def generate_test_grb_data(n_photons=3972, has_qg=True, qg_strength=0.001):
    """Genera dati GRB di test"""
    
    np.random.seed(42)
    
    # Parametri base
    redshift = 1.822
    energies = np.random.lognormal(0.5, 1.2, n_photons)
    energies = np.clip(energies, 0.1, 80.8)
    times = np.random.exponential(500, n_photons)
    
    # Lag intrinseci
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # Effetti QG se richiesti
    if has_qg:
        qg_delay = qg_strength * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    # Rumore
    times += 0.1 * np.random.randn(n_photons)
    
    return energies, times, redshift

def test_cosmological_parameters():
    """Test robustezza a parametri cosmologici"""
    
    print("🔬 Test Parametri Cosmologici...")
    
    # Parametri da testare
    H0_values = [65.0, 67.4, 70.0, 72.0, 75.0]  # km/s/Mpc
    Omega_M_values = [0.25, 0.30, 0.35, 0.40, 0.45]
    Omega_Lambda_values = [0.60, 0.70, 0.75, 0.80, 0.85]
    
    results = {}
    
    # Test H0
    print("  🔬 Testando H0...")
    H0_results = []
    for H0 in H0_values:
        energies, times, redshift = generate_test_grb_data()
        
        # Calcola d_L con H0 diverso
        c = 3e5  # km/s
        d_L = (c / H0) * redshift * (1 + redshift)
        
        # Analisi QG
        correlation = np.corrcoef(energies, times)[0, 1]
        significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
        
        slope, _ = np.polyfit(energies, times, 1)
        if abs(slope) > 1e-10:
            E_QG = d_L * 3.086e22 / (c * abs(slope)) / 1e9
        else:
            E_QG = np.inf
        
        H0_results.append({
            'H0': H0,
            'correlation': correlation,
            'significance': significance,
            'E_QG': E_QG
        })
    
    results['H0_variation'] = H0_results
    
    # Test Omega_M
    print("  🔬 Testando Omega_M...")
    Omega_M_results = []
    for Omega_M in Omega_M_values:
        energies, times, redshift = generate_test_grb_data()
        
        # Calcola d_L con Omega_M diverso (approssimazione)
        c = 3e5
        H0 = 70.0
        Omega_Lambda = 0.70
        d_L = (c / H0) * redshift * (1 + redshift) * (1 + 0.1 * (Omega_M - 0.30))
        
        # Analisi QG
        correlation = np.corrcoef(energies, times)[0, 1]
        significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
        
        slope, _ = np.polyfit(energies, times, 1)
        if abs(slope) > 1e-10:
            E_QG = d_L * 3.086e22 / (c * abs(slope)) / 1e9
        else:
            E_QG = np.inf
        
        Omega_M_results.append({
            'Omega_M': Omega_M,
            'correlation': correlation,
            'significance': significance,
            'E_QG': E_QG
        })
    
    results['Omega_M_variation'] = Omega_M_results
    
    return results

def test_intrinsic_lag_models():
    """Test robustezza a modelli lag intrinseci"""
    
    print("🔬 Test Modelli Lag Intrinseci...")
    
    # Modelli lag da testare
    lag_models = {
        'power_law': lambda E, alpha, beta: alpha * np.power(E, -beta),
        'exponential': lambda E, alpha, beta: alpha * np.exp(-E / beta),
        'logarithmic': lambda E, alpha, beta: alpha * np.log(E / beta),
        'linear': lambda E, alpha, beta: alpha * E + beta,
        'quadratic': lambda E, alpha, beta, gamma: alpha * E**2 + beta * E + gamma
    }
    
    results = {}
    
    for model_name, model_func in lag_models.items():
        print(f"  🔬 Testando modello {model_name}...")
        
        # Genera dati con lag intrinseci specifici
        energies, times, redshift = generate_test_grb_data()
        
        # Applica modello lag specifico
        if model_name == 'quadratic':
            lag_params = [0.1, -0.01, 0.001]
            intrinsic_lag = model_func(energies, *lag_params)
        else:
            lag_params = [0.1, 10.0]
            intrinsic_lag = model_func(energies, *lag_params)
        
        times += intrinsic_lag
        
        # Analisi QG
        correlation = np.corrcoef(energies, times)[0, 1]
        significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
        
        slope, _ = np.polyfit(energies, times, 1)
        
        results[model_name] = {
            'correlation': correlation,
            'significance': significance,
            'slope': slope,
            'lag_parameters': lag_params
        }
    
    return results

def test_detection_thresholds():
    """Test robustezza a soglie detection"""
    
    print("🔬 Test Soglie Detection...")
    
    # Soglie da testare
    thresholds = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    
    results = {}
    
    for threshold in thresholds:
        print(f"  🔬 Testando soglia {threshold}σ...")
        
        # Genera dati
        energies, times, redshift = generate_test_grb_data()
        
        # Analisi QG
        correlation = np.corrcoef(energies, times)[0, 1]
        significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
        
        # Applica soglia
        detection = significance >= threshold
        
        results[f'threshold_{threshold}'] = {
            'threshold': threshold,
            'significance': significance,
            'detection': detection,
            'correlation': correlation
        }
    
    return results

def test_data_filters():
    """Test robustezza a filtri dati"""
    
    print("🔬 Test Filtri Dati...")
    
    # Filtri da testare
    filters = {
        'no_filter': lambda E, T: np.ones(len(E), dtype=bool),
        'energy_min_0.1': lambda E, T: E >= 0.1,
        'energy_min_1.0': lambda E, T: E >= 1.0,
        'energy_max_10.0': lambda E, T: E <= 10.0,
        'energy_max_50.0': lambda E, T: E <= 50.0,
        'time_min_0': lambda E, T: T >= 0,
        'time_max_1000': lambda E, T: T <= 1000,
        'time_max_2000': lambda E, T: T <= 2000,
        'combined_strict': lambda E, T: (E >= 1.0) & (E <= 10.0) & (T >= 0) & (T <= 1000),
        'combined_loose': lambda E, T: (E >= 0.1) & (E <= 50.0) & (T >= -100) & (T <= 2000)
    }
    
    results = {}
    
    for filter_name, filter_func in filters.items():
        print(f"  🔬 Testando filtro {filter_name}...")
        
        # Genera dati
        energies, times, redshift = generate_test_grb_data()
        
        # Applica filtro
        mask = filter_func(energies, times)
        filtered_energies = energies[mask]
        filtered_times = times[mask]
        
        if len(filtered_energies) > 10:
            # Analisi QG su dati filtrati
            correlation = np.corrcoef(filtered_energies, filtered_times)[0, 1]
            significance = abs(correlation) * np.sqrt(len(filtered_energies) - 2) / np.sqrt(1 - correlation**2)
            
            slope, _ = np.polyfit(filtered_energies, filtered_times, 1)
        else:
            correlation = 0
            significance = 0
            slope = 0
        
        results[filter_name] = {
            'n_photons_original': len(energies),
            'n_photons_filtered': len(filtered_energies),
            'filter_efficiency': len(filtered_energies) / len(energies),
            'correlation': correlation,
            'significance': significance,
            'slope': slope
        }
    
    return results

def create_robustness_plots(cosmological_results, lag_results, threshold_results, filter_results):
    """Crea grafici di robustezza"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Methodology Robustness Test Results', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Parametri Cosmologici
    H0_values = [r['H0'] for r in cosmological_results['H0_variation']]
    H0_significances = [r['significance'] for r in cosmological_results['H0_variation']]
    
    ax1.plot(H0_values, H0_significances, 'o-', color='#e74c3c', linewidth=2, markersize=8)
    ax1.set_xlabel('H₀ (km/s/Mpc)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax1.set_title('Robustness to H₀ Variation', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=2.0, color='red', linestyle='--', alpha=0.5, label='2σ threshold')
    ax1.legend()
    
    # Plot 2: Modelli Lag Intrinseci
    lag_models = list(lag_results.keys())
    lag_significances = [lag_results[model]['significance'] for model in lag_models]
    
    bars = ax2.bar(lag_models, lag_significances, color='#3498db', alpha=0.8)
    ax2.set_xlabel('Lag Model', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax2.set_title('Robustness to Lag Models', fontsize=16, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=2.0, color='red', linestyle='--', alpha=0.5, label='2σ threshold')
    ax2.legend()
    
    # Plot 3: Soglie Detection
    thresholds = [r['threshold'] for r in threshold_results.values()]
    detections = [r['detection'] for r in threshold_results.values()]
    detection_rate = np.mean(detections)
    
    ax3.bar(thresholds, detections, color='#f39c12', alpha=0.8)
    ax3.set_xlabel('Detection Threshold (σ)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Detection (1=Yes, 0=No)', fontsize=14, fontweight='bold')
    ax3.set_title(f'Detection Rate: {detection_rate:.1%}', fontsize=16, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Filtri Dati
    filter_names = list(filter_results.keys())
    filter_significances = [filter_results[name]['significance'] for name in filter_names]
    filter_efficiencies = [filter_results[name]['filter_efficiency'] for name in filter_names]
    
    bars = ax4.bar(filter_names, filter_significances, color='#9b59b6', alpha=0.8)
    ax4.set_xlabel('Data Filter', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax4.set_title('Robustness to Data Filters', fontsize=16, fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=2.0, color='red', linestyle='--', alpha=0.5, label='2σ threshold')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('robustness_test_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici robustezza creati: robustness_test_results.png")

def main():
    """Funzione principale per test robustezza"""
    
    print("="*70)
    print("TEST ROBUSTEZZA METODOLOGICA")
    print("Variazione parametri e modelli per testare robustezza")
    print("="*70)
    
    # Test robustezza
    print("\n🔬 Test Parametri Cosmologici...")
    cosmological_results = test_cosmological_parameters()
    
    print("\n🔬 Test Modelli Lag Intrinseci...")
    lag_results = test_intrinsic_lag_models()
    
    print("\n🔬 Test Soglie Detection...")
    threshold_results = test_detection_thresholds()
    
    print("\n🔬 Test Filtri Dati...")
    filter_results = test_data_filters()
    
    # Crea grafici
    print("\n📊 Creazione grafici robustezza...")
    create_robustness_plots(cosmological_results, lag_results, threshold_results, filter_results)
    
    # Compila risultati
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'cosmological_parameters': cosmological_results,
        'intrinsic_lag_models': lag_results,
        'detection_thresholds': threshold_results,
        'data_filters': filter_results,
        'summary': {
            'H0_significance_range': [min([r['significance'] for r in cosmological_results['H0_variation']]),
                                     max([r['significance'] for r in cosmological_results['H0_variation']])],
            'lag_model_significance_range': [min([r['significance'] for r in lag_results.values()]),
                                           max([r['significance'] for r in lag_results.values()])],
            'detection_rate': np.mean([r['detection'] for r in threshold_results.values()]),
            'filter_significance_range': [min([r['significance'] for r in filter_results.values()]),
                                        max([r['significance'] for r in filter_results.values()])]
        }
    }
    
    # Salva risultati
    with open('robustness_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI TEST ROBUSTEZZA")
    print("="*70)
    
    print(f"🎯 H₀ Significatività Range: {test_results['summary']['H0_significance_range'][0]:.2f}σ - {test_results['summary']['H0_significance_range'][1]:.2f}σ")
    print(f"🎯 Lag Model Significatività Range: {test_results['summary']['lag_model_significance_range'][0]:.2f}σ - {test_results['summary']['lag_model_significance_range'][1]:.2f}σ")
    print(f"🎯 Detection Rate: {test_results['summary']['detection_rate']:.1%}")
    print(f"🎯 Filter Significatività Range: {test_results['summary']['filter_significance_range'][0]:.2f}σ - {test_results['summary']['filter_significance_range'][1]:.2f}σ")
    
    print(f"\n🔬 Robustezza Parametri Cosmologici:")
    for result in cosmological_results['H0_variation']:
        print(f"  H₀ = {result['H0']}: {result['significance']:.2f}σ")
    
    print(f"\n🔬 Robustezza Modelli Lag:")
    for model_name, result in lag_results.items():
        print(f"  {model_name}: {result['significance']:.2f}σ")
    
    print(f"\n🔬 Robustezza Filtri Dati:")
    for filter_name, result in filter_results.items():
        print(f"  {filter_name}: {result['significance']:.2f}σ (efficienza: {result['filter_efficiency']:.1%})")
    
    print("\n" + "="*70)
    print("✅ Test robustezza completato!")
    print("📊 Risultati salvati: robustness_test_results.json")
    print("📈 Grafici salvati: robustness_test_results.png")
    print("="*70)

if __name__ == "__main__":
    main()
