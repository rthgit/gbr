#!/usr/bin/env python3
"""
INVESTIGAZIONE ANOMALIE SPECIFICHE
==================================

Investigazione approfondita delle anomalie rilevate:
- Ensemble Methods: 6.37σ
- Bayesian Optimization: 3.04σ
- Power Law Lag Model: 4.04σ
- Quadratic Lag Model: 3.34σ

Test per distinguere tra segnale reale e bias metodologici.

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

def generate_null_data(n_photons=3972):
    """Genera dati null (senza QG) per test"""
    
    np.random.seed(42)
    
    # Dati completamente casuali
    energies = np.random.lognormal(0.5, 1.2, n_photons)
    energies = np.clip(energies, 0.1, 80.8)
    times = np.random.exponential(500, n_photons)
    
    # Solo lag intrinseci, nessun QG
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # Rumore
    times += 0.1 * np.random.randn(n_photons)
    
    return energies, times

def generate_qg_injected_data(n_photons=3972, qg_strength=0.001):
    """Genera dati con QG iniettato noto"""
    
    np.random.seed(43)
    
    # Dati base
    energies = np.random.lognormal(0.5, 1.2, n_photons)
    energies = np.clip(energies, 0.1, 80.8)
    times = np.random.exponential(500, n_photons)
    
    # Lag intrinseci
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # QG iniettato noto
    qg_delay = qg_strength * (energies / 10.0) * (1 + 0.1 * times / 1000)
    times += qg_delay
    
    # Rumore
    times += 0.1 * np.random.randn(n_photons)
    
    return energies, times, qg_strength

def ensemble_methods_analysis(energies, times):
    """Analisi ensemble methods (anomalia 6.37σ)"""
    
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
    """Analisi Bayesian optimization (anomalia 3.04σ)"""
    
    if len(energies) < 10:
        return None
    
    # Parametri da ottimizzare (semplificato per velocità)
    parameters = {
        'energy_min': [0.1, 0.5, 1.0, 2.0],
        'energy_max': [10.0, 20.0, 50.0, 100.0],
        'time_min': [0, 50, 100, 200],
        'time_max': [500, 1000, 2000, 5000]
    }
    
    best_significance = 0
    best_parameters = None
    optimization_history = []
    
    # Grid search semplificato
    for energy_min in parameters['energy_min']:
        for energy_max in parameters['energy_max']:
            for time_min in parameters['time_min']:
                for time_max in parameters['time_max']:
                    
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
                                'time_max': time_max
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
                                'time_max': time_max
                            }
    
    return {
        'best_parameters': best_parameters,
        'best_significance': best_significance,
        'optimization_history': optimization_history,
        'n_evaluations': len(optimization_history)
    }

def power_law_lag_analysis(energies, times):
    """Analisi power law lag model (anomalia 4.04σ)"""
    
    if len(energies) < 10:
        return None
    
    # Modello power law
    def power_law(E, t0, alpha, beta):
        return t0 + alpha * np.power(E, -beta)
    
    try:
        # Fit power law
        popt, pcov = curve_fit(power_law, energies, times, 
                              p0=[np.mean(times), 0.1, 0.3], 
                              bounds=([-np.inf, -10, -2], [np.inf, 10, 2]))
        
        predicted = power_law(energies, *popt)
        residuals = times - predicted
        
        # Analisi residui
        if len(residuals) > 2:
            corr = np.corrcoef(energies, residuals)[0, 1]
            sig = abs(corr) * np.sqrt(len(residuals) - 2) / np.sqrt(1 - corr**2)
            
            return {
                'model_parameters': popt.tolist(),
                'model_covariance': pcov.tolist(),
                'residual_correlation': corr,
                'residual_significance': sig,
                'rms_residuals': np.sqrt(np.mean(residuals**2)),
                'model_fit_quality': 1.0 - np.var(residuals) / np.var(times)
            }
    except:
        pass
    
    return None

def quadratic_lag_analysis(energies, times):
    """Analisi quadratic lag model (anomalia 3.34σ)"""
    
    if len(energies) < 10:
        return None
    
    # Modello quadratico
    def quadratic(E, t0, alpha, beta, gamma):
        return t0 + alpha * E**2 + beta * E + gamma
    
    try:
        # Fit quadratico
        popt, pcov = curve_fit(quadratic, energies, times, 
                              p0=[np.mean(times), 0.001, 0.01, 0.1], 
                              bounds=([-np.inf, -1, -1, -1], [np.inf, 1, 1, 1]))
        
        predicted = quadratic(energies, *popt)
        residuals = times - predicted
        
        # Analisi residui
        if len(residuals) > 3:
            corr = np.corrcoef(energies, residuals)[0, 1]
            sig = abs(corr) * np.sqrt(len(residuals) - 3) / np.sqrt(1 - corr**2)
            
            return {
                'model_parameters': popt.tolist(),
                'model_covariance': pcov.tolist(),
                'residual_correlation': corr,
                'residual_significance': sig,
                'rms_residuals': np.sqrt(np.mean(residuals**2)),
                'model_fit_quality': 1.0 - np.var(residuals) / np.var(times)
            }
    except:
        pass
    
    return None

def test_anomaly_robustness():
    """Test robustezza delle anomalie"""
    
    print("🔬 Test Robustezza Anomalie...")
    
    # Test 1: Dati null (nessun QG)
    print("  🔬 Testando con dati null...")
    null_energies, null_times = generate_null_data()
    
    null_ensemble = ensemble_methods_analysis(null_energies, null_times)
    null_bayesian = bayesian_optimization_analysis(null_energies, null_times)
    null_power_law = power_law_lag_analysis(null_energies, null_times)
    null_quadratic = quadratic_lag_analysis(null_energies, null_times)
    
    # Test 2: QG iniettato noto
    print("  🔬 Testando con QG iniettato...")
    qg_energies, qg_times, qg_strength = generate_qg_injected_data()
    
    qg_ensemble = ensemble_methods_analysis(qg_energies, qg_times)
    qg_bayesian = bayesian_optimization_analysis(qg_energies, qg_times)
    qg_power_law = power_law_lag_analysis(qg_energies, qg_times)
    qg_quadratic = quadratic_lag_analysis(qg_energies, qg_times)
    
    # Test 3: Multiple realizations
    print("  🔬 Testando multiple realizzazioni...")
    n_realizations = 10
    null_realizations = []
    qg_realizations = []
    
    for i in range(n_realizations):
        # Dati null
        n_energies, n_times = generate_null_data()
        n_ensemble = ensemble_methods_analysis(n_energies, n_times)
        if n_ensemble:
            null_realizations.append(n_ensemble['ensemble_significance'])
        
        # Dati QG
        q_energies, q_times, _ = generate_qg_injected_data()
        q_ensemble = ensemble_methods_analysis(q_energies, q_times)
        if q_ensemble:
            qg_realizations.append(q_ensemble['ensemble_significance'])
    
    return {
        'null_data': {
            'ensemble': null_ensemble,
            'bayesian': null_bayesian,
            'power_law': null_power_law,
            'quadratic': null_quadratic
        },
        'qg_data': {
            'ensemble': qg_ensemble,
            'bayesian': qg_bayesian,
            'power_law': qg_power_law,
            'quadratic': qg_quadratic,
            'injected_qg_strength': qg_strength
        },
        'multiple_realizations': {
            'null_significances': null_realizations,
            'qg_significances': qg_realizations,
            'n_realizations': n_realizations
        }
    }

def test_anomaly_calibration():
    """Test calibrazione delle anomalie"""
    
    print("🔬 Test Calibrazione Anomalie...")
    
    # Test con diversi livelli di QG
    qg_strengths = [0.0, 0.0001, 0.0005, 0.001, 0.002, 0.005]
    calibration_results = []
    
    for qg_strength in qg_strengths:
        print(f"  🔬 Testando QG strength = {qg_strength}...")
        
        if qg_strength == 0.0:
            energies, times = generate_null_data()
        else:
            energies, times, _ = generate_qg_injected_data(qg_strength=qg_strength)
        
        # Test tutte le metodologie
        ensemble_result = ensemble_methods_analysis(energies, times)
        bayesian_result = bayesian_optimization_analysis(energies, times)
        power_law_result = power_law_lag_analysis(energies, times)
        quadratic_result = quadratic_lag_analysis(energies, times)
        
        calibration_results.append({
            'qg_strength': qg_strength,
            'ensemble_significance': ensemble_result['ensemble_significance'] if ensemble_result else 0,
            'bayesian_significance': bayesian_result['best_significance'] if bayesian_result else 0,
            'power_law_significance': power_law_result['residual_significance'] if power_law_result else 0,
            'quadratic_significance': quadratic_result['residual_significance'] if quadratic_result else 0
        })
    
    return calibration_results

def create_anomaly_investigation_plots(robustness_results, calibration_results):
    """Crea grafici per investigazione anomalie"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Anomaly Investigation Results', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Robustezza Anomalie
    methods = ['Ensemble', 'Bayesian', 'Power Law', 'Quadratic']
    null_significances = [
        robustness_results['null_data']['ensemble']['ensemble_significance'] if robustness_results['null_data']['ensemble'] else 0,
        robustness_results['null_data']['bayesian']['best_significance'] if robustness_results['null_data']['bayesian'] else 0,
        robustness_results['null_data']['power_law']['residual_significance'] if robustness_results['null_data']['power_law'] else 0,
        robustness_results['null_data']['quadratic']['residual_significance'] if robustness_results['null_data']['quadratic'] else 0
    ]
    qg_significances = [
        robustness_results['qg_data']['ensemble']['ensemble_significance'] if robustness_results['qg_data']['ensemble'] else 0,
        robustness_results['qg_data']['bayesian']['best_significance'] if robustness_results['qg_data']['bayesian'] else 0,
        robustness_results['qg_data']['power_law']['residual_significance'] if robustness_results['qg_data']['power_law'] else 0,
        robustness_results['qg_data']['quadratic']['residual_significance'] if robustness_results['qg_data']['quadratic'] else 0
    ]
    
    x = np.arange(len(methods))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, null_significances, width, 
                   label='Null Data', color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, qg_significances, width,
                   label='QG Injected', color='#3498db', alpha=0.8)
    
    ax1.set_xlabel('Method', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax1.set_title('Anomaly Robustness Test', fontsize=16, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=3.0, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
    ax1.legend()
    
    # Plot 2: Multiple Realizations
    null_realizations = robustness_results['multiple_realizations']['null_significances']
    qg_realizations = robustness_results['multiple_realizations']['qg_significances']
    
    ax2.hist(null_realizations, bins=5, alpha=0.7, label='Null Data', color='#e74c3c')
    ax2.hist(qg_realizations, bins=5, alpha=0.7, label='QG Data', color='#3498db')
    ax2.set_xlabel('Ensemble Significance (σ)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=14, fontweight='bold')
    ax2.set_title('Multiple Realizations Distribution', fontsize=16, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Calibration Curve
    qg_strengths = [r['qg_strength'] for r in calibration_results]
    ensemble_sigs = [r['ensemble_significance'] for r in calibration_results]
    bayesian_sigs = [r['bayesian_significance'] for r in calibration_results]
    
    ax3.plot(qg_strengths, ensemble_sigs, 'o-', label='Ensemble', color='#e74c3c', linewidth=2)
    ax3.plot(qg_strengths, bayesian_sigs, 's-', label='Bayesian', color='#3498db', linewidth=2)
    ax3.set_xlabel('QG Strength', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax3.set_title('Calibration Curve', fontsize=16, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=3.0, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
    ax3.legend()
    
    # Plot 4: Anomaly Summary
    anomaly_summary = {
        'Ensemble Methods': max(null_significances[0], qg_significances[0]),
        'Bayesian Optimization': max(null_significances[1], qg_significances[1]),
        'Power Law Lag': max(null_significances[2], qg_significances[2]),
        'Quadratic Lag': max(null_significances[3], qg_significances[3])
    }
    
    bars = ax4.bar(anomaly_summary.keys(), anomaly_summary.values(), 
                   color=['#e74c3c', '#3498db', '#f39c12', '#9b59b6'], alpha=0.8)
    ax4.set_xlabel('Method', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Max Significance (σ)', fontsize=14, fontweight='bold')
    ax4.set_title('Anomaly Summary', fontsize=16, fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=3.0, color='red', linestyle='--', alpha=0.5, label='3σ threshold')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('anomaly_investigation_test_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici investigazione anomalie creati: anomaly_investigation_test_results.png")

def main():
    """Funzione principale per investigazione anomalie"""
    
    print("="*70)
    print("INVESTIGAZIONE ANOMALIE SPECIFICHE")
    print("Analisi approfondita delle anomalie rilevate nei test precedenti")
    print("="*70)
    
    # Test robustezza anomalie
    print("\n🔬 Test Robustezza Anomalie...")
    robustness_results = test_anomaly_robustness()
    
    # Test calibrazione anomalie
    print("\n🔬 Test Calibrazione Anomalie...")
    calibration_results = test_anomaly_calibration()
    
    # Crea grafici
    print("\n📊 Creazione grafici investigazione anomalie...")
    create_anomaly_investigation_plots(robustness_results, calibration_results)
    
    # Compila risultati
    investigation_results = {
        'timestamp': datetime.now().isoformat(),
        'robustness_test': robustness_results,
        'calibration_test': calibration_results,
        'summary': {
            'null_ensemble_significance': robustness_results['null_data']['ensemble']['ensemble_significance'] if robustness_results['null_data']['ensemble'] else 0,
            'qg_ensemble_significance': robustness_results['qg_data']['ensemble']['ensemble_significance'] if robustness_results['qg_data']['ensemble'] else 0,
            'null_bayesian_significance': robustness_results['null_data']['bayesian']['best_significance'] if robustness_results['null_data']['bayesian'] else 0,
            'qg_bayesian_significance': robustness_results['qg_data']['bayesian']['best_significance'] if robustness_results['qg_data']['bayesian'] else 0,
            'null_power_law_significance': robustness_results['null_data']['power_law']['residual_significance'] if robustness_results['null_data']['power_law'] else 0,
            'qg_power_law_significance': robustness_results['qg_data']['power_law']['residual_significance'] if robustness_results['qg_data']['power_law'] else 0,
            'null_quadratic_significance': robustness_results['null_data']['quadratic']['residual_significance'] if robustness_results['null_data']['quadratic'] else 0,
            'qg_quadratic_significance': robustness_results['qg_data']['quadratic']['residual_significance'] if robustness_results['qg_data']['quadratic'] else 0,
            'avg_null_realizations': np.mean(robustness_results['multiple_realizations']['null_significances']),
            'avg_qg_realizations': np.mean(robustness_results['multiple_realizations']['qg_significances'])
        }
    }
    
    # Salva risultati
    with open('anomaly_investigation_test_results.json', 'w') as f:
        json.dump(investigation_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI INVESTIGAZIONE ANOMALIE")
    print("="*70)
    
    print(f"🎯 Ensemble Methods - Null: {investigation_results['summary']['null_ensemble_significance']:.2f}σ, QG: {investigation_results['summary']['qg_ensemble_significance']:.2f}σ")
    print(f"🎯 Bayesian Optimization - Null: {investigation_results['summary']['null_bayesian_significance']:.2f}σ, QG: {investigation_results['summary']['qg_bayesian_significance']:.2f}σ")
    print(f"🎯 Power Law Lag - Null: {investigation_results['summary']['null_power_law_significance']:.2f}σ, QG: {investigation_results['summary']['qg_power_law_significance']:.2f}σ")
    print(f"🎯 Quadratic Lag - Null: {investigation_results['summary']['null_quadratic_significance']:.2f}σ, QG: {investigation_results['summary']['qg_quadratic_significance']:.2f}σ")
    
    print(f"\n🔬 Multiple Realizations:")
    print(f"  Null Data Average: {investigation_results['summary']['avg_null_realizations']:.2f}σ")
    print(f"  QG Data Average: {investigation_results['summary']['avg_qg_realizations']:.2f}σ")
    
    print(f"\n🔬 Calibration Results:")
    for result in calibration_results:
        print(f"  QG Strength {result['qg_strength']}: Ensemble {result['ensemble_significance']:.2f}σ, Bayesian {result['bayesian_significance']:.2f}σ")
    
    print("\n" + "="*70)
    print("✅ Investigazione anomalie completata!")
    print("📊 Risultati salvati: anomaly_investigation_test_results.json")
    print("📈 Grafici salvati: anomaly_investigation_test_results.png")
    print("="*70)

if __name__ == "__main__":
    main()
