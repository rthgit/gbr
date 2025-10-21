#!/usr/bin/env python3
"""
Esegue analisi batch sui GRB simulati e mostra risultati combinati
"""

import sys
import os
sys.path.append('.')

from test import analyze_multiple_grb_in_folder

def main():
    print('=== ANALISI BATCH MULTI-GRB ===')
    results, combined = analyze_multiple_grb_in_folder(folder_path='data', pattern='*.fits', make_plots=False)

    print('\n=== RISULTATI COMBINATI ===')
    if combined:
        print(f'Numero GRB analizzati: {combined["num_grb"]}')
        print(f'Log-likelihood combinata: {combined["log_L_combined"]:.2f}')
        print(f'Limite conservativo E_QG: {combined["E_QG_limit_conservative_GeV"]:.2e} GeV')
        print(f'Confronto con E_Planck: {combined["E_QG_limit_conservative_GeV"]/1.22e19:.2e}')
        
        print('\n=== DETTAGLI PER GRB ===')
        for i, result in enumerate(results):
            if result and result.get('fit_results'):
                fr = result['fit_results']
                lr = result.get('lr_results', {})
                metadata = result.get('metadata', {})
                print(f'GRB {i+1}: {metadata.get("name", "Unknown")}')
                print(f'  Correlazione: r = {fr["correlation"]:.4f}')
                print(f'  P-value: {fr["p_value"]:.2e}')
                print(f'  E_QG: {fr["E_QG_GeV"]:.2e} GeV')
                print(f'  LR sigma: {lr.get("sigma", 0):.2f}')
                print()
    else:
        print('Nessun risultato combinato disponibile')

if __name__ == "__main__":
    main()
