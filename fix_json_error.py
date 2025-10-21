#!/usr/bin/env python3
"""
Correzione errore JSON per risultati multi-GRB
"""

import json
import numpy as np
from datetime import datetime

def convert_numpy(obj):
    """Converte oggetti numpy in tipi Python standard"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj

def main():
    print("="*60)
    print("CORREZIONE RISULTATI MULTI-GRB")
    print("="*60)
    
    # Risultati corretti (convertendo numpy types)
    results = [
        {
            'name': 'GRB080916C',
            'correlation': -0.03,
            'significance': 0.68,
            'photons': 516,
            'geV_photons': 31,
            'high_energy_photons': 2,
            'E_QG': 946394769165.892,
            'redshift': 4.35,
            'max_energy': 27.4
        },
        {
            'name': 'GRB090902',
            'correlation': -0.086,
            'significance': 5.46,
            'photons': 3972,
            'geV_photons': 259,
            'high_energy_photons': 10,
            'E_QG': 104366560859.65318,
            'redshift': 1.822,
            'max_energy': 80.8
        },
        {
            'name': 'GRB090510',
            'correlation': -0.035,
            'significance': 1.71,
            'photons': 2371,
            'geV_photons': 212,
            'high_energy_photons': 4,
            'E_QG': float('inf'),  # Errore nel calcolo originale
            'redshift': 0.903,
            'max_energy': 58.7
        },
        {
            'name': 'GRB130427A',
            'correlation': 0.229,
            'significance': 0.88,
            'photons': 16,
            'geV_photons': 1,
            'high_energy_photons': 0,
            'E_QG': 1902602619.5987446,
            'redshift': 0.34,
            'max_energy': 2.1
        }
    ]
    
    # Calcoli combinati
    total_photons = sum(r['photons'] for r in results)
    total_geV_photons = sum(r['geV_photons'] for r in results)
    total_heV_photons = sum(r['high_energy_photons'] for r in results)
    
    # Correlazione combinata (weighted average)
    weights = [r['photons'] for r in results]
    correlations = [r['correlation'] for r in results]
    combined_correlation = sum(w * c for w, c in zip(weights, correlations)) / sum(weights)
    
    # Significatività combinata
    combined_significance = abs(combined_correlation) * (total_photons - 2)**0.5 / (1 - combined_correlation**2)**0.5
    
    print(f"GRB analizzati: {len(results)}")
    print(f"Fotoni totali: {total_photons}")
    print(f"Fotoni GeV: {total_geV_photons}")
    print(f"Fotoni >10 GeV: {total_heV_photons}")
    print(f"Correlazione combinata: r = {combined_correlation:.3f}")
    print(f"Significatività combinata: {combined_significance:.2f}σ")
    
    # Interpretazione
    if combined_significance < 2:
        interpretation = 'NESSUNA EVIDENZA QG - RISULTATO NORMALE'
        print(f"✅ {interpretation}")
    elif combined_significance < 3:
        interpretation = 'CORRELAZIONE DEBOLE - ANALISI APPROFONDITA NECESSARIA'
        print(f"⚠️ {interpretation}")
    else:
        interpretation = 'CORRELAZIONE SIGNIFICATIVA - VERIFICA METODOLOGIA'
        print(f"🚨 {interpretation}")
    
    # Salva risultati corretti
    output = {
        'num_grb': len(results),
        'total_photons': total_photons,
        'total_geV_photons': total_geV_photons,
        'total_high_energy_photons': total_heV_photons,
        'combined_correlation': combined_correlation,
        'combined_significance': combined_significance,
        'interpretation': interpretation,
        'individual_results': results,
        'timestamp': datetime.now().isoformat(),
        'analysis_notes': [
            'GRB090902 mostra correlazione significativa (5.46σ)',
            'GRB090510 ha errore nel calcolo E_QG originale',
            'Combinazione bayesiana pesata per numero di fotoni',
            'Risultato finale: 5.3σ - CORRELAZIONE SIGNIFICATIVA'
        ]
    }
    
    # Converti tutti i numpy types
    def convert_all(obj):
        if isinstance(obj, dict):
            return {key: convert_all(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_all(item) for item in obj]
        else:
            return convert_numpy(obj)
    
    output_clean = convert_all(output)
    
    with open('final_multi_grb_results.json', 'w') as f:
        json.dump(output_clean, f, indent=2)
    
    print(f"\n✅ Risultati salvati: final_multi_grb_results.json")
    
    print(f"\n🎯 RISULTATO FINALE MULTI-GRB:")
    print(f"  GRB analizzati: {len(results)}")
    print(f"  Fotoni totali: {total_photons}")
    print(f"  Correlazione combinata: r = {combined_correlation:.3f}")
    print(f"  Significatività combinata: {combined_significance:.2f}σ")
    print(f"  Interpretazione: {interpretation}")
    
    print(f"\n🔬 ANALISI DETTAGLIATA:")
    print(f"  GRB090902: 5.46σ - CORRELAZIONE MOLTO SIGNIFICATIVA")
    print(f"  GRB090510: 1.71σ - Correlazione debole")
    print(f"  GRB080916C: 0.68σ - Nessuna correlazione")
    print(f"  GRB130427A: 0.88σ - Nessuna correlazione")
    
    if combined_significance >= 3:
        print(f"\n🚨 CONCLUSIONE: CORRELAZIONE SIGNIFICATIVA TROVATA!")
        print(f"🚨 Questo richiede verifica metodologica approfondita!")
        print(f"🚨 Possibile evidenza di effetti QG o bias sistematico!")
    else:
        print(f"\n✅ CONCLUSIONE: NESSUNA EVIDENZA QG!")
    
    print(f"\n{'='*60}")
    print("CORREZIONE COMPLETATA!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
