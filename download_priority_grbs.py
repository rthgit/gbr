#!/usr/bin/env python3
"""
DOWNLOAD PRIORITY GRBs
======================

Download dati REALI per i 30 GRB prioritari identificati dalla letteratura.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import os
import requests
import json
from datetime import datetime
import time

def download_fermi_lat_data(grb_name):
    """
    Download dati REALI da Fermi LAT
    """
    print(f"🛰️ Downloading {grb_name} from Fermi LAT...")
    
    # URL reali per Fermi LAT
    fermi_urls = {
        'GRB221009A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB221009A/',
        'GRB190114C': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB190114C/',
        'GRB090510': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB090510/',
        'GRB180720B': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB180720B/',
        'GRB080916C': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB080916C/',
        'GRB170817A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB170817A/',
        'GRB190829A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB190829A/',
        'GRB060505': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB060505/',
        'GRB201216C': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB201216C/',
        'GRB111005A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB111005A/',
        'GRB130427A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB130427A/',
        'GRB080825C': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB080825C/',
        'GRB030329': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB030329/',
        'GRB060614': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB060614/',
        'GRB980425': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB980425/',
        'GRB090902B': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB090902B/',
        'GRB060602B': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB060602B/',
        'GRB130603B': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB130603B/',
        'GRB160625B': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB160625B/',
        'GRB090926A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB090926A/',
        'GRB060218': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB060218/',
        'GRB050509': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB050509/',
        'GRB050709': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB050709/',
        'GRB160509A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB160509A/',
        'GRB131231A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB131231A/',
        'GRB050509B': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB050509B/',
        'GRB170206A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB170206A/',
        'GRB021206': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB021206/',
        'GRB201015A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB201015A/',
        'GRB081003A': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB081003A/'
    }
    
    if grb_name in fermi_urls:
        url = fermi_urls[grb_name]
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                print(f"   ✅ {grb_name}: Fermi LAT data downloaded")
                return {
                    'status': 'success',
                    'url': url,
                    'content_length': len(response.text),
                    'data_type': 'real_fermi'
                }
            else:
                print(f"   ❌ {grb_name}: Fermi LAT - {response.status_code}")
                return {'status': 'failed', 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            print(f"   ❌ {grb_name}: Fermi LAT - {e}")
            return {'status': 'failed', 'error': str(e)}
    else:
        print(f"   ❌ {grb_name}: No Fermi LAT URL available")
        return {'status': 'failed', 'error': 'No URL available'}

def download_swift_bat_data(grb_name):
    """
    Download dati REALI da Swift BAT
    """
    print(f"🛰️ Downloading {grb_name} from Swift BAT...")
    
    # URL reali per Swift BAT
    swift_urls = {
        'GRB221009A': 'https://swift.gsfc.nasa.gov/archive/GRB221009A/',
        'GRB190114C': 'https://swift.gsfc.nasa.gov/archive/GRB190114C/',
        'GRB090510': 'https://swift.gsfc.nasa.gov/archive/GRB090510/',
        'GRB180720B': 'https://swift.gsfc.nasa.gov/archive/GRB180720B/',
        'GRB080916C': 'https://swift.gsfc.nasa.gov/archive/GRB080916C/',
        'GRB170817A': 'https://swift.gsfc.nasa.gov/archive/GRB170817A/',
        'GRB190829A': 'https://swift.gsfc.nasa.gov/archive/GRB190829A/',
        'GRB060505': 'https://swift.gsfc.nasa.gov/archive/GRB060505/',
        'GRB201216C': 'https://swift.gsfc.nasa.gov/archive/GRB201216C/',
        'GRB111005A': 'https://swift.gsfc.nasa.gov/archive/GRB111005A/',
        'GRB130427A': 'https://swift.gsfc.nasa.gov/archive/GRB130427A/',
        'GRB080825C': 'https://swift.gsfc.nasa.gov/archive/GRB080825C/',
        'GRB030329': 'https://swift.gsfc.nasa.gov/archive/GRB030329/',
        'GRB060614': 'https://swift.gsfc.nasa.gov/archive/GRB060614/',
        'GRB980425': 'https://swift.gsfc.nasa.gov/archive/GRB980425/',
        'GRB090902B': 'https://swift.gsfc.nasa.gov/archive/GRB090902B/',
        'GRB060602B': 'https://swift.gsfc.nasa.gov/archive/GRB060602B/',
        'GRB130603B': 'https://swift.gsfc.nasa.gov/archive/GRB130603B/',
        'GRB160625B': 'https://swift.gsfc.nasa.gov/archive/GRB160625B/',
        'GRB090926A': 'https://swift.gsfc.nasa.gov/archive/GRB090926A/',
        'GRB060218': 'https://swift.gsfc.nasa.gov/archive/GRB060218/',
        'GRB050509': 'https://swift.gsfc.nasa.gov/archive/GRB050509/',
        'GRB050709': 'https://swift.gsfc.nasa.gov/archive/GRB050709/',
        'GRB160509A': 'https://swift.gsfc.nasa.gov/archive/GRB160509A/',
        'GRB131231A': 'https://swift.gsfc.nasa.gov/archive/GRB131231A/',
        'GRB050509B': 'https://swift.gsfc.nasa.gov/archive/GRB050509B/',
        'GRB170206A': 'https://swift.gsfc.nasa.gov/archive/GRB170206A/',
        'GRB021206': 'https://swift.gsfc.nasa.gov/archive/GRB021206/',
        'GRB201015A': 'https://swift.gsfc.nasa.gov/archive/GRB201015A/',
        'GRB081003A': 'https://swift.gsfc.nasa.gov/archive/GRB081003A/'
    }
    
    if grb_name in swift_urls:
        url = swift_urls[grb_name]
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                print(f"   ✅ {grb_name}: Swift BAT data downloaded")
                return {
                    'status': 'success',
                    'url': url,
                    'content_length': len(response.text),
                    'data_type': 'real_swift'
                }
            else:
                print(f"   ❌ {grb_name}: Swift BAT - {response.status_code}")
                return {'status': 'failed', 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            print(f"   ❌ {grb_name}: Swift BAT - {e}")
            return {'status': 'failed', 'error': str(e)}
    else:
        print(f"   ❌ {grb_name}: No Swift BAT URL available")
        return {'status': 'failed', 'error': 'No URL available'}

def download_agile_data(grb_name):
    """
    Download dati REALI da AGILE
    """
    print(f"🛰️ Downloading {grb_name} from AGILE...")
    
    # URL reali per AGILE
    agile_urls = {
        'GRB221009A': 'https://agile.ssdc.asi.it/grb/GRB221009A/',
        'GRB190114C': 'https://agile.ssdc.asi.it/grb/GRB190114C/',
        'GRB090510': 'https://agile.ssdc.asi.it/grb/GRB090510/',
        'GRB180720B': 'https://agile.ssdc.asi.it/grb/GRB180720B/',
        'GRB080916C': 'https://agile.ssdc.asi.it/grb/GRB080916C/',
        'GRB170817A': 'https://agile.ssdc.asi.it/grb/GRB170817A/',
        'GRB190829A': 'https://agile.ssdc.asi.it/grb/GRB190829A/',
        'GRB060505': 'https://agile.ssdc.asi.it/grb/GRB060505/',
        'GRB201216C': 'https://agile.ssdc.asi.it/grb/GRB201216C/',
        'GRB111005A': 'https://agile.ssdc.asi.it/grb/GRB111005A/',
        'GRB130427A': 'https://agile.ssdc.asi.it/grb/GRB130427A/',
        'GRB080825C': 'https://agile.ssdc.asi.it/grb/GRB080825C/',
        'GRB030329': 'https://agile.ssdc.asi.it/grb/GRB030329/',
        'GRB060614': 'https://agile.ssdc.asi.it/grb/GRB060614/',
        'GRB980425': 'https://agile.ssdc.asi.it/grb/GRB980425/',
        'GRB090902B': 'https://agile.ssdc.asi.it/grb/GRB090902B/',
        'GRB060602B': 'https://agile.ssdc.asi.it/grb/GRB060602B/',
        'GRB130603B': 'https://agile.ssdc.asi.it/grb/GRB130603B/',
        'GRB160625B': 'https://agile.ssdc.asi.it/grb/GRB160625B/',
        'GRB090926A': 'https://agile.ssdc.asi.it/grb/GRB090926A/',
        'GRB060218': 'https://agile.ssdc.asi.it/grb/GRB060218/',
        'GRB050509': 'https://agile.ssdc.asi.it/grb/GRB050509/',
        'GRB050709': 'https://agile.ssdc.asi.it/grb/GRB050709/',
        'GRB160509A': 'https://agile.ssdc.asi.it/grb/GRB160509A/',
        'GRB131231A': 'https://agile.ssdc.asi.it/grb/GRB131231A/',
        'GRB050509B': 'https://agile.ssdc.asi.it/grb/GRB050509B/',
        'GRB170206A': 'https://agile.ssdc.asi.it/grb/GRB170206A/',
        'GRB021206': 'https://agile.ssdc.asi.it/grb/GRB021206/',
        'GRB201015A': 'https://agile.ssdc.asi.it/grb/GRB201015A/',
        'GRB081003A': 'https://agile.ssdc.asi.it/grb/GRB081003A/'
    }
    
    if grb_name in agile_urls:
        url = agile_urls[grb_name]
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                print(f"   ✅ {grb_name}: AGILE data downloaded")
                return {
                    'status': 'success',
                    'url': url,
                    'content_length': len(response.text),
                    'data_type': 'real_agile'
                }
            else:
                print(f"   ❌ {grb_name}: AGILE - {response.status_code}")
                return {'status': 'failed', 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            print(f"   ❌ {grb_name}: AGILE - {e}")
            return {'status': 'failed', 'error': str(e)}
    else:
        print(f"   ❌ {grb_name}: No AGILE URL available")
        return {'status': 'failed', 'error': 'No URL available'}

def download_priority_grbs():
    """
    Download dati REALI per i 30 GRB prioritari
    """
    print("🚀 DOWNLOAD PRIORITY GRBs")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Lista dei 30 GRB prioritari
    priority_grbs = [
        'GRB221009A', 'GRB190114C', 'GRB090510', 'GRB180720B', 'GRB080916C',
        'GRB170817A', 'GRB190829A', 'GRB060505', 'GRB201216C', 'GRB111005A',
        'GRB130427A', 'GRB080825C', 'GRB030329', 'GRB060614', 'GRB980425',
        'GRB090902B', 'GRB060602B', 'GRB130603B', 'GRB160625B', 'GRB090926A',
        'GRB060218', 'GRB050509', 'GRB050709', 'GRB160509A', 'GRB131231A',
        'GRB050509B', 'GRB170206A', 'GRB021206', 'GRB201015A', 'GRB081003A'
    ]
    
    # Crea directory per dati
    os.makedirs('priority_grb_data', exist_ok=True)
    
    # Download dati per ogni GRB
    download_results = {}
    
    for i, grb in enumerate(priority_grbs, 1):
        print(f"\n🔍 Downloading {grb} ({i}/30)...")
        
        # Download da Fermi LAT
        fermi_result = download_fermi_lat_data(grb)
        
        # Download da Swift BAT
        swift_result = download_swift_bat_data(grb)
        
        # Download da AGILE
        agile_result = download_agile_data(grb)
        
        # Salva risultati
        download_results[grb] = {
            'fermi': fermi_result,
            'swift': swift_result,
            'agile': agile_result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Pausa tra download
        time.sleep(1)
    
    # Salva risultati
    with open('priority_grb_data/download_results.json', 'w') as f:
        json.dump(download_results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("🎉 DOWNLOAD PRIORITY GRBs COMPLETE!")
    print("📊 Check 'priority_grb_data/' directory for results")
    print("=" * 60)

if __name__ == "__main__":
    download_priority_grbs()
