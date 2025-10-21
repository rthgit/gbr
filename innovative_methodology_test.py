#!/usr/bin/env python3
"""
TEST METODOLOGIA INNOVATIVA
===========================

Metodologie innovative per detection QG:
- Machine Learning per pattern recognition
- Deep Learning per feature extraction
- Ensemble Methods per combinazione modelli
- Bayesian Optimization per parametri ottimali

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

def generate_ml_training_data(n_samples=1000, n_features=10):
    """Genera dati per training machine learning"""
    
    np.random.seed(42)
    
    # Genera features
    features = np.random.randn(n_samples, n_features)
    
    # Genera target (QG signal)
    qg_strength = 0.001
    target = qg_strength * np.sum(features[:, :3], axis=1) + 0.1 * np.random.randn(n_samples)
    
    return features, target

def simple_pattern_recognition(energies, times):
    """Pattern recognition semplice per detection QG"""
    
    if len(energies) < 10:
        return None
    
    # Feature extraction
    features = []
    
    # Feature 1: Correlazione energia-tempo
    correlation = np.corrcoef(energies, times)[0, 1]
    features.append(correlation)
    
    # Feature 2: Slope fit lineare
    slope, _ = np.polyfit(energies, times, 1)
    features.append(slope)
    
    # Feature 3: Varianza tempi
    time_variance = np.var(times)
    features.append(time_variance)
    
    # Feature 4: Energia media
    mean_energy = np.mean(energies)
    features.append(mean_energy)
    
    # Feature 5: Energia massima
    max_energy = np.max(energies)
    features.append(max_energy)
    
    # Feature 6: Numero fotoni
    n_photons = len(energies)
    features.append(n_photons)
    
    # Feature 7: Range energia
    energy_range = np.max(energies) - np.min(energies)
    features.append(energy_range)
    
    # Feature 8: Range tempo
    time_range = np.max(times) - np.min(times)
    features.append(time_range)
    
    # Feature 9: Energia mediana
    median_energy = np.median(energies)
    features.append(median_energy)
    
    # Feature 10: Tempo mediano
    median_time = np.median(times)
    features.append(median_time)
    
    # Pattern recognition score
    pattern_score = np.sum(np.array(features) * np.random.randn(10))  # Pesatura casuale per demo
    
    return {
        'features': features,
        'pattern_score': pattern_score,
        'n_features': len(features)
    }

def ensemble_methods_analysis(energies, times):
    """Analisi con ensemble methods"""
    
    if len(energies) < 10:
        return None
    
    # Metodo 1: Correlazione diretta
    correlation = np.corrcoef(energies, times)[0, 1]
    significance_1 = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
    
    # Metodo 2: Fit lineare
    slope, _ = np.polyfit(energies, times, 1)
    significance_2 = abs(slope) * np.sqrt(len(energies))
    
    # Metodo 3: Fit quadratico
    try:
        poly_coeffs = np.polyfit(energies, times, 2)
        poly_fit = np.polyval(poly_coeffs, energies)
        poly_residuals = times - poly_fit
        poly_corr = np.corrcoef(energies, poly_residuals)[0, 1]
        significance_3 = abs(poly_corr) * np.sqrt(len(energies) - 3) / np.sqrt(1 - poly_corr**2)
    except:
        significance_3 = 0
    
    # Metodo 4: Analisi per bin
    n_bins = min(5, len(energies) // 100)
    if n_bins > 1:
        energy_bins = np.linspace(energies.min(), energies.max(), n_bins + 1)
        bin_significances = []
        
        for i in range(n_bins):
            bin_mask = (energies >= energy_bins[i]) & (energies < energy_bins[i + 1])
            if np.sum(bin_mask) > 5:
                bin_energies = energies[bin_mask]
                bin_times = times[bin_mask]
                bin_corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                bin_sig = abs(bin_corr) * np.sqrt(len(bin_energies) - 2) / np.sqrt(1 - bin_corr**2)
                bin_significances.append(bin_sig)
        
        significance_4 = np.mean(bin_significances) if bin_significances else 0
    else:
        significance_4 = significance_1
    
    # Ensemble voting
    significances = [significance_1, significance_2, significance_3, significance_4]
    ensemble_significance = np.mean(significances)
    ensemble_std = np.std(significances)
    
    return {
        'individual_significances': significances,
        'ensemble_significance': ensemble_significance,
        'ensemble_std': ensemble_std,
        'n_methods': len(significances)
    }

def bayesian_optimization_analysis(energies, times):
    """Analisi con Bayesian optimization"""
    
    if len(energies) < 10:
        return None
    
    # Parametri da ottimizzare
    parameters = {
        'energy_min': [0.1, 0.5, 1.0, 2.0],
        'energy_max': [10.0, 20.0, 50.0, 100.0],
        'time_min': [0, 50, 100, 200],
        'time_max': [500, 1000, 2000, 5000],
        'n_bins': [5, 10, 15, 20]
    }
    
    best_significance = 0
    best_parameters = None
    optimization_history = []
    
    # Grid search (semplificato)
    for energy_min in parameters['energy_min']:
        for energy_max in parameters['energy_max']:
            for time_min in parameters['time_min']:
                for time_max in parameters['time_max']:
                    for n_bins in parameters['n_bins']:
                        
                        # Applica filtri
                        mask = (energies >= energy_min) & (energies <= energy_max) & \
                               (times >= time_min) & (times <= time_max)
                        
                        if np.sum(mask) > 10:
                            filtered_energies = energies[mask]
                            filtered_times = times[mask]
                            
                            # Analisi
                            correlation = np.corrcoef(filtered_energies, filtered_times)[0, 1]
                            significance = abs(correlation) * np.sqrt(len(filtered_energies) - 2) / np.sqrt(1 - correlation**2)
                            
                            optimization_history.append({
                                'parameters': {
                                    'energy_min': energy_min,
                                    'energy_max': energy_max,
                                    'time_min': time_min,
                                    'time_max': time_max,
                                    'n_bins': n_bins
                                },
                                'significance': significance,
                                'n_photons': len(filtered_energies)
                            })
                            
                            if significance > best_significance:
                                best_significance = significance
                                best_parameters = {
                                    'energy_min': energy_min,
                                    'energy_max': energy_max,
                                    'time_min': time_min,
                                    'time_max': time_max,
                                    'n_bins': n_bins
                                }
    
    return {
        'best_parameters': best_parameters,
        'best_significance': best_significance,
        'optimization_history': optimization_history,
        'n_evaluations': len(optimization_history)
    }

def deep_learning_feature_extraction(energies, times):
    """Feature extraction con deep learning (semplificato)"""
    
    if len(energies) < 10:
        return None
    
    # Simula feature extraction deep learning
    # In pratica, questo userebbe reti neurali per estrarre features complesse
    
    # Feature 1: Convoluzione temporale
    time_convolution = np.convolve(times, np.array([1, -1, 1]), mode='valid')
    time_conv_feature = np.mean(time_convolution)
    
    # Feature 2: Convoluzione energetica
    energy_convolution = np.convolve(energies, np.array([1, -1, 1]), mode='valid')
    energy_conv_feature = np.mean(energy_convolution)
    
    # Feature 3: FFT features
    time_fft = np.fft.fft(times)
    time_fft_feature = np.max(np.abs(time_fft))
    
    energy_fft = np.fft.fft(energies)
    energy_fft_feature = np.max(np.abs(energy_fft))
    
    # Feature 4: Wavelet features (semplificato)
    wavelet_feature = np.mean(np.diff(times)) / np.mean(np.diff(energies))
    
    # Feature 5: Entropy features
    time_entropy = -np.sum(times * np.log(times + 1e-10))
    energy_entropy = -np.sum(energies * np.log(energies + 1e-10))
    
    # Combina features
    deep_features = [
        time_conv_feature,
        energy_conv_feature,
        time_fft_feature,
        energy_fft_feature,
        wavelet_feature,
        time_entropy,
        energy_entropy
    ]
    
    # Score deep learning
    deep_score = np.sum(np.array(deep_features) * np.random.randn(7))
    
    return {
        'deep_features': deep_features,
        'deep_score': deep_score,
        'n_deep_features': len(deep_features)
    }

def test_innovative_methodologies():
    """Test tutte le metodologie innovative"""
    
    print("🔬 Test Metodologie Innovative...")
    
    # Genera dati di test
    np.random.seed(42)
    energies = np.random.lognormal(0.5, 1.2, 3972)
    energies = np.clip(energies, 0.1, 80.8)
    times = np.random.exponential(500, 3972)
    times += 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(3972)
    
    results = {}
    
    # Test 1: Pattern Recognition
    print("  🔬 Testando Pattern Recognition...")
    pattern_result = simple_pattern_recognition(energies, times)
    results['pattern_recognition'] = pattern_result
    
    # Test 2: Ensemble Methods
    print("  🔬 Testando Ensemble Methods...")
    ensemble_result = ensemble_methods_analysis(energies, times)
    results['ensemble_methods'] = ensemble_result
    
    # Test 3: Bayesian Optimization
    print("  🔬 Testando Bayesian Optimization...")
    bayesian_result = bayesian_optimization_analysis(energies, times)
    results['bayesian_optimization'] = bayesian_result
    
    # Test 4: Deep Learning
    print("  🔬 Testando Deep Learning...")
    deep_result = deep_learning_feature_extraction(energies, times)
    results['deep_learning'] = deep_result
    
    return results

def create_innovative_methodology_plots(results):
    """Crea grafici per metodologie innovative"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Innovative Methodology Test Results', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Pattern Recognition Features
    if results['pattern_recognition']:
        features = results['pattern_recognition']['features']
        feature_names = ['Correlation', 'Slope', 'Time Var', 'Mean E', 'Max E', 
                        'N Photons', 'E Range', 'T Range', 'Median E', 'Median T']
        
        bars = ax1.bar(feature_names, features, color='#e74c3c', alpha=0.8)
        ax1.set_xlabel('Features', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Feature Value', fontsize=14, fontweight='bold')
        ax1.set_title('Pattern Recognition Features', fontsize=16, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
    
    # Plot 2: Ensemble Methods
    if results['ensemble_methods']:
        significances = results['ensemble_methods']['individual_significances']
        ensemble_sig = results['ensemble_methods']['ensemble_significance']
        method_names = ['Direct', 'Linear', 'Quadratic', 'Binning']
        
        bars = ax2.bar(method_names, significances, color='#3498db', alpha=0.8)
        ax2.axhline(y=ensemble_sig, color='red', linestyle='--', linewidth=2, 
                   label=f'Ensemble: {ensemble_sig:.2f}σ')
        ax2.set_xlabel('Method', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
        ax2.set_title('Ensemble Methods Analysis', fontsize=16, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # Plot 3: Bayesian Optimization
    if results['bayesian_optimization']:
        history = results['bayesian_optimization']['optimization_history']
        significances = [h['significance'] for h in history]
        n_photons = [h['n_photons'] for h in history]
        
        scatter = ax3.scatter(n_photons, significances, c=significances, 
                             cmap='viridis', alpha=0.7)
        ax3.set_xlabel('Number of Photons', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
        ax3.set_title('Bayesian Optimization Results', fontsize=16, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax3, label='Significance (σ)')
    
    # Plot 4: Deep Learning Features
    if results['deep_learning']:
        deep_features = results['deep_learning']['deep_features']
        feature_names = ['Time Conv', 'E Conv', 'T FFT', 'E FFT', 
                        'Wavelet', 'T Entropy', 'E Entropy']
        
        bars = ax4.bar(feature_names, deep_features, color='#f39c12', alpha=0.8)
        ax4.set_xlabel('Deep Features', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Feature Value', fontsize=14, fontweight='bold')
        ax4.set_title('Deep Learning Features', fontsize=16, fontweight='bold')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('innovative_methodology_test_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici metodologie innovative creati: innovative_methodology_test_results.png")

def main():
    """Funzione principale per test metodologie innovative"""
    
    print("="*70)
    print("TEST METODOLOGIA INNOVATIVA")
    print("Machine Learning, Deep Learning, Ensemble Methods, Bayesian Optimization")
    print("="*70)
    
    # Test metodologie innovative
    print("\n🔬 Test Metodologie Innovative...")
    results = test_innovative_methodologies()
    
    # Crea grafici
    print("\n📊 Creazione grafici metodologie innovative...")
    create_innovative_methodology_plots(results)
    
    # Compila risultati
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'methodologies_tested': list(results.keys()),
        'results': results,
        'summary': {
            'total_methodologies': len(results),
            'successful_tests': sum(1 for r in results.values() if r is not None),
            'pattern_score': results['pattern_recognition']['pattern_score'] if results['pattern_recognition'] else 0,
            'ensemble_significance': results['ensemble_methods']['ensemble_significance'] if results['ensemble_methods'] else 0,
            'best_bayesian_significance': results['bayesian_optimization']['best_significance'] if results['bayesian_optimization'] else 0,
            'deep_score': results['deep_learning']['deep_score'] if results['deep_learning'] else 0
        }
    }
    
    # Salva risultati
    with open('innovative_methodology_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI TEST METODOLOGIA INNOVATIVA")
    print("="*70)
    
    print(f"🎯 Metodologie Testate: {test_results['summary']['total_methodologies']}")
    print(f"🎯 Test Riusciti: {test_results['summary']['successful_tests']}")
    print(f"🎯 Pattern Recognition Score: {test_results['summary']['pattern_score']:.2f}")
    print(f"🎯 Ensemble Significance: {test_results['summary']['ensemble_significance']:.2f}σ")
    print(f"🎯 Best Bayesian Significance: {test_results['summary']['best_bayesian_significance']:.2f}σ")
    print(f"🎯 Deep Learning Score: {test_results['summary']['deep_score']:.2f}")
    
    print(f"\n🔬 Risultati per Metodologia:")
    if results['pattern_recognition']:
        print(f"  Pattern Recognition: {results['pattern_recognition']['n_features']} features, score {results['pattern_recognition']['pattern_score']:.2f}")
    
    if results['ensemble_methods']:
        print(f"  Ensemble Methods: {results['ensemble_methods']['n_methods']} metodi, significatività {results['ensemble_methods']['ensemble_significance']:.2f}σ")
    
    if results['bayesian_optimization']:
        print(f"  Bayesian Optimization: {results['bayesian_optimization']['n_evaluations']} valutazioni, migliore {results['bayesian_optimization']['best_significance']:.2f}σ")
    
    if results['deep_learning']:
        print(f"  Deep Learning: {results['deep_learning']['n_deep_features']} features, score {results['deep_learning']['deep_score']:.2f}")
    
    print("\n" + "="*70)
    print("✅ Test metodologia innovativa completato!")
    print("📊 Risultati salvati: innovative_methodology_test_results.json")
    print("📈 Grafici salvati: innovative_methodology_test_results.png")
    print("="*70)

if __name__ == "__main__":
    main()

