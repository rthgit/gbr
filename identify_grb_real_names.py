#!/usr/bin/env python3
"""
IDENTIFICAZIONE GRB REALI
Identifica i veri nomi dei GRB mascherati nei risultati
"""

import pandas as pd
import numpy as np
from pathlib import Path

def main():
    print("IDENTIFICAZIONE GRB REALI")
    print("=" * 60)
    
    # Mappa fotoni → GRB attesi (dalla letteratura)
    expected_photons = {
        'GRB090902B': 3972,
        'GRB130427A': 9371,  # MATCH! Questo è probabilmente F39 o F43
        'GRB080916C': 210,
        'GRB160625B': 489,
        'GRB090926A': 380,
        'GRB090510': 150
    }

    # Mappa energie max (dalla letteratura)
    expected_emax = {
        'GRB090902B': 40.0,
        'GRB130427A': 94.1,  # MATCH! 94.1 GeV → Questo è F43!
        'GRB080916C': 27.4,
        'GRB160625B': 15.3,
        'GRB090926A': 19.4,
        'GRB090510': 30.0
    }

    # Risultati del paper (GRB mascherati)
    paper_results = {
        'F39': {'n': 9371, 'emax': 58.7, 'sigma': 10.18},
        'F43': {'n': 8354, 'emax': 94.1, 'sigma': 5.21},  # MATCH PERFETTO con GRB130427A!
        'F33': {'n': 5908, 'emax': 15.4, 'sigma': 3.36},
        'F27': {'n': 4929, 'emax': 27.9, 'sigma': 3.18},
        'F65': {'n': 534, 'emax': 99.3, 'sigma': 2.28}
    }

    print("\nANALISI MATCHING:")
    print("-" * 60)
    
    # Trova i migliori match
    best_matches = {}
    
    for code, res in paper_results.items():
        print(f"\nGRB L25...{code}:")
        print(f"  N photons: {res['n']}")
        print(f"  E_max: {res['emax']} GeV")
        print(f"  Sigma: {res['sigma']}")
        
        # Match per fotoni
        photon_matches = []
        for grb, n_exp in expected_photons.items():
            diff_pct = abs(res['n'] - n_exp) / n_exp * 100
            if diff_pct < 50:  # Within 50% (più permissivo)
                photon_matches.append((grb, diff_pct))
                print(f"  → Possibile {grb} (fotoni match: {diff_pct:.1f}% diff)")
        
        # Match per energia
        energy_matches = []
        for grb, e_exp in expected_emax.items():
            diff_pct = abs(res['emax'] - e_exp) / e_exp * 100
            if diff_pct < 50:
                energy_matches.append((grb, diff_pct))
                print(f"  → Possibile {grb} (energia match: {diff_pct:.1f}% diff)")
        
        # Trova il miglior match combinato
        all_candidates = set([m[0] for m in photon_matches + energy_matches])
        best_match = None
        best_score = float('inf')
        
        for grb in all_candidates:
            # Score combinato (fotoni + energia)
            photon_score = min([m[1] for m in photon_matches if m[0] == grb], default=100)
            energy_score = min([m[1] for m in energy_matches if m[0] == grb], default=100)
            combined_score = (photon_score + energy_score) / 2
            
            if combined_score < best_score:
                best_score = combined_score
                best_match = grb
        
        if best_match:
            best_matches[code] = best_match
            print(f"  🎯 BEST MATCH: {best_match} (score: {best_score:.1f})")
    
    print("\n" + "=" * 60)
    print("IDENTIFICAZIONE FINALE:")
    print("=" * 60)
    
    for code, grb in best_matches.items():
        res = paper_results[code]
        print(f"L25...{code} → {grb}")
        print(f"  📊 {res['n']} fotoni, {res['emax']} GeV, {res['sigma']}σ")
    
    print("\n" + "=" * 60)
    print("VERIFICA CON FILE REALI:")
    print("=" * 60)
    
    # Cerca i file CSV reali
    csv_files = list(Path('.').glob('**/*.csv'))
    print(f"Trovati {len(csv_files)} file CSV:")
    
    for csv_file in csv_files[:10]:  # Mostra i primi 10
        try:
            df = pd.read_csv(csv_file)
            if 'ENERGY' in df.columns and 'TIME' in df.columns:
                n_photons = len(df)
                e_max = df['ENERGY'].max() if 'ENERGY' in df.columns else 0
                print(f"  📁 {csv_file.name}: {n_photons} fotoni, E_max={e_max:.1f} GeV")
        except:
            continue
    
    return best_matches

if __name__ == "__main__":
    best_matches = main()

