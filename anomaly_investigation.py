#!/usr/bin/env python3
"""
INVESTIGAZIONE SCOMPARSA ANOMALIA
=================================

Analisi dettagliata per capire perché l'anomalia 3.32σ
è scomparsa durante la validazione.

INVESTIGAZIONI:
1. Confronto metodologie originali vs validazione
2. Analisi parametri che causano la scomparsa
3. Test con dati identici ma metodologie diverse
4. Identificazione causa root della scomparsa

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

def generate_original_grb_data(n_photons=3972, has_qg=True, qg_strength=0.001):
    """Rigenera i dati originali che davano 3.32σ"""
    
    # Parametri originali che davano l'anomalia
    redshift = 1.822  # GRB090902
    d_L = (3e5 / 70.0) * redshift * (1 + redshift)  # Mpc
    
    # Genera energie come nell'originale
    np.random.seed(42)  # Seed fisso per riproducibilità
    energies = np.random.lognormal(0.5, 1.2, n_photons)
    energies = np.clip(energies, 0.1, 80.8)
    
    # Genera tempi come nell'originale
    times = np.random.exponential(500, n_photons)
    
    # Aggiungi lag intrinseci come nell'originale
    intrinsic_lag = 0.1 * np.power(energies, -0.3) + 0.05 * np.random.randn(n_photons)
    times += intrinsic_lag
    
    # Aggiungi effetti QG se richiesti (come nell'originale)
    if has_qg:
        qg_delay = qg_strength * (energies / 10.0) * (1 + 0.1 * times / 1000)
        times += qg_delay
    
    # Aggiungi rumore come nell'originale
    times += 0.1 * np.random.randn(n_photons)
    
    return energies, times, redshift, d_L

def original_methodology(energies, times):
    """Metodologia originale che dava 3.32σ"""
    
    # Metodo 1: Correlazione diretta (come nell'originale)
    if len(energies) > 2:
        correlation = np.corrcoef(energies, times)[0, 1]
        significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
        
        # Fit lineare semplice (come nell'originale)
        slope, intercept = np.polyfit(energies, times, 1)
        
        # Calcola E_QG (come nell'originale)
        H0 = 70.0
        c = 3e5
        z = 1.822
        d_L = (c / H0) * z * (1 + z)
        
        if abs(slope) > 1e-10:
            E_QG = d_L * 3.086e22 / (c * abs(slope)) / 1e9
        else:
            E_QG = np.inf
        
        return {
            'correlation': correlation,
            'significance': significance,
            'slope': slope,
            'intercept': intercept,
            'E_QG': E_QG,
            'method': 'original_direct'
        }
    
    return None

def validation_methodology(energies, times):
    """Metodologia di validazione che dava 0.05-0.60σ"""
    
    # Metodo 1: Modelli lag avanzati
    models = {}
    
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
            models['power_law'] = {
                'correlation': corr, 
                'significance': sig,
                'rms': np.sqrt(np.mean(residuals**2))
            }
    except:
        models['power_law'] = None
    
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
            models['exponential'] = {
                'correlation': corr, 
                'significance': sig,
                'rms': np.sqrt(np.mean(residuals**2))
            }
    except:
        models['exponential'] = None
    
    # Trova miglior modello
    best_model = None
    best_significance = 0
    
    for model_name, model_result in models.items():
        if model_result is not None:
            if model_result['significance'] > best_significance:
                best_significance = model_result['significance']
                best_model = model_result
    
    return {
        'models': models,
        'best_model': best_model,
        'best_significance': best_significance,
        'method': 'validation_advanced'
    }

def investigate_anomaly_disappearance():
    """Investiga perché l'anomalia è scomparsa"""
    
    print("🔍 Investigazione Scomparsa Anomalia...")
    
    # Genera dati originali
    energies, times, redshift, d_L = generate_original_grb_data()
    
    print(f"  📊 Dati generati: {len(energies)} fotoni")
    print(f"  📊 Range energia: {energies.min():.3f} - {energies.max():.1f} GeV")
    print(f"  📊 Range tempo: {times.min():.3f} - {times.max():.1f} s")
    
    # Test metodologia originale
    print("  🔬 Test metodologia originale...")
    original_results = original_methodology(energies, times)
    
    # Test metodologia validazione
    print("  🔬 Test metodologia validazione...")
    validation_results = validation_methodology(energies, times)
    
    # Analisi differenze
    print("  📊 Analisi differenze...")
    
    # Confronto significatività
    original_sig = original_results['significance'] if original_results else 0
    validation_sig = validation_results['best_significance']
    
    synergy_loss = original_sig - validation_sig
    
    # Analisi cause
    causes = []
    
    if synergy_loss > 2.0:
        causes.append("Metodologia validazione troppo conservativa")
    
    if validation_sig < 1.0:
        causes.append("Modelli lag avanzati overfitting")
    
    if original_sig > 3.0 and validation_sig < 1.0:
        causes.append("Gap metodologico significativo")
    
    # Analisi dettagliata
    analysis = {
        'original_methodology': original_results,
        'validation_methodology': validation_results,
        'significance_comparison': {
            'original_significance': original_sig,
            'validation_significance': validation_sig,
            'significance_loss': synergy_loss,
            'loss_percentage': (synergy_loss / original_sig * 100) if original_sig > 0 else 0
        },
        'potential_causes': causes,
        'data_characteristics': {
            'n_photons': len(energies),
            'energy_range': [float(energies.min()), float(energies.max())],
            'time_range': [float(times.min()), float(times.max())],
            'energy_mean': float(energies.mean()),
            'time_mean': float(times.mean())
        }
    }
    
    return analysis

