#!/usr/bin/env python3
"""
SUITE DI VALIDAZIONE AVANZATA
============================

Test avanzati per validare e ottimizzare la metodologia
di detection QG in GRB data.

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

def generate_optimized_grb_data(n_photons, has_qg=False, qg_strength=0.001, noise_level=0.05):
    """Genera dati GRB ottimizzati per test"""
    
    # Parametri realistici
    redshift = np.random.uniform(0.1, 4.0)
    d_L = (3e5 / 70.0) * redshift * (1 + redshift)  # Mpc
    
    # Genera energie più realistiche
    energies = np.random.lognormal(0.3, 1.0, n_photons)
    energies = np.clip(energies, 0.1, 100.0)
    
    # Genera tempi con struttura più realistica
    times = np.random.exponential(300, n_photons)
    
    # Aggiungi lag intrinseci più deboli
    intrinsic_lag = 0.05 * np.power(energies, -0.2) + 0.02 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # Aggiungi effetti QG se richiesti
    if has_qg:
        # QG effect più forte e realistico
        qg_delay = qg_strength * (energies / 5.0) * (1 + 0.2 * times / 500)
        times += qg_delay
    
    # Rumore ridotto
    times += noise_level * np.random.randn(n_photons)
    
    return energies, times, redshift, d_L

def advanced_lag_modeling(energies, times):
    """Modellazione lag avanzata con multiple tecniche"""
    
    models = {}
    
    # Modello 1: Power Law ottimizzato
    def power_law_opt(E, t0, alpha, beta):
        return t0 + alpha * np.power(E, beta)
    
    try:
        popt, _ = curve_fit(power_law_opt, energies, times, 
                          p0=[np.mean(times), 0.1, -0.3], 
                          bounds=([-np.inf, -10, -1], [np.inf, 10, 1]))
        predicted = power_law_opt(energies, *popt)
        residuals = times - predicted
        
        if len(residuals) > 2:
            corr = np.corrcoef(energies, residuals)[0, 1]
            sig = abs(corr) * np.sqrt(len(residuals) - 2) / np.sqrt(1 - corr**2)
            models['power_law_opt'] = {
                'correlation': corr, 
                'significance': sig,
                'parameters': popt.tolist(),
                'rms': np.sqrt(np.mean(residuals**2))
            }
    except:
        models['power_law_opt'] = None
    
    # Modello 2: Broken Power Law
    def broken_power_law(E, t0, alpha1, alpha2, E_break):
        return t0 + np.where(E < E_break, 
                           alpha1 * np.power(E, -0.3), 
                           alpha2 * np.power(E, -0.5))
    
    try:
        E_break_init = np.median(energies)
        popt, _ = curve_fit(broken_power_law, energies, times, 
                          p0=[np.mean(times), 0.1, 0.05, E_break_init], 
                          bounds=([-np.inf, -10, -10, 0.1], [np.inf, 10, 10, 100]))
        predicted = broken_power_law(energies, *popt)
        residuals = times - predicted
        
        if len(residuals) > 2:
            corr = np.corrcoef(energies, residuals)[0, 1]
            sig = abs(corr) * np.sqrt(len(residuals) - 2) / np.sqrt(1 - corr**2)
            models['broken_power_law'] = {
                'correlation': corr, 
                'significance': sig,
                'parameters': popt.tolist(),
                'rms': np.sqrt(np.mean(residuals**2))
            }
    except:
        models['broken_power_law'] = None
    
    # Modello 3: Multi-component
    def multi_component(E, t0, alpha1, alpha2, alpha3):
        power_law = alpha1 * np.power(E, -0.3)
        exponential = alpha2 * np.exp(-E / 10.0)
        logarithmic = alpha3 * np.log(E)
        return t0 + power_law + exponential + logarithmic
    
    try:
        popt, _ = curve_fit(multi_component, energies, times, 
                          p0=[np.mean(times), 0.05, 0.02, 0.01], 
                          bounds=([-np.inf, -5, -5, -5], [np.inf, 5, 5, 5]))
        predicted = multi_component(energies, *popt)
        residuals = times - predicted
        
        if len(residuals) > 2:
            corr = np.corrcoef(energies, residuals)[0, 1]
            sig = abs(corr) * np.sqrt(len(residuals) - 2) / np.sqrt(1 - corr**2)
            models['multi_component'] = {
                'correlation': corr, 
                'significance': sig,
                'parameters': popt.tolist(),
                'rms': np.sqrt(np.mean(residuals**2))
            }
    except:
        models['multi_component'] = None
    
    return models

def sensitivity_analysis():
    """Analisi di sensibilità con soglie multiple"""
    
    print("🔍 Sensitivity Analysis...")
    
    # Test con soglie multiple
    thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
    results = {}
    
    for threshold in thresholds:
        print(f"  Testing threshold: {threshold}σ")
        
        # Genera dataset con QG
        n_grbs = 50
        detections = 0
        
        for i in range(n_grbs):
            energies, times, _, _ = generate_optimized_grb_data(
                n_photons=2000, has_qg=True, qg_strength=0.002)
            
            # Analisi con modelli avanzati
            models = advanced_lag_modeling(energies, times)
            
            # Trova miglior modello
            best_sig = 0
            for model_name, model_result in models.items():
                if model_result is not None:
                    if model_result['significance'] > best_sig:
                        best_sig = model_result['significance']
            
            # Detection se sopra soglia
            if best_sig >= threshold:
                detections += 1
        
        detection_rate = detections / n_grbs
        results[threshold] = {
            'threshold': threshold,
            'detection_rate': detection_rate,
            'detections': detections,
            'total_grbs': n_grbs
        }
        
        print(f"    Detection rate: {detection_rate:.2f}")
    
    return results

def false_positive_analysis():
    """Analisi false positive con soglie multiple"""
    
    print("🎲 False Positive Analysis...")
    
    # Test con soglie multiple
    thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
    results = {}
    
    for threshold in thresholds:
        print(f"  Testing threshold: {threshold}σ")
        
        # Genera dataset SENZA QG
        n_grbs = 100
        false_positives = 0
        
        for i in range(n_grbs):
            energies, times, _, _ = generate_optimized_grb_data(
                n_photons=2000, has_qg=False)
            
            # Analisi con modelli avanzati
            models = advanced_lag_modeling(energies, times)
            
            # Trova miglior modello
            best_sig = 0
            for model_name, model_result in models.items():
                if model_result is not None:
                    if model_result['significance'] > best_sig:
                        best_sig = model_result['significance']
            
            # False positive se sopra soglia
            if best_sig >= threshold:
                false_positives += 1
        
        false_positive_rate = false_positives / n_grbs
        results[threshold] = {
            'threshold': threshold,
            'false_positive_rate': false_positive_rate,
            'false_positives': false_positives,
            'total_grbs': n_grbs
        }
        
        print(f"    False positive rate: {false_positive_rate:.2f}")
    
    return results

def optimal_threshold_analysis():
    """Trova soglia ottimale bilanciando sensitivity e specificity"""
    
    print("🎯 Optimal Threshold Analysis...")
    
    # Test con soglie multiple
    thresholds = np.arange(1.0, 3.5, 0.1)
    results = []
    
    for threshold in thresholds:
        # Test sensitivity
        n_grbs_qg = 50
        detections = 0
        for i in range(n_grbs_qg):
            energies, times, _, _ = generate_optimized_grb_data(
                n_photons=2000, has_qg=True, qg_strength=0.002)
            
            models = advanced_lag_modeling(energies, times)
            best_sig = max([m['significance'] for m in models.values() if m is not None] + [0])
            
            if best_sig >= threshold:
                detections += 1
        
        sensitivity = detections / n_grbs_qg
        
        # Test specificity
        n_grbs_no_qg = 100
        false_positives = 0
        for i in range(n_grbs_no_qg):
            energies, times, _, _ = generate_optimized_grb_data(
                n_photons=2000, has_qg=False)
            
            models = advanced_lag_modeling(energies, times)
            best_sig = max([m['significance'] for m in models.values() if m is not None] + [0])
            
            if best_sig >= threshold:
                false_positives += 1
        
        specificity = 1 - (false_positives / n_grbs_no_qg)
        
        # Calcola F1-score
        precision = sensitivity if sensitivity > 0 else 0
        recall = sensitivity
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            'threshold': threshold,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'f1_score': f1_score,
            'precision': precision,
            'recall': recall
        })
    
    # Trova soglia ottimale
    best_result = max(results, key=lambda x: x['f1_score'])
    
    return results, best_result

def create_advanced_plots(sensitivity_results, false_positive_results, optimal_results, best_threshold):
    """Crea grafici avanzati"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Advanced Validation Suite Results', fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Sensitivity vs Threshold
    thresholds = [r['threshold'] for r in sensitivity_results.values()]
    detection_rates = [r['detection_rate'] for r in sensitivity_results.values()]
    
    ax1.plot(thresholds, detection_rates, 'o-', color='#3498db', linewidth=2, markersize=8)
    ax1.set_xlabel('Threshold (σ)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Detection Rate', fontsize=14, fontweight='bold')
    ax1.set_title('Sensitivity Analysis', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    
    # Plot 2: False Positive Rate vs Threshold
    thresholds_fp = [r['threshold'] for r in false_positive_results.values()]
    fp_rates = [r['false_positive_rate'] for r in false_positive_results.values()]
    
    ax2.plot(thresholds_fp, fp_rates, 'o-', color='#e74c3c', linewidth=2, markersize=8)
    ax2.set_xlabel('Threshold (σ)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('False Positive Rate', fontsize=14, fontweight='bold')
    ax2.set_title('False Positive Analysis', fontsize=16, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)
    
    # Plot 3: ROC Curve
    thresholds_roc = [r['threshold'] for r in optimal_results]
    sensitivities = [r['sensitivity'] for r in optimal_results]
    specificities = [r['specificity'] for r in optimal_results]
    
    ax3.plot(1 - np.array(specificities), sensitivities, 'o-', color='#9b59b6', linewidth=2, markersize=8)
    ax3.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    ax3.set_xlabel('False Positive Rate', fontsize=14, fontweight='bold')
    ax3.set_ylabel('True Positive Rate (Sensitivity)', fontsize=14, fontweight='bold')
    ax3.set_title('ROC Curve', fontsize=16, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    
    # Plot 4: F1-Score vs Threshold
    f1_scores = [r['f1_score'] for r in optimal_results]
    
    ax4.plot(thresholds_roc, f1_scores, 'o-', color='#27ae60', linewidth=2, markersize=8)
    ax4.axvline(best_threshold['threshold'], color='#e74c3c', linewidth=2, 
                linestyle='--', label=f'Optimal: {best_threshold["threshold"]:.1f}σ')
    ax4.set_xlabel('Threshold (σ)', fontsize=14, fontweight='bold')
    ax4.set_ylabel('F1-Score', fontsize=14, fontweight='bold')
    ax4.set_title('F1-Score vs Threshold', fontsize=16, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    ax4.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig('advanced_validation_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici avanzati creati: advanced_validation_results.png")

def main():
    """Funzione principale per suite avanzata"""
    
    print("="*70)
    print("SUITE DI VALIDAZIONE AVANZATA")
    print("Ottimizzazione metodologia QG detection")
    print("="*70)
    
    # Analisi di sensibilità
    print("\n🔍 Analisi di Sensibilità...")
    sensitivity_results = sensitivity_analysis()
    
    # Analisi false positive
    print("\n🎲 Analisi False Positive...")
    false_positive_results = false_positive_analysis()
    
    # Analisi soglia ottimale
    print("\n🎯 Analisi Soglia Ottimale...")
    optimal_results, best_threshold = optimal_threshold_analysis()
    
    # Crea grafici
    print("\n📊 Creazione grafici avanzati...")
    create_advanced_plots(sensitivity_results, false_positive_results, optimal_results, best_threshold)
    
    # Compila risultati
    advanced_results = {
        'timestamp': datetime.now().isoformat(),
        'sensitivity_analysis': sensitivity_results,
        'false_positive_analysis': false_positive_results,
        'optimal_threshold_analysis': optimal_results,
        'best_threshold': best_threshold,
        'recommendations': {
            'optimal_threshold': best_threshold['threshold'],
            'expected_sensitivity': best_threshold['sensitivity'],
            'expected_specificity': best_threshold['specificity'],
            'expected_f1_score': best_threshold['f1_score']
        }
    }
    
    # Salva risultati
    with open('advanced_validation_results.json', 'w') as f:
        json.dump(advanced_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI SUITE AVANZATA")
    print("="*70)
    
    print(f"🎯 Soglia Ottimale: {best_threshold['threshold']:.1f}σ")
    print(f"📊 Sensitivity: {best_threshold['sensitivity']:.2f}")
    print(f"📊 Specificity: {best_threshold['specificity']:.2f}")
    print(f"📊 F1-Score: {best_threshold['f1_score']:.2f}")
    
    print(f"\n🔍 Analisi Sensibilità:")
    for threshold, result in sensitivity_results.items():
        print(f"  {threshold}σ: {result['detection_rate']:.2f} detection rate")
    
    print(f"\n🎲 Analisi False Positive:")
    for threshold, result in false_positive_results.items():
        print(f"  {threshold}σ: {result['false_positive_rate']:.2f} false positive rate")
    
    print(f"\n🎯 RACCOMANDAZIONI:")
    print(f"  ✅ Soglia ottimale: {best_threshold['threshold']:.1f}σ")
    print(f"  ✅ Sensitivity attesa: {best_threshold['sensitivity']:.2f}")
    print(f"  ✅ Specificity attesa: {best_threshold['specificity']:.2f}")
    print(f"  ✅ F1-Score atteso: {best_threshold['f1_score']:.2f}")
    
    print("\n" + "="*70)
    print("✅ Suite avanzata completata!")
    print("📊 Risultati salvati: advanced_validation_results.json")
    print("📈 Grafici salvati: advanced_validation_results.png")
    print("="*70)

if __name__ == "__main__":
    main()
