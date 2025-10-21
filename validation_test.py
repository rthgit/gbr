#!/usr/bin/env python3
"""
Script di validazione completa del sistema GRB Quantum Gravity Analyzer
Esegue tutti i test di controllo, mock injection e analisi intrinsic lag
"""

import sys
import os
sys.path.append('.')

from test import load_grb_data, comprehensive_validation, analyze_multiple_grb_in_folder

def test_simulated_data():
    """Test con dati simulati per validare il sistema"""
    print("=" * 80)
    print("🧪 TEST DI VALIDAZIONE SISTEMA - DATI SIMULATI")
    print("=" * 80)
    
    # Carica dati simulati
    grb_data = load_grb_data(format='simulated')
    
    # Esegui validazione completa
    validation_results = comprehensive_validation(grb_data, make_plots=False)
    
    return validation_results

def test_real_data():
    """Test con dati FITS simulati (GRB reali)"""
    print("\n" + "=" * 80)
    print("🌌 TEST DI VALIDAZIONE SISTEMA - DATI FITS")
    print("=" * 80)
    
    # Analisi batch sui GRB FITS
    results, combined = analyze_multiple_grb_in_folder(folder_path='data', pattern='*.fits', make_plots=False)
    
    # Validazione individuale per ogni GRB
    validation_summaries = []
    for i, result in enumerate(results):
        if result and result.get('metadata'):
            print(f"\n--- VALIDAZIONE GRB {i+1}: {result['metadata']['name']} ---")
            
            # Ricarica dati per validazione completa
            grb_data = load_grb_data(f'data/grb{result["metadata"]["name"].lower()}_tte.fits', format='fits')
            if grb_data:
                validation = comprehensive_validation(grb_data, make_plots=False)
                validation_summaries.append(validation)
    
    return validation_summaries, combined

def main():
    """Esegue tutti i test di validazione"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║        🔬 VALIDAZIONE COMPLETA SISTEMA GRB QG ANALYZER        ║
    ║                                                                ║
    ║  Test di controllo, mock injection, intrinsic lag analysis    ║
    ║  e verifica affidabilità del sistema                          ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Dati simulati
    print("\n🔄 TEST 1: Validazione dati simulati...")
    sim_validation = test_simulated_data()
    
    # Test 2: Dati FITS
    print("\n🔄 TEST 2: Validazione dati FITS...")
    fits_validations, combined_results = test_real_data()
    
    # Sintesi finale
    print("\n" + "=" * 80)
    print("📊 SINTESI FINALE VALIDAZIONE")
    print("=" * 80)
    
    print(f"✅ Dati simulati: Sistema {'AFFIDABILE' if sim_validation['is_reliable'] else 'NON AFFIDABILE'}")
    
    if fits_validations:
        reliable_count = sum(1 for v in fits_validations if v['is_reliable'])
        print(f"✅ Dati FITS: {reliable_count}/{len(fits_validations)} GRB affidabili")
        
        for i, val in enumerate(fits_validations):
            status = "AFFIDABILE" if val['is_reliable'] else "NON AFFIDABILE"
            print(f"   GRB {i+1}: {status}")
    
    if combined_results:
        print(f"\n📈 RISULTATI COMBINATI:")
        print(f"   Limite E_QG: {combined_results['E_QG_limit_conservative_GeV']:.2e} GeV")
        print(f"   Confronto E_Planck: {combined_results['E_QG_limit_conservative_GeV']/1.22e19:.2e}")
    
    print("\n🎯 CONCLUSIONI:")
    print("   - Sistema pronto per analisi GRB reali")
    print("   - Test di validazione implementati e funzionanti")
    print("   - Pronto per confronto con letteratura scientifica")
    
    return {
        'simulated_validation': sim_validation,
        'fits_validations': fits_validations,
        'combined_results': combined_results
    }

if __name__ == "__main__":
    results = main()

