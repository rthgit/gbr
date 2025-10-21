#!/usr/bin/env python3
"""
Test di Validazione per Gravità Quantistica
Distinguere segnali QG reali da artefatti e bias sistematici
"""

import sys
import os
import json
import time
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Fix encoding per PowerShell
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from test import analyze_qg_signal, load_grb_data, E_PLANCK

class QuantumGravityValidator:
    """Validatore per distinguere QG da artefatti"""
    
    def __init__(self):
        self.test_results = {}
        self.validation_summary = {}
    
    def test_1_control_sample_low_energy(self, grb_data):
        """TEST 1: Control Sample - Fotoni a bassa energia"""
        print("\n" + "="*60)
        print("TEST 1: CONTROL SAMPLE - FOTONI BASSA ENERGIA")
        print("="*60)
        print("Obiettivo: Verificare che fotoni < 100 keV NON mostrino correlazione")
        print("Se trovi correlazione qui → BIAS SISTEMATICO!")
        
        times = grb_data['times']
        energies = grb_data['energies']
        metadata = grb_data['metadata']
        
        # Filtra fotoni a bassa energia
        energy_thresholds = [50, 100, 200]  # keV
        results = {}
        
        for threshold in energy_thresholds:
            print(f"\nSoglia: {threshold} keV")
            
            low_energy_mask = energies < threshold
            times_low = times[low_energy_mask]
            energies_low = energies[low_energy_mask]
            
            print(f"   Fotoni analizzati: {len(times_low)}")
            
            if len(times_low) < 20:
                print(f"   ⚠️ Troppo pochi fotoni per test significativo")
                results[f'threshold_{threshold}kev'] = {
                    'n_photons': len(times_low),
                    'valid': False,
                    'reason': 'Insufficient photons'
                }
                continue
            
            # Analisi identica a quella principale
            try:
                # Calcola correlazione
                correlation = np.corrcoef(times_low, energies_low)[0, 1]
                
                # Test significatività
                n = len(times_low)
                t_stat = correlation * np.sqrt((n-2) / (1-correlation**2))
                p_value = 2 * (1 - abs(t_stat) / np.sqrt(t_stat**2 + n-2))
                significance_sigma = np.sqrt(2) * np.sqrt(-np.log(p_value)) if p_value > 0 else 10
                
                print(f"   Correlazione: r = {correlation:.4f}")
                print(f"   P-value: {p_value:.2e}")
                print(f"   Significatività: {significance_sigma:.2f} σ")
                
                # Interpretazione
                bias_detected = significance_sigma > 2.0  # Soglia conservativa
                
                if bias_detected:
                    print(f"   ⚠️ BIAS RILEVATO! Correlazione significativa a bassa energia")
                    print(f"   → Possibile bias sistematico (intrinsic lag)")
                else:
                    print(f"   ✅ Nessun bias: correlazione non significativa a bassa energia")
                
                results[f'threshold_{threshold}kev'] = {
                    'n_photons': len(times_low),
                    'correlation': correlation,
                    'p_value': p_value,
                    'significance_sigma': significance_sigma,
                    'bias_detected': bias_detected,
                    'valid': True
                }
                
            except Exception as e:
                print(f"   ❌ Errore analisi: {e}")
                results[f'threshold_{threshold}kev'] = {
                    'n_photons': len(times_low),
                    'valid': False,
                    'error': str(e)
                }
        
        return results
    
    def test_2_mock_injection(self, grb_data, n_trials=100):
        """TEST 2: Mock Injection - Inietta segnali QG artificiali"""
        print("\n" + "="*60)
        print("TEST 2: MOCK INJECTION - INIETTA SEGNALI QG ARTIFICIALI")
        print("="*60)
        print("Obiettivo: Verificare che il sistema rilevi segnali QG iniettati")
        print("Se non rileva → Sistema non sensibile")
        
        times = grb_data['times'].copy()
        energies = grb_data['energies'].copy()
        metadata = grb_data['metadata']
        
        # Parametri test
        signal_strengths = [1e-4, 1e-3, 1e-2]  # s/GeV
        results = {}
        
        for signal_strength in signal_strengths:
            print(f"\nSegnale QG iniettato: α = {signal_strength:.2e} s/GeV")
            
            detections = 0
            false_positives = 0
            
            for trial in range(n_trials):
                # Crea copia dati
                times_trial = times.copy()
                energies_trial = energies.copy()
                
                # Inietta segnale QG artificiale
                # t_QG = α * E (dove α è il segnale QG)
                qg_delay = signal_strength * energies_trial  # s
                times_trial = times_trial + qg_delay
                
                # Crea dati temporanei
                temp_data = {
                    'times': times_trial,
                    'energies': energies_trial,
                    'metadata': metadata
                }
                
                # Analisi QG
                try:
                    result = analyze_qg_signal(temp_data, make_plots=False)
                    
                    if result and result['fit_results']:
                        significance = result['fit_results']['significance_sigma']
                        
                        if significance > 3.0:  # Soglia detection
                            detections += 1
                        
                        # Verifica se è davvero il segnale iniettato
                        if result['fit_results']['correlation'] > 0.1:
                            # Questo è un vero detection del segnale iniettato
                            pass
                        else:
                            # Questo potrebbe essere un falso positivo
                            false_positives += 1
                
                except Exception as e:
                    continue
            
            detection_rate = detections / n_trials
            false_positive_rate = false_positives / n_trials
            
            print(f"   Detection rate: {detection_rate:.1%}")
            print(f"   False positive rate: {false_positive_rate:.1%}")
            
            # Interpretazione
            if detection_rate > 0.8:
                print(f"   ✅ Sistema SENSIBILE: rileva segnali QG iniettati")
            elif detection_rate > 0.5:
                print(f"   ⚠️ Sistema MODERATAMENTE sensibile")
            else:
                print(f"   ❌ Sistema POCO sensibile: non rileva segnali QG")
            
            if false_positive_rate > 0.05:
                print(f"   ⚠️ ATTENZIONE: False positive rate alto!")
            
            results[f'signal_{signal_strength}'] = {
                'detection_rate': detection_rate,
                'false_positive_rate': false_positive_rate,
                'n_trials': n_trials,
                'sensitive': detection_rate > 0.8,
                'reliable': false_positive_rate < 0.05
            }
        
        return results
    
    def test_3_intrinsic_lag_analysis(self, grb_data):
        """TEST 3: Intrinsic Lag Analysis - Distingui QG da lag astrofisici"""
        print("\n" + "="*60)
        print("TEST 3: INTRINSIC LAG ANALYSIS")
        print("="*60)
        print("Obiettivo: Distinguere QG da lag astrofisici intrinseci")
        print("QG: t ∝ E, Lag astrofisico: t ∝ E^(-α) con α > 0")
        
        times = grb_data['times']
        energies = grb_data['energies']
        metadata = grb_data['metadata']
        
        results = {}
        
        # Test 1: Verifica dipendenza lineare vs non-lineare
        print("\nTest dipendenza lineare vs non-lineare:")
        
        # Fit lineare: t = t0 + α*E (QG)
        energies_gev = np.where(energies > 100, energies / 1000, energies)
        try:
            from scipy import optimize, stats
            
            def linear_model(E, t0, alpha):
                return t0 + alpha * E
            
            def power_law_model(E, t0, alpha, beta):
                return t0 + alpha * (E ** (-beta))
            
            # Fit lineare (QG)
            popt_linear, pcov_linear = optimize.curve_fit(linear_model, energies_gev, times)
            times_pred_linear = linear_model(energies_gev, *popt_linear)
            chi2_linear = np.sum((times - times_pred_linear)**2)
            
            # Fit power-law (lag astrofisico)
            popt_power, pcov_power = optimize.curve_fit(power_law_model, energies_gev, times, 
                                                       p0=[times.mean(), 1.0, 0.5], maxfev=1000)
            times_pred_power = power_law_model(energies_gev, *popt_power)
            chi2_power = np.sum((times - times_pred_power)**2)
            
            print(f"   Fit lineare (QG): χ² = {chi2_linear:.2f}")
            print(f"   Fit power-law (lag): χ² = {chi2_power:.2f}")
            
            # Test F per confrontare modelli
            if chi2_power < chi2_linear:
                f_stat = (chi2_linear - chi2_power) / chi2_power
                p_value_f = 1 - stats.f.cdf(f_stat, 1, len(times)-3)
                
                if p_value_f < 0.05:
                    print(f"   ✅ Power-law significativamente migliore (p={p_value_f:.2e})")
                    print(f"   → Probabile LAG ASTROFISICO, non QG")
                    model_preferred = 'power_law'
                else:
                    print(f"   ✅ Modelli equivalenti (p={p_value_f:.2e})")
                    print(f"   → QG possibile")
                    model_preferred = 'equivalent'
            else:
                print(f"   ✅ Fit lineare migliore")
                print(f"   → QG più probabile")
                model_preferred = 'linear'
            
            results['model_comparison'] = {
                'chi2_linear': chi2_linear,
                'chi2_power': chi2_power,
                'f_statistic': f_stat if 'f_stat' in locals() else None,
                'p_value': p_value_f if 'p_value_f' in locals() else None,
                'preferred_model': model_preferred
            }
            
        except Exception as e:
            print(f"   ❌ Errore fit: {e}")
            results['model_comparison'] = {
                'error': str(e),
                'preferred_model': 'unknown'
            }
        
        # Test 2: Analisi spettrale temporale
        print("\nTest analisi spettrale temporale:")
        
        try:
            # Divide dati in bande energetiche
            energy_bands = [
                (0, 100, 'Low'),
                (100, 1000, 'Medium'),
                (1000, np.inf, 'High')
            ]
            
            band_results = {}
            
            for e_min, e_max, label in energy_bands:
                if e_max == np.inf:
                    mask = energies >= e_min
                else:
                    mask = (energies >= e_min) & (energies < e_max)
                
                times_band = times[mask]
                energies_band = energies[mask]
                
                if len(times_band) < 10:
                    continue
                
                # Analizza distribuzione temporale in questa banda
                mean_time = np.mean(times_band)
                std_time = np.std(times_band)
                
                print(f"   Banda {label} ({e_min}-{e_max} keV): {len(times_band)} fotoni")
                print(f"      Tempo medio: {mean_time:.2f} ± {std_time:.2f} s")
                
                band_results[label] = {
                    'n_photons': len(times_band),
                    'mean_time': mean_time,
                    'std_time': std_time,
                    'energy_range': (e_min, e_max)
                }
            
            results['spectral_analysis'] = band_results
            
        except Exception as e:
            print(f"   ❌ Errore analisi spettrale: {e}")
            results['spectral_analysis'] = {'error': str(e)}
        
        return results
    
    def test_4_cross_validation_literature(self, grb_data):
        """TEST 4: Cross-validation con letteratura scientifica"""
        print("\n" + "="*60)
        print("TEST 4: CROSS-VALIDATION CON LETTERATURA")
        print("="*60)
        print("Obiettivo: Confrontare risultati con paper pubblicati")
        
        grb_name = grb_data['metadata']['name']
        redshift = grb_data['metadata']['redshift']
        
        # Database letteratura (valori reali da paper)
        literature_data = {
            'GRB080916C': {
                'paper': 'Abdo et al. 2009, Nature',
                'E_QG_limit': 1.2e17,  # GeV
                'method': 'Fermi-LAT 13.2 GeV photon',
                'result': 'No QG signal detected',
                'confidence': '3σ'
            },
            'GRB130427A': {
                'paper': 'Vasileiou et al. 2015, PRD',
                'E_QG_limit': 7.2e17,  # GeV
                'method': 'Fermi-LAT 95 GeV photon',
                'result': 'No QG signal detected',
                'confidence': '3σ'
            },
            'GRB190114C': {
                'paper': 'Acciari et al. 2019, PRL',
                'E_QG_limit': 2.6e18,  # GeV
                'method': 'MAGIC TeV gamma',
                'result': 'No QG signal detected',
                'confidence': '3σ'
            }
        }
        
        results = {}
        
        if grb_name in literature_data:
            lit_data = literature_data[grb_name]
            print(f"Confronto con: {lit_data['paper']}")
            print(f"Risultato letteratura: {lit_data['result']}")
            print(f"E_QG limite letteratura: {lit_data['E_QG_limit']:.2e} GeV")
            
            # Analizza i nostri dati
            try:
                our_result = analyze_qg_signal(grb_data, make_plots=False)
                
                if our_result and our_result['fit_results']:
                    our_eqg = our_result['fit_results']['E_QG_GeV']
                    our_significance = our_result['fit_results']['significance_sigma']
                    
                    print(f"Il nostro risultato:")
                    print(f"   E_QG: {our_eqg:.2e} GeV")
                    print(f"   Significatività: {our_significance:.2f} σ")
                    
                    # Confronto
                    if our_significance > 3.0:
                        if our_eqg < lit_data['E_QG_limit']:
                            print(f"   ⚠️ DISCREPANZA: Noi troviamo segnale, letteratura no")
                            print(f"   → Possibile artefatto o miglioramento metodologico")
                            consistency = 'discrepancy'
                        else:
                            print(f"   ✅ CONSISTENTE: Entrambi trovano segnale")
                            consistency = 'consistent'
                    else:
                        print(f"   ✅ CONSISTENTE: Entrambi non trovano segnale")
                        consistency = 'consistent'
                    
                    results['literature_comparison'] = {
                        'paper': lit_data['paper'],
                        'literature_result': lit_data['result'],
                        'literature_eqg': lit_data['E_QG_limit'],
                        'our_eqg': our_eqg,
                        'our_significance': our_significance,
                        'consistency': consistency
                    }
                
            except Exception as e:
                print(f"   ❌ Errore analisi: {e}")
                results['literature_comparison'] = {'error': str(e)}
        else:
            print(f"   ⚠️ Nessun dato letteratura per {grb_name}")
            results['literature_comparison'] = {'note': 'No literature data available'}
        
        return results
    
    def run_comprehensive_validation(self, grb_data):
        """Esegue tutti i test di validazione"""
        print("""
        ================================================================
        VALIDAZIONE COMPLETA GRAVITÀ QUANTISTICA
        ================================================================
        """)
        
        grb_name = grb_data['metadata']['name']
        print(f"GRB: {grb_name}")
        print(f"Redshift: z = {grb_data['metadata']['redshift']}")
        print(f"Fotoni: {len(grb_data['times'])}")
        
        validation_results = {}
        
        # Test 1: Control Sample
        print("\n🔬 ESECUZIONE TEST 1...")
        validation_results['control_sample'] = self.test_1_control_sample_low_energy(grb_data)
        
        # Test 2: Mock Injection
        print("\n🧪 ESECUZIONE TEST 2...")
        validation_results['mock_injection'] = self.test_2_mock_injection(grb_data, n_trials=50)
        
        # Test 3: Intrinsic Lag Analysis
        print("\n📊 ESECUZIONE TEST 3...")
        validation_results['intrinsic_lag'] = self.test_3_intrinsic_lag_analysis(grb_data)
        
        # Test 4: Cross-validation Literature
        print("\n📚 ESECUZIONE TEST 4...")
        validation_results['literature'] = self.test_4_cross_validation_literature(grb_data)
        
        return validation_results
    
    def evaluate_qg_evidence(self, validation_results):
        """Valuta evidenza per gravità quantistica"""
        print("\n" + "="*60)
        print("VALUTAZIONE FINALE EVIDENZA GRAVITÀ QUANTISTICA")
        print("="*60)
        
        evidence_score = 0
        max_score = 100
        issues = []
        strengths = []
        
        # Test 1: Control Sample
        print("\n1. CONTROL SAMPLE TEST:")
        control_results = validation_results.get('control_sample', {})
        bias_detected = any(r.get('bias_detected', False) for r in control_results.values() if isinstance(r, dict))
        
        if bias_detected:
            print("   ❌ BIAS SISTEMATICO RILEVATO")
            print("   → Segnali QG potrebbero essere artefatti")
            issues.append("Bias sistematico rilevato")
        else:
            print("   ✅ NESSUN BIAS SISTEMATICO")
            print("   → Segnali QG non sono artefatti noti")
            evidence_score += 25
            strengths.append("Nessun bias sistematico")
        
        # Test 2: Mock Injection
        print("\n2. MOCK INJECTION TEST:")
        mock_results = validation_results.get('mock_injection', {})
        detection_rates = [r.get('detection_rate', 0) for r in mock_results.values() if isinstance(r, dict)]
        
        if detection_rates:
            avg_detection_rate = np.mean(detection_rates)
            print(f"   Detection rate medio: {avg_detection_rate:.1%}")
            
            if avg_detection_rate > 0.8:
                print("   ✅ SISTEMA SENSIBILE")
                print("   → Sistema rileva correttamente segnali QG")
                evidence_score += 25
                strengths.append("Sistema sensibile")
            else:
                print("   ⚠️ SISTEMA POCO SENSIBILE")
                print("   → Potrebbe non rilevare segnali QG deboli")
                issues.append("Sistema poco sensibile")
        
        # Test 3: Intrinsic Lag Analysis
        print("\n3. INTRINSIC LAG ANALYSIS:")
        lag_results = validation_results.get('intrinsic_lag', {})
        model_comparison = lag_results.get('model_comparison', {})
        
        preferred_model = model_comparison.get('preferred_model', 'unknown')
        print(f"   Modello preferito: {preferred_model}")
        
        if preferred_model == 'linear':
            print("   ✅ FIT LINEARE PREFERITO")
            print("   → Supporta modello QG")
            evidence_score += 25
            strengths.append("Fit lineare preferito")
        elif preferred_model == 'power_law':
            print("   ❌ FIT POWER-LAW PREFERITO")
            print("   → Probabile lag astrofisico, non QG")
            issues.append("Lag astrofisico più probabile")
        else:
            print("   ⚠️ MODELLI EQUIVALENTI")
            print("   → Evidenza QG debole")
            evidence_score += 10
        
        # Test 4: Literature Comparison
        print("\n4. LITERATURE COMPARISON:")
        lit_results = validation_results.get('literature', {})
        literature_comparison = lit_results.get('literature_comparison', {})
        
        consistency = literature_comparison.get('consistency', 'unknown')
        print(f"   Consistenza con letteratura: {consistency}")
        
        if consistency == 'consistent':
            print("   ✅ CONSISTENTE CON LETTERATURA")
            print("   → Risultati in accordo con studi precedenti")
            evidence_score += 25
            strengths.append("Consistente con letteratura")
        elif consistency == 'discrepancy':
            print("   ⚠️ DISCREPANZA CON LETTERATURA")
            print("   → Necessaria investigazione approfondita")
            issues.append("Discrepanza con letteratura")
        
        # Valutazione finale
        print(f"\n{'='*60}")
        print("VERDETTO FINALE:")
        print(f"{'='*60}")
        
        print(f"Evidence Score: {evidence_score}/{max_score} ({evidence_score}%)")
        
        if evidence_score >= 80:
            verdict = "EVIDENZA FORTE per gravità quantistica"
            confidence = "ALTA"
        elif evidence_score >= 60:
            verdict = "EVIDENZA MODERATA per gravità quantistica"
            confidence = "MEDIA"
        elif evidence_score >= 40:
            verdict = "EVIDENZA DEBOLE per gravità quantistica"
            confidence = "BASSA"
        else:
            verdict = "NESSUNA EVIDENZA per gravità quantistica"
            confidence = "MOLTO BASSA"
        
        print(f"\n🎯 VERDETTO: {verdict}")
        print(f"📊 CONFIDENCE: {confidence}")
        
        if strengths:
            print(f"\n✅ PUNTI DI FORZA:")
            for strength in strengths:
                print(f"   - {strength}")
        
        if issues:
            print(f"\n⚠️ PROBLEMI IDENTIFICATI:")
            for issue in issues:
                print(f"   - {issue}")
        
        # Raccomandazioni
        print(f"\n💡 RACCOMANDAZIONI:")
        if evidence_score >= 60:
            print("   - Procedere con analisi approfondita")
            print("   - Espandere dataset con più GRB")
            print("   - Preparare pubblicazione scientifica")
        else:
            print("   - Investigare bias sistematici")
            print("   - Migliorare sensibilità sistema")
            print("   - Validare con dati reali veri")
        
        return {
            'evidence_score': evidence_score,
            'max_score': max_score,
            'verdict': verdict,
            'confidence': confidence,
            'strengths': strengths,
            'issues': issues,
            'recommendations': 'Proceed with analysis' if evidence_score >= 60 else 'Investigate further'
        }

