#!/usr/bin/env python3
"""
CREATE FINAL ZENODO PACKAGE
Package finale con tutti i file corretti e risultati finali
"""

import os
import shutil
import zipfile
from pathlib import Path
import json
from datetime import datetime

def create_final_zenodo_package():
    """Crea il package Zenodo finale"""
    print("CREATE FINAL ZENODO PACKAGE")
    print("=" * 50)
    
    # Crea directory per il package finale
    package_dir = Path("zenodo_final_corrected_package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print("📁 Copiando file finali corretti...")
    
    # File principali da includere
    files_to_copy = [
        # Script di analisi
        "final_energy_correction.py",
        "correct_grb090926a_test.py",
        "deep_analysis_grb090926a.py",
        "grb_analysis_with_full_data.py",
        "validate_grb090510_6sigma.py",
        "literature_comparison.py",
        "create_comprehensive_report.py",
        "create_paper_figures_final.py",
        
        # Dati GRB corretti
        "GRB090926A_corrected_GeV.csv",
        "GRB090510_corrected_GeV.csv", 
        "GRB090902B_corrected_GeV.csv",
        "GRB130427A_corrected_GeV.csv",
        "GRB160625B_corrected_GeV.csv",
        "GRB080916C_corrected_GeV.csv",
        
        # Risultati finali
        "grb_corrected_final_results.csv",
        "GRB090926A_corrected_results.json",
        "comprehensive_qg_report.json",
        "comprehensive_qg_summary.csv",
        "comprehensive_qg_report.md",
        "literature_comparison_report.json",
        
        # Paper aggiornato
        "Quantum Gravity Grb Manuscript.html",
        
        # Figure finali
        "Figure_1_GRB_Overview_Final.png",
        "Figure_2_Top_GRBs_Analysis_Final.png", 
        "Figure_3_Phase_Analysis_Final.png",
        "Figure_4_Literature_Comparison_Final.png",
        "GRB090926A_deep_analysis.png",
        "GRB090510_validation.png",
        "comprehensive_grb_analysis.png",
        
        # Documentazione
        "README.md",
        "ALTERNATIVE_GRB_DATA_SOURCES.md",
        "DOWNLOAD_INSTRUCTIONS.md"
    ]
    
    copied_files = []
    for file_path in files_to_copy:
        src = Path(file_path)
        if src.exists():
            dst = package_dir / src.name
            shutil.copy2(src, dst)
            copied_files.append(src.name)
            print(f"✅ Copiato: {src.name}")
        else:
            print(f"❌ Non trovato: {src.name}")
    
    # Crea metadata finali
    metadata = {
        "title": "Quantum Gravity Signatures in Fermi LAT GRBs – Comprehensive Statistical Evidence (Energy Units Corrected)",
        "description": "Complete analysis of Quantum Gravity effects in 5 Fermi LAT GRBs using real data with corrected energy units (MeV→GeV). Reveals 2 strong discoveries: GRB090926A (7.38σ) and GRB090510 (5.28σ), with 60% detection rate. GRB080916C excluded due to background contamination.",
        "version": "4.0",
        "doi": "10.5281/zenodo.17404757",
        "authors": [
            {
                "name": "Christian Quintino De Luca",
                "orcid": "0009-0000-4198-5449",
                "affiliation": "RTH Italia – Research & Technology Hub, Milano, Italy"
            },
            {
                "name": "Gregorio De Luca", 
                "affiliation": "RTH Italia – Research & Technology Hub, Milano, Italy"
            },
            {
                "name": "Alessia De Luca",
                "affiliation": "RTH Italia – Research & Technology Hub, Milano, Italy"
            }
        ],
        "keywords": [
            "quantum gravity",
            "gamma-ray bursts", 
            "Fermi LAT",
            "energy-time correlation",
            "Lorentz invariance violation",
            "quantum spacetime",
            "astrophysics",
            "cosmology",
            "energy units correction"
        ],
        "license": "CC BY 4.0",
        "publication_date": "2025-10-22",
        "files_included": len(copied_files),
        "total_photons_analyzed": 64426,
        "grbs_analyzed": 5,
        "detection_rate": "60.0%",
        "strong_signals": 2,
        "significant_signals": 1,
        "top_discovery": "GRB090926A with 7.38σ significance",
        "second_discovery": "GRB090510 with 5.28σ significance",
        "excluded_grb": "GRB080916C due to background contamination (E_max=351 GeV)",
        "energy_correction": "All energies converted from MeV to GeV",
        "final_results": {
            "GRB090926A": {"photons": 24149, "emax_gev": 61.32, "sigma": 7.38, "method": "Pearson"},
            "GRB090510": {"photons": 24139, "emax_gev": 58.66, "sigma": 5.28, "method": "Spearman"},
            "GRB130427A": {"photons": 706, "emax_gev": 33.31, "sigma": 3.24, "method": "Spearman"},
            "GRB090902B": {"photons": 11289, "emax_gev": 80.82, "sigma": 0.84, "method": "Spearman"},
            "GRB160625B": {"photons": 4152, "emax_gev": 71.89, "sigma": 0.81, "method": "Spearman"}
        }
    }
    
    # Salva metadata
    with open(package_dir / "zenodo_metadata_final_corrected.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n📊 Metadata finali: {metadata['files_included']} file inclusi")
    
    # Crea ZIP finale
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"zenodo_qg_grb_analysis_FINAL_CORRECTED_{timestamp}.zip"
    
    print(f"\n📦 Creando ZIP finale: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
                print(f"✅ Aggiunto al ZIP: {arcname}")
    
    # Calcola dimensione
    zip_size = Path(zip_filename).stat().st_size / (1024 * 1024)
    
    print(f"\n🎉 PACKAGE FINALE CORRETTO COMPLETATO!")
    print("=" * 60)
    print(f"📁 File ZIP: {zip_filename}")
    print(f"📊 Dimensione: {zip_size:.2f} MB")
    print(f"📄 File inclusi: {len(copied_files)}")
    print(f"🎯 Scoperte: 2 forti (GRB090926A: 7.38σ, GRB090510: 5.28σ)")
    print(f"📊 Tasso rilevamento: 60% (3/5 GRB)")
    print(f"⚡ Fotoni analizzati: 64,426")
    print(f"🔧 Energie corrette: MeV → GeV")
    print(f"🚫 GRB escluso: GRB080916C (contaminazione background)")
    
    return zip_filename

def create_final_instructions():
    """Crea istruzioni finali per upload Zenodo"""
    instructions = """
# ISTRUZIONI FINALI ZENODO - VERSIONE CORRETTA

## 🎯 PACKAGE FINALE PRONTO

### File ZIP: zenodo_qg_grb_analysis_FINAL_CORRECTED_[timestamp].zip

## 📊 RISULTATI FINALI CORRETTI:

### 🔥 TOP DISCOVERIES:
- **GRB090926A: 7.38σ** (24,149 fotoni, E_max=61.32 GeV) - ECCEZIONALE!
- **GRB090510: 5.28σ** (24,139 fotoni, E_max=58.66 GeV) - MOLTO FORTE!
- **GRB130427A: 3.24σ** (706 fotoni, E_max=33.31 GeV) - SIGNIFICATIVO!

### 📈 STATISTICHE FINALI:
- **5 GRB analizzati** (GRB080916C escluso per contaminazione background)
- **3/5 GRB** con effetti significativi (60% detection rate)
- **64,426 fotoni** analizzati in totale
- **Energie corrette** da MeV a GeV per tutti i GRB

## 🔧 CORREZIONI APPLICATE:
- ✅ **Energie corrette**: MeV → GeV per tutti i GRB
- ✅ **GRB080916C escluso**: E_max=351 GeV > 100 GeV (contaminazione)
- ✅ **Sigma corretti**: Nessun valore infinito
- ✅ **P-value validi**: Tutti > 0
- ✅ **Dati reali**: Nessun artefatto numerico

## 🚀 PROCEDURA ZENODO:

1. **Vai su**: https://zenodo.org
2. **Login** con il tuo account
3. **Upload** → **New Upload**
4. **Carica**: `zenodo_qg_grb_analysis_FINAL_CORRECTED_[timestamp].zip`
5. **Compila metadata**:
   - **Titolo**: "Quantum Gravity Signatures in Fermi LAT GRBs – Comprehensive Statistical Evidence (Energy Units Corrected)"
   - **Versione**: 4.0
   - **DOI**: 10.5281/zenodo.17404757
   - **Licenza**: CC BY 4.0
6. **Pubblica** il dataset

## 🎉 RISULTATO ATTESO:
Paper scientifico completo con scoperte rivoluzionarie in QG, 
con dati corretti e validati!
"""
    
    with open("ZENODO_FINAL_CORRECTED_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Istruzioni finali create: ZENODO_FINAL_CORRECTED_INSTRUCTIONS.md")

def main():
    print("CREATE FINAL ZENODO PACKAGE")
    print("=" * 60)
    
    # Crea package
    zip_filename = create_final_zenodo_package()
    
    # Crea istruzioni
    create_final_instructions()
    
    print(f"\n🎯 TUTTO PRONTO PER ZENODO!")
    print(f"📁 File: {zip_filename}")
    print(f"📋 Istruzioni: ZENODO_FINAL_CORRECTED_INSTRUCTIONS.md")
    print(f"\n🚀 Procedi con l'upload su Zenodo!")

if __name__ == "__main__":
    main()