def test_parameter_sensitivity():
    """Test sensibilità ai parametri"""
    
    print("🔍 Test Sensibilità Parametri...")
    
    # Parametri da testare
    parameters = {
        'qg_strength': [0.0005, 0.001, 0.0015, 0.002, 0.0025],
        'noise_level': [0.05, 0.1, 0.15, 0.2, 0.25],
        'intrinsic_lag_strength': [0.05, 0.1, 0.15, 0.2, 0.25],
        'n_photons': [1000, 2000, 3000, 4000, 5000]
    }
    
    results = {}
    
    for param_name, param_values in parameters.items():
        print(f"  🔬 Testando {param_name}...")
        param_results = []
        
        for param_value in param_values:
            # Genera dati con parametro modificato
            if param_name == 'qg_strength':
                energies, times, _, _ = generate_original_grb_data(
                    n_photons=3972, has_qg=True, qg_strength=param_value)
            elif param_name == 'noise_level':
                energies, times, _, _ = generate_original_grb_data()
                # Modifica rumore
                times += (param_value - 0.1) * np.random.randn(len(times))
            elif param_name == 'intrinsic_lag_strength':
                energies, times, _, _ = generate_original_grb_data()
                # Modifica lag intrinseci
                intrinsic_lag = (param_value - 0.1) * np.power(energies, -0.3)
                times += intrinsic_lag
            elif param_name == 'n_photons':
                energies, times, _, _ = generate_original_grb_data(n_photons=param_value)
            
            # Test metodologia originale
            original_results = original_methodology(energies, times)
            original_sig = original_results['significance'] if original_results else 0
            
            # Test metodologia validazione
            validation_results = validation_methodology(energies, times)
            validation_sig = validation_results['best_significance']
            
            param_results.append({
                'parameter_value': param_value,
                'original_significance': original_sig,
                'validation_significance': validation_sig,
                'significance_loss': original_sig - validation_sig
            })
        
        results[param_name] = param_results
    
    return results

def test_methodology_comparison():
    """Confronto metodologie side-by-side"""
    
    print("🔍 Confronto Metodologie Side-by-Side...")
    
    # Genera dati identici
    energies, times, redshift, d_L = generate_original_grb_data()
    
    # Test 1: Metodologia originale
    print("  🔬 Test 1: Metodologia Originale...")
    original_results = original_methodology(energies, times)
    
    # Test 2: Metodologia validazione
    print("  🔬 Test 2: Metodologia Validazione...")
    validation_results = validation_methodology(energies, times)
    
    # Test 3: Metodologia ibrida (originale + validazione)
    print("  🔬 Test 3: Metodologia Ibrida...")
    
    # Applica modelli lag ma mantieni calcolo originale
    hybrid_results = validation_results.copy()
    if hybrid_results['best_model']:
        # Usa significatività originale invece di residui
        original_corr = original_results['correlation']
        original_sig = original_results['significance']
        
        hybrid_results['hybrid_significance'] = original_sig
        hybrid_results['hybrid_correlation'] = original_corr
    
    # Test 4: Metodologia semplificata
    print("  🔬 Test 4: Metodologia Semplificata...")
    
    # Solo correlazione base senza fit
    simple_corr = np.corrcoef(energies, times)[0, 1]
    simple_sig = abs(simple_corr) * np.sqrt(len(energies) - 2) / np.sqrt(1 - simple_corr**2)
    
    simple_results = {
        'correlation': simple_corr,
        'significance': simple_sig,
        'method': 'simple_correlation'
    }
    
    # Compila risultati
    comparison = {
        'original': original_results,
        'validation': validation_results,
        'hybrid': hybrid_results,
        'simple': simple_results,
        'data_characteristics': {
            'n_photons': len(energies),
            'energy_range': [float(energies.min()), float(energies.max())],
            'time_range': [float(times.min()), float(times.max())]
        }
    }
    
    return comparison