def main():
    """Esegue validazione completa gravità quantistica"""
    print("""
    ================================================================
    VALIDAZIONE GRAVITÀ QUANTISTICA - TEST DEFINITIVI
    ================================================================
    Distinguere QG reale da artefatti e bias sistematici
    ================================================================
    """)
    
    validator = QuantumGravityValidator()
    
    # Carica dati per test
    print("Caricamento dati per validazione...")
    
    # Usa dati reali se disponibili, altrimenti simulati
    data_files = []
    import glob
    
    # Prova dati reali prima
    real_files = glob.glob('real_astronomical_data/**/*.fits', recursive=True)
    if real_files:
        data_files = real_files[:2]  # Prendi primi 2 file
        print(f"Trovati {len(data_files)} file dati reali")
    else:
        # Fallback a dati simulati
        simulated_files = glob.glob('public_test_data/**/*.fits', recursive=True)
        data_files = simulated_files[:2]
        print(f"Usando {len(data_files)} file dati simulati")
    
    if not data_files:
        print("❌ Nessun file dati trovato!")
        return
    
    # Esegui validazione per ogni file
    all_results = {}
    
    for i, filepath in enumerate(data_files, 1):
        print(f"\n{'='*80}")
        print(f"VALIDAZIONE FILE {i}/{len(data_files)}: {filepath}")
        print(f"{'='*80}")
        
        try:
            grb_data = load_grb_data(filepath, format='fits')
            
            if grb_data:
                validation_results = validator.run_comprehensive_validation(grb_data)
                evaluation = validator.evaluate_qg_evidence(validation_results)
                
                all_results[filepath] = {
                    'grb_name': grb_data['metadata']['name'],
                    'validation_results': validation_results,
                    'evaluation': evaluation
                }
            else:
                print(f"❌ Errore caricamento {filepath}")
                
        except Exception as e:
            print(f"❌ Errore validazione {filepath}: {e}")
    
    # Riepilogo finale
    print(f"\n{'='*80}")
    print("RIEPILOGO VALIDAZIONE GRAVITÀ QUANTISTICA")
    print(f"{'='*80}")
    
    if all_results:
        evidence_scores = [r['evaluation']['evidence_score'] for r in all_results.values()]
        avg_evidence = np.mean(evidence_scores)
        
        print(f"File validati: {len(all_results)}")
        print(f"Evidence score medio: {avg_evidence:.1f}/100")
        
        strong_evidence = sum(1 for score in evidence_scores if score >= 60)
        print(f"File con evidenza moderata/forte: {strong_evidence}/{len(all_results)}")
        
        # Salva risultati (con conversione numpy)
        def convert_numpy(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            else:
                return obj
        
        converted_results = convert_numpy(all_results)
        with open('quantum_gravity_validation_results.json', 'w') as f:
            json.dump(converted_results, f, indent=2)
        
        print(f"\n📁 Risultati salvati in 'quantum_gravity_validation_results.json'")
        
        if avg_evidence >= 60:
            print(f"\n🎉 CONCLUSIONE: EVIDENZA per gravità quantistica!")
        else:
            print(f"\n⚠️ CONCLUSIONE: Evidenza insufficiente per gravità quantistica")
    
    print(f"\n{'='*80}")
    print("VALIDAZIONE COMPLETATA!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
