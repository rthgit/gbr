#!/usr/bin/env python3
"""
TROVA I DATI CORRETTI PER IL SEGNALE 10.18σ
Cerca file con ~9371 fotoni per GRB130427A
"""

import pandas as pd
from pathlib import Path

def find_grb_files_with_photons():
    """Trova tutti i file CSV e conta i fotoni"""
    print("RICERCA FILE CON DATI CORRETTI")
    print("=" * 50)
    
    # Cerca tutti i file CSV
    csv_files = list(Path('.').glob('**/*.csv'))
    print(f"Trovati {len(csv_files)} file CSV totali")
    
    # Target: file con ~9371 fotoni (per il segnale 10.18σ)
    target_photons = 9371
    tolerance = 500  # ±500 fotoni
    
    candidates = []
    
    print(f"\nCercando file con {target_photons} ± {tolerance} fotoni...")
    print("-" * 50)
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            if 'ENERGY' in df.columns and 'TIME' in df.columns:
                n_photons = len(df)
                e_max = df['ENERGY'].max()
                
                # Controlla se è vicino al target
                if abs(n_photons - target_photons) <= tolerance:
                    candidates.append({
                        'file': csv_file,
                        'photons': n_photons,
                        'emax': e_max,
                        'diff': abs(n_photons - target_photons)
                    })
                    print(f"🎯 CANDIDATO: {csv_file.name}")
                    print(f"   📊 {n_photons} fotoni (diff: {abs(n_photons - target_photons)})")
                    print(f"   ⚡ E_max: {e_max:.1f} GeV")
                    print()
        
        except Exception as e:
            continue
    
    if not candidates:
        print("❌ Nessun file trovato con ~9371 fotoni!")
        print("\nCerchiamo file con numero di fotoni simile...")
        
        # Cerca file con numero di fotoni alto
        high_photon_files = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if 'ENERGY' in df.columns and 'TIME' in df.columns:
                    n_photons = len(df)
                    if n_photons > 5000:  # File con molti fotoni
                        high_photon_files.append({
                            'file': csv_file,
                            'photons': n_photons,
                            'emax': df['ENERGY'].max()
                        })
            except:
                continue
        
        # Ordina per numero di fotoni
        high_photon_files.sort(key=lambda x: x['photons'], reverse=True)
        
        print("\nFile con più fotoni trovati:")
        print("-" * 50)
        for item in high_photon_files[:10]:
            print(f"📁 {item['file'].name}: {item['photons']} fotoni, E_max={item['emax']:.1f} GeV")
    
    else:
        # Ordina candidati per differenza
        candidates.sort(key=lambda x: x['diff'])
        
        print(f"\n✅ TROVATI {len(candidates)} CANDIDATI!")
        print("=" * 50)
        
        best_candidate = candidates[0]
        print(f"🏆 MIGLIOR CANDIDATO:")
        print(f"   📁 File: {best_candidate['file']}")
        print(f"   📊 Fotoni: {best_candidate['photons']}")
        print(f"   ⚡ E_max: {best_candidate['emax']:.1f} GeV")
        print(f"   🎯 Differenza: {best_candidate['diff']} fotoni")
        
        return best_candidate['file']
    
    return None

def analyze_grb_results_files():
    """Analizza i file di risultati per trovare il segnale 10.18σ"""
    print("\nANALISI FILE RISULTATI")
    print("=" * 50)
    
    # Cerca file di risultati
    result_files = list(Path('.').glob('**/*results*.csv'))
    
    for result_file in result_files:
        try:
            df = pd.read_csv(result_file)
            print(f"\n📁 Analizzando: {result_file}")
            
            if 'sigma_max' in df.columns:
                max_sigma = df['sigma_max'].max()
                max_idx = df['sigma_max'].idxmax()
                max_grb = df.iloc[max_idx]
                
                print(f"   🎯 Max sigma: {max_sigma:.2f}")
                print(f"   📊 GRB: {max_grb.get('name', 'N/A')}")
                print(f"   📊 Fotoni: {max_grb.get('n_photons', 'N/A')}")
                
                if max_sigma > 8.0:  # Cerca segnali > 8σ
                    print(f"   🔥 SEGNALE FORTE TROVATO!")
                    return result_file, max_grb
        
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    return None, None

def main():
    print("RICERCA DATI CORRETTI PER SEGNALE 10.18σ")
    print("=" * 60)
    
    # Trova file con numero di fotoni corretto
    correct_file = find_grb_files_with_photons()
    
    # Analizza file di risultati
    result_file, max_grb = analyze_grb_results_files()
    
    print("\n" + "=" * 60)
    print("CONCLUSIONI:")
    print("=" * 60)
    
    if correct_file:
        print(f"✅ File corretto trovato: {correct_file}")
        print("   Questo dovrebbe contenere il segnale 10.18σ")
    else:
        print("❌ File corretto non trovato")
        print("   Il segnale 10.18σ potrebbe essere in un file diverso")
    
    if result_file and max_grb is not None:
        print(f"✅ Segnale forte trovato in: {result_file}")
        print(f"   GRB: {max_grb.get('name', 'N/A')}")
        print(f"   Sigma: {max_grb.get('sigma_max', 'N/A'):.2f}")
    
    print("\n💡 RACCOMANDAZIONE:")
    print("   Controlla i file di risultati per trovare il GRB con 10.18σ")
    print("   Il file potrebbe avere un nome diverso da GRB130427A")

if __name__ == "__main__":
    main()

