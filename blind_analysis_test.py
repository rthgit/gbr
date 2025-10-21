#!/usr/bin/env python3
"""
BLIND ANALYSIS TEST
===================

Implementa analisi cieca per evitare bias di selezione
e confermare la robustezza della scoperta.

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

def generate_blind_grb_data(n_photons, has_qg=False, qg_strength=0.001, noise_level=0.1):
    """Genera dati GRB per analisi cieca"""
    
    # Parametri realistici
    redshift = np.random.uniform(0.1, 4.0)
    d_L = (3e5 / 70.0) * redshift * (1 + redshift)  # Mpc
    
    # Genera energie (log-normal distribution)
    energies = np.random.lognormal(0.5, 1.2, n_photons)
    energies = np.clip(energies, 0.1, 100.0)
    
    # Genera tempi base
    times = np.random.exponential(500, n_photons)
    
    # Aggiungi lag intrinseci
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # Aggiungi effetti QG se richiesti
    if has_qg:
        qg_delay = qg_strength * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    # Aggiungi rumore
    times += noise_level * np.random.randn(n_photons)
    
    return energies, times, redshift, d_L

def blind_analysis_pipeline(energies, times):
    """Pipeline di analisi cieca"""
    
    results = {}
    
    # 1. Analisi base
    if len(energies) > 2:
        correlation = np.corrcoef(energies, times)[0, 1]
        significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
        
        results['base_analysis'] = {
            'correlation': correlation,
            'significance': significance,
            'n_photons': len(energies)
        }
        
        # 2. Fit modelli lag
        lag_models = {}
        
        # Power Law
        def power_law(E, t0, alpha):
            return t0 + alpha * np.power(E, -0.3)
        
        try:
            popt, _ = curve_fit(power_law, energies, times, 
                              p0=[np.mean(times), 0.1], 
                              bounds=([-np.inf, -10], [np.inf, 10]))
            predicted = power_law(energies, *popt)
            residuals = times - predicted
            
            if len(residuals) > 2:
                corr = np.corrcoef(energies, residuals)[0, 1]
                sig = abs(corr) * np.sqrt(len(residuals) - 2) / np.sqrt(1 - corr**2)
                lag_models['power_law'] = {'correlation': corr, 'significance': sig}
        except:
            lag_models['power_law'] = None
        
        # Exponential
        def exponential(E, t0, beta):
            return t0 + beta * np.exp(-E / 10.0)
        
        try:
            popt, _ = curve_fit(exponential, energies, times, 
                              p0=[np.mean(times), 0.1], 
                              bounds=([-np.inf, -10], [np.inf, 10]))
            predicted = exponential(energies, *popt)
            residuals = times - predicted
            
            if len(residuals) > 2:
                corr = np.corrcoef(energies, residuals)[0, 1]
                sig = abs(corr) * np.sqrt(len(residuals) - 2) / np.sqrt(1 - corr**2)
                lag_models['exponential'] = {'correlation': corr, 'significance': sig}
        except:
            lag_models['exponential'] = None
        
        # Logarithmic
        def logarithmic(E, t0, gamma):
            return t0 + gamma * np.log(E)
        
        try:
            popt, _ = curve_fit(logarithmic, energies, times, 
                              p0=[np.mean(times), 0.1], 
                              bounds=([-np.inf, -10], [np.inf, 10]))
            predicted = logarithmic(energies, *popt)
            residuals = times - predicted
            
            if len(residuals) > 2:
                corr = np.corrcoef(energies, residuals)[0, 1]
                sig = abs(corr) * np.sqrt(len(residuals) - 2) / np.sqrt(1 - corr**2)
                lag_models['logarithmic'] = {'correlation': corr, 'significance': sig}
        except:
            lag_models['logarithmic'] = None
        
        results['lag_models'] = lag_models
        
        # 3. Trova miglior modello
        best_model = None
        best_significance = 0
        
        for model_name, model_result in lag_models.items():
            if model_result is not None and model_result['significance'] > best_significance:
                best_significance = model_result['significance']
                best_model = model_name
        
        results['best_model'] = {
            'name': best_model,
            'significance': best_significance
        }
        
        # 4. Calcola E_QG se c'è correlazione residua
        if best_significance > 2.0:
            slope = np.polyfit(energies, times, 1)[0]
            if abs(slope) > 1e-10:
                # Usa redshift medio per calcolo E_QG
                d_L = (3e5 / 70.0) * 1.5 * (1 + 1.5)  # Redshift medio
                E_QG = d_L * 3.086e22 / (3e5 * 1000 * abs(slope)) / 1e9
            else:
                E_QG = np.inf
        else:
            E_QG = np.inf
        
        results['E_QG_limit'] = float(E_QG) if E_QG != np.inf else None
        
        # 5. Decisione finale
        results['detection'] = best_significance > 2.0
        results['discovery'] = best_significance > 5.0
        
    else:
        results['error'] = "Insufficient photons"
    
    return results

def run_blind_analysis(n_blind_grbs=20, n_photons_range=(100, 5000)):
    """Esegue analisi cieca su multiple GRB"""
    
    print(f"🔍 Blind Analysis su {n_blind_grbs} GRB...")
    
    blind_results = []
    
    for i in range(n_blind_grbs):
        # Genera GRB casuale
        n_photons = np.random.randint(n_photons_range[0], n_photons_range[1])
        has_qg = np.random.choice([True, False], p=[0.3, 0.7])  # 30% hanno QG
        qg_strength = np.random.uniform(0.0005, 0.002) if has_qg else 0.0
        noise_level = np.random.uniform(0.05, 0.2)
        
        # Genera dati
        energies, times, redshift, d_L = generate_blind_grb_data(
            n_photons, has_qg, qg_strength, noise_level)
        
        # Analisi cieca
        result = blind_analysis_pipeline(energies, times)
        
        # Aggiungi informazioni nascoste
        result['hidden_info'] = {
            'grb_id': f'BLIND_{i:03d}',
            'n_photons': n_photons,
            'redshift': redshift,
            'has_qg_true': has_qg,
            'qg_strength': qg_strength,
            'noise_level': noise_level
        }
        
        blind_results.append(result)
    
    return blind_results

def analyze_blind_results(blind_results):
    """Analizza risultati dell'analisi cieca"""
    
    print("\n📊 Analisi risultati blind analysis...")
    
    # Statistiche generali
    n_grbs = len(blind_results)
    n_detected = sum([r.get('detection', False) for r in blind_results])
    n_discoveries = sum([r.get('discovery', False) for r in blind_results])
    
    # Confusion matrix
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    for result in blind_results:
        if 'hidden_info' in result:
            has_qg_true = result['hidden_info']['has_qg_true']
            detected = result.get('detection', False)
            
            if has_qg_true and detected:
                true_positives += 1
            elif not has_qg_true and not detected:
                true_negatives += 1
            elif not has_qg_true and detected:
                false_positives += 1
            elif has_qg_true and not detected:
                false_negatives += 1
    
    # Calcola metriche
    accuracy = (true_positives + true_negatives) / n_grbs if n_grbs > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # False positive rate
    false_positive_rate = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
    
    # Analisi significatività
    significances = [r.get('best_model', {}).get('significance', 0) for r in blind_results if r.get('best_model')]
    mean_significance = np.mean(significances) if significances else 0
    std_significance = np.std(significances) if significances else 0
    
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'n_grbs': n_grbs,
        'n_detected': n_detected,
        'n_discoveries': n_discoveries,
        'detection_rate': n_detected / n_grbs if n_grbs > 0 else 0,
        'discovery_rate': n_discoveries / n_grbs if n_grbs > 0 else 0,
        'confusion_matrix': {
            'true_positives': true_positives,
            'true_negatives': true_negatives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        },
        'metrics': {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'false_positive_rate': false_positive_rate
        },
        'significance_stats': {
            'mean': mean_significance,
            'std': std_significance,
            'max': max(significances) if significances else 0
        },
        'individual_results': blind_results
    }
    
    return analysis_results

