"""
ULTIMATE VALIDATION RESULTS ANALYZER
Estrae e analizza i risultati chiave dai test
"""

import json
import numpy as np

print("="*70)
print("📊 ANALISI RISULTATI ULTIMATE VALIDATION")
print("="*70)

# Carica risultati
try:
    with open('ultimate_validation_suite.json', 'r') as f:
        results = json.load(f)
    
    print("\n✅ File caricato con successo!")
    
    # =========================================
    # SEZIONE 1: TEST ROBUSTEZZA
    # =========================================
    print("\n" + "="*70)
    print("🔬 TEST 1: ROBUSTEZZA ESTREMI")
    print("="*70)
    
    if 'robustness_tests' in results:
        rob = results['robustness_tests']
        
        print("\n📊 FILTRI ENERGETICI:")
        if 'energy_filters' in rob:
            for test_name, sig in rob['energy_filters'].items():
                status = "✅" if abs(sig) > 3 else "⚠️" if abs(sig) > 2 else "❌"
                print(f"  {status} {test_name}: {sig:.2f}σ")
        
        print("\n📊 FINESTRE TEMPORALI:")
        if 'time_windows' in rob:
            for test_name, sig in rob['time_windows'].items():
                status = "✅" if abs(sig) > 3 else "⚠️" if abs(sig) > 2 else "❌"
                print(f"  {status} {test_name}: {sig:.2f}σ")
        
        print("\n📊 METODI CORRELAZIONE:")
        if 'correlation_methods' in rob:
            for method, sig in rob['correlation_methods'].items():
                status = "✅" if abs(sig) > 3 else "⚠️" if abs(sig) > 2 else "❌"
                print(f"  {status} {method}: {sig:.2f}σ")
    
    # =========================================
    # SEZIONE 2: BIAS SISTEMATICI
    # =========================================
    print("\n" + "="*70)
    print("🔬 TEST 2: BIAS SISTEMATICI")
    print("="*70)
    
    if 'systematic_bias_tests' in results:
        bias = results['systematic_bias_tests']
        
        print("\n📊 DATI RANDOMIZZATI (deve essere ~0σ):")
        if 'randomized_data' in bias:
            sig = bias['randomized_data']
            status = "✅" if abs(sig) < 1 else "⚠️" if abs(sig) < 2 else "🚨"
            print(f"  {status} Significance: {sig:.2f}σ")
            if abs(sig) > 2:
                print("  🚨 PROBLEMA: Segnale su dati random!")
        
        print("\n📊 BOOTSTRAP (deve essere simile a originale):")
        if 'bootstrap' in bias:
            sig_mean = bias['bootstrap'].get('mean', 0)
            sig_std = bias['bootstrap'].get('std', 0)
            print(f"  📊 Mean: {sig_mean:.2f}σ ± {sig_std:.2f}σ")
            
            # Check se originale dentro CI
            original = 5.46
            if abs(sig_mean - original) < 2*sig_std:
                print("  ✅ Originale dentro confidence interval")
            else:
                print("  🚨 Originale FUORI confidence interval!")
        
        print("\n📊 SUBSET CASUALI (deve replicare):")
        if 'random_subsets' in bias:
            sigs = bias['random_subsets']
            if isinstance(sigs, list):
                mean_sig = np.mean(sigs)
                std_sig = np.std(sigs)
                print(f"  📊 Mean: {mean_sig:.2f}σ ± {std_sig:.2f}σ")
                print(f"  📊 Range: [{min(sigs):.2f}, {max(sigs):.2f}]σ")
    
    # =========================================
    # SEZIONE 3: FALSI POSITIVI
    # =========================================
    print("\n" + "="*70)
    print("🔬 TEST 3: FALSI POSITIVI")
    print("="*70)
    
    if 'false_positive_tests' in results:
        fp = results['false_positive_tests']
        
        print("\n📊 DATI COMPLETAMENTE RANDOM:")
        if 'completely_random' in fp:
            fp_rate = fp['completely_random'].get('false_positive_rate', 0)
            n_exceed = fp['completely_random'].get('n_exceeding_threshold', 0)
            n_total = fp['completely_random'].get('n_tests', 100)
            
            print(f"  📊 False positive rate: {fp_rate*100:.2f}%")
            print(f"  📊 Tests exceeding 5σ: {n_exceed}/{n_total}")
            
            if fp_rate < 0.01:
                print("  ✅ Tasso accettabile (<1%)")
            elif fp_rate < 0.05:
                print("  ⚠️ Tasso borderline (1-5%)")
            else:
                print("  🚨 PROBLEMA: Troppi falsi positivi!")
        
        print("\n📊 PERMUTATION TEST:")
        if 'permutation' in fp:
            p_value = fp['permutation'].get('p_value', 1)
            print(f"  📊 P-value: {p_value:.6f}")
            
            if p_value < 0.001:
                print("  ✅ Altamente significativo")
            elif p_value < 0.01:
                print("  ✅ Significativo")
            elif p_value < 0.05:
                print("  ⚠️ Marginalmente significativo")
            else:
                print("  🚨 NON significativo!")
    
    # =========================================
    # SEZIONE 4: CAMPIONI CONTROLLO
    # =========================================
    print("\n" + "="*70)
    print("🔬 TEST 4: CAMPIONI CONTROLLO")
    print("="*70)
    
    if 'control_samples' in results:
        ctrl = results['control_samples']
        
        print("\n📊 BANDE ENERGETICHE:")
        for band in ['low_energy', 'high_energy', 'mid_energy']:
            if band in ctrl:
                sig = ctrl[band]
                status = "✅" if abs(sig) > 3 else "⚠️" if abs(sig) > 2 else "❌"
                print(f"  {status} {band.replace('_', ' ').title()}: {sig:.2f}σ")
        
        print("\n📊 FINESTRE TEMPORALI:")
        for window in ['early_time', 'late_time']:
            if window in ctrl:
                sig = ctrl[window]
                status = "✅" if abs(sig) > 3 else "⚠️" if abs(sig) > 2 else "❌"
                print(f"  {status} {window.replace('_', ' ').title()}: {sig:.2f}σ")
    
    # =========================================
    # VALUTAZIONE FINALE
    # =========================================
    print("\n" + "="*70)
    print("🎯 VALUTAZIONE FINALE")
    print("="*70)
    
    # Conta quanti test passano
    tests_passed = 0
    tests_total = 0
    red_flags = []
    
    # Check randomized data
    if 'systematic_bias_tests' in results and 'randomized_data' in results['systematic_bias_tests']:
        tests_total += 1
        sig = results['systematic_bias_tests']['randomized_data']
        if abs(sig) < 2:
            tests_passed += 1
        else:
            red_flags.append(f"Randomized data: {sig:.2f}σ (dovrebbe essere ~0)")
    
    # Check bootstrap stability
    if 'systematic_bias_tests' in results and 'bootstrap' in results['systematic_bias_tests']:
        tests_total += 1
        boot = results['systematic_bias_tests']['bootstrap']
        if 'std' in boot and boot['std'] < 1.0:
            tests_passed += 1
        else:
            red_flags.append(f"Bootstrap std: {boot.get('std', 0):.2f}σ (alta varianza)")
    
    # Check false positive rate
    if 'false_positive_tests' in results and 'completely_random' in results['false_positive_tests']:
        tests_total += 1
        fp_rate = results['false_positive_tests']['completely_random'].get('false_positive_rate', 0)
        if fp_rate < 0.05:
            tests_passed += 1
        else:
            red_flags.append(f"FP rate: {fp_rate*100:.1f}% (troppo alto)")
    
    print(f"\n📊 Test passati: {tests_passed}/{tests_total}")
    
    if red_flags:
        print(f"\n🚨 RED FLAGS IDENTIFICATI ({len(red_flags)}):")
        for i, flag in enumerate(red_flags, 1):
            print(f"  {i}. {flag}")
    else:
        print("\n✅ Nessun red flag critico identificato!")
    
    # Verdetto finale
    print("\n" + "="*70)
    if tests_passed == tests_total and not red_flags:
        print("🎉 VERDETTO: Segnale ROBUSTO - Passa tutti i test!")
    elif tests_passed >= tests_total * 0.7:
        print("⚠️ VERDETTO: Segnale MODERATO - Alcuni problemi minori")
    else:
        print("🚨 VERDETTO: Segnale DUBBIO - Problemi significativi")
    print("="*70)
    
except FileNotFoundError:
    print("\n❌ File 'ultimate_validation_suite.json' non trovato!")
    print("   Assicurati di essere nella cartella corretta.")
except json.JSONDecodeError:
    print("\n❌ Errore nel parsing del JSON!")
except Exception as e:
    print(f"\n❌ Errore: {e}")

print("\n" + "="*70)
print("✅ Analisi completata!")
print("="*70)
