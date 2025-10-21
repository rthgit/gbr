#!/usr/bin/env python3
"""
Script per eseguire analisi multi-strumento su dati reali simulati
Fermi GBM/LAT + Swift BAT + MAGIC
"""

import sys
import os

# Fix encoding per PowerShell
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from test import analyze_multi_instrument_data, E_PLANCK

def main():
    """Esegue l'analisi multi-strumento completa"""
    print("""
    ================================================================
    ANALISI MULTI-STRUMENTO GRB - DATI REALI SIMULATI
    ================================================================
    Fermi GBM/LAT + Swift BAT + MAGIC
    Combinazione Bayesiana per limite E_QG robusto
    ================================================================
    """)
    
    # Verifica che i dati esistano
    data_folders = ['data/fermi', 'data/swift', 'data/magic']
    for folder in data_folders:
        if not os.path.exists(folder):
            print(f"ERRORE: Cartella {folder} non trovata!")
            print("Esegui prima: python download_real_data.py")
            return
    
    # Esegui analisi multi-strumento
    print("\nAvvio analisi multi-strumento...")
    all_results, final_combined = analyze_multi_instrument_data(
        data_folder='data', 
        make_plots=False  # Headless mode
    )
    
    # Riepilogo finale
    print("\n" + "="*80)
    print("RIEPILOGO FINALE ANALISI MULTI-STRUMENTO")
    print("="*80)
    
    if final_combined:
        print(f"\nSTRUMENTI ATTIVI: {len([k for k, v in all_results.items() if v['num_grb'] > 0])}")
        print(f"GRB TOTALI ANALIZZATI: {final_combined['num_grb']}")
        print(f"LOG-LIKELIHOOD TOTALE: {final_combined['log_L_combined']:.2f}")
        print(f"E_QG LIMITE FINALE: {final_combined['E_QG_limit_conservative_GeV']:.2e} GeV")
        print(f"RAPPORTO E_Planck: {final_combined['E_QG_limit_conservative_GeV'] / E_PLANCK:.2e}")
        
        # Interpretazione risultati
        print(f"\nINTERPRETAZIONE:")
        if final_combined['E_QG_limit_conservative_GeV'] / E_PLANCK > 0.1:
            print("   ✅ LIMITE ROBUSTO: E_QG > 10% E_Planck")
            print("   → Consistente con relatività generale")
        else:
            print("   ⚠️ LIMITE DEBOLE: E_QG < 10% E_Planck")
            print("   → Necessari più dati per limite stringente")
        
        print(f"\nDETTAGLI PER STRUMENTO:")
        for instrument, data in all_results.items():
            if data['num_grb'] > 0:
                print(f"\n{instrument.upper()}:")
                print(f"   GRB: {data['num_grb']}")
                if data['combined']:
                    print(f"   E_QG: {data['combined']['E_QG_limit_conservative_GeV']:.2e} GeV")
                    print(f"   vs Planck: {data['combined']['E_QG_limit_conservative_GeV'] / E_PLANCK:.2e}")
    else:
        print("ERRORE: Nessun risultato combinato ottenuto!")
    
    print(f"\nFILE GENERATI:")
    print("   - qg_multi_instrument_results.json (risultati finali)")
    print("   - qg_multi_results.json (per ogni strumento)")
    print("   - qg_analysis_results.json (singoli GRB)")
    
    print("\n" + "="*80)
    print("ANALISI COMPLETATA!")
    print("="*80)

if __name__ == "__main__":
    main()