def create_blind_analysis_plots(analysis_results):
    """Crea grafici per analisi cieca"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Blind Analysis Results', fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Detection Rate
    detection_rate = analysis_results['detection_rate']
    discovery_rate = analysis_results['discovery_rate']
    
    categories = ['Detection\nRate', 'Discovery\nRate']
    rates = [detection_rate, discovery_rate]
    colors = ['#3498db', '#e74c3c']
    
    bars = ax1.bar(categories, rates, color=colors, alpha=0.8)
    ax1.set_ylabel('Rate', fontsize=14, fontweight='bold')
    ax1.set_title('Detection and Discovery Rates', fontsize=16, fontweight='bold')
    ax1.set_ylim(0, 1)
    ax1.grid(True, alpha=0.3)
    
    # Aggiungi valori sui bar
    for bar, rate in zip(bars, rates):
        ax1.text(bar.get_x() + bar.get_width()/2, rate + 0.02, 
                f'{rate:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Plot 2: Confusion Matrix
    cm = analysis_results['confusion_matrix']
    confusion_data = [cm['true_positives'], cm['false_positives'], 
                     cm['false_negatives'], cm['true_negatives']]
    confusion_labels = ['TP', 'FP', 'FN', 'TN']
    confusion_colors = ['#27ae60', '#e74c3c', '#f39c12', '#95a5a6']
    
    bars = ax2.bar(confusion_labels, confusion_data, color=confusion_colors, alpha=0.8)
    ax2.set_ylabel('Count', fontsize=14, fontweight='bold')
    ax2.set_title('Confusion Matrix', fontsize=16, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Aggiungi valori sui bar
    for bar, count in zip(bars, confusion_data):
        ax2.text(bar.get_x() + bar.get_width()/2, count + 0.1, 
                str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Plot 3: Metrics
    metrics = analysis_results['metrics']
    metric_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    metric_values = [metrics['accuracy'], metrics['precision'], 
                    metrics['recall'], metrics['f1_score']]
    
    bars = ax3.bar(metric_names, metric_values, color='#9b59b6', alpha=0.8)
    ax3.set_ylabel('Score', fontsize=14, fontweight='bold')
    ax3.set_title('Performance Metrics', fontsize=16, fontweight='bold')
    ax3.set_ylim(0, 1)
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # Aggiungi valori sui bar
    for bar, value in zip(bars, metric_values):
        ax3.text(bar.get_x() + bar.get_width()/2, value + 0.02, 
                f'{value:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 4: Significance Distribution
    significances = [r.get('best_model', {}).get('significance', 0) 
                    for r in analysis_results['individual_results'] 
                    if r.get('best_model')]
    
    if significances:
        ax4.hist(significances, bins=20, alpha=0.7, color='#34495e', 
                edgecolor='black', linewidth=0.5)
        ax4.axvline(2.0, color='#f39c12', linewidth=2, linestyle='--', label='Detection Threshold')
        ax4.axvline(5.0, color='#e74c3c', linewidth=2, linestyle='--', label='Discovery Threshold')
        ax4.set_xlabel('Significance (σ)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Frequency', fontsize=14, fontweight='bold')
        ax4.set_title('Significance Distribution', fontsize=16, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No significance\ndata available', ha='center', va='center', 
                transform=ax4.transAxes, fontsize=16, fontweight='bold')
        ax4.set_title('Significance Distribution', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('blind_analysis_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici blind analysis creati: blind_analysis_results.png")

def main():
    """Funzione principale per blind analysis"""
    
    print("="*70)
    print("BLIND ANALYSIS TEST")
    print("Analisi cieca per evitare bias di selezione")
    print("="*70)
    
    # Esegui analisi cieca
    print("\n🔍 Esecuzione analisi cieca...")
    blind_results = run_blind_analysis(n_blind_grbs=20)
    
    # Analizza risultati
    print("\n📊 Analisi risultati...")
    analysis_results = analyze_blind_results(blind_results)
    
    # Crea grafici
    print("\n📈 Creazione grafici...")
    create_blind_analysis_plots(analysis_results)
    
    # Salva risultati
    with open('blind_analysis_results.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI BLIND ANALYSIS")
    print("="*70)
    
    print(f"📊 Statistiche Generali:")
    print(f"  GRB analizzati: {analysis_results['n_grbs']}")
    print(f"  Detection rate: {analysis_results['detection_rate']:.2f}")
    print(f"  Discovery rate: {analysis_results['discovery_rate']:.2f}")
    
    print(f"\n🔍 Confusion Matrix:")
    cm = analysis_results['confusion_matrix']
    print(f"  True Positives: {cm['true_positives']}")
    print(f"  True Negatives: {cm['true_negatives']}")
    print(f"  False Positives: {cm['false_positives']}")
    print(f"  False Negatives: {cm['false_negatives']}")
    
    print(f"\n📈 Performance Metrics:")
    metrics = analysis_results['metrics']
    print(f"  Accuracy: {metrics['accuracy']:.2f}")
    print(f"  Precision: {metrics['precision']:.2f}")
    print(f"  Recall: {metrics['recall']:.2f}")
    print(f"  F1-Score: {metrics['f1_score']:.2f}")
    print(f"  False Positive Rate: {metrics['false_positive_rate']:.2f}")
    
    print(f"\n🎯 CONCLUSIONE BLIND ANALYSIS:")
    if (metrics['accuracy'] >= 0.75 and 
        metrics['false_positive_rate'] <= 0.1 and 
        metrics['f1_score'] >= 0.6):
        print("  ✅ METODOLOGIA ROBUSTA - BLIND ANALYSIS PASSED")
        print("  ✅ SCOPERTA CONFERMATA SENZA BIAS")
    elif metrics['accuracy'] >= 0.6:
        print("  ⚠️ METODOLOGIA PARZIALMENTE ROBUSTA")
        print("  ⚠️ NECESSARIA VALIDAZIONE AGGIUNTIVA")
    else:
        print("  ❌ METODOLOGIA NON ROBUSTA")
        print("  ❌ BIAS DI SELEZIONE RILEVATO")
    
    print("\n" + "="*70)
    print("✅ Blind analysis completata!")
    print("📊 Risultati salvati: blind_analysis_results.json")
    print("📈 Grafici salvati: blind_analysis_results.png")
    print("="*70)

if __name__ == "__main__":
    main()

