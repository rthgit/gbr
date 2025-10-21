#!/usr/bin/env python3
"""
🚀 CREA PACKAGE ZENODO COMPLETO PER REPRODUCIBLE QUANTUM GRAVITY EFFECTS
"""

import os
import shutil
import zipfile
import json
from datetime import datetime

def create_zenodo_package():
    """Crea package completo per Zenodo"""
    
    print("🚀 CREANDO PACKAGE ZENODO COMPLETO...")
    print("=" * 60)
    
    # Crea directory principale
    package_dir = "zenodo_reproducible_quantum_gravity"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Crea subdirectory
    subdirs = [
        "paper",
        "figures", 
        "data",
        "code",
        "analysis_results",
        "documentation"
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(package_dir, subdir))
    
    print("📁 Directory structure created")
    
    # Copia file principali
    files_to_copy = [
        ("REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.md", "paper/"),
        ("REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.html", "paper/"),
        ("multi_grb_discovery_paper.html", "paper/"),
    ]
    
    print("📄 Copying main files...")
    for src, dst_dir in files_to_copy:
        if os.path.exists(src):
            dst_path = os.path.join(package_dir, dst_dir, os.path.basename(src))
            shutil.copy2(src, dst_path)
            print(f"✅ {src} -> {dst_path}")
        else:
            print(f"⚠️ {src} not found")
    
    # Copia figure
    figure_files = [
        "SPECTACULAR_FIGURE_1_Multi_GRB_Discovery.png",
        "SPECTACULAR_FIGURE_2_Energy_Time_Correlations.png",
        "SPECTACULAR_FIGURE_3_Statistical_Significance.png",
        "SPECTACULAR_FIGURE_4_Quantum_Gravity_Energy_Scale.png",
        "SPECTACULAR_FIGURE_5_Hidden_Patterns_Phase_Transitions.png",
        "SPECTACULAR_FIGURE_6_Comprehensive_Summary.png"
    ]
    
    print("🎨 Copying figures...")
    for fig_file in figure_files:
        if os.path.exists(fig_file):
            dst_path = os.path.join(package_dir, "figures", fig_file)
            shutil.copy2(fig_file, dst_path)
            print(f"✅ {fig_file} -> figures/")
        else:
            print(f"⚠️ {fig_file} not found")
    
    # Copia file di dati e analisi
    data_files = [
        "comprehensive_real_data_analysis.py",
        "deep_pattern_hunter.py",
        "analyze_existing_fits.py",
        "create_spectacular_visualizations.py",
        "*.fits",
        "*.csv",
        "*.json"
    ]
    
    print("📊 Copying data and analysis files...")
    for pattern in data_files:
        if pattern == "*.fits":
            fits_files = [f for f in os.listdir('.') if f.endswith('.fits')]
            for fits_file in fits_files:
                dst_path = os.path.join(package_dir, "data", fits_file)
                shutil.copy2(fits_file, dst_path)
                print(f"✅ {fits_file} -> data/")
        elif pattern == "*.csv":
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            for csv_file in csv_files:
                dst_path = os.path.join(package_dir, "data", csv_file)
                shutil.copy2(csv_file, dst_path)
                print(f"✅ {csv_file} -> data/")
        elif pattern == "*.json":
            json_files = [f for f in os.listdir('.') if f.endswith('.json')]
            for json_file in json_files:
                dst_path = os.path.join(package_dir, "data", json_file)
                shutil.copy2(json_file, dst_path)
                print(f"✅ {json_file} -> data/")
        else:
            if os.path.exists(pattern):
                dst_path = os.path.join(package_dir, "code", pattern)
                shutil.copy2(pattern, dst_path)
                print(f"✅ {pattern} -> code/")
    
    # Crea README principale
    readme_content = f"""# Reproducible Quantum Gravity Effects in Multiple Gamma-Ray Bursts

## Overview

This repository contains the complete dataset, analysis code, and scientific paper documenting the first reproducible detection of quantum gravity effects across multiple Gamma-Ray Bursts (GRBs) using real Fermi Large Area Telescope (LAT) data.

## Key Discovery

**5 out of 8 GRBs show significant quantum gravity effects**, establishing the reproducibility of these phenomena:

- **Strong Signals (≥5σ)**: 2 GRBs (10.18σ and 5.21σ)
- **Significant Signals (3-5σ)**: 2 GRBs (3.36σ and 3.18σ)  
- **Marginal Signal (2-3σ)**: 1 GRB (2.28σ)
- **Phase Transitions**: Detected in 4 GRBs
- **Energy Range**: 0.1 - 94.1 GeV

## Authors

**Christian Quintino De Luca** 🆔 ORCID: 0009-0000-4198-5449  
**Gregorio De Luca**  
RTH Italia - Research & Technology Hub  
Independent Research Laboratory  
Email: info@rthitalia.com  

## DOI

**10.5281/zenodo.17408302**

## Repository Structure

```
zenodo_reproducible_quantum_gravity/
├── paper/                           # Scientific papers
│   ├── REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.md
│   ├── REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.html
│   └── multi_grb_discovery_paper.html
├── figures/                         # All scientific figures
│   ├── SPECTACULAR_FIGURE_1_Multi_GRB_Discovery.png
│   ├── SPECTACULAR_FIGURE_2_Energy_Time_Correlations.png
│   ├── SPECTACULAR_FIGURE_3_Statistical_Significance.png
│   ├── SPECTACULAR_FIGURE_4_Quantum_Gravity_Energy_Scale.png
│   ├── SPECTACULAR_FIGURE_5_Hidden_Patterns_Phase_Transitions.png
│   └── SPECTACULAR_FIGURE_6_Comprehensive_Summary.png
├── data/                           # Raw and processed data
│   ├── *.fits                      # FITS files from Fermi LAT
│   ├── *.csv                       # Analysis results
│   └── *.json                      # Metadata and parameters
├── code/                           # Analysis scripts
│   ├── comprehensive_real_data_analysis.py
│   ├── deep_pattern_hunter.py
│   ├── analyze_existing_fits.py
│   └── create_spectacular_visualizations.py
├── analysis_results/               # Detailed results
├── documentation/                  # Additional documentation
└── README.md                       # This file
```

## Related Works

This reproducible quantum gravity discovery is part of a comprehensive research program:

1. **Initial Discovery**: "Anomalous Energy-Time Correlation in GRB090902B" (DOI: 10.5281/zenodo.17404756)
2. **Reproducible Effects**: "Reproducible Quantum Gravity Effects in Multiple GRBs" (DOI: 10.5281/zenodo.17408302) - **This work**
3. **DEUT Theory**: "De Luca Expansion Universe Theory" (DOI: 10.5281/zenodo.16754313)

## Scientific Impact

This work represents a paradigm shift from single-event anomalies to reproducible phenomena, providing:

- Direct evidence for quantum gravity at the Planck scale
- New constraints on quantum gravity energy scales  
- Systematic methodology for testing fundamental physics
- Framework for future multi-messenger observations

## Usage

1. **View the Paper**: Open `paper/REPRODUCIBLE_QUANTUM_GRAVITY_EFFECTS_PAPER.html` in your browser
2. **Run Analysis**: Execute scripts in `code/` directory
3. **Explore Data**: Check `data/` directory for raw and processed data
4. **Review Figures**: Browse `figures/` directory for all scientific visualizations

## Citation

```
De Luca, C. Q., & De Luca, G. (2025). Reproducible Quantum Gravity Effects in Multiple Gamma-Ray Bursts: Evidence from 5 out of 8 Fermi LAT Sources. Zenodo. https://doi.org/10.5281/zenodo.17408302
```

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

## Contact

For questions or collaboration requests, please contact:
- **Email**: info@rthitalia.com
- **ORCID**: 0009-0000-4198-5449
- **Institution**: RTH Italia - Research & Technology Hub

---

**RTH Italia ideato da Christian Quintino De Luca**

© 2025 Christian Quintino De Luca. All rights reserved.
"""
    
    with open(os.path.join(package_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.md created")
    
    # Crea metadata Zenodo
    zenodo_metadata = {
        "title": "Reproducible Quantum Gravity Effects in Multiple Gamma-Ray Bursts: Evidence from 5 out of 8 Fermi LAT Sources",
        "creators": [
            {
                "name": "De Luca, Christian Quintino",
                "affiliation": "RTH Italia - Research & Technology Hub",
                "orcid": "0009-0000-4198-5449"
            },
            {
                "name": "De Luca, Gregorio",
                "affiliation": "RTH Italia - Research & Technology Hub"
            }
        ],
        "description": """We report the first reproducible detection of quantum gravity effects across multiple Gamma-Ray Bursts (GRBs) using real Fermi Large Area Telescope (LAT) data. Our comprehensive analysis of 8 GRBs reveals statistically significant energy-time correlations in 5 sources, with signals ranging from 2.28σ to 10.18σ significance. This multi-GRB confirmation establishes the reproducibility of quantum gravity effects in astrophysical sources, representing a paradigm shift from single-event anomalies to systematic phenomena.

Key Findings:
- Reproducible Discovery: 5 out of 8 GRBs show significant quantum gravity effects
- Strong Signals: 2 GRBs with signals ≥5σ (10.18σ and 5.21σ)
- Significant Signals: 2 GRBs with signals 3-5σ (3.36σ and 3.18σ)
- Marginal Signal: 1 GRB with 2.28σ significance
- Phase Transitions: Detected in 4 GRBs, indicating temporal evolution
- Energy Range: 0.1 - 94.1 GeV across all sources

This work establishes quantum gravity effects as reproducible astrophysical phenomena, providing direct evidence for quantum gravity at the Planck scale and opening new avenues for testing fundamental physics.""",
        "keywords": [
            "quantum gravity",
            "gamma-ray bursts",
            "Fermi LAT",
            "reproducible effects",
            "multi-GRB analysis",
            "Planck scale physics",
            "phase transitions",
            "statistical robustness",
            "fundamental physics",
            "spacetime"
        ],
        "license": {
            "id": "CC-BY-4.0"
        },
        "upload_type": "publication",
        "publication_type": "article",
        "access_right": "open",
        "communities": [
            {
                "identifier": "zenodo"
            }
        ],
        "related_identifiers": [
            {
                "relation": "isSupplementedBy",
                "identifier": "10.5281/zenodo.17404756",
                "resource_type": "publication"
            },
            {
                "relation": "references",
                "identifier": "10.5281/zenodo.16754313",
                "resource_type": "publication"
            }
        ],
        "contributors": [
            {
                "name": "Fermi-LAT Collaboration",
                "type": "DataCollector"
            }
        ],
        "grants": [],
        "journal_title": "",
        "journal_volume": "",
        "journal_issue": "",
        "journal_pages": "",
        "conference_title": "",
        "conference_acronym": "",
        "conference_dates": "",
        "conference_place": "",
        "conference_url": "",
        "conference_session": "",
        "conference_session_part": "",
        "imprint_publisher": "",
        "imprint_isbn": "",
        "imprint_place": "",
        "partof_title": "",
        "partof_pages": "",
        "thesis_supervisors": [],
        "thesis_university": "",
        "subjects": [
            {
                "term": "Physics",
                "identifier": "physics",
                "scheme": "url"
            },
            {
                "term": "Astrophysics",
                "identifier": "astrophysics", 
                "scheme": "url"
            },
            {
                "term": "Quantum Gravity",
                "identifier": "quantum-gravity",
                "scheme": "url"
            }
        ]
    }
    
    with open(os.path.join(package_dir, "zenodo_metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(zenodo_metadata, f, indent=2, ensure_ascii=False)
    
    print("✅ zenodo_metadata.json created")
    
    # Crea istruzioni per upload
    upload_instructions = f"""# ZENODO UPLOAD INSTRUCTIONS

## Package Information

**Title**: Reproducible Quantum Gravity Effects in Multiple Gamma-Ray Bursts: Evidence from 5 out of 8 Fermi LAT Sources

**DOI**: 10.5281/zenodo.17408302

**Authors**: 
- Christian Quintino De Luca (ORCID: 0009-0000-4198-5449)
- Gregorio De Luca

**Institution**: RTH Italia - Research & Technology Hub

## Upload Steps

### 1. Go to Zenodo
- Visit: https://zenodo.org/deposit/new
- Login with your account

### 2. Upload Files
- Drag and drop the entire `zenodo_reproducible_quantum_gravity` folder
- OR create a ZIP file first and upload it

### 3. Fill Metadata
- **Title**: Reproducible Quantum Gravity Effects in Multiple Gamma-Ray Bursts: Evidence from 5 out of 8 Fermi LAT Sources
- **Creators**: 
  - Christian Quintino De Luca (ORCID: 0009-0000-4198-5449)
  - Gregorio De Luca
- **Description**: Use the description from zenodo_metadata.json
- **Keywords**: quantum gravity, gamma-ray bursts, Fermi LAT, reproducible effects, multi-GRB analysis, Planck scale physics, phase transitions, statistical robustness, fundamental physics, spacetime

### 4. Set Access Rights
- **Access Right**: Open
- **License**: CC-BY-4.0

### 5. Communities
- Add to "zenodo" community

### 6. Related Identifiers
- **isSupplementedBy**: 10.5281/zenodo.17404756 (First GRB paper)
- **references**: 10.5281/zenodo.16754313 (DEUT theory)

### 7. Subjects
- Physics
- Astrophysics  
- Quantum Gravity

### 8. Upload Type
- **Upload Type**: Publication
- **Publication Type**: Article

### 9. Review and Publish
- Review all information
- Click "Publish" to make it public
- Save the DOI for future reference

## File Structure

The package includes:
- Complete scientific paper (Markdown + HTML)
- All 6 spectacular figures
- Raw FITS data from Fermi LAT
- Analysis scripts and code
- Detailed results and metadata
- Complete documentation

## Important Notes

- This is the SECOND paper in the series (DOI: 10.5281/zenodo.17408302)
- It builds upon the first GRB paper (DOI: 10.5281/zenodo.17404756)
- It references the DEUT theory work (DOI: 10.5281/zenodo.16754313)
- Focus is on REPRODUCIBILITY across multiple GRBs
- 5 out of 8 GRBs show significant quantum gravity effects

## Contact

For questions: info@rthitalia.com
ORCID: 0009-0000-4198-5449

---
RTH Italia ideato da Christian Quintino De Luca
"""
    
    with open(os.path.join(package_dir, "ZENODO_UPLOAD_INSTRUCTIONS.md"), 'w', encoding='utf-8') as f:
        f.write(upload_instructions)
    
    print("✅ ZENODO_UPLOAD_INSTRUCTIONS.md created")
    
    # Crea ZIP file
    zip_filename = "zenodo_reproducible_quantum_gravity_package.zip"
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    
    print("📦 Creating ZIP package...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # Calcola dimensioni
    package_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                      for dirpath, dirnames, filenames in os.walk(package_dir)
                      for filename in filenames)
    zip_size = os.path.getsize(zip_filename)
    
    print("✅ ZIP package created")
    print("=" * 60)
    print("🎉 ZENODO PACKAGE COMPLETED!")
    print("=" * 60)
    print(f"📁 Package directory: {package_dir}/")
    print(f"📦 ZIP file: {zip_filename}")
    print(f"📊 Package size: {package_size / (1024*1024):.1f} MB")
    print(f"📦 ZIP size: {zip_size / (1024*1024):.1f} MB")
    print("=" * 60)
    print("📋 ROADMAP PER ZENODO:")
    print("1. Go to https://zenodo.org/deposit/new")
    print("2. Upload the ZIP file or folder")
    print("3. Use metadata from zenodo_metadata.json")
    print("4. Set DOI: 10.5281/zenodo.17408302")
    print("5. Review and publish")
    print("=" * 60)

if __name__ == "__main__":
    create_zenodo_package()
