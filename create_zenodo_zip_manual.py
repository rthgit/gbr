#!/usr/bin/env python3
"""
🚀 CREA ZIP MANUALE PER ZENODO
"""

import os
import shutil
import zipfile
import json

def create_manual_zip():
    """Crea ZIP manuale per Zenodo"""
    
    print("🚀 CREANDO ZIP MANUALE PER ZENODO...")
    print("=" * 50)
    
    # Lista file da includere
    files_to_include = [
        # Paper principale
        "REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.md",
        "REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.html", 
        "multi_grb_discovery_paper.html",
        
        # Figure
        "SPECTACULAR_FIGURE_1_Multi_GRB_Discovery.png",
        "SPECTACULAR_FIGURE_2_Energy_Time_Correlations.png",
        "SPECTACULAR_FIGURE_3_Statistical_Significance.png",
        "SPECTACULAR_FIGURE_4_Quantum_Gravity_Energy_Scale.png",
        "SPECTACULAR_FIGURE_5_Hidden_Patterns_Phase_Transitions.png",
        "SPECTACULAR_FIGURE_6_Comprehensive_Summary.png",
        
        # Script di analisi
        "comprehensive_real_data_analysis.py",
        "deep_pattern_hunter.py",
        "analyze_existing_fits.py",
        "create_spectacular_visualizations.py",
        
        # Istruzioni
        "ZENODO_INSTRUCTIONS.md",
        
        # File dati (se presenti)
    ]
    
    # Aggiungi file FITS, CSV, JSON se presenti
    for ext in ['.fits', '.csv', '.json']:
        for file in os.listdir('.'):
            if file.endswith(ext):
                files_to_include.append(file)
    
    # Crea ZIP
    zip_filename = "ZENODO_PACKAGE_REPRODUCIBLE_QG_EFFECTS.zip"
    
    print(f"📦 Creating ZIP: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"✅ Added: {file}")
            else:
                print(f"⚠️ Missing: {file}")
        
        # Aggiungi README
        readme_content = """# Reproducible Quantum Gravity Effects in Multiple Gamma-Ray Bursts

## Authors
- Christian Quintino De Luca (ORCID: 0009-0000-4198-5449)
- Gregorio De Luca
- RTH Italia - Research & Technology Hub

## DOI
10.5281/zenodo.17408302

## Key Discovery
5 out of 8 GRBs show significant quantum gravity effects (2.28σ to 10.18σ)

## Files
- Paper: REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.html
- Figures: SPECTACULAR_FIGURE_*.png
- Analysis: *.py scripts
- Data: *.fits, *.csv, *.json files
- Instructions: ZENODO_INSTRUCTIONS.md

## Contact
info@rthitalia.com

---
RTH Italia ideato da Christian Quintino De Luca
"""
        
        zipf.writestr("README.md", readme_content)
        print("✅ Added: README.md")
    
    # Calcola dimensioni
    zip_size = os.path.getsize(zip_filename)
    
    print("=" * 50)
    print("🎉 ZIP CREATO CON SUCCESSO!")
    print("=" * 50)
    print(f"📦 File: {zip_filename}")
    print(f"📊 Dimensione: {zip_size / (1024*1024):.1f} MB")
    print("=" * 50)
    print("📋 PROSSIMI PASSI:")
    print("1. Vai su https://zenodo.org/deposit/new")
    print("2. Carica il file ZIP")
    print("3. Segui le istruzioni in ZENODO_INSTRUCTIONS.md")
    print("4. Usa DOI: 10.5281/zenodo.17408302")
    print("=" * 50)

if __name__ == "__main__":
    create_manual_zip()