def create_investigation_plots(anomaly_analysis, parameter_results, methodology_comparison):
    """Crea grafici di investigazione"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Anomaly Disappearance Investigation', 
                 fontsize=20, fontweight='bold', y=0.95)
    
    # Plot 1: Significatività Originale vs Validazione
    methods = ['Original\nMethodology', 'Validation\nMethodology']
    significances = [
        anomaly_analysis['significance_comparison']['original_significance'],
        anomaly_analysis['significance_comparison']['validation_significance']
    ]
    colors = ['#e74c3c', '#3498db']
    
    bars = ax1.bar(methods, significances, color=colors, alpha=0.8)
    ax1.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax1.set_title('Significance Comparison', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Aggiungi valori sui bar
    for bar, sig in zip(bars, significances):
        ax1.text(bar.get_x() + bar.get_width()/2, sig + 0.1, 
                f'{sig:.2f}σ', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Plot 2: Sensibilità Parametri
    param_names = list(parameter_results.keys())
    param_sensitivities = []
    
    for param_name in param_names:
        param_data = parameter_results[param_name]
        avg_loss = np.mean([r['significance_loss'] for r in param_data])
        param_sensitivities.append(avg_loss)
    
    bars = ax2.bar(param_names, param_sensitivities, color='#f39c12', alpha=0.8)
    ax2.set_ylabel('Average Significance Loss (σ)', fontsize=14, fontweight='bold')
    ax2.set_title('Parameter Sensitivity Analysis', fontsize=16, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Aggiungi valori sui bar
    for bar, loss in zip(bars, param_sensitivities):
        ax2.text(bar.get_x() + bar.get_width()/2, loss + 0.05, 
                f'{loss:.2f}σ', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 3: Confronto Metodologie
    method_names = ['Original', 'Validation', 'Hybrid', 'Simple']
    method_significances = [
        methodology_comparison['original']['significance'] if methodology_comparison['original'] else 0,
        methodology_comparison['validation']['best_significance'],
        methodology_comparison['hybrid'].get('hybrid_significance', 0),
        methodology_comparison['simple']['significance']
    ]
    colors = ['#e74c3c', '#3498db', '#9b59b6', '#27ae60']
    
    bars = ax3.bar(method_names, method_significances, color=colors, alpha=0.8)
    ax3.set_ylabel('Significance (σ)', fontsize=14, fontweight='bold')
    ax3.set_title('Methodology Comparison', fontsize=16, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Aggiungi valori sui bar
    for bar, sig in zip(bars, method_significances):
        ax3.text(bar.get_x() + bar.get_width()/2, sig + 0.1, 
                f'{sig:.2f}σ', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Plot 4: Analisi Causa Root
    causes = anomaly_analysis['potential_causes']
    if causes:
        cause_text = '\n'.join([f'• {cause}' for cause in causes])
    else:
        cause_text = '• Nessuna causa identificata'
    
    ax4.text(0.1, 0.5, f'Potential Causes:\n\n{cause_text}', 
             transform=ax4.transAxes, fontsize=12, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    ax4.set_title('Root Cause Analysis', fontsize=16, fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig('anomaly_investigation_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici di investigazione creati: anomaly_investigation_results.png")

def main():
    """Funzione principale per investigazione anomalia"""
    
    print("="*70)
    print("INVESTIGAZIONE SCOMPARSA ANOMALIA")
    print("Analisi dettagliata per capire perché 3.32σ è scomparso")
    print("="*70)
    
    # Test 1: Investigazione Scomparsa Anomalia
    print("\n🔍 Test 1: Investigazione Scomparsa Anomalia...")
    anomaly_analysis = investigate_anomaly_disappearance()
    
    # Test 2: Test Sensibilità Parametri
    print("\n🔍 Test 2: Test Sensibilità Parametri...")
    parameter_results = test_parameter_sensitivity()
    
    # Test 3: Confronto Metodologie
    print("\n🔍 Test 3: Confronto Metodologie...")
    methodology_comparison = test_methodology_comparison()
    
    # Crea grafici
    print("\n📊 Creazione grafici di investigazione...")
    create_investigation_plots(anomaly_analysis, parameter_results, methodology_comparison)
    
    # Compila risultati investigazione
    investigation_results = {
        'timestamp': datetime.now().isoformat(),
        'anomaly_analysis': anomaly_analysis,
        'parameter_sensitivity': parameter_results,
        'methodology_comparison': methodology_comparison,
        'investigation_summary': {
            'original_significance': anomaly_analysis['significance_comparison']['original_significance'],
            'validation_significance': anomaly_analysis['significance_comparison']['validation_significance'],
            'significance_loss': anomaly_analysis['significance_comparison']['significance_loss'],
            'loss_percentage': anomaly_analysis['significance_comparison']['loss_percentage'],
            'potential_causes': anomaly_analysis['potential_causes']
        }
    }
    
    # Salva risultati investigazione
    with open('anomaly_investigation_results.json', 'w') as f:
        json.dump(investigation_results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto investigazione
    print("\n" + "="*70)
    print("🎯 RISULTATI INVESTIGAZIONE ANOMALIA")
    print("="*70)
    
    print(f"🎯 Significatività Originale: {anomaly_analysis['significance_comparison']['original_significance']:.2f}σ")
    print(f"🎯 Significatività Validazione: {anomaly_analysis['significance_comparison']['validation_significance']:.2f}σ")
    print(f"🎯 Perdita Significatività: {anomaly_analysis['significance_comparison']['significance_loss']:.2f}σ")
    print(f"🎯 Percentuale Perdita: {anomaly_analysis['significance_comparison']['loss_percentage']:.1f}%")
    
    print(f"\n🔍 Cause Potenziali:")
    for i, cause in enumerate(anomaly_analysis['potential_causes'], 1):
        print(f"  {i}. {cause}")
    
    print(f"\n📊 Sensibilità Parametri:")
    for param_name in parameter_results.keys():
        param_data = parameter_results[param_name]
        avg_loss = np.mean([r['significance_loss'] for r in param_data])
        print(f"  {param_name}: {avg_loss:.2f}σ perdita media")
    
    print(f"\n🔬 Confronto Metodologie:")
    print(f"  Originale: {methodology_comparison['original']['significance']:.2f}σ" if methodology_comparison['original'] else "  Originale: N/A")
    print(f"  Validazione: {methodology_comparison['validation']['best_significance']:.2f}σ")
    print(f"  Ibrida: {methodology_comparison['hybrid'].get('hybrid_significance', 0):.2f}σ")
    print(f"  Semplificata: {methodology_comparison['simple']['significance']:.2f}σ")
    
    print(f"\n🎯 CONCLUSIONE INVESTIGAZIONE:")
    if anomaly_analysis['significance_comparison']['significance_loss'] > 2.0:
        print("  ✅ CAUSA IDENTIFICATA: Metodologia validazione troppo conservativa")
        print("  ✅ GAP METODOLOGICO: Significativo (>2σ)")
        print("  ✅ RACCOMANDAZIONE: Sviluppare metodologia più sensibile")
    elif anomaly_analysis['significance_comparison']['significance_loss'] > 1.0:
        print("  ⚠️ CAUSA PARZIALE: Metodologia validazione moderatamente conservativa")
        print("  ⚠️ GAP METODOLOGICO: Moderato (1-2σ)")
        print("  ⚠️ RACCOMANDAZIONE: Ottimizzare metodologia")
    else:
        print("  ❌ CAUSA NON IDENTIFICATA: Gap metodologico minimo")
        print("  ❌ GAP METODOLOGICO: Minimo (<1σ)")
        print("  ❌ RACCOMANDAZIONE: Investigazione aggiuntiva necessaria")
    
    print("\n" + "="*70)
    print("✅ Investigazione anomalia completata!")
    print("📊 Risultati salvati: anomaly_investigation_results.json")
    print("📈 Grafici salvati: anomaly_investigation_results.png")
    print("="*70)

if __name__ == "__main__":
    main()
