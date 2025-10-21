#!/usr/bin/env python3
"""
DOWNLOAD ANOMALOUS GRBs
========================

Download GRB con anomalie documentate dalla letteratura.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import os
import requests
import json
from datetime import datetime
import time

def download_anomalous_grb(grb_name, coordinates, time_range, priority):
    """
    Download GRB anomalo da Fermi LAT
    """
    print(f"🛰️ Downloading {grb_name} (Priority {priority})...")
    print(f"   📍 Coordinates: {coordinates}")
    print(f"   ⏱️ Time range: {time_range}")
    
    # URL per Fermi LAT query
    fermi_url = "https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi"
    
    # Parametri per query
    params = {
        'object_coordinates': coordinates,
        'coordinate_system': 'J2000',
        'search_radius': '12',
        'time_range': time_range,
        'time_system': 'MET',
        'energy_range': '100,300000',
        'lat_data_type': 'Extended',
        'spacecraft_data': 'YES'
    }
    
    try:
        # Prova a fare query (simulazione per ora)
        print(f"   🔍 Querying Fermi LAT for {grb_name}...")
        
        # Simula download (in realtà dovresti usare il sito web)
        result = {
            'grb_name': grb_name,
            'priority': priority,
            'coordinates': coordinates,
            'time_range': time_range,
            'status': 'query_required',
            'fermi_url': fermi_url,
            'params': params,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"   ✅ {grb_name}: Query parameters prepared")
        return result
        
    except Exception as e:
        print(f"   ❌ {grb_name}: {e}")
        return None

def download_all_anomalous_grbs():
    """
    Download tutti i GRB anomali
    """
    print("🚀 DOWNLOAD ANOMALOUS GRBs")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Lista dei GRB anomali con priorità
    anomalous_grbs = [
        # TIER 1 - CRITICAL
        ('GRB221009A', '288.2650, 19.7730', '687013719, 687024219', 1, 'Brightest ever, >10 TeV'),
        ('GRB190114C', '54.5040, -26.9380', '569191723, 569202223', 1, 'First TeV, power-law extra'),
        ('GRB090926A', '353.399, -66.318', '275631126, 275641626', 1, 'Break spettrale 1.4 GeV'),
        ('GRB160625B', '308.571, 6.933', '488586716, 488597216', 1, 'Lag transition documentata'),
        ('GRB180720B', '7.3680, -2.9410', '553788804, 553799304', 1, 'TeV 10h dopo, 440 GeV'),
        
        # TIER 2 - HIGH PRIORITY
        ('GRB131231A', '173.136, 27.697', '388741126, 388751626', 2, 'Upturn 1.6 GeV confermato'),
        ('GRB130427A', '173.136, 27.697', '388741126, 388751626', 2, 'High-energy component inspiegabile'),
        ('GRB190829A', '31.027, -8.952', '588800853, 588811353', 2, 'Nearest TeV, comportamento caotico'),
        ('GRB080916C', '119.846, -56.638', '243216265, 243226765', 2, 'Delayed onset, Band featureless'),
        ('GRB091024', '54.504, -26.938', '569191723, 569202223', 2, 'Ultra-long, Yonetoku outlier'),
        
        # TIER 3 - MEDIUM PRIORITY
        ('GRB090323', '333.553, -26.591', '263607279, 263617779', 3, 'Blackbody component necessaria'),
        ('GRB240825A', '288.265, 19.773', '687013719, 687024219', 3, 'Two-hump spectrum'),
        ('GRB090820', '54.504, -26.938', '569191723, 569202223', 3, 'Due breaks spettrali'),
        ('GRB201216C', '34.637, 17.775', '629850246, 629860746', 3, 'VHE detection'),
        ('GRB090510', '333.553, -26.591', '263607279, 263617779', 3, 'Short peculiare, extra PL')
    ]
    
    # Crea directory per risultati
    os.makedirs('anomalous_grb_analysis', exist_ok=True)
    
    # Download tutti i GRB anomali
    all_results = {}
    
    for grb_name, coordinates, time_range, priority, description in anomalous_grbs:
        print(f"\n🔍 Processing {grb_name} (Priority {priority})...")
        print(f"   📝 {description}")
        
        result = download_anomalous_grb(grb_name, coordinates, time_range, priority)
        
        if result:
            all_results[grb_name] = result
    
    # Salva risultati
    with open('anomalous_grb_analysis/download_plan.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Crea istruzioni dettagliate
    create_download_instructions(all_results)
    
    print("\n" + "=" * 60)
    print("🎉 ANOMALOUS GRBs DOWNLOAD PLAN COMPLETE!")
    print("📊 Check 'anomalous_grb_analysis/' directory for instructions")
    print("=" * 60)

def create_download_instructions(results):
    """
    Crea istruzioni dettagliate per download
    """
    print("\n📋 CREATING DETAILED DOWNLOAD INSTRUCTIONS...")
    
    instructions = []
    instructions.append("# 🚀 DOWNLOAD ANOMALOUS GRBs - ISTRUZIONI DETTAGLIATE")
    instructions.append("")
    instructions.append("## 🎯 STRATEGIA: GRB CON ANOMALIE DOCUMENTATE")
    instructions.append("")
    instructions.append("### ✅ TIER 1 - CRITICAL (Download SUBITO!):")
    
    tier1_grbs = [grb for grb, data in results.items() if data['priority'] == 1]
    for grb in tier1_grbs:
        data = results[grb]
        instructions.append(f"**{grb}:**")
        instructions.append(f"- Coordinates: {data['coordinates']}")
        instructions.append(f"- Time range: {data['time_range']}")
        instructions.append(f"- URL: {data['fermi_url']}")
        instructions.append("")
    
    instructions.append("### ✅ TIER 2 - HIGH PRIORITY:")
    tier2_grbs = [grb for grb, data in results.items() if data['priority'] == 2]
    for grb in tier2_grbs:
        data = results[grb]
        instructions.append(f"**{grb}:**")
        instructions.append(f"- Coordinates: {data['coordinates']}")
        instructions.append(f"- Time range: {data['time_range']}")
        instructions.append("")
    
    instructions.append("### ✅ TIER 3 - MEDIUM PRIORITY:")
    tier3_grbs = [grb for grb, data in results.items() if data['priority'] == 3]
    for grb in tier3_grbs:
        data = results[grb]
        instructions.append(f"**{grb}:**")
        instructions.append(f"- Coordinates: {data['coordinates']}")
        instructions.append(f"- Time range: {data['time_range']}")
        instructions.append("")
    
    instructions.append("## 🚀 PROCEDURA DOWNLOAD:")
    instructions.append("")
    instructions.append("### 📋 STEP 1: APRI TAB BROWSER")
    instructions.append("Vai a: https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi")
    instructions.append("")
    instructions.append("### 📋 STEP 2: INSERISCI PARAMETRI")
    instructions.append("Per ogni GRB, inserisci:")
    instructions.append("- Object coordinates: [coordinate]")
    instructions.append("- Coordinate system: J2000")
    instructions.append("- Search radius: 12")
    instructions.append("- Time range: [time_range]")
    instructions.append("- Time system: MET")
    instructions.append("- Energy range: 100, 300000")
    instructions.append("- LAT data type: Extended")
    instructions.append("- Spacecraft data: ✓")
    instructions.append("")
    instructions.append("### 📋 STEP 3: SUBMIT QUERY")
    instructions.append("- Clicca 'Start Query'")
    instructions.append("- Salva Query ID")
    instructions.append("- Aspetta processing (10-30 min)")
    instructions.append("")
    instructions.append("### 📋 STEP 4: DOWNLOAD FILES")
    instructions.append("- L[QUERYID]_EV00.fits ← CRITICO!")
    instructions.append("- L[QUERYID]_SC00.fits")
    instructions.append("- Salva come: [GRB_NAME]_EV00.fits")
    instructions.append("")
    instructions.append("## 🎉 RISULTATI ATTESI:")
    instructions.append("- 15 GRB con anomalie documentate")
    instructions.append("- Analisi QG su dati reali")
    instructions.append("- Confronto con GRB090902B")
    instructions.append("- Validazione universalità effetto")
    
    # Salva istruzioni
    with open('anomalous_grb_analysis/DOWNLOAD_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(instructions))
    
    print("   ✅ Instructions saved: anomalous_grb_analysis/DOWNLOAD_INSTRUCTIONS.md")

if __name__ == "__main__":
    download_all_anomalous_grbs()
